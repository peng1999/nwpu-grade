import logging
from typing import Optional

import requests
from lxml import etree
from pydantic import Field
from requests.cookies import RequestsCookieJar

from .base import GradeItem, ScraperBase, DetailedItem, ConfigBase

logger = logging.getLogger(__name__)


class Config(ConfigBase):
    username: str = Field(description='学号')
    password: str = Field(description='密码')


class NWPUGradeItem(GradeItem, DetailedItem):
    daily_score: Optional[str]  # 平时成绩
    midterm_score: Optional[str]  # 期中成绩
    exp_score: Optional[str]  # 实验成绩
    test_score: Optional[str]  # 期末成绩

    def fmt_detail(self) -> str:
        texts = []
        if self.daily_score is not None:
            texts.append(f'平时成绩：{self.daily_score}\n')
        if self.midterm_score is not None:
            texts.append(f'期中成绩：{self.midterm_score}\n')
        if self.exp_score is not None:
            texts.append(f'实验成绩：{self.exp_score}\n')
        if self.test_score is not None:
            texts.append(f'期末成绩：{self.test_score}\n')
        return ''.join(texts)


class LoginFailedError(Exception):
    pass


class Scraper(ScraperBase):
    LOGIN_URL = "http://us.nwpu.edu.cn/eams/login.action"
    GRADE_URL = "http://us.nwpu.edu.cn/eams/teach/grade/course/person!historyCourseGrade.action" \
                "?projectType=MAJOR"

    def __init__(self, config):
        self.cookies: Optional[RequestsCookieJar] = None

        assert isinstance(config, Config)
        self.config: Config = config

    def login(self):
        login_data = {'username': self.config.username, 'password': self.config.password}
        r = requests.post(self.LOGIN_URL, data=login_data, allow_redirects=False)
        self.cookies = r.cookies

    def get_data(self):
        r = requests.get(self.GRADE_URL, cookies=self.cookies)
        if r.url.startswith(self.LOGIN_URL):
            return None
        else:
            return r

    def request_grade(self):
        logger.info('access us.nwpu.edu.cn to query grades...')
        r = None
        if self.cookies is not None:
            r = self.get_data()
        if r is None:
            logger.info('account info absent or expired, login...')
            self.login()
            r = self.get_data()
        if r is None:
            raise LoginFailedError()
        tree = etree.HTML(r.text)
        trs = tree.cssselect("div.grid table tbody tr")
        if len(trs) == 0:
            logger.warning(f'cannot find grades')
            logger.warning(f'history: {r.history}')
            logger.warning(f'url: {r.url}')
            logger.warning(f'status: {r.status_code}')
            logger.warning(f'text: {r.text}')

        grades = [
            NWPUGradeItem(
                semester=tr[0].text,
                course_name=tr[3][0].text,
                course_id=tr[1].text,
                credit=tr[5].text,
                score=tr[10].text,
                daily_score=tr[6].text,
                midterm_score=tr[7].text,
                exp_score=tr[8].text,
                test_score=tr[9].text,
            )
            for tr in trs
        ]

        return grades

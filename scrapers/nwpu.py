import logging
from typing import Optional

import requests
from lxml import etree
from pydantic import Field
from requests.cookies import RequestsCookieJar

from . import get_config
from .base import GradeItem, ScraperBase, DetailedItem, ConfigBase


class Config(ConfigBase):
    username: str = Field(description='用户名')
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


def strip_if_not_none(x: Optional[str]):
    if x is not None:
        return x.strip()
    else:
        return x


class Scraper(ScraperBase):
    LOGIN_URL = "http://us.nwpu.edu.cn/eams/login.action"
    GRADE_URL = "http://us.nwpu.edu.cn/eams/teach/grade/course/person!historyCourseGrade.action" \
                "?projectType=MAJOR"

    def __init__(self):
        self.cookies: Optional[RequestsCookieJar] = None
        self.username = get_config('username')
        self.password = get_config('password', passwd=True)

    def login(self):
        login_data = {'username': self.username, 'password': self.password}
        r = requests.post(self.LOGIN_URL, data=login_data, allow_redirects=False)
        self.cookies = r.cookies

    def get_data(self):
        r = requests.get(self.GRADE_URL, cookies=self.cookies)
        if r.url.startswith(self.LOGIN_URL):
            return None
        else:
            return r

    def request_grade(self):
        logging.info('access us.nwpu.edu.cn to query grades...')
        r = None
        if self.cookies is not None:
            r = self.get_data()
        if r is None:
            logging.info('account info absent or expired, login...')
            self.login()
            r = self.get_data()
        tree = etree.HTML(r.text)
        trs = tree.cssselect("div.grid table tbody tr")
        if len(trs) == 0:
            logging.warning(f'cannot find grades')
            logging.warning(f'history: {r.history}')
            logging.warning(f'url: {r.url}')
            logging.warning(f'status: {r.status_code}')
            logging.warning(f'text: {r.text}')

        grades = [
            NWPUGradeItem(
                semester=tr[0].text,
                course_name=tr[3][0].text,
                course_id=tr[1].text,
                credit=tr[5].text,
                score=tr[10].text.strip(),
                daily_score=strip_if_not_none(tr[6].text),
                midterm_score=strip_if_not_none(tr[7].text),
                exp_score=strip_if_not_none(tr[8].text),
                test_score=strip_if_not_none(tr[9].text),
            )
            for tr in trs
        ]

        return grades

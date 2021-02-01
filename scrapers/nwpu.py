import logging
from typing import Optional, List, Tuple

import requests
from lxml import etree
from pydantic import Field
from requests.cookies import RequestsCookieJar

from .base import GradeItem, ScraperBase, ConfigBase

logger = logging.getLogger(__name__)


class Config(ConfigBase):
    username: str = Field(description='学号')
    password: str = Field(description='密码')


class NWPUGradeItem(GradeItem):
    id: str

    def detail_id(self):
        return self.id


class DetailedItem(GradeItem):
    details: List[Tuple[str, str, str]]  # (项目，分数，百分比)

    def __str__(self) -> str:
        texts = [super().__str__(), '\n']
        texts.extend(f'{it[0]}（{it[2]}%）：{it[1]}\n' for it in self.details)
        return ''.join(texts)


class LoginFailedError(Exception):
    pass


class Scraper(ScraperBase):
    LOGIN_URL = "http://us.nwpu.edu.cn/eams/login.action"
    GRADE_URL = "http://us.nwpu.edu.cn/eams/teach/grade/course/person!historyCourseGrade.action" \
                "?projectType=MAJOR"
    DETAIL_URL = "http://us.nwpu.edu.cn/eams/teach/grade/course/person!info.action"

    def __init__(self, config):
        self.cookies: Optional[RequestsCookieJar] = None

        assert isinstance(config, Config)
        self.config: Config = config

    def login(self):
        login_data = {'username': self.config.username, 'password': self.config.password}
        r = requests.post(self.LOGIN_URL, data=login_data, allow_redirects=False)
        self.cookies = r.cookies

    def request(self, method, url, **kwargs):
        def auth_not_valid(r_):
            return (r_ is None or r_.url.startswith(self.LOGIN_URL) or
                    r_.text.startswith('This session has been expired'))

        r = None
        if self.cookies is not None:
            r = requests.request(method, url, cookies=self.cookies, **kwargs)
        if auth_not_valid(r):
            logger.info('account info absent or expired, login...')
            self.login()
            r = requests.request(method, url, cookies=self.cookies, **kwargs)
        if auth_not_valid(r):
            raise LoginFailedError()
        return r

    def request_grade(self):
        logger.info('access us.nwpu.edu.cn to query grades...')
        r = self.request('GET', self.GRADE_URL)
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
                id=tr[3][0].attrib['onclick'][9:-1]
            )
            for tr in trs
        ]

        return grades

    def request_grade_detail(self, detail_id) -> GradeItem:
        logger.info('access us.nwpu.edu.cn to query detail info...')
        r = self.request('POST', self.DETAIL_URL, data={'courseGrade.id': detail_id})
        tree = etree.HTML(r.text)
        info_rows = tree.cssselect('.infoTable tr')
        grid_rows = tree.cssselect('.gridtable > tbody > tr')

        details = [
            (row[0].text, row[4][0].text, row[5].text)
            for row in grid_rows
            if row[5].text is not None
        ]

        item = DetailedItem(
            semester=info_rows[2][1].text,
            course_name=info_rows[1][5].text,
            course_id=info_rows[1][3].text,
            credit=info_rows[2][3].text,
            score=info_rows[4][1][0].text,
            details=details
        )

        return item

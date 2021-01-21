import logging
from typing import Optional

import requests
from lxml import etree
from requests.cookies import RequestsCookieJar

from . import get_config
from .base import GradeItem, ScraperBase


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
        while r is None:
            logging.info('account info absent or expired, login...')
            self.login()
            r = self.get_data()
        tree = etree.HTML(r.text)
        trs = tree.cssselect("div.grid table tbody tr")

        grades = [
            GradeItem(
                semester=tr[0].text,
                course_name=tr[3][0].text,
                course_id=tr[1].text,
                credit=tr[5].text,
                score=tr[10].text.strip()
            )
            for tr in trs
        ]

        return grades

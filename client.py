#!/usr/bin/python3
import logging
import sys
import http.cookiejar
import urllib.error
import urllib.parse
import urllib.request
import getpass
from typing import List

from lxml import etree

from data import Course

try:
    import config
except ImportError:
    pass


def get_config(name: str, passwd=False):
    if 'config' in globals() and hasattr(config, name):
        return getattr(config, name)

    prompt = name + ': '
    if passwd:
        return getpass.getpass(prompt)
    return input(prompt)


class NWPUgrade:
    def __init__(self):
        self.values = {'username': get_config('username'), 'password': get_config('password', passwd=True)}
        self.loginUrl = "http://us.nwpu.edu.cn/eams/login.action"
        self.gradeUrl = "http://us.nwpu.edu.cn/eams/teach/grade/course/person!historyCourseGrade.action" \
                        "?projectType=MAJOR "
        self.cookie = http.cookiejar.CookieJar()
        self.handler = urllib.request.HTTPCookieProcessor(self.cookie)
        self.opener = urllib.request.build_opener(self.handler)
        self.data = urllib.parse.urlencode(self.values)
        self.grades: List[Course] = []

    def login(self):
        self.opener.open(self.loginUrl, self.data.encode('UTF-8'))
        result = self.opener.open(self.gradeUrl)
        content = result.read().decode('UTF-8')
        return content

    def grade(self):
        logging.info('access us.nwpu.edu.cn to query grades...')
        content = self.login()
        tree = etree.HTML(content)
        trs = tree.cssselect("div.grid table tbody tr")

        self.grades = [
            Course(
                semester=tr[0].text,
                course_name=tr[3][0].text,
                course_id=tr[1].text,
                credit=tr[5].text,
                score=tr[10].text.strip()
            )
            for tr in trs
        ]

    def printgrade(self, *, file=sys.stdout, avg_all=True, avg_by_year=True):
        def print_to_file(*args):
            print(*args, file=file)

        mark = 0
        credit = 0
        years = []
        mark_by_year = {}
        credit_by_year = {}
        for grade in self.grades:
            print_to_file()
            print_to_file(grade.semester)  # 学期
            print_to_file(grade.course_name)  # 课程名称
            print_to_file('学分：', grade.credit)  # 学分
            print_to_file('最终成绩：', grade.score)  # 成绩
            try:
                mark += float(grade.score) * float(grade.credit)
                credit += float(grade.credit)

                year = grade.semester.split()[0]
                if year not in mark_by_year:
                    years.append(year)
                    mark_by_year[year] = 0
                    credit_by_year[year] = 0
                mark_by_year[year] += float(grade.score) * float(grade.credit)
                credit_by_year[year] += float(grade.credit)
            except ValueError:
                pass

        if avg_by_year:
            print_to_file()
            for year in years:
                print_to_file(year, '学年学分绩', mark_by_year[year] / credit_by_year[year])

        if avg_all:
            print_to_file()
            if credit != 0:
                print_to_file('总学分绩', mark / credit)


if __name__ == "__main__":
    NWPU = NWPUgrade()
    NWPU.grade()
    NWPU.printgrade()

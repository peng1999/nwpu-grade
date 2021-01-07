#!/usr/bin/python3
# _*_coding:utf-8_*_

import http.cookiejar
import urllib.error
import urllib.parse
import urllib.request
import getpass
# noinspection PyUnresolvedReferences
from lxml import cssselect, etree

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
        self.grades = {}

    def login(self):
        self.opener.open(self.loginUrl, self.data.encode('UTF-8'))
        result = self.opener.open(self.gradeUrl)
        content = result.read().decode('UTF-8')
        return content

    def grade(self):
        content = self.login()
        tree = etree.HTML(content)
        trs = tree.cssselect("div.grid table tbody tr")

        self.grades = [(tr[0].text, tr[3][0].text, tr[5].text, tr[10].text, tr[11].text) for tr
                       in trs]

    def printgrade(self):
        mark = 0
        credit = 0
        years = []
        mark_by_year = {}
        credit_by_year = {}
        for grade in self.grades:
            print()
            print(grade[0])  # 学期
            print(grade[1])  # 课程名称
            print('学分：', grade[2])  # 学分
            print('最终成绩：', grade[3])  # 成绩
            try:
                mark += float(grade[3]) * float(grade[2])
                credit += float(grade[2])

                year = grade[0].split()[0]
                if year not in mark_by_year:
                    years.append(year)
                    mark_by_year[year] = 0
                    credit_by_year[year] = 0
                mark_by_year[year] += float(grade[3]) * float(grade[2])
                credit_by_year[year] += float(grade[2])
            except ValueError:
                pass

        print()
        for year in years:
            print(year, '学年学分绩', mark_by_year[year] / credit_by_year[year])

        print()
        if credit != 0:
            print('你的总学分绩', mark / credit)


if __name__ == "__main__":
    NWPU = NWPUgrade()
    NWPU.grade()
    NWPU.printgrade()

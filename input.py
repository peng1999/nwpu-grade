#!/usr/bin/python3
# _*_coding:utf-8_*_

import http.cookiejar
import urllib.error
import urllib.parse
import urllib.request
from lxml import cssselect, etree


class NWPUgrade:
    def __init__(self):
        self.values = {'username': input('username: '), 'password': input('password: ')}
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

        self.grades = [(tr[0].text, tr[3][0].text, tr[5].text, tr[10].text, tr[11].text) for tr in trs]
        self.printgrade()

    def printgrade(self):
        mark = 0
        credit = 0
        for grade in self.grades:
            print(grade[0])  # 学期
            print(grade[1])  # 课程名称
            print('学分：', grade[2])  # 学分
            print('最终成绩：', grade[3])  # 成绩
            if grade[3].strip() != 'P':
                mark += float(grade[3]) * float(grade[2])
                credit += float(grade[2])
        print('你的学分绩', mark / credit)


NWPU = NWPUgrade()
NWPU.grade()

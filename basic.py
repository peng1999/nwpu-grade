#!/usr/bin/python
# _*_coding:utf-8_*_

import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import http.cookiejar
import re


class NWPUgrade:
    def __init__(self):
        try:
            self.values = {'username': "username", 'password': "password"}
            self.loginUrl = "http://us.nwpu.edu.cn/eams/login.action"
            self.gradeUrl = "http://us.nwpu.edu.cn/eams/teach/grade/course/person!historyCourseGrade.action" \
                            "?projectType=MAJOR "
            self.cookie = http.cookiejar.CookieJar()
            self.handler = urllib.request.HTTPCookieProcessor(self.cookie)
            self.opener = urllib.request.build_opener(self.handler)
            self.data = urllib.parse.urlencode(self.values)
            self.grades = {}
        except:
            print('ERROR')

    def login(self):
        try:

            result = self.opener.open(self.loginUrl, self.data)
            result = self.opener.open(self.gradeUrl)
            content = result.read().decode('UTF-8')
            return content
        except:
            print('ERROR')

    def grade(self):
        try:
            content = self.login()
            pattern = re.compile(
                '<tr>.*?<td>(.*?)</td.*?<a.*?>(.*?)</a.*?<td.*?<td>(.*?)</td>.*?<td.*?<td.*?<td.*?<td.*?<td.*?<td.*?>\s*(.*?)\r\n</td>.*?</td>.*?</tr>',
                re.S)
            self.grades = re.findall(pattern, content)
            self.printgrade()
        except:
            print('ERROR')

    def printgrade(self):
        try:
            mark = 0
            credit = 0
            for grade in self.grades:
                print(grade[0])  # 学期
                print(grade[1])  # 课程名称
                print('学分：', grade[2])  # 学分
                print('最终成绩：', grade[3])  # 成绩
                print()
                if grade[3] != 'P':
                    mark += float(grade[3]) * float(grade[2])
                    credit += float(grade[2])
            print('您的学分绩', mark / credit)
        except:
            print('ERROR')


NWPU = NWPUgrade()
NWPU.grade()

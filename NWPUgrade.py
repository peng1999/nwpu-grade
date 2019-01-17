#!/usr/bin/python
# _*_coding:utf-8_*_

import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import http.cookiejar
import re
import time
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from config import username, password, from_addr, smtp_password, to_addr, smtp_server
import smtplib


class NWPUgrade:
    def __init__(self):
        try:
            self.values = {'username': username, 'password': password}
            self.loginUrl = "http://us.nwpu.edu.cn/eams/login.action"
            self.gradeUrl = "http://us.nwpu.edu.cn/eams/teach/grade/course/person!historyCourseGrade.action" \
                            "?projectType=MAJOR "
            self.message = ''
            self.cookie = http.cookiejar.CookieJar()
            self.handler = urllib.request.HTTPCookieProcessor(self.cookie)
            self.opener = urllib.request.build_opener(self.handler)
            self.data = urllib.parse.urlencode(self.values)
            self.grades = {}
        except:
            print('ERROR1')

    def login(self):
        try:
            result = self.opener.open(self.loginUrl, self.data)
            result = self.opener.open(self.gradeUrl)
            content = result.read().decode('UTF-8')
            return content
        except:
            print('ERROR2')

    def grade(self):
        try:
            content = self.login()
            pattern = re.compile(
                '<tr>.*?<td>(.*?)</td.*?<a.*?>(.*?)</a.*?<td.*?<td>(.*?)</td>.*?<td.*?<td.*?<td.*?<td.*?<td.*?<td.*?>\s*(.*?)\r\n</td>.*?</td>.*?</tr>',
                re.S)
            self.grades = re.findall(pattern, content)
        except:
            print('ERROR3')

    def printgrade(self):
        try:
            mark = 0
            credit = 0
            for grade in self.grades:
                print(grade[0])  # 学期
                print(grade[1])  # 课程名称
                print('学分：', grade[2])  # 学分
                print('最终成绩：', grade[3])  # 成绩
                if grade[3] != 'P':
                    mark += float(grade[3]) * float(grade[2])
                    credit += float(grade[2])
            print('你的学分绩', mark / credit)
        except:
            print('ERROR4')

    def getgrades(self):
        try:
            return self.grades
        except:
            print('ERROR5')


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr(( \
        Header(name, 'utf-8').encode(), addr.encode('utf-8') if isinstance(addr, str) else addr))


def sendemail(text):
    msg = MIMEText(text, 'plain', 'utf-8')
    msg['From'] = _format_addr('Python <%s>' % from_addr)
    msg['To'] = _format_addr('管理员 <%s>' % to_addr)
    msg['Subject'] = Header('您的成绩单', 'utf-8').encode()
    server = smtplib.SMTP_SSL(smtp_server, 465)
    server.set_debuglevel(1)
    server.login(from_addr, smtp_password)
    server.sendmail(from_addr, [to_addr], msg.as_string())
    server.quit()


def main():
    NWPU = NWPUgrade()
    NWPU.grade()
    NWPU.printgrade()  # 先打印目前的成绩
    grades = NWPU.getgrades()
    SubjectNumber = len(grades)
    while True:
        try:
            time.sleep(15 * 60)  # 15分钟检测一次
            NWPU.grade()
            Newgrades = NWPU.getgrades()
            NewNumber = len(Newgrades)
            if NewNumber > SubjectNumber:  # 有新成绩
                SubjectNumber = NewNumber
                mark = 0
                credit = 0
                Newgrade = []
                for grade in Newgrades:
                    if grade not in grades:
                        Newgrade.append(grade)  # 可能同时更新复数个
                    if grade[3] != 'P':
                        mark += float(grade[3]) * float(grade[2])
                        credit += float(grade[2])
                GPA = mark / credit  # 计算学分绩
                grades = Newgrades
                text = ''
                for grade in Newgrade:
                    text = text + "学期：%s  \n课程名称：%s  \n学分：%s  \n成绩：%s  \n" % (grade[0], grade[1], grade[2], grade[3])
                text = text + '学分绩：%f' % GPA
                sendemail(text)
        except:
            continue


if __name__ == '__main__':
    main()

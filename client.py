#!/usr/bin/python3
import abc
import logging
import getpass
from collections import OrderedDict
from typing import List

import requests
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


class ScraperBase(abc.ABC):
    @abc.abstractmethod
    def request_grade(self): ...

    def avg_by_year(self, grades: List[Course]):
        total_mark = 0.
        total_credit = 0.
        years = []
        mark_by_year: OrderedDict[str, float] = OrderedDict()
        credit_by_year: OrderedDict[str, float] = OrderedDict()
        for grade in grades:
            try:
                score = float(grade.score)
                credit = float(grade.credit)
            except ValueError:
                pass
            else:
                total_mark += score * credit
                total_credit += credit

                year = grade.semester.split()[0]
                if year not in mark_by_year:
                    years.append(year)

                mark_by_year[year] = mark_by_year.get(year, 0) + score * credit
                credit_by_year[year] = credit_by_year.get(year, 0) + credit

        gpa_by_year = {}
        for year in years:
            gpa_by_year[year] = mark_by_year[year] / credit_by_year[year]

        total_gpa = float('nan')
        if total_credit != 0:
            total_gpa = total_mark / total_credit

        return total_gpa, gpa_by_year

    def fmt_grades(self, grades: List[Course]):
        msg: List[str] = []

        for grade in grades:
            msg.append(f'\n'
                       f'{grade.semester}\n'  # 学期
                       f'{grade.course_name}\n'  # 课程名称
                       f'学分：{grade.credit}\n'  # 学分
                       f'最终成绩：{grade.score}\n'  # 成绩
                       )

        return ''.join(msg)

    def fmt_gpa(self, grades: List[Course], by_year=False):
        total_gpa, gpa_by_year = self.avg_by_year(grades)
        msg: List[str] = []

        if by_year:
            for year in gpa_by_year:
                msg.append(f'{year} 学年学分绩：{gpa_by_year[year]}\n')
            msg.append('\n')

        msg.append(f'总学分绩：{total_gpa}\n')

        return ''.join(msg)


class NWPUScraper(ScraperBase):
    LOGIN_URL = "http://us.nwpu.edu.cn/eams/login.action"
    GRADE_URL = "http://us.nwpu.edu.cn/eams/teach/grade/course/person!historyCourseGrade.action" \
                "?projectType=MAJOR"

    def __init__(self):
        self.username = get_config('username')
        self.password = get_config('password', passwd=True)

    def request_grade(self):
        logging.info('access us.nwpu.edu.cn to query grades...')
        login_data = {'username': self.username, 'password': self.password}
        r = requests.post(self.LOGIN_URL, data=login_data, allow_redirects=False)
        cookies = r.cookies
        r = requests.get(self.GRADE_URL, cookies=cookies)
        tree = etree.HTML(r.text)
        trs = tree.cssselect("div.grid table tbody tr")

        grades = [
            Course(
                semester=tr[0].text,
                course_name=tr[3][0].text,
                course_id=tr[1].text,
                credit=tr[5].text,
                score=tr[10].text.strip()
            )
            for tr in trs
        ]

        return grades


class BUAAScraper(ScraperBase):
    GRADE_URL = "https://app.buaa.edu.cn/buaascore/wap/default/index"

    def __init__(self):
        self.cookie = get_config('cookie')

    def request_grade(self):
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile '
                          'Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://app.buaa.edu.cn',
            'Cookie': self.cookie,
        }

        r = requests.post(self.GRADE_URL, headers=headers)
        json_list = r.json()['d']
        grades = [Course(
                      semester=json_list[i]['year']
                               + ' ' + ('秋' if json_list[i]['xq'] == '1' else '春'),
                      course_name=json_list[i]['kcmc'],
                      course_id=json_list[i]['kcmc'],
                      credit=json_list[i]['xf'],
                      score=json_list[i]['kccj'],
                  )
                  for i in json_list]

        return grades


def main():
    scraper = BUAAScraper()
    grades = scraper.request_grade()

    print('\n'.join([
        scraper.fmt_grades(grades),
        scraper.fmt_gpa(grades, by_year=True),
    ]))


if __name__ == "__main__":
    main()

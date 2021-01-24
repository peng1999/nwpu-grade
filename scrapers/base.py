import abc
import getpass
import json
import logging
import sys
from collections import OrderedDict
from datetime import datetime
from typing import List, Dict

from pydantic import Field, BaseModel

try:
    # noinspection PyUnresolvedReferences
    import config
except ImportError:
    pass


def get_config(name: str, passwd=False):
    if 'config' in globals() and hasattr(config, name):
        return getattr(config, name)

    if sys.argv[0].endswith('bot.py'):
        raise ValueError(f'Missing configuration `{name}`')

    prompt = name + ': '
    if passwd:
        return getpass.getpass(prompt)
    return input(prompt)


class ConfigBase(BaseModel):
    interval: int = Field(60 * 60, ge=30 * 60, description='查询间隔（至少1800秒）')

    @classmethod
    def get_key_name(cls, *, required=False) -> Dict[str, str]:
        """返回一个词典，代表配置项和名称"""
        fields = cls.__fields__
        return {name: fields[name].field_info.description
                for name in fields
                if not required or fields[name].required}


class GradeItem(BaseModel):
    semester: str
    course_name: str
    course_id: str
    score: str
    credit: str


class GradeData(BaseModel):
    courses: List[GradeItem]
    time: datetime = Field(default_factory=datetime.now)

    @staticmethod
    def load(filename):
        with open(filename, 'r') as f:
            return GradeData(**json.load(f))

    def save(self, filename):
        logging.info(f'write data to {filename}')
        with open(filename, 'w') as f:
            f.write(self.json())


def diff_courses(new: List[GradeItem], old: List[GradeItem]):
    """returns new courses compared to old"""
    id_score_pairs = [(course.course_id, course.score) for course in old]
    return [
        course for course in new
        if (course.course_id, course.score) not in id_score_pairs
    ]


def semesters(grades: List[GradeItem]):
    s: List[str] = []
    for course in grades:
        if course.semester not in s:
            s.append(course.semester)
    return s


def courses_by_semester(grades: List[GradeItem], semester: str):
    return [course for course in grades if course.semester == semester]


class ScraperBase(abc.ABC):
    @abc.abstractmethod
    def request_grade(self) -> List[GradeItem]:
        ...

    @classmethod
    def avg_by_year(cls, grades: List[GradeItem]):
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

    @classmethod
    def fmt_grades(cls, grades: List[GradeItem]):
        msg: List[str] = []

        for grade in grades:
            msg.append(f'\n'
                       f'{grade.semester}\n'  # 学期
                       f'{grade.course_name}\n'  # 课程名称
                       f'学分：{grade.credit}\n'  # 学分
                       f'最终成绩：{grade.score}\n'  # 成绩
                       )

        return ''.join(msg)

    @classmethod
    def fmt_gpa(cls, grades: List[GradeItem], by_year=False):
        total_gpa, gpa_by_year = cls.avg_by_year(grades)
        msg: List[str] = []

        if by_year:
            for year in gpa_by_year:
                msg.append(f'{year} 学年学分绩：{gpa_by_year[year]}\n')
            msg.append('\n')

        msg.append(f'总学分绩：{total_gpa}\n')

        return ''.join(msg)


class DetailedItem(abc.ABC):
    @abc.abstractmethod
    def fmt_detail(self) -> str: ...

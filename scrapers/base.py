import abc
import json
import logging
from collections import OrderedDict
from datetime import datetime
from typing import List

from pydantic import Field, BaseModel


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

    def diff(self, old: 'GradeData'):
        id_score_pairs = [(course.course_id, course.score) for course in old.courses]
        return [
            course for course in self.courses
            if (course.course_id, course.score) not in id_score_pairs
        ]

    def semesters(self):
        s: List[str] = []
        for course in self.courses:
            if course.semester not in s:
                s.append(course.semester)
        return s

    def courses_by_semester(self, semester):
        return [course for course in self.courses if course.semester == semester]


class ScraperBase(abc.ABC):
    @abc.abstractmethod
    def request_grade(self) -> List[GradeItem]: ...

    def avg_by_year(self, grades: List[GradeItem]):
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

    def fmt_grades(self, grades: List[GradeItem]):
        msg: List[str] = []

        for grade in grades:
            msg.append(f'\n'
                       f'{grade.semester}\n'  # 学期
                       f'{grade.course_name}\n'  # 课程名称
                       f'学分：{grade.credit}\n'  # 学分
                       f'最终成绩：{grade.score}\n'  # 成绩
                       )

        return ''.join(msg)

    def fmt_gpa(self, grades: List[GradeItem], by_year=False):
        total_gpa, gpa_by_year = self.avg_by_year(grades)
        msg: List[str] = []

        if by_year:
            for year in gpa_by_year:
                msg.append(f'{year} 学年学分绩：{gpa_by_year[year]}\n')
            msg.append('\n')

        msg.append(f'总学分绩：{total_gpa}\n')

        return ''.join(msg)

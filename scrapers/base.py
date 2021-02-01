import abc
import json
import logging
from collections import OrderedDict
from base64 import b64encode, b64decode
from datetime import datetime
from typing import List, Dict

from pydantic import Field, BaseModel

from db import User

logger = logging.getLogger(__name__)


class B64BaseModel(BaseModel):

    def base64(self):
        return b64encode(self.json().encode('utf-8'))

    @classmethod
    def parse_base64(cls, text: bytes):
        return cls(**json.loads(b64decode(text).decode('utf-8')))


class ConfigBase(B64BaseModel):
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

    class Config:
        anystr_strip_whitespace = True

    def __str__(self):
        return (f'{self.semester}\n'  # 学期
                f'{self.course_name}\n'  # 课程名称
                f'学分：{self.credit}\n'  # 学分
                f'最终成绩：{self.score}\n'  # 成绩
                )

    def detail_id(self):
        return self.course_id


class GradeData(B64BaseModel):
    courses: List[GradeItem]
    time: datetime = Field(default_factory=datetime.now)

    @classmethod
    def load(cls, user_id):
        user: User = User.get(user_id=user_id)
        return cls.parse_base64(user.data)

    def save(self, user_id):
        logger.info(f'updating data of {user_id}')
        query = User.update(data=self.base64()).where(User.user_id == user_id)
        query.execute()


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
    config: ConfigBase

    @abc.abstractmethod
    def request_grade(self) -> List[GradeItem]:
        ...

    def request_grade_detail(self, detail_id) -> GradeItem:
        items = self.request_grade()
        for item in items:
            if item.detail_id() == detail_id:
                return item
        raise ValueError('id not found')

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
        return '\n'.join(str(grade) for grade in grades)

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

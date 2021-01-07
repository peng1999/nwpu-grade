import json
import logging
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class Course(BaseModel):
    semester: str
    course_name: str
    course_id: str
    score: str
    credit: str


class GradeData(BaseModel):
    courses: List[Course]
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

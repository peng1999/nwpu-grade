import requests
from pydantic import Field

from .base import GradeItem, ScraperBase, ConfigBase


class Config(ConfigBase):
    cookie: str = Field(description='用于登录的 Cookie')
    data: str = Field(description='查询的学期（例如`xq=1&year=2020-2021`）')


class Scraper(ScraperBase):
    GRADE_URL = "https://app.buaa.edu.cn/buaascore/wap/default/index"

    def __init__(self, config):
        assert isinstance(config, Config)
        self.config: Config = config

    def request_grade(self):
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile '
                          'Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://app.buaa.edu.cn',
            'Cookie': self.config.cookie,
        }

        r = requests.post(self.GRADE_URL, data=self.config.data, headers=headers)
        json_list = r.json()['d']
        grades = [
            GradeItem(
                semester=json_list[i]['year'] + ' ' + ('秋' if json_list[i]['xq'] == '1' else '春'),
                course_name=json_list[i]['kcmc'],
                course_id=json_list[i]['kcmc'],
                credit=json_list[i]['xf'],
                score=json_list[i]['kccj'],
            )
            for i in json_list
        ]

        return grades

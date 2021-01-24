from datetime import datetime
from functools import wraps
from typing import List, Optional

from peewee import fn
from telegram import Update
from telegram.utils.helpers import escape_markdown

from db import User
from scrapers import Scraper
from scrapers.base import GradeItem


def restricted(func):
    @wraps(func)
    def wrapped(update: Update, context, *args, **kwargs):
        user_id = update.effective_user.id

        is_in_list = (User
                      .select(fn.COUNT(User.user_id).alias('count'))
                      .where(User.user_id == user_id)
                      .get()
                      .count) == 1
        if not is_in_list:
            update.effective_chat.send_message(
                "请输入 /start 以开始")
            return
        return func(update, context, *args, **kwargs)

    return wrapped


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


def to_callback_data(prefix, data):
    return f'{prefix}:{data}'


def from_callback_data(data: str):
    _, _, data = data.partition(':')
    return data


def print_courses(courses: List[GradeItem], *, avg_by_year=True, avg_all=True):
    if avg_by_year and not avg_all:
        raise ValueError('avg_all should be True when avg_by_year is True')

    msg = [Scraper.fmt_grades(courses)]

    if avg_by_year or avg_all:
        msg.append(Scraper.fmt_gpa(courses, by_year=avg_by_year))

    return '\n'.join(msg)


def render_grade(courses: List[GradeItem], time: Optional[datetime] = None):
    if time is None:
        time = datetime.now()
    text = print_courses(courses, avg_by_year=False)
    text = escape_markdown(text, version=2)
    text += f'\n_{time:%F %T}_'.replace('-', '\\-')
    return text

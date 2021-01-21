import logging
from datetime import datetime
from functools import wraps
from typing import List, Optional

from telegram import Update
from telegram.utils.helpers import escape_markdown

import config
from scrapers import Scraper
from scrapers.base import GradeItem


def restricted(func):
    @wraps(func)
    def wrapped(update: Update, context, *args, **kwargs):
        user_id = update.effective_user.id
        username = update.effective_user.username
        if int(user_id) != config.allow_user and username != config.allow_user:
            logging.warning(f'Unauthorized access denied for {user_id} `{username}`.')
            update.effective_chat.send_message(
                "I'm not your bot! Refer to https://github.com/peng1999/nwpu-grade to deploy your "
                "own bot.")
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

import logging
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from bot.util import restricted, build_menu, render_grade
from bot import GRADE_DATA_FILE
from scrapers import Scraper
from scrapers.base import GradeData


@restricted
def query(update: Update, context: CallbackContext):
    logging.info(f'/query from user {update.effective_user.id}')

    try:
        # If there exists cached data within 1 hour, use it
        grade_data = GradeData.load(GRADE_DATA_FILE)
        if datetime.now() - grade_data.time > timedelta(hours=1):
            raise FileNotFoundError

    except FileNotFoundError:
        # If not, access server to update it
        nwpu_client = Scraper()
        grades = nwpu_client.request_grade()
        grade_data = GradeData(courses=grades)
        grade_data.save(GRADE_DATA_FILE)

    semester = grade_data.semesters()
    button_list = [InlineKeyboardButton(s, callback_data=s) for s in semester]
    button_list.append(InlineKeyboardButton('全部', callback_data='all'))
    markup = InlineKeyboardMarkup(build_menu(button_list, 2))

    text = render_grade(grade_data.courses, grade_data.time)
    update.message.reply_text(text, reply_markup=markup, parse_mode='MarkdownV2')


def button(update: Update, context: CallbackContext):
    q = update.callback_query
    logging.info(f'button clicked with data=`{q.data}`')
    grade_data = GradeData.load(GRADE_DATA_FILE)
    if q.data == 'all':
        courses = grade_data.courses
    else:
        courses = grade_data.courses_by_semester(q.data)
    text = render_grade(courses, grade_data.time)
    q.answer()
    # bypass the exception raised when text not change
    if text.strip() != update.effective_message.text.strip():
        q.edit_message_text(text,
                            reply_markup=update.effective_message.reply_markup,
                            parse_mode='MarkdownV2')

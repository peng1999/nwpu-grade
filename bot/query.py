import logging
from typing import List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from bot.util import restricted, build_menu, render_grade, to_callback_data, from_callback_data
from scrapers import Scraper, get_scraper
from scrapers.base import courses_by_semester, semesters, GradeItem, DetailedItem


def menu_from_grades(grades: List[GradeItem], detail=None):
    semester = semesters(grades)
    button_list = [InlineKeyboardButton(s, callback_data=to_callback_data('query/list', s))
                   for s in semester]
    button_list.append(
        InlineKeyboardButton('全部', callback_data=to_callback_data('query/list', 'all')))
    if detail is not None:
        button_list.append(
            InlineKeyboardButton('查询小分', callback_data=to_callback_data('query/detail', detail)))
    markup = InlineKeyboardMarkup(build_menu(button_list, 2))
    return markup


@restricted
def query(update: Update, context: CallbackContext):
    logging.info(f'/query from user {update.effective_user.id}')

    client = get_scraper()
    grades = client.request_grade()

    markup = menu_from_grades(grades)

    text = render_grade(grades)
    update.message.reply_text(text, reply_markup=markup, parse_mode='MarkdownV2')


@restricted
def query_button(update: Update, context: CallbackContext):
    q = update.callback_query
    logging.info(f'button clicked with data=`{q.data}`')
    data = from_callback_data(q.data)

    client = get_scraper()
    grades = client.request_grade()

    if data == 'all':
        courses = grades
        markup = menu_from_grades(grades)
    else:
        courses = courses_by_semester(grades, data)
        markup = menu_from_grades(grades, detail=data)

    text = render_grade(courses)
    q.answer()
    # bypass the exception raised when text not change
    if text.strip() != update.effective_message.text_markdown_v2.strip():
        q.edit_message_text(text,
                            reply_markup=markup,
                            parse_mode='MarkdownV2')


@restricted
def detail_button(update: Update, context: CallbackContext):
    q = update.callback_query
    q.answer()
    data = from_callback_data(q.data)

    client = get_scraper()
    grades = client.request_grade()
    courses = courses_by_semester(grades, data)

    button_list = [
        InlineKeyboardButton(
            c.course_name,
            callback_data=to_callback_data('query/single', c.course_id))
        for c in courses
    ]
    button_list.append(
        InlineKeyboardButton('返回', callback_data=to_callback_data('query/list', data)))
    markup = InlineKeyboardMarkup(build_menu(button_list, 2))

    q.edit_message_text('请选择要查看的课程', reply_markup=markup)


@restricted
def detail_item_button(update: Update, context: CallbackContext):
    q = update.callback_query
    q.answer()
    data = from_callback_data(q.data)

    client = get_scraper()
    grades = client.request_grade()

    text = ''
    for c in grades:
        if c.course_id == data:
            msg = [Scraper.fmt_grades([c])]
            if isinstance(c, DetailedItem):
                msg.append(c.fmt_detail())
            text = '\n'.join(msg)
            break

    q.edit_message_text(text, reply_markup=update.effective_message.reply_markup)

import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from bot.util import restricted, build_menu, render_grade
from bot import get_scraper
from scrapers.base import courses_by_semester, semesters


@restricted
def query(update: Update, context: CallbackContext):
    logging.info(f'/query from user {update.effective_user.id}')

    client = get_scraper()
    grades = client.request_grade()

    semester = semesters(grades)
    button_list = [InlineKeyboardButton(s, callback_data=s) for s in semester]
    button_list.append(InlineKeyboardButton('全部', callback_data='all'))
    markup = InlineKeyboardMarkup(build_menu(button_list, 2))

    text = render_grade(grades)
    update.message.reply_text(text, reply_markup=markup, parse_mode='MarkdownV2')


def button(update: Update, context: CallbackContext):
    q = update.callback_query
    logging.info(f'button clicked with data=`{q.data}`')

    client = get_scraper()
    grades = client.request_grade()

    if q.data == 'all':
        courses = grades
    else:
        courses = courses_by_semester(grades, q.data)
    text = render_grade(courses)
    q.answer()
    # bypass the exception raised when text not change
    if text.strip() != update.effective_message.text_markdown_v2.strip():
        q.edit_message_text(text,
                            reply_markup=update.effective_message.reply_markup,
                            parse_mode='MarkdownV2')

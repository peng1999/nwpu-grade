import logging
import os
import threading
from datetime import datetime, timedelta
from functools import wraps
from io import StringIO
from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CallbackContext, CommandHandler, CallbackQueryHandler
from telegram.update import Update

import config
from client import NWPUgrade
from data import GradeData, Course

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def restricted(func):
    @wraps(func)
    def wrapped(update: Update, context, *args, **kwargs):
        user_id = update.effective_user.id
        username = update.effective_user.username
        if user_id != config.allow_user and username != config.allow_user:
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


try:
    GRADE_DATA_PATH = config.data_path
except AttributeError:
    GRADE_DATA_PATH = '.'
GRADE_DATA_FILE = os.path.join(GRADE_DATA_PATH, 'data.json')

updater = Updater(token=config.token, use_context=True)
stop_flag = threading.Event()  # background thread is running when not set
stop_flag.set()


def print_courses(courses: List[Course]):
    nwpu_client = NWPUgrade()
    nwpu_client.grades = courses
    with StringIO() as sio:
        nwpu_client.printgrade(file=sio)
        return sio.getvalue()


@restricted
def start(update: Update, context: CallbackContext):
    logging.info(f'/start from user {update.effective_user.id}')
    username = update.effective_user.username
    if username is not None:
        logging.info(f'username is `{username}`')

    update.effective_chat.send_message(f'Hello {update.effective_user.full_name}!')


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
        nwpu_client = NWPUgrade()
        nwpu_client.grade()
        grade_data = GradeData(courses=nwpu_client.grades)
        grade_data.save(GRADE_DATA_FILE)

    semester = grade_data.semesters()
    button_list = [InlineKeyboardButton(s, callback_data=s) for s in semester]
    button_list.append(InlineKeyboardButton('全部', callback_data='all'))
    markup = InlineKeyboardMarkup(build_menu(button_list, 2))

    text = print_courses(grade_data.courses)
    update.message.reply_text(text, reply_markup=markup)
    # update.effective_chat.send_message(text)


def button(update: Update, context: CallbackContext):
    q = update.callback_query
    logging.info(f'button clicked with data=`{q.data}`')
    grade_data = GradeData.load(GRADE_DATA_FILE)
    if q.data == 'all':
        courses = grade_data.courses
    else:
        courses = grade_data.courses_by_semester(q.data)
    text = print_courses(courses)
    q.answer()
    # bypass the exception raised when text not change
    if text.strip() != update.effective_message.text.strip():
        q.edit_message_text(text, reply_markup=update.effective_message.reply_markup)


def query_diff():
    logging.info('querying diff')

    try:
        grade_data = GradeData.load(GRADE_DATA_FILE)
    except FileNotFoundError:
        return []

    nwpu_client = NWPUgrade()
    nwpu_client.grade()
    new_grade_data = GradeData(courses=nwpu_client.grades)
    new_grade_data.save(GRADE_DATA_FILE)

    return new_grade_data.diff(grade_data)


def listen_loop(chat_id: int):
    wait_time = 60 * 60
    while not stop_flag.wait(timeout=wait_time):
        # everyone is sleeping during this time, so don't update
        if 3 <= datetime.now().hour < 7:
            continue
        diff = query_diff()
        if len(diff) > 0:
            updater.bot.send_message(chat_id, 'New updates!')
            text = print_courses(diff)
            updater.bot.send_message(chat_id, text)
    updater.bot.send_message(chat_id, 'Monitor stopped!')
    logging.info('background thread stopped')


@restricted
def start_listen(update: Update, context: CallbackContext):
    if not stop_flag.is_set():
        update.effective_chat.send_message('Already started!')
        return
    stop_flag.clear()

    background_thread = threading.Thread(name='background', target=listen_loop,
                                         args=(update.effective_chat.id,))
    background_thread.daemon = True
    background_thread.start()
    update.effective_chat.send_message('Started monitor grade change!')
    logging.info('background thread started')


@restricted
def stop_listen(update: Update, context: CallbackContext):
    if stop_flag.is_set():
        update.effective_chat.send_message('Already stopped!')
        return
    logging.info('stopping background thread...')
    stop_flag.set()


dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('query', query))
dispatcher.add_handler(CallbackQueryHandler(button))
dispatcher.add_handler(CommandHandler('start_listen', start_listen))
dispatcher.add_handler(CommandHandler('stop_listen', stop_listen))
updater.start_polling()

updater.idle()

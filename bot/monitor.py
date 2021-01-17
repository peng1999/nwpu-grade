import logging
import threading
from datetime import datetime

from telegram import Update
from telegram.ext import CallbackContext

import config
from bot.util import print_courses, restricted
from bot import GRADE_DATA_FILE, updater
from scrapers import Scraper
from scrapers.base import GradeData

stop_flag = threading.Event()  # background thread is running when not set
stop_flag.set()


def query_diff():
    logging.info('querying diff')

    try:
        grade_data = GradeData.load(GRADE_DATA_FILE)
    except FileNotFoundError:
        return []

    nwpu_client = Scraper()
    grades = nwpu_client.request_grade()
    new_grade_data = GradeData(courses=grades)
    new_grade_data.save(GRADE_DATA_FILE)

    return new_grade_data.diff(grade_data), grade_data.diff(new_grade_data)


def listen_loop(chat_id: int):
    try:
        wait_time = config.interval
    except AttributeError:
        wait_time = 30 * 60

    try:
        while not stop_flag.wait(timeout=wait_time):
            # everyone is sleeping during this time, so don't update
            if 3 <= datetime.now().hour < 7:
                continue
            diff, redraw = query_diff()
            if len(diff) > 0:
                msg = '有新的成绩！\n\n'
                msg += print_courses(diff, avg_all=False, avg_by_year=False)
                updater.bot.send_message(chat_id, msg)
            if len(redraw) > 0:
                msg = '有成绩被撤回：\n\n'
                msg += '，'.join([course.course_name for course in redraw])
                updater.bot.send_message(chat_id, msg)
    finally:
        updater.bot.send_message(chat_id, 'Monitor stopped!')
        logging.info('background thread stopped')


@restricted
def start_monitor(update: Update, context: CallbackContext):
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
def stop_monitor(update: Update, context: CallbackContext):
    if stop_flag.is_set():
        update.effective_chat.send_message('Already stopped!')
        return
    logging.info('stopping background thread...')
    stop_flag.set()


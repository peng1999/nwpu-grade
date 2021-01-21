import logging
import threading
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

import config
from bot.util import print_courses, restricted
from bot import GRADE_DATA_FILE, updater, get_scraper
from scrapers.base import GradeData, diff_courses

stop_flag = threading.Event()  # background thread is running when not set
stop_flag.set()


def query_diff():
    logging.info('querying diff')

    try:
        grade_data = GradeData.load(GRADE_DATA_FILE)
    except FileNotFoundError:
        return []

    grades = get_scraper().request_grade()
    new_grade_data = GradeData(courses=grades)
    new_grade_data.save(GRADE_DATA_FILE)

    return (diff_courses(new_grade_data.courses, grade_data.courses),
            diff_courses(grade_data.courses, new_grade_data.courses))


def listen_loop(chat_id: int):
    try:
        wait_time = config.interval
    except AttributeError:
        wait_time = 30 * 60

    try:
        grades = get_scraper().request_grade()
        GradeData(courses=grades).save(GRADE_DATA_FILE)
    except Exception as e:
        logging.error(e)
        updater.bot.send_message(chat_id, '初始状态获取失败，程序可能不能正确运行！')

    while not stop_flag.wait(timeout=wait_time):
        try:
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
        except Exception as e:
            logging.error(e)

    logging.info('background thread stopped')
    updater.bot.send_message(chat_id, '停止监视！')


@restricted
def start_monitor(update: Update, context: CallbackContext):
    if not stop_flag.is_set():
        update.effective_chat.send_message('已经在监视了！')
        return
    stop_flag.clear()

    background_thread = threading.Thread(name='background', target=listen_loop,
                                         args=(update.effective_chat.id,))
    background_thread.daemon = True
    background_thread.start()
    update.effective_chat.send_message('开始监视新的成绩！')
    logging.info('background thread started')


@restricted
def stop_monitor(update: Update, context: CallbackContext):
    if stop_flag.is_set():
        update.effective_chat.send_message('Already stopped!')
        return
    logging.info('stopping background thread...')
    stop_flag.set()


@restricted
def monitor_status(update: Update, context: CallbackContext):
    if stop_flag.is_set():
        text = '*未运行*'
    else:
        text = '*运行中*'

    try:
        grade_data = GradeData.load(GRADE_DATA_FILE)
        text += f'\n\n最后一次查询时间：\n{grade_data.time:%F %T}'.replace('-', '\\-')
    except FileNotFoundError:
        pass

    markup = InlineKeyboardMarkup([[InlineKeyboardButton('刷新', callback_data='monitor/status')]])

    q = update.callback_query
    if q is not None:
        q.answer()
        if text.strip() != update.effective_message.text_markdown_v2.strip():
            q.edit_message_text(text, reply_markup=markup, parse_mode='MarkdownV2')
    else:
        update.message.reply_text(text, reply_markup=markup, parse_mode='MarkdownV2')


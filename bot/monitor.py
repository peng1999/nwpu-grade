import logging
import random
import threading
from collections import defaultdict
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from bot.util import restricted
from bot import updater
from db import User
from scrapers import get_scraper, get_user_config
from scrapers.base import GradeData, diff_courses

logger = logging.getLogger(__name__)


def new_stop_flag():
    logger.info(f'creating stop_flag')
    stop_flag = threading.Event()  # background thread is running when not set
    stop_flag.set()
    return stop_flag


stop_flags = defaultdict(new_stop_flag)


def get_stop_flag(user_id):
    return stop_flags[str(user_id)]


def query_diff(user_id):
    logger.info('querying diff')

    try:
        grade_data = GradeData.load(user_id)
    except FileNotFoundError:
        return []

    grades = get_scraper(user_id).request_grade()
    if len(grades) == 0:
        raise ValueError('grade list is null, skipped')

    new_grade_data = GradeData(courses=grades)
    new_grade_data.save(user_id)

    return (diff_courses(new_grade_data.courses, grade_data.courses),
            diff_courses(grade_data.courses, new_grade_data.courses))


def listen_loop(user_id: int, fist_wait=None):
    scraper = get_scraper(user_id)
    wait_time = fist_wait or scraper.config.interval

    while not get_stop_flag(user_id).wait(timeout=wait_time):
        try:
            # everyone is sleeping during this time, so don't update
            if 3 <= datetime.now().hour < 7:
                continue
            diff, redraw = query_diff(user_id)
            if len(diff) > 0:
                msg = '有新的成绩！\n\n'
                msg += scraper.fmt_grades(diff)
                updater.bot.send_message(user_id, msg)
            if len(redraw) > 0:
                msg = '有成绩被撤回：\n\n'
                msg += '，'.join([course.course_name for course in redraw])
                updater.bot.send_message(user_id, msg)
        except Exception as e:
            logger.error(f'{type(e)}: {e}')
        wait_time = scraper.config.interval

    logger.info('background thread stopped')
    updater.bot.send_message(user_id, '已停止监视！')


@restricted
def start_monitor(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    stop_flag = get_stop_flag(user_id)

    if not stop_flag.is_set():
        update.effective_chat.send_message('已经在监视了！')
        return

    scraper = get_scraper(user_id)
    try:
        grades = scraper.request_grade()
        GradeData(courses=grades).save(user_id)
    except Exception as e:
        logger.error(f'{type(e)}: {e}')
        updater.bot.send_message(user_id, '初始状态获取失败，程序可能不能正确运行！')

    query = User.update(monitor_running=True).where(User.user_id == user_id)
    query.execute()
    stop_flag.clear()

    background_thread = threading.Thread(name='background', target=listen_loop, args=(user_id,))
    background_thread.daemon = True
    background_thread.start()
    update.effective_chat.send_message('开始监视新的成绩！')
    logger.info('background thread started')


@restricted
def stop_monitor(update: Update, context: CallbackContext, *, interactive=True):
    user_id = update.effective_user.id
    stop_flag = get_stop_flag(user_id)

    if stop_flag.is_set():
        if interactive:
            update.effective_chat.send_message('已经停止了!')
        return

    logger.info('stopping background thread...')
    query = User.update(monitor_running=False).where(User.user_id == user_id)
    query.execute()
    stop_flag.set()


def resume_all_monitor():
    for user in User.select().where(User.monitor_running == True):
        user_id = user.user_id
        upper = get_user_config(user_id).interval - 1
        wait_time = random.randint(0, upper)
        stop_flag = get_stop_flag(user_id)

        logger.info(f'background thread of `{user_id}` will start after {wait_time}s')
        t = threading.Thread(name='background', target=listen_loop, args=(user_id, wait_time))
        t.daemon = True
        stop_flag.clear()
        t.start()


@restricted
def monitor_status(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    stop_flag = get_stop_flag(user_id)
    if stop_flag.is_set():
        text = '*未运行*'
    else:
        text = '*运行中*'

    text += '\n\n最后一次查询时间：'
    try:
        grade_data = GradeData.load(user_id)
        text += f'\n{grade_data.time:%F %T}'.replace('-', '\\-')
    except Exception as e:
        logger.info(f'GradeData load failed with error: {type(e)}: {e}')
        text += '_Unknown_'

    markup = InlineKeyboardMarkup([[InlineKeyboardButton('刷新', callback_data='monitor/status')]])

    q = update.callback_query
    if q is not None:
        q.answer()
        if text.strip() != update.effective_message.text_markdown_v2.strip():
            q.edit_message_text(text, reply_markup=markup, parse_mode='MarkdownV2')
    else:
        update.message.reply_text(text, reply_markup=markup, parse_mode='MarkdownV2')

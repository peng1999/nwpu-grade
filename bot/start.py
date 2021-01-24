import logging

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler

import scrapers
from bot.util import build_menu
from db import User
from scrapers import get_config_cls


def start(update: Update, context: CallbackContext):
    logging.info(f'/start from user {update.effective_user.id}')
    username = update.effective_user.username
    if username is not None:
        logging.info(f'username is `{username}`')

    update.effective_chat.send_message(f'Hello {update.effective_user.full_name}，'
                                       f'欢迎使用大学成绩提醒器！')

    markup = ReplyKeyboardMarkup(build_menu(scrapers.universities, 2), resize_keyboard=True)
    update.effective_chat.send_message('请选择你的学校', reply_markup=markup)

    return 'university'


def choose_university(update: Update, context: CallbackContext):
    university = update.message.text
    markup = ReplyKeyboardRemove()
    update.effective_chat.send_message(f'你选择了：{university}', reply_markup=markup)

    context.user_data['settings'] = {}
    context.user_data['university'] = university
    return prompt_setting(update, context)


def prompt_setting(update: Update, context: CallbackContext):
    settings: dict = context.user_data['settings']
    university: str = context.user_data['university']

    config = get_config_cls(university)
    required_settings = config.get_key_name(required=True)

    for k in required_settings:
        if k in settings:
            continue
        else:
            update.effective_chat.send_message(f'请输入{required_settings[k]}')
            context.user_data['cur_setting'] = k
            return 'settings'

    new_config = config(**settings)
    user, _ = User.get_or_create(user_id=update.effective_user.id)
    user.chat_id = update.effective_chat.id
    user.university = university
    user.config = new_config.json()
    user.save()

    update.effective_chat.send_message('设置成功！')
    help_text(update, context)
    return ConversationHandler.END


def settings_answer(update: Update, context: CallbackContext):
    settings: dict = context.user_data['settings']
    cur_setting = context.user_data['cur_setting']
    settings[cur_setting] = update.message.text
    return prompt_setting(update, context)


def cancel(update: Update, context: CallbackContext):
    markup = ReplyKeyboardRemove()
    update.effective_chat.send_message('Canceled', reply_markup=markup)
    return ConversationHandler.END


def help_text(update: Update, context: CallbackContext):
    update.effective_chat.send_message("""
/start - 开始
/query - 查询所有成绩
/start_monitor - 开始监视成绩
/stop_monitor - 停止监视成绩
/monitor_status - 监视器状态
/help - 显示帮助信息
    """)
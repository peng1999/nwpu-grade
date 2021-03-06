import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

import config
import scrapers
from bot import monitor
from bot.basic import help_text
from bot.util import build_menu, restricted, from_callback_data, to_callback_data
from db import User
from scrapers import get_config_cls

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    logger.info(f'/start from user {update.effective_user.id}')
    username = update.effective_user.username
    if username is not None:
        logger.info(f'username is `{username}`')

    update.effective_chat.send_message(f'Hello {update.effective_user.full_name}，'
                                       f'欢迎使用大学成绩提醒器！\n'
                                       f'{config.disclaimer}')

    button_list = [InlineKeyboardButton(u, callback_data=to_callback_data('start/choose', u))
                   for u in scrapers.universities]
    markup = InlineKeyboardMarkup(build_menu(button_list, 2))
    update.effective_chat.send_message('请选择你的学校', reply_markup=markup)

    return 'university'


def choose_university_button(update: Update, context: CallbackContext):
    q = update.callback_query
    university = from_callback_data(q.data)

    if university not in scrapers.universities:
        update.effective_chat.send_message(f'不支持{university}！请联系 @pg999w 以支持该学校')
        update.effective_chat.send_message('请选择你的学校')
        return

    q.edit_message_text(f'你选择了：{university}')
    q.answer()

    context.user_data['settings'] = {}
    context.user_data['university'] = university
    return prompt_setting(update, context)


def prompt_setting(update: Update, context: CallbackContext):
    settings: dict = context.user_data['settings']
    university: str = context.user_data['university']

    config_cls = get_config_cls(university)
    required_settings = config_cls.get_key_name(required=True)

    for k in required_settings:
        if k in settings:
            continue
        else:
            update.effective_chat.send_message(f'请输入{required_settings[k]}')
            context.user_data['cur_setting'] = k
            return 'settings'

    new_config = config_cls(**settings)
    user, is_created = User.get_or_create(user_id=update.effective_user.id)
    query = User.update(
        chat_id=update.effective_chat.id,
        university=university,
        config=new_config.base64(),
    ).where(User.user_id == user.user_id)
    query.execute()
    if is_created:
        scrapers.update_user_config(user.user_id, new_config)

    update.effective_chat.send_message('设置成功！')
    help_text(update, context)
    return ConversationHandler.END


def settings_answer(update: Update, context: CallbackContext):
    settings: dict = context.user_data['settings']
    cur_setting = context.user_data['cur_setting']
    settings[cur_setting] = update.message.text
    return prompt_setting(update, context)


@restricted
def forget_me(update: Update, context: CallbackContext):
    monitor.stop_monitor(update, context, interactive=False)
    user: User = User.get(user_id=update.effective_user.id)
    logger.info(f'deleting user `{user.user_id}`')
    user.delete_instance()
    update.effective_chat.send_message('删除成功！使用 /start 以重新开始')

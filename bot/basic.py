import logging

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler

from scrapers.nwpu import LoginFailedError

logger = logging.getLogger(__name__)


def cancel(update: Update, context: CallbackContext):
    markup = ReplyKeyboardRemove()
    update.effective_chat.send_message('Canceled', reply_markup=markup)
    return ConversationHandler.END


def unsupported_command(update: Update, context: CallbackContext):
    update.effective_chat.send_message('此处不支持命令！请先用 /cancel 取消会话')


def help_text(update: Update, context: CallbackContext):
    update.effective_chat.send_message("""
/start - 开始
/query - 查询所有成绩
/start_monitor - 开始监视成绩
/stop_monitor - 停止监视成绩
/monitor_status - 监视器状态
/forget_me - 删除帐号信息
/help - 显示帮助信息
    """)


def error_handler(update: Update, context: CallbackContext):
    if isinstance(context.error, LoginFailedError):
        update.effective_chat.send_message('登录失败！')

    t = type(context.error)
    logger.error(msg=f'{t.__name__}: {context.error}')

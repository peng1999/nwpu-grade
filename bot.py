import logging

from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
from telegram.update import Update

from bot_impl import updater
from bot_impl.monitor import start_monitor, stop_monitor
from bot_impl.query import query, button
from bot_impl.util import restricted

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


@restricted
def start(update: Update, context: CallbackContext):
    logging.info(f'/start from user {update.effective_user.id}')
    username = update.effective_user.username
    if username is not None:
        logging.info(f'username is `{username}`')

    update.effective_chat.send_message(f'Hello {update.effective_user.full_name}!')
    help_text(update, context)


def help_text(update: Update, context: CallbackContext):
    update.effective_chat.send_message("""
/start - 开始
/query - 查询所有成绩
/start_monitor - 开始监视成绩
/stop_monitor - 停止监视成绩
/help - 显示帮助信息
    """)


dispatcher = updater.dispatcher

# start
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help_text))

# query
dispatcher.add_handler(CommandHandler('query', query))
dispatcher.add_handler(CallbackQueryHandler(button))

# monitor
dispatcher.add_handler(CommandHandler('start_monitor', start_monitor))
dispatcher.add_handler(CommandHandler('stop_monitor', stop_monitor))

updater.start_polling()

updater.idle()

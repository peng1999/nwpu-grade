import logging

from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler
from telegram.update import Update

from bot import updater
from bot.monitor import start_monitor, stop_monitor, monitor_status
from bot.query import query, query_button, detail_button, detail_item_button
from bot.util import restricted

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
/monitor_status - 监视器状态
/help - 显示帮助信息
    """)


dispatcher = updater.dispatcher

# start
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('help', help_text))

# query
dispatcher.add_handler(CommandHandler('query', query))
dispatcher.add_handler(CallbackQueryHandler(query_button, pattern='query/list'))
dispatcher.add_handler(CallbackQueryHandler(detail_button, pattern='query/detail'))
dispatcher.add_handler(CallbackQueryHandler(detail_item_button, pattern='query/single'))

# monitor
dispatcher.add_handler(CommandHandler('start_monitor', start_monitor))
dispatcher.add_handler(CommandHandler('stop_monitor', stop_monitor))
dispatcher.add_handler(CommandHandler('monitor_status', monitor_status))
dispatcher.add_handler(CallbackQueryHandler(monitor_status, pattern='monitor/status'))

updater.start_polling()

updater.idle()

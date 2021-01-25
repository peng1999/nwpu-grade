import logging

from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, \
    Filters

from bot import updater
from bot.monitor import start_monitor, stop_monitor, monitor_status, resume_all_monitor
from bot.query import query, query_button, detail_button, detail_item_button
from bot.account import start, help_text, cancel, choose_university, settings_answer, forget_me

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

dispatcher = updater.dispatcher

# account
start_handler = CommandHandler('start', start)
cancel_handler = CommandHandler('cancel', cancel)
university_handler = MessageHandler(Filters.text & (~Filters.command), choose_university)
settings_handler = MessageHandler(Filters.text & (~Filters.command), settings_answer)

dispatcher.add_handler(ConversationHandler(
    entry_points=[start_handler],
    states={
        'university': [university_handler],
        'settings': [settings_handler],
    },
    fallbacks=[cancel_handler]
))

dispatcher.add_handler(CommandHandler('forget_me', forget_me))
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

resume_all_monitor()

updater.idle()

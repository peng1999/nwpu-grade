from functools import wraps
from io import StringIO
import logging

from telegram.update import Update
from telegram.ext import Updater, CallbackContext, CommandHandler

import config
from client import NWPUgrade

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
                "I'm not your bot! Refer to https://github.com/peng1999/nwpu-grade to deploy your own bot.")
            return
        return func(update, context, *args, **kwargs)
    return wrapped


updater = Updater(token=config.token, use_context=True)
dispatcher = updater.dispatcher


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

    nwpu_client = NWPUgrade()
    nwpu_client.grade()

    with StringIO() as sio:
        nwpu_client.printgrade(file=sio)
        update.effective_chat.send_message(sio.getvalue())


dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('query', query))
updater.start_polling()

updater.idle()
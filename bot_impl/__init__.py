import os

from telegram.ext import Updater

import config

try:
    GRADE_DATA_PATH = config.data_path
except AttributeError:
    GRADE_DATA_PATH = '.'

GRADE_DATA_FILE = os.path.join(GRADE_DATA_PATH, 'data.json')
updater = Updater(token=config.token, use_context=True)
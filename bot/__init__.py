import os
from functools import lru_cache

from telegram.ext import Updater

import config
from scrapers import Scraper

try:
    GRADE_DATA_PATH = config.data_path
except AttributeError:
    GRADE_DATA_PATH = '.'

GRADE_DATA_FILE = os.path.join(GRADE_DATA_PATH, 'data.json')

updater = Updater(token=config.token, use_context=True)


@lru_cache(maxsize=1)
def get_scraper():
    """Scraper factory"""
    return Scraper()

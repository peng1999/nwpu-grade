import getpass
import importlib
import sys
from typing import Any, Type

from .base import ScraperBase

try:
    # noinspection PyUnresolvedReferences
    import config
except ImportError:
    pass


def get_config(name: str, passwd=False):
    if 'config' in globals() and hasattr(config, name):
        return getattr(config, name)

    if sys.argv[0].endswith('bot.py'):
        raise ValueError(f'Missing configuration `{name}`')

    prompt = name + ': '
    if passwd:
        return getpass.getpass(prompt)
    return input(prompt)


mode = get_config('university')
cur_module: Any = importlib.import_module(f'{__name__}.{mode}')
Scraper: Type[ScraperBase] = cur_module.Scraper

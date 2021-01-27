import importlib
from functools import lru_cache
from glob import glob
from os import path
from typing import Any, Type

from db import User
from .base import ScraperBase, ConfigBase

universities = [
    path.basename(f)[:-3]
    for f in glob(path.join(path.dirname(__file__), '*.py'))
]
universities.remove('__init__')
universities.remove('base')


@lru_cache(maxsize=None)
def get_module(name) -> Any:
    return importlib.import_module(f'{__name__}.{name}')


@lru_cache(maxsize=None)
def get_config_cls(name) -> Type[ConfigBase]:
    return get_module(name).Config


def get_user_config(user_id):
    user: User = User.get(user_id=user_id)
    config_cls = get_config_cls(user.university)
    config = config_cls.parse_base64(user.config)
    return config


def update_user_config(user_id, config):
    scraper = get_scraper(user_id)
    scraper.config = config


@lru_cache(maxsize=100)
def get_scraper(user_id) -> ScraperBase:
    """Scraper factory"""
    user: User = User.get(user_id=user_id)
    config = get_user_config(user_id)
    return get_module(user.university).Scraper(config)

import importlib
from functools import lru_cache
from glob import glob
from os import path
from typing import Any, Type

from .base import ScraperBase, get_config, ConfigBase

# TODO: delete this
mode = get_config('university')
cur_module: Any = importlib.import_module(f'{__name__}.{mode}')
Scraper: Type[ScraperBase] = cur_module.Scraper

universities = [
    path.basename(f)[:-3]
    for f in glob(path.join(path.dirname(__file__), '*.py'))
]
universities.remove('__init__')
universities.remove('base')


@lru_cache()
def get_module(name) -> Any:
    return importlib.import_module(f'{__name__}.{name}')


@lru_cache()
def get_config_cls(name) -> Type[ConfigBase]:
    return get_module(name).Config


@lru_cache(maxsize=100)
def get_scraper():
    """Scraper factory"""
    return Scraper()

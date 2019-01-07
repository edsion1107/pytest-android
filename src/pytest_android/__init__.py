#!/usr/bin/env python
# encoding: utf-8

"""
@author: edsion
@file: __init__.py.py
@time: 2019-01-03 17:21
"""
import logging
from pkg_resources import get_distribution, DistributionNotFound
from .fixtrues import *
from .hooks import pytest_exception_interact

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    logging.error('package is not installed')
    __version__ = '0.0.0'

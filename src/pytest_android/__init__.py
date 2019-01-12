#!/usr/bin/env python
# encoding: utf-8

"""
@author: edsion
@file: __init__.py.py
@time: 2019-01-03 17:21
"""

from pkg_resources import get_distribution, DistributionNotFound

from .fixtrues import *  # 导入fixture
from .hooks import *  # 导入hook

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    print('package is not installed')
    __version__ = '0.0.0'

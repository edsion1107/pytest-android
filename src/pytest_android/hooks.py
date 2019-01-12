#!/usr/bin/env python
# encoding: utf-8

"""
@author: edsion
@file: hooks.py
@time: 2019-01-03 17:25
"""
import logging
from uiautomator2 import UIAutomatorServer, UiObjectNotFoundError

try:
    import allure
except ImportError:
    logging.warning('allure not installed.')
    allure = None


def pytest_exception_interact(node, call, report):
    if isinstance(call.excinfo.value, UiObjectNotFoundError):
        for k, v in node.funcargs.items():
            if isinstance(v, UIAutomatorServer):
                if allure:
                    allure.attach(v.dump_hierarchy(), call.excinfo.typename, allure.attachment_type.XML)
                    allure.attach(v.screenshot(format='raw'), call.excinfo.typename, allure.attachment_type.JPG)
                break

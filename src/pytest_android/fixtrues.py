#!/usr/bin/env python
# encoding: utf-8

"""
@author: edsion
@file: fixtrues.py
@time: 2019-01-03 17:22
"""
import time
import json
import logging
import pytest
import uiautomator2
from .utils import click_marker, swipe_marker

try:
    import allure
except ImportError:
    logging.warning('allure not installed.')
    allure = None
# import for type hits
from _pytest.fixtures import SubRequest
from uiautomator2 import UIAutomatorServer

# __all__ 只能影响`from xxx import *`的情况，直接导入不受影响
__all__ = ['driver', 'show_case_name', 'app_start', 'app_stop']


@pytest.fixture(scope='session', autouse=True)
def driver(variables: dict) -> UIAutomatorServer:
    """初始化设备
    1. 连接设备。(配置文件中)需要指定`device`节点，至少包括`serial`（有线）和`addr`（无线）其中一个。有线连接比无线优先级高；
不存在`serial`时，直接使用无线连接；通过`serial`连接设备失败时，自动使用`addr`重连；`serial`值为空，自动连接当前唯一的设备
    2. 设置 uiautomator2 的全局参数，目前有：click_post_delay、wait_timeout
    3. 执行 uiautomator2 功能插件的注册，目前有：点击、滑动时自动截图
    """

    assert variables  # 需要通过 pytest 的命令行参数"--variables xxx"指定配置文件，可以同时指定多个
    logging.debug(json.dumps(variables, indent=4))
    device = variables.get('device')
    assert device

    logging.debug("设备参数：{0}".format(json.dumps(device, indent=4)))
    u2_conf = variables.get('uiautomator2')
    logging.debug("uiautomator2配置：{0}".format(json.dumps(u2_conf, indent=4)))
    try:
        logging.info('尝试通过USB连接设备')
        if 'serial' not in device:  # 没有 serial 参数直接走Wi-Fi连接
            raise OSError
        else:
            d = uiautomator2.connect_usb(device.get('serial'))
    except OSError:
        logging.warning('尝试通过WI-FI（网络）连接设备')
        d = uiautomator2.connect_wifi(device.get('addr'))

    logging.info('device info: {0}'.format(json.dumps(d.device_info, indent=4)))

    def _screenshot(stage, func_name, args, kwargs, ret):
        if stage == 'before':
            if 'click' in func_name:
                logging.info(f'[{func_name}] ({args[0]},{args[1]})')
                im = d.screenshot()
                if allure:
                    allure.attach(click_marker(im, *args), f'{func_name}: ({args[0]},{args[1]})',
                                  allure.attachment_type.JPG)
            elif 'swipe' in func_name:
                logging.info(f'[{func_name}] from: ({args[0]},{args[1]}), to ({args[2]},{args[3]})')
                im = d.screenshot()
                if allure:
                    allure.attach(swipe_marker(im, *args),
                                  f'{func_name}: ({args[0]},{args[1]}) to ({args[2]},{args[3]})',
                                  allure.attachment_type.JPG)

    if variables.get('uiautomator2', {}).get('auto_screenshot', None):
        d.hooks_register(_screenshot)

    # 此处可以添加一些全局初始化设置
    d.click_post_delay = u2_conf.get('click_post_delay') or d.click_post_delay  # default no delay
    d.wait_timeout = u2_conf.get('wait_timeout') or d.wait_timeout
    configurator = u2_conf.get('Configurator')

    if configurator:
        d.jsonrpc.setConfigurator(configurator)
    logging.debug('UiAutomator Configurator: {0}'.format(json.dumps(d.jsonrpc.getConfigurator(), indent=4)))

    assert isinstance(d, UIAutomatorServer)
    return d


@pytest.fixture(scope='function', autouse=True)
def show_case_name(request: SubRequest, driver: UIAutomatorServer) -> None:
    """toast提示显示用例描述或名字，便于了解进度"""
    # 因为要支持 pytest.mark.parametrize 生成的多条case的情况，所以这里用node的name
    logging.info(f'case name: {request.node.name}')
    driver.toast.show(request.node.name, 3)  # toast提示显示2秒


@pytest.fixture(scope='function', autouse=True)
def app_start(variables: dict, driver: UIAutomatorServer, show_case_name: None) -> bool:
    """启动app，（仅）通过当前 app 包名判断是否启动"""
    package_name = variables.get('package_name')
    activity = variables.get('MainActivity', None)
    logging.info(f'start app: {package_name}, activity: {activity}')
    start = time.time()

    driver.app_start(package_name, activity, wait=True, stop=True)
    time.sleep(driver.click_post_delay)
    while time.time() - start < 30:
        res = driver.current_app()  # https://github.com/openatx/uiautomator2/issues/200
        if res.get('package') == package_name:
            return True
    return False


@pytest.fixture(scope='function', autouse=True)
def app_stop(request: SubRequest, variables: dict, driver: UIAutomatorServer) -> None:
    """每条case结束自动close app"""

    def _close():
        package_name = variables.get('package_name')
        logging.info(f'stop app: {package_name}')
        driver.app_stop(package_name)
        time.sleep(1)

    request.addfinalizer(_close)

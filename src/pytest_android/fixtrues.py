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
import requests
import uiautomator2
from requests.adapters import HTTPAdapter
from uiautomator2.adbutils import AdbClient
from requests.exceptions import ConnectTimeout, ConnectionError
from .utils import click_marker, swipe_marker

try:
    import allure
except ImportError:
    pass
# import for type hints
from _pytest.fixtures import SubRequest
from _pytest.config import Config
from uiautomator2 import UIAutomatorServer

# __all__ 只能影响`from xxx import *`的情况，直接导入不受影响
__all__ = ['driver', 'uiautomator2_hook', 'show_case_name', 'app_start']


@pytest.fixture(scope='session', autouse=True)
def driver(pytestconfig: Config, variables: dict) -> UIAutomatorServer:
    """初始化设备
    1. 连接设备。(配置文件中)需要指定`device`节点，至少包括`serial`（有线）和`addr`（无线）其中一个。有线连接比无线优先级高；
不存在`serial`时，直接使用无线连接；通过`serial`连接设备失败时，自动使用`addr`重连；`serial`值为空，自动连接当前唯一的设备
    2. 设置 uiautomator2 的全局参数，目前有：click_post_delay、wait_timeout
    """

    assert variables  # 需要通过 pytest 的命令行参数"--variables xxx"指定配置文件，可以同时指定多个
    logging.debug(json.dumps(variables, indent=4))
    device_conf = variables.get('device')
    assert device_conf
    logging.debug("设备参数：{0}".format(json.dumps(device_conf, indent=4)))
    u2_conf = variables.get('uiautomator2')
    logging.debug("uiautomator2配置：{0}".format(json.dumps(u2_conf, indent=4)))

    logging.info('尝试通过USB连接设备')
    adb = AdbClient()
    if 'serial' in device_conf:
        # 配置了serial参数并且通过adb能检测到，才usb直连
        if adb.device(device_conf.get('serial')) or device_conf.get('serial') is None:
            try:
                d = uiautomator2.connect_usb(device_conf.get('serial'))
            except RuntimeError:
                logging.info(f"配置文件：{pytestconfig.option.variables}")
                logging.error(f'检测到多台设备，但未通过配置文件指定其中一个\n'
                              f'请断开其他或修改配置文件:{pytestconfig.option.variables}')
                pytest.fail(f'检测到多台设备，但未通过配置文件指定其中一个\n'
                            f'请断开其他或修改配置文件:{pytestconfig.option.variables}', pytrace=False)
        else:
            logging.warning('尝试通过WI-FI（网络）连接设备')  # 其他情况走ip连接
            d = uiautomator2.connect_wifi(device_conf.get('addr'))
    else:
        logging.warning('尝试通过WI-FI（网络）连接设备')  # 其他情况走ip连接
        d = uiautomator2.connect_wifi(device_conf.get('addr'))

    try:
        r = requests.get(d._server_url + '/ping', timeout=3)
        if r.status_code != 200 or r.text != 'pong':
            raise ConnectionError
    except (ConnectTimeout, ConnectionError):
        logging.error(f'连接失败: {d._server_url}')
        pytest.fail(f'连接失败: {d._server_url}', pytrace=False)

    # 此处可以添加一些全局初始化设置
    d.click_post_delay = u2_conf.get('click_post_delay') or d.click_post_delay  # default no delay
    d.wait_timeout = u2_conf.get('wait_timeout') or d.wait_timeout
    configurator = u2_conf.get('Configurator')

    if configurator:
        d.jsonrpc.setConfigurator(configurator)
    logging.debug('UiAutomator Configurator: {0}'.format(json.dumps(d.jsonrpc.getConfigurator(), indent=4)))

    assert isinstance(d, UIAutomatorServer)
    return d


@pytest.fixture(scope='session', autouse=True)
def uiautomator2_hook(driver: UIAutomatorServer, variables: dict) -> None:
    """执行 uiautomator2 功能插件的注册，目前有：点击、滑动时自动截图"""

    def _screenshot(stage, func_name, args, kwargs, ret):
        if stage == 'before':
            if 'click' in func_name:
                logging.info(f'[{func_name}] ({args[0]},{args[1]})')
                im = driver.screenshot()
                if allure:
                    allure.attach(click_marker(im, *args), f'{func_name}: ({args[0]},{args[1]})',
                                  allure.attachment_type.JPG)
            elif 'swipe' in func_name:
                logging.info(f'[{func_name}] from: ({args[0]},{args[1]}), to ({args[2]},{args[3]})')
                im = driver.screenshot()
                if allure:
                    allure.attach(swipe_marker(im, *args),
                                  f'{func_name}: ({args[0]},{args[1]}) to ({args[2]},{args[3]})',
                                  allure.attachment_type.JPG)

    if variables.get('uiautomator2', {}).get('auto_screenshot', None):
        driver.hooks_register(_screenshot)


@pytest.fixture(scope='function', autouse=True)
def show_case_name(request: SubRequest, driver: UIAutomatorServer) -> None:
    """toast提示显示用例描述或名字，便于了解进度"""
    # 因为要支持 pytest.mark.parametrize 生成的多条case的情况，所以这里用node的name
    logging.info(f'case name: {request.node.name}')
    driver.toast.show(request.node.name, 3)  # toast提示显示2秒


@pytest.fixture(scope='function', autouse=True)
def app_start(variables: dict, driver: UIAutomatorServer, show_case_name: None) -> bool:
    """用例执行前启动 app，完成后强行停止该 app。启动时（仅）通过当前 app 包名判断是否启动"""
    # 依赖 show_case_name 是为了保证 fixture 执行顺序
    package_name = variables.get('package_name')
    activity = variables.get('MainActivity', None)
    res = driver.shell(f'pm path {package_name}')
    if res.exit_code != 0:
        logging.error(f'{package_name} not installed.')
        pytest.fail(f'{package_name} not installed.', pytrace=False)
    logging.info(f'start app: {package_name}, activity: {activity}')
    start = time.time()

    driver.app_start(package_name, activity, wait=True, stop=True)
    time.sleep(driver.click_post_delay)
    while time.time() - start < 30:
        res = driver.current_app()  # https://github.com/openatx/uiautomator2/issues/200
        if res.get('package') == package_name:
            success = True
            break
    else:
        success = False
    yield success
    logging.info(f'stop app: {package_name}')
    driver.app_stop(package_name)
    time.sleep(1)


@pytest.fixture
def notify(variables: dict):
    s = requests.session()
    s.mount('https://', HTTPAdapter(max_retries=3))
    token = variables.get('notify').get('token')
    if variables.get('notify').get('backend') == 'serverchan':
        url = f'https://sc.ftqq.com/{token}.send'

        def _notify(content: str) -> requests.Response:
            r = s.post(url, data={'text': content})
            logging.debug(r.text)
            assert r.status_code == 200
            assert r.json().get('errno') == 0
            return r
    else:
        url = variables.get('notify').get('url')
        s.headers.update({'Authorization': f'Token {token}'})

        def _notify(content: str) -> requests.Response:
            r = s.post(url, json={'content': content})
            logging.debug(r.text)
            assert r.status_code == 201
            return r
    return _notify

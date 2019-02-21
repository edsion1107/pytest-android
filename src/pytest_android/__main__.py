#!/usr/bin/env python
# encoding: utf-8

"""
@author: edsion
@file: __main__.py
@time: 2019-02-14 15:00
"""
import os
import filecmp
import hashlib
import zipfile
import argparse
import shutil
import platform
import webbrowser
from requests.exceptions import ConnectionError, ConnectTimeout
from retry import retry
from pathlib import Path
from urllib.parse import urlparse
from progressbar import DataTransferBar
from requests_download import download, HashTracker, ProgressTracker
from uiautomator2.__main__ import cache_download as u2_download
from uiautomator2.__main__ import appdir as u2_appdir
from uiautomator2.version import __apk_version__ as u2_apk_version
from . import __version__
from . import __name__ as pkg_name

BASE_DIR = Path.home().joinpath(f'.{pkg_name}')
if not BASE_DIR.exists():
    BASE_DIR.mkdir()

PYTEST = {'url': 'https://raw.githubusercontent.com/edsion1107/pytest-android/master/pytest.ini',
          'hash': '062fc3979aca4f6b3099f1c78b5766535d1a877bd17679c2c4fad32c3212def1', 'hash_func': hashlib.sha256}
CONFIG = {'url': 'https://raw.githubusercontent.com/edsion1107/pytest-android/master/config.yaml',
          'hash': '2cb2166d8ebe1b640b5ab15383deef7a300c68505880e558c0b30ef54a739a84', 'hash_func': hashlib.sha256}

UIAUTOMATOR2 = [
    {'url': 'https://github.com/openatx/android-uiautomator-server/releases/download/%s/app-uiautomator.apk',
     'hash': None, 'hash_func': None},
    {'url': 'https://github.com/openatx/android-uiautomator-server/releases/download/%s/app-uiautomator-test.apk',
     'hash': None, 'hash_func': None},
]
SCRCPY = {'url': 'https://github.com/Genymobile/scrcpy/releases/download/v1.6/scrcpy-win64-v1.6.zip',
          'hash': 'f66b7eace8dd6537a9a27176fd824704a284d8e82077ccc903344396043f90c9', 'hash_func': hashlib.sha256}


def hash_local_file(filepath: str or Path, hash_str='', hash_func=hashlib.md5) -> bool:
    """根据输入的算法（一般是 md5 或 sha1 ），计算本地文件的 hash 字符串，从而实现校验本地文件完整性或是否最新"""
    assert Path(filepath).is_file()

    if hash_str and hash_func:
        m = hash_func()
        with open(filepath, 'rb') as f:
            for line in f:
                m.update(line)
            else:
                res = m.hexdigest()
        return hash_str == res
    else:
        print('unknown hash string or func, skipped.')
        return True


@retry(exceptions=(ConnectionError, ConnectTimeout, AssertionError), tries=3)
def cache_download(url: str, hash_str: str = '', hash_func=None) -> Path:
    """ 根据 URL 下载文件，并校验完整性（如果一致则不重新下载） """
    filename = Path(urlparse(url).path).name
    filepath = BASE_DIR.joinpath(hashlib.md5(url.encode()).hexdigest(), filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    if filepath.exists():
        print(f'发现本地文件:{filepath}\n尝试校验...', end=''),
        if hash_local_file(filepath, hash_str, hash_func):
            print('成功')
            return filepath
        else:
            print('失败，重新下载')
            filepath.unlink()

    print(f'开始下载 {url}')
    # 文件不存在、或校验不通过执行下载
    progress = ProgressTracker(DataTransferBar())
    if hash_func:
        hasher = HashTracker(hash_func())
        download(url, filepath, trackers=(progress, hasher))
        print(hasher.hashobj.hexdigest())
        assert hasher.hashobj.hexdigest() == hash_str
    else:
        download(url, filepath, trackers=(progress,))
    print(f'缓存路径：{filepath}')
    return filepath


def compare_and_ask(src: Path, dest: Path) -> bool:
    assert src.is_file()
    assert dest.is_file()
    if filecmp.cmp(src, dest, shallow=True):
        return True
    else:
        ask = input('存在冲突，是否直接覆盖（Y/N）？')
        if ask.upper().strip() == 'Y':
            dest.write_bytes(src.read_bytes())
        else:
            print(f'请手动合并文件：\n1. {src}\n2. {dest.resolve()}\n')
            return False


def download_cmd(args: dict):
    if args.get('pytest.ini'):
        url = PYTEST.get('url')
        filename = Path(urlparse(url).path).name
        if args.get('force'):
            filepath = BASE_DIR.joinpath(hashlib.md5(url.encode()).hexdigest(), filename)
            filepath.unlink()
        src = cache_download(url, PYTEST.get('hash'), PYTEST.get('hash_func'))
        dest = Path('pytest.ini')
        if dest.exists():
            compare_and_ask(src, dest)
        else:
            dest.write_bytes(src.read_bytes())

    if args.get('config.yaml'):
        url = CONFIG.get('url')
        filename = Path(urlparse(url).path).name
        if args.get('force'):
            filepath = BASE_DIR.joinpath(hashlib.md5(url.encode()).hexdigest(), filename)
            filepath.unlink()
        src = cache_download(url, CONFIG.get('hash'), CONFIG.get('hash_func'))
        dest = Path('config.yaml')
        if dest.exists():
            compare_and_ask(src, dest)
        else:
            dest.write_bytes(src.read_bytes())

    if args.get('uiautomator2'):
        for app in UIAUTOMATOR2:
            url = app.get('url') % u2_apk_version
            filename = Path(urlparse(url).path).name
            if args.get('force'):
                filepath = Path(u2_appdir).joinpath(hashlib.sha224(url.encode()).hexdigest(), filename)
                filepath.unlink()
            src = u2_download(url, filename)
            print(src)
        else:
            print('下载完毕，请手动安装')

    if args.get('scrcpy'):
        if platform.machine() == 'AMD64' and platform.system() == 'Windows':
            url = SCRCPY.get('url')
            filename = Path(urlparse(url).path).name
            if args.get('force'):
                filepath = BASE_DIR.joinpath(hashlib.md5(url.encode()).hexdigest(), filename)
                filepath.unlink()
            src = cache_download(url, SCRCPY.get('hash'), SCRCPY.get('hash_func'))
            zipfile.ZipFile(src).extractall()  # 解压到当前路径
        else:
            print('warning: 未提供预编译版本，请参考项目主页（https://github.com/Genymobile/scrcpy），手动编译')


def cleanup_cmd(args: argparse.Namespace):
    shutil.rmtree(BASE_DIR, ignore_errors=True)
    if args.all:
        shutil.rmtree(u2_appdir, ignore_errors=True)


def auth_cmd(args: argparse.Namespace):
    if args.wework:
        print('请扫描浏览器中展示的二维码，授权后 token 会自动发送到你的企业微信中')
        webbrowser.open('https://wecar.i1hao.com/wework/qr_connect', new=1)
    elif args.serverchan:
        print('请按照浏览器中的指引，github 授权和绑定微信公众号，即可在网页上找到"SCKEY"(token)')
        print('注意：serverchan 的消息推送频率有限制，具体以页面显示为准')
        webbrowser.open('https://sc.ftqq.com', new=1)


def main():
    parser = argparse.ArgumentParser(
        # usage='python -m pytest_android ',
        description='pytest-android cli')
    parser.add_argument('-V', '--version', action='version', version=__version__)
    parser.add_argument('--proxy', action='store', type=str, required=False, default='',
                        help='HTTP代理（被墙、内网等情况下使用）')
    subparsers = parser.add_subparsers(dest="subparser_name")

    d = subparsers.add_parser('download', help='下载配置文件（示例）、外部依赖')
    d.add_argument('-F', '--force', action='store_true', required=False, default=False,
                   help='删除本地缓存，再执行下载')
    d.add_argument('--pytest.ini', action='store_true', default=False,
                   help='下载 pytest 配置文件（示例），并拷贝到当前目录')
    d.add_argument('--config.yaml', action='store_true', default=False,
                   help='下载工程配置文件（示例），并拷贝到当前目录')
    d.add_argument('--uiautomator2', action='store_true', default=False,
                   help='下载uiautomator2 apk 和 uiautomator2 test apk，并显示其路径。具体版本由安装的 uiautomator2 模块指定')
    d.add_argument('--scrcpy', action='store_true', default=False,
                   help='scrcpy，外部录屏工具，并解压到当前目录')
    d.add_argument('--init', action='store_const', const=['pytest.ini', 'config.yaml'],
                   help='init %(const)s')

    c = subparsers.add_parser('clean', help='清理下载缓存')
    c.add_argument('--all', action='store_true', help='清除所有（包括uiautomator2）')

    a = subparsers.add_parser('authentication', help='用户认证（使用后端 api ）')
    a.add_argument('--wework', action='store_true', default=False, help='企业微信认证（需管理员开通此服务）')
    a.add_argument('--serverchan', action='store_true', default=False, help='ServerChan认证')

    args = parser.parse_args()

    # 设置全局代理
    os.environ['HTTP_PROXY'] = args.proxy
    os.environ['HTTPS_PROXY'] = args.proxy

    if args.subparser_name == 'download':
        args = vars(args)
        if args.get('init'):
            for i in args.get('init'):
                args[i] = True
        download_cmd(args)
    elif args.subparser_name == 'clean':
        cleanup_cmd(args)

    elif args.subparser_name == 'authentication':
        auth_cmd(args)


if __name__ == '__main__':
    main()

# pytest-android

![PyPI version](https://img.shields.io/pypi/v/pytest-android.svg) ![Python versions](https://img.shields.io/pypi/pyversions/pytest-android.svg) ![See Build Status on Travis CI](https://travis-ci.org/edsion1107/pytest-android.svg?branch=master)

[TOC]

pytest-android is a plugin for [pytest](http://pytest.org/) that provides a configured 'driver' for Android Automated Testing, using [uiautomator2](https://github.com/openatx/uiautomator2).

pytest-android 是 [pytest](http://pytest.org/) 的插件，它通过 [uiautomator2](https://github.com/openatx/uiautomator2) 为 Android 自动化测试提供“驱动”。

## 功能

- 整合 [uiautomator2](https://github.com/openatx/uiautomator2)，实现基于控件的自动化测试
- 借助 [allure](https://github.com/allure-framework/allure-python) 生成测试报告
- 依赖 [pytest-variables](https://github.com/pytest-dev/pytest-variables) 实现参数化配置
- 借助 hook 机制，实现“点击、滑动时自动截图”、“异常时自动抓取控件信息和截图”等 fixture，减少重复工作
- 通过安装 pytest 插件，实现诸如“失败重试”、“分布式执行”、“用例分层”等



## 依赖

**强烈建议** 使用 git 对代码进行版本控制，灵活运用分支开发的策略，并且将自动化整合进 DevOps 流程中。

**推荐** 本地开发使用基于`virtualenv`的工具实现环境隔离和解决各个模块之间的依赖，如`pipenv`。

**建议** 生产环境使用`docker`对各个设备之间进行“隔离”。

### 1. 安装 python

macOS、linux可以通过 [pyenv](https://github.com/pyenv/pyenv) 实现多个 python 版本的共存和切换，Windows上需要下载可执行文件、手动安装和配置环境变量。

> 因为使用了 python 3.6 的 [f-string](https://realpython.com/python-f-strings/) 特性，所以建议的 python 版本大于等于3.6。

> 因为 [uiautomator2](https://github.com/openatx/uiautomator2) 的某些依赖库目前还不支持python 3.7，所以当前 python 版本需要小于 3.7。

具体安装过程略。

### 2. 安装依赖模块

你可以直接通过`pip`命令安装:

```bash
pip install pytest>=4.0         # 必须
pip install pytest-variables    # 必须

# 必须，根据你选择的配置文件格式，二选一
pip install PyYAML    # 推荐
pip install hjson

pip install uiautomator2>=0.1.7    # 必须（目前支持的驱动框架，后续可能还会添加Appium）
pipenv install weditor		# 必须，uiautomator2 配套的录制工具

pip install pillow    # 可选，如果使用“自动截图”功能，需要通过此模块为截图添加“水印“
pip install allure-pytest		# 可选，使用allure生成报告
pipenv install pytest-rerunfailures		# 可选，使 pytest 支持失败重试
```



也可以使用`pipenv`进行安装（推荐）：

```bash
# macOS
brew install pipenv
# windows,linux
pip install --user pipenv

pipenv install pytest>=4.0         # 必须
pipenv install pytest-variables    # 必须

# 必须，根据你选择的配置文件格式，二选一
pipenv install PyYAML    # 推荐
pipenv install hjson

pipenv install uiautomator2>=0.1.7    # 必须，目前支持的驱动框架，后续可能还会添加 Appium 
pipenv install weditor		# 必须，uiautomator2 配套的录制工具

pipenv install pillow    # 可选，如果使用“自动截图”功能，需要通过此模块为截图添加“水印“
pipenv install allure-pytest		# 可选，使用 allure 生成报告
pipenv install pytest-rerunfailures		# 可选，使 pytest 支持失败重试
```



## 安装

直接通过`pip`命令安装：

```bash
pip install pytest-android
```



通过`pipenv`安装：

```bash
pipenv install pytest-android
```



## 使用

### 1. 配置文件

#### 1.1 config.yaml

TODO：参考的配置文件例子`config.yaml`，链接或内容，待补充

创建项目级配置文件，参考`config.yaml`。此文件可以使用 yaml 和 hjson 格式（由 pytest-variables 插件实现），文件名任意（在下一步中指定）。

配置文件可以同时指定多个（遇到相同字段，后面的会覆盖前面的），借助此功能可以实现：指定设备参数、实现复杂情况下的兼容性测试等。

#### 1.2 pytest.ini

创建 pytest 的配置文件，参考[文档](https://docs.pytest.org/en/latest/reference.html#configuration-options)进行基础配置。

添加`addopts = --variables config.yaml`，指定项目配置文件。



[可选]

如果使用 allure 生成报告，并安装了对应依赖，可以通过`--alluredir`指定报告的路径，通过`--clean-alluredir`指定开始前是否清理历史数据。更多参数可参考[插件文档](https://docs.qameta.io/allure/#_pytest)

如果借助 pytest-rerunfailures 插件实现失败重试，参考[插件文档](https://github.com/pytest-dev/pytest-rerunfailures)，添加`--reruns`

其他诸如 log 、markers，和第三方插件配置，根据需要参考对应文档。



### 2. Fixtures

此处文档可能更新不及时，通过执行命令`python -m pytest --fixtures`，可以列出所有 fixtures 及其最新说明文档。

| Name           |  Scope   | Autouse | Description                                                  |
| :------------- | :------: | :-----: | :----------------------------------------------------------- |
| driver         | session  |  True   | 初始化设备 解锁、清理后台，设置驱动层参数和执行某些功能插件的注册 |
| show_case_name | function |  True   | toast 提示显示用例描述或名字，便于了解进度                   |
| app_start      | function |  True   | 启动 app ，（仅）通过当前 app 包名判断是否启动               |
| app_stop       | function |  True   | 每条 case 结束自动 close app                                 |



根据 pytest 的[加载顺序](https://docs.pytest.org/en/latest/writing_plugins.html#plugin-discovery-order-at-tool-startup)，插件中定义的 fixture 是可以被 `conftest.py`和本地插件`pytest_plugins `覆盖的。也就是说，如果具体到项目时不满足需求，可以在`conftest.py`文件中，编写同名fixture，修改`scope`、`autoues`和其具体行为。

## Issues

如果插件使用中遇到问题，请通过 github issues 提交。

## 贡献代码

Contributions are very welcome. 

## License

Distributed under the terms of the [MIT](LICENSE) license, "pytest-android" is free and open source software.

根据[MIT](LICENSE)许可条款分发，“pytest-android”是免费的开源软件。
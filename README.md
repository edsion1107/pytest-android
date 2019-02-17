# pytest-android

![PyPI version](https://img.shields.io/pypi/v/pytest-android.svg) ![Python versions](https://img.shields.io/pypi/pyversions/pytest-android.svg) ![See Build Status on Travis CI](https://travis-ci.org/edsion1107/pytest-android.svg?branch=master)

pytest-android is a plugin for [pytest](http://pytest.org/) that provides a configured 'driver' for Android Automated Testing, using [uiautomator2](https://github.com/openatx/uiautomator2).

pytest-android 是 [pytest](http://pytest.org/) 的插件，它通过 [uiautomator2](https://github.com/openatx/uiautomator2) 为 Android 自动化测试提供“驱动”。



目录
=================

* [pytest-android](#pytest-android)
* [目录](#目录)
 * [主要功能](#主要功能)
 * [安装](#安装)
    * [1. 安装 python](#1-安装-python)
    * [2. 创建工程](#2-创建工程)
    * [3. 安装插件和一些可选模块](#3-安装插件和一些可选模块)
 * [使用](#使用)
    * [1. 创建配置文件](#1-创建配置文件)
       * [1.1 创建配置文件 config.yaml 和 pytest.ini](#11-创建配置文件-configyaml-和-pytestini)
       * [1.2 根据需求调整配置[可选]](#12-根据需求调整配置可选)
    * [2. 编写用例](#2-编写用例)
       * [2.1 可用的Fixtures](#21-可用的fixtures)
       * [2.2 编写用例](#22-编写用例)
 * [Issues](#issues)
 * [License](#license)

## 主要功能

- 整合 [uiautomator2](https://github.com/openatx/uiautomator2)，实现基于控件的自动化测试
- 依赖 [pytest-variables](https://github.com/pytest-dev/pytest-variables) 实现参数化配置
- 借助 [allure](https://github.com/allure-framework/allure-python) 生成测试报告
- 借助 hook 机制，实现“点击、滑动时自动截图”、“异常时自动抓取控件信息和截图”等 fixture，减少重复工作
- 通过安装 pytest 插件，实现诸如“失败重试”、“分布式执行”、“用例分层”等



## 安装

**强烈建议** 使用 git 对代码进行版本控制，灵活运用分支开发的策略，并且将自动化整合进 DevOps 流程中。

**推荐** 本地开发使用基于`virtualenv`的工具实现环境隔离和解决各个模块之间的依赖，如`pipenv`。

**建议** 生产环境使用`docker`对各个设备之间进行“隔离”。

### 1. 安装 python

macOS、linux可以通过 [pyenv](https://github.com/pyenv/pyenv) 实现多个 python 版本的共存和切换，Windows上需要下载可执行文件、手动安装和配置环境变量。

> 因为使用了 python 3.6 的 [f-string](https://realpython.com/python-f-strings/) 特性，所以建议的 python 版本大于等于3.6。

具体安装过程略。

### 2. 创建工程

```bash
mkdir demo
cd demo
```

### 3. 安装插件和一些可选模块

推荐使用 [pipenv](https://github.com/pypa/pipenv) 进行环境管理：

```bash
# macOS
brew install pipenv
# windows,linux
pip install --user pipenv

# 必须，根据您的配置文件格式，二选一（因为插件目前在 alpha 测试阶段，需要添加`--pre`参数）
# 注意，pipenv在2018.11.26版本之后，才能支持额外（extras）模块（即安装时的中括号语法），所以使用较新的版本、或手动安装
pipenv install --pre pytest-android[yaml]	# yaml 作为配置文件，推荐
pipenv install --pre pytest-android[hjson]	# json 作为配置文件

# 以下为可选模块，根据需要选择性安装
pipenv install weditor		# uiautomator2 的录制工具
pipenv install allure-pytest		# 使用 allure 生成报告
pipenv install pytest-rerunfailures		# 使 pytest 支持失败重试
```
> PS: pip版本大于等于18时，pipenv需要的最低版本为2018.11.26（如果低于此版本会导致一系列错误）

> 注意：根据[这里的观点](https://pipenv.readthedocs.io/en/latest/advanced/#pipfile-vs-setup-py)，pytest-android 作为 **libraries**，将部署到某个特定的环境中，然后才能使所有依赖项和子依赖项的确切版本具体化。

## 使用

### 1. 创建配置文件

#### ~~1.1 config.yaml~~

~~创建项目级配置文件，参考 [config.yaml](https://raw.githubusercontent.com/edsion1107/pytest-android/master/config.yaml)。此文件可以使用 yaml 和 hjson 格式（由 pytest-variables 插件实现），文件名任意。~~

~~配置文件可以同时指定多个（遇到相同字段，后面的会覆盖前面的），借助此功能可以实现：指定设备参数、实现复杂情况下的兼容性测试等。~~

#### ~~1.2 pytest.ini~~

~~创建 pytest 的配置文件，参考[文档](https://docs.pytest.org/en/latest/reference.html#configuration-options)进行基础配置。~~

~~添加`addopts = --variables config.yaml`，指定项目配置文件。~~

#### 1.1 创建配置文件 config.yaml 和 pytest.ini

项目配置文件 config.yaml，pytest 配置文件 pytest.ini ，区别：

pytest.ini 只能有一个，且文件名不可修改；

config.yaml 可以有多个（通过 pytest-variables 插件实现，需在pytest.ini 中指定），文件名任意，并且可以同时载入多个文件（遇到重复字段时，最后一个生效）。

通过配置文件，可以对测试进行参数化配置，提高测试的灵活性，降低代码维护的工作量，和减少可能的疏忽导致的异常。

目前已实现命令行工具，可以直接执行命令下载对应的配置文件示例：

```bash
pipenv run python -m pytest_android download --init
```

如果已经手动创建，或者想重新下载指定的文件，可以附加对应的参数：

```bash
pipenv run python -m pytest_android download --pytest.ini
pipenv run python -m pytest_android download --config.yaml
```



> 当本地文件与示例文件不一致时，会提示是否覆盖，可以选择N然后手动合并。



#### 1.2 根据需求调整配置[可选]

如果使用 allure 生成报告，并安装了对应依赖，可以通过`--alluredir`指定报告的路径，通过`--clean-alluredir`指定开始前是否清理历史数据。更多参数可参考[插件文档](https://docs.qameta.io/allure/#_pytest)

如果借助 pytest-rerunfailures 插件实现失败重试，参考[插件文档](https://github.com/pytest-dev/pytest-rerunfailures)，添加`--reruns`

其他诸如 log 、markers，和第三方插件配置，根据需要参考对应文档。



### 2. 编写用例

#### 2.1 可用的Fixtures

此处文档可能更新不及时，通过执行命令`python -m pytest --fixtures`，可以列出所有 fixtures 及其最新说明文档。

| Name           |  Scope   | Autouse | Description                                    |
| :------------- | :------: | :-----: | :--------------------------------------------- |
| driver         | session  |  True   | 初始化设备                                     |
| show_case_name | function |  True   | toast 提示显示用例描述或名字，便于了解进度     |
| app_start      | function |  True   | 启动 app ，（仅）通过当前 app 包名判断是否启动 |

根据 pytest 的[加载顺序](https://docs.pytest.org/en/latest/writing_plugins.html#plugin-discovery-order-at-tool-startup)，插件中定义的 fixture 是可以被 `conftest.py`和本地插件`pytest_plugins `覆盖的。也就是说，如果具体到项目时不满足需求，可以在工程内新建`conftest.py`文件，编写同名 fixture，修改`scope`、`autoues`和其具体行为。



#### 2.2 编写用例

新建文件 `test_demo.py`，输入以下代码：

```python
#!/usr/bin/env python
# encoding: utf-8
from uiautomator2 import UIAutomatorServer


def test_233(driver: UIAutomatorServer):
    print(driver.device_info)
```



运行：

```bash
pipenv run python -m pytest
```



## Issues

如果插件使用中遇到问题，请通过 [github issues](https://github.com/edsion1107/pytest-android/issues) 提交。



## License

Distributed under the terms of the [MIT](LICENSE) license, "pytest-android" is free and open source software.

根据[MIT](LICENSE)许可条款分发，“pytest-android”是免费的开源软件。
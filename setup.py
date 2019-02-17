#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path
from setuptools import setup

with open(Path(__file__).parent / "README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pytest-android',
    use_scm_version=True,
    packages=['pytest_android'],
    package_dir={"": "src"},
    author='edsion',
    author_email='edsion@i1hao.com',
    maintainer='edsion',
    maintainer_email='edsion@i1hao.com',
    license='MIT',
    url='https://github.com/edsion1107/pytest-android',
    description='This fixture provides a configured "driver" for Android Automated Testing, using uiautomator2.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='~=3.6',
    install_requires=['pytest', 'pytest-variables', 'progressbar2', 'requests_download', 'retry', 'uiautomator2', ],
    setup_requires=['setuptools_scm', 'setuptools_scm_git_archive'],
    extras_require={
        'hjson': ['hjson'],
        'yaml': ['PyYAML'],
        'allure': ['pillow', 'allure-pytest'],
        'rerunfailures': ['pytest-rerunfailures'],
        'weditor': ['weditor'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Quality Assurance',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Operating System :: MacOS',
        'Operating System :: Android',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Natural Language :: Chinese (Simplified)',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'pytest11': [
            # 格式：插件名=模块名，插件名可以用'-',python的模块则用'_'
            'pytest-android = pytest_android',
        ],
    },
)

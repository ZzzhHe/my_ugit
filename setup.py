"""使用 setup.py 来构建自己的 ugit 包"""

#!/usr/bin/env python3

"""
在 Python 中，setup.py 是用于构建和分发 Python 包的模块。
它通常包含有关包的信息，例如名称、版本和依赖项，以及构建和安装包的说明。

为了能够在开发的同时运行ugit包来检测效果，需要使用开发模式
python3 setup.py develop --user
"""

# https://setuptools.pypa.io/en/latest/userguide/quickstart.html
from setuptools import setup

setup (name = 'ugit',
        version = '1.0',
        packages = ['ugit'],
        entry_points = {
            'console_scripts' : [
                'ugit = ugit.cli:main'
            ]
        })
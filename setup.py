"""use setup.py to make my own python package -- ugit"""

#!/usr/bin/env python3

"""
if we use development mode, we can edit the source and run it immediately
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
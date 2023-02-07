"""
Manages the data in .ugit directory. 
Here will be the code that actually touches files on disk.
"""

import os

GIT_DIR = ".ugit"

def init():
    os.makedirs(GIT_DIR)
"""
the basic higher-level logic of ugit
to implement higher-level structures for storing directories
"""
import os

from . import data

def write_tree(directory='.'):
    """
    print a directory recursively
    """
    with os.scandir(directory) as it:
        for entry in it:
            full = f'{directory}/{entry.name}'
            if is_ignored(full):
                continue
            
            if entry.is_file(follow_symlinks=False):
                with open(full, 'rb') as f:
                    # get a separate OID for each file
                    print(data.hash_object(f.read(), full))
            elif entry.is_dir(follow_symlinks=False):
                write_tree(full)
    
    # TODO: actually create the tree object

def is_ignored(path):
    """
    ignore it the directory that isn't part of the user's files?
    """
    return '.ugit' in path.split('/')
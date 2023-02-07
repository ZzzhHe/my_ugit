"""
the basic higher-level logic of ugit
to implement higher-level structures for storing directories
"""
import os

from . import data

def write_tree(directory='.'):
    """
    create a tree to represent the directory recursively
    
    iterate through every level of the given directory,
    save separate levels of the directory as different entries
    
    for a level of the directory, iterate every item in this directory,  
    then create a tree for this level and return it
    if the item is a file: get and save oid of this file
    if the item is a directory: use recursion to go to the deeper level, 
                                then get the return: an oid that deeper level's tree
    """
    
    
    entries = []
    with os.scandir(directory) as it:
        for entry in it:
            full = f'{directory}/{entry.name}'
            if is_ignored(full):
                continue
            
            if entry.is_file(follow_symlinks=False):
                type_ = 'blob'
                with open(full, 'rb') as f:
                    # get a separate OID for each file
                    oid = data.hash_object(f.read())
            elif entry.is_dir(follow_symlinks=False):
                # get an oid of the tree that can represent the directory
                type_ = 'tree'
                oid = write_tree(full)
            
            entries.append((entry.name, oid, type_))
    
    # create a tree for this level of the directory
    tree = ''.join(f'{type_} {oid} {name}\n'
                for name, oid, type_ in sorted(entries))

    # return the oid of the tree (the content in files in /objects show a extra tree)
    return data.hash_object(tree.encode(), 'tree')

def is_ignored(path):
    """
    ignore it the directory that isn't part of the user's files?
    """
    return '.ugit' in path.split('/')
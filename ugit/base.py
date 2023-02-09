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
    
    :return: the oid of the tree of the directory
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

def _iter_tree_entries(oid):
    """
    a generator that will take an OID of a tree, 
    tokenize it line-by-line and yield the raw string values.
    """
    if not oid:
        return
    tree = data.get_object(oid, 'tree')
    for entry in tree.decode().splitlines():
        type_, oid, name = entry.split(' ', 2)
        # yield a generator
        # https://stackoverflow.com/questions/231767/what-does-the-yield-keyword-do 
        yield type_, oid, name

def get_tree(oid, base_path="."):
    """
    uses '_iter_tree_entries' to recursively parse a tree into a dictionary
    
    :return: a dictionary {path: oid} contains every node in the tree
    """
    result = {}
    for type_, oid, name in _iter_tree_entries(oid):
        assert '/' not in name
        # . :'the current folder'.
        # .. :'the folder containing the current folder'.
        assert name not in ('..', '.')
        path = base_path + name
        if type_ == 'blob':
            result[path] = oid
        elif type_ == 'tree':
            # 'update()' inserts the specified items to the dictionary.
            result.update(get_tree(oid, f'{path}/'))
        else:
            assert False, f'Unknow tree entry {type_}'
    return result

def _empty_current_directory():
    """
    delete all existing stuff before reading
    """
    # os.walk()
    # Generate the file names in a directory tree 
    # by walking the tree either top-down or bottom-up. 
    # :root: is a string, the path to the directory
    # :dirnames:  is a list of the names of the subdirectories in dirpath 
    #            (including symlinks to directories, and excluding '.' and '..')
    # :filenames: is a list of the names of the non-directory files in root
    for root, dirnames, filenames in os.walk('.', topdown=False):
        # iterate every files
        for filename in filenames:
            # Return a relative filepath to path 
            path = os.path.relpath(f'{root}/{filename}')
            if is_ignored(path) or not os.path.isfile(path):
                continue
            os.remove(path)
        # iterate every directory
        for dirname in dirnames:
            path = os.path.relpath(f'{root}/{dirname}')
            if is_ignored(path):
                continue
            try:
                # delete a empty directory
                os.rmdir(path)
            except(FileNotFoundError, OSError):
                # Deletion might fail if the directory contains ignored files,
                # so it's OK
                pass

def read_tree(tree_oid):
    """
    uses 'get_tree' to get the file OIDs 
    and writes them into the working directory.
    (recover the whole tree)
    """
    _empty_current_directory()
    for path, oid in get_tree(tree_oid, base_path='./').items():
        # 'exist_ok': no error will be raised if the target directory already exists.
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            # write content of object
            f.write(data.get_object(oid))

def commit(message):
    """
    write the "tree" key and the commit message to the commit object
    
    :return: a text file stored in the object database 
            with the type of 'commit'
    """
    commit = f'tree {write_tree()}\n'
    commit += '\n'
    commit += f'{message}\n'
    
    return data.hash_object(commit.encode(), 'commit')

def is_ignored(path):
    """
    ignore it the directory that isn't part of the user's files?
    """
    return '.ugit' in path.split('/')
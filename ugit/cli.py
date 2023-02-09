"""
In charge of parsing and processing user input.
"""

# https://docs.python.org/3/library/argparse.html
import argparse
import os 
import sys
import textwrap

from . import data
from . import base


def main():
    # parse the args and call whatever function was selected
    args = parse_args()
    args.func(args)
    
def parse_args():
    parser = argparse.ArgumentParser()
    
    # when a program performs several different functions 
    # which require different kinds of command-line arguments
    # use subparsers
    commands = parser.add_subparsers(dest="command")
    commands.required = True
    
    # create parser for 'init' command, and bind 'init' with init()
    init_parser = commands.add_parser('init')
    init_parser.set_defaults(func=init)
    
    # create parser for 'hash-object' command, and bind 'hash-object' with hash_object()
    hash_object_parser = commands.add_parser('hash-object')
    hash_object_parser.set_defaults(func=hash_object)
    hash_object_parser.add_argument('file')
    
    # create parser for 'cat-file' command, and bind
    cat_file_parser = commands.add_parser('cat-file')
    cat_file_parser.set_defaults(func=cat_file)
    cat_file_parser.add_argument('object')
    
    # create parser for 'write-tree' command, and bind
    write_tree_parser = commands.add_parser('write-tree')
    write_tree_parser.set_defaults(func=write_tree)
    
    # create parser for 'read-tree' command, and bind
    read_tree_parser = commands.add_parser ('read-tree')
    read_tree_parser.set_defaults (func=read_tree)
    read_tree_parser.add_argument ('tree')
    
    # create parser for 'commit' command, and bind
    commit_parser = commands.add_parser ('commit')
    commit_parser.set_defaults (func=commit)
    commit_parser.add_argument ('-m', '--message', required=True)
    
    log_parser = commands.add_parser ('log')
    log_parser.set_defaults (func=log)
    commit_parser.add_argument ('oid', nargs='?')

    # Namespace(command='init') 
    # Namespace(command='hash-object', argument='file') 
    # Namespace(command='cat-file', argument='object') 
    # Namespace(command='write-tree') 
    # Namespace(command='read-tree', argument='tree') 
    # Namespace(command='commit', argument='-m') 
    # Namespace(command='log', argument='oid') 
    return parser.parse_args()
    
def init(args):
    """ 
    init a empty ugit respository
    """
    data.init()
    print(f'Initialized empty ugit respository in {os.getcwd()}/{data.GIT_DIR}')
    
def hash_object(args):
    """ 
    save objects to object database in ugit respository
    with content-addressable storage, which means 
    finding a object is based on the content of the object itself
    """
    with open(args.file, 'rb') as f:
        print(data.hash_object(f.read()))
        
def cat_file(args):
    """ 
    print an object by its OID
    
    args.object(): get 'object' argument from command line
    """
    sys.stdout.flush()
    sys.stdout.buffer.write(data.get_object(args.object, expected=None))

def write_tree(args):
    """
    take the current working directory 
    and store it to the object database
    """
    print(base.write_tree())

def read_tree(args):
    """
    take an OID of a tree and extract it to the working directory. 
    (the opposite of write-tree)
    """
    base.read_tree(args.tree)

def commit(args):
    """
    command that will accept a commit message, 
    snapshot the current directory and save the resulting object.
    """
    print(base.commit(args.message))

def log(args):
    """
    print entire commit history 
    
    start from the HEAD commit or input oid from CLI
    and walk its parents until we reach a commit without a parent
    """
    oid = args.oid or data.get_HEAD()
    while oid:
        commit = base.get_commit(oid)
        
        print(f'commit {oid}\n')
        print(textwrap.indent (commit.message, '    '))
        print('')
        
        oid = commit.parent
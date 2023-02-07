"""
In charge of parsing and processing user input.
"""

# https://docs.python.org/3/library/argparse.html
import argparse
import os 

from . import data


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
    
    # create parese for 'init' command, and bind 'init' with init()
    init_parser = commands.add_parser('init')
    init_parser.set_defaults(func=init)
    
    # create parese for 'hash-object' command, and bind 'hash-object' with hash_object()
    hash_object_parser = commands.add_parser('hash-object')
    hash_object_parser.set_defaults(func=hash_object)
    hash_object_parser.add_argument('file')

    # Namespace(command='init') 
    # Namespace(command='hash-object', argument='file') 
    return parser.parse_args()
    
def init(args):
    """ init a empty ugit respository
    """
    data.init()
    print(f'Initialized empty ugit respository in {os.getcwd()}/{data.GIT_DIR}')
    
def hash_object(args):
    """ refer to the file's object using its hash
    """
    with open(args.file, 'rb') as f:
        print(data.hash_object(f.read()))
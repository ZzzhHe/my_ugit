"""
Add argument parser
"""

# https://docs.python.org/3/library/argparse.html
import argparse

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

    # Namespace(command='init') 
    return parser.parse_args()
    
def init(args):
    print("Hello World")
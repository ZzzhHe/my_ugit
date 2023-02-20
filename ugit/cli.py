"""
In charge of parsing and processing user input.
"""

# https://docs.python.org/3/library/argparse.html
import argparse
import os 
import sys
import textwrap
import subprocess

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
    
    # resolve name to oid in argparse
    oid = base.get_oid
    
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
    cat_file_parser.add_argument('object', type=oid)
    
    # create parser for 'write-tree' command, and bind
    write_tree_parser = commands.add_parser('write-tree')
    write_tree_parser.set_defaults(func=write_tree)
    
    # create parser for 'read-tree' command, and bind
    read_tree_parser = commands.add_parser ('read-tree')
    read_tree_parser.set_defaults (func=read_tree)
    read_tree_parser.add_argument ('tree', type=oid)
    
    # create parser for 'commit' command, and bind
    commit_parser = commands.add_parser ('commit')
    commit_parser.set_defaults (func=commit)
    commit_parser.add_argument ('-m', '--message', required=True)
    
    log_parser = commands.add_parser ('log')
    log_parser.set_defaults (func=log)
    # pass HEAD by default in argparse
    log_parser.add_argument ('oid', default='@', type=oid, nargs='?')
    
    checkout_parser = commands.add_parser ('checkout')
    checkout_parser.set_defaults (func=checkout)
    checkout_parser.add_argument ('commit')
    
    tag_parser = commands.add_parser ('tag')
    tag_parser.set_defaults (func=tag)
    tag_parser.add_argument ('name')
    # pass HEAD by default in argparse
    tag_parser.add_argument ('oid', default='@', type=oid, nargs='?')
    
    # a visualization tool to see all the mess that we've created, called 'k'
    k_parser = commands.add_parser ('k')
    k_parser.set_defaults (func=k)
    
    branch_parser = commands.add_parser ('branch')
    branch_parser.set_defaults (func=branch)
    branch_parser.add_argument ('name')
    branch_parser.add_argument ('start_point', default='@', type=oid, nargs='?')

    # Namespace(command='init') 
    # Namespace(command='hash-object', argument='file') 
    # Namespace(command='cat-file', argument='object') 
    # Namespace(command='write-tree') 
    # Namespace(command='read-tree', argument='tree') 
    # Namespace(command='commit', argument='-m') 
    # Namespace(command='log', argument='oid' (default='@')) 
    # Namespace(command='checkout', argument='commit') 
    # Namespace(command='tag', argument='name'; 'oid'(default='@'))
    # Namespace(command='branch', argument='name'; 'start_point'( default='@'))
    
    return parser.parse_args()
    
def init(args):
    """ 
    init a empty ugit respository
    """
    base.init()
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
    for oid in base.iter_commits_and_parents({args.oid}):
        commit = base.get_commit(oid)
        
        print(f'commit {oid}\n')
        print(textwrap.indent (commit.message, '    '))
        print('')

def checkout(args):
    """
    move HEAD to point to oid
    """
    base.checkout(args.commit)

def tag(args):
    """
    create a tag for a oid to remember this oid easily
    """
    oid = args.oid or data.get_ref('HEAD')
    base.create_tag(args.name, oid)

def k(args):
    """
    a graphical visualization tool to see all the mess that we've created
    """
    dot = 'digraph commits {\n'
    
    oids = set()
    # make tag name point to oid as note, including 'HEAD' tag
    for refname, ref in data.iter_refs(deref=False):
        dot += f'"{refname}" [shape=note]\n'
        dot += f'"{refname}" -> "{ref.value}"\n'
        # only ono-symbolic refs can be added into the set of oids
        if not ref.symbolic:
            oids.add(ref.value)
    
    # create a whole graph represent the history commits
    for oid in base.iter_commits_and_parents(oids):
        commit = base.get_commit(oid)
        dot += f'"{oid}" [shape=box style=filled label="{oid[:10]}"]\n'
        if commit.parent:
            dot += f'"{oid}" -> "{commit.parent}"\n'
    
    dot += '}'
    print (dot)
    
    with subprocess.Popen (
            ['dot', '-Txlib', '/dev/stdin'],
            stdin=subprocess.PIPE) as proc:
        proc.communicate (dot.encode ())
    
def branch(args):
    """
    point a branch to a specific OID
    """
    base.create_branch(args.name, args.start_point)
    print(f'Branch {args.name} created at {args.start_point[:10]}')
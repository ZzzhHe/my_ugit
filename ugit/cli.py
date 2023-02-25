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
from . import diff
from . import remote


def main():
    # parse the args and call whatever function was selected
    # initialized the GIT_GIR
    with data.change_git_dir('.'):
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
    
    diff_parser = commands.add_parser ('diff')
    diff_parser.set_defaults (func=_diff)
    diff_parser.add_argument ('--cached', action='store_true')
    diff_parser.add_argument ('commit', nargs='?')
    
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
    branch_parser.add_argument ('name', nargs='?')
    branch_parser.add_argument ('start_point', default='@', type=oid, nargs='?')

    status_parser = commands.add_parser('status')
    status_parser.set_defaults(func=status)
    
    reset_parser = commands.add_parser ('reset')
    reset_parser.set_defaults (func=reset)
    reset_parser.add_argument ('commit', type=oid)
    
    show_parser = commands.add_parser('show')
    show_parser.set_defaults(func=show)
    show_parser.add_argument('oid', default='@', type=oid, nargs='?')
    
    merge_parser = commands.add_parser('merge')
    merge_parser.set_defaults(func=merge)
    merge_parser.add_argument('commit', type=oid)
    
    merge_base_parser = commands.add_parser('merge-base')
    merge_base_parser.set_defaults(func=merge_base)
    merge_base_parser.add_argument('commit1', type=oid)
    merge_base_parser.add_argument('commit2', type=oid)
    
    fetch_parser = commands.add_parser('fetch')
    fetch_parser.set_defaults(func=fetch)
    fetch_parser.add_argument('remote')
    
    push_parser = commands.add_parser('push')
    push_parser.set_defaults(func=push)
    push_parser.add_argument('remote')
    push_parser.add_argument('branch')
    
    add_parser = commands.add_parser ('add')
    add_parser.set_defaults (func=add)
    add_parser.add_argument ('files', nargs='+')
    
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

def _print_commit(oid, commit, refs=None):
    """
    print commit info
    """
    refs_str = f'({", ".join(refs)})' if refs else ''
    print(f'commit {oid}{refs_str}\n')
    print(textwrap.indent(commit.message, '    '))
    print('')

def log(args):
    """
    print entire commit history 
    
    start from the HEAD commit or input oid from CLI
    and walk its parents until we reach a commit without a parent
    """
    refs = {}
    for refname, ref in data.iter_refs():
        # 1 oid vs. more ref (may be 0)
        refs.setdefault(ref.value, []).append(refname)
        
    for oid in base.iter_commits_and_parents({args.oid}):
        commit = base.get_commit(oid)
        _print_commit(oid, commit, refs.get(oid))

def show(args):
    """
    show the commit message and the textual diff from the last commit
    """
    if not args.oid:
        return 
    commit = base.get_commit(args.oid)
    parent_tree = None
    if commit.parents:
        parent_tree = base.get_commit(commit.parents[0]).tree
        
    _print_commit(args.oid, commit)
    result = diff.diff_trees(
        base.get_tree(parent_tree), 
        base.get_tree(commit.tree))
    # Since "diff"'s output is a byte string, 
    # output it raw to stdout using sys.stdout.buffer.write()
    sys.stdout.flush ()
    sys.stdout.buffer.write (result)

def _diff(args):
    """
    compare
        no parameter: diff from the index to the working directory, which can quickly find unstaged changes.
        --cached: diff from HEAD to the index, which can quickly find which changes are going to be commited.
        --specific ommit: diff from the commit to the index or working directory
                            (depending on whether --cached was provided).
    """
    oid = args.commit and base.get_oid (args.commit)
    
    if args.commit:
        # If a commit was provided explicitly, diff from it
        tree_from = base.get_tree(oid and base.get_commit(oid).tree)
    
    if args.cache:
        tree_to = base.get_index_tree()
        if not args.commit:
            # If no commit was provided, diff from HEAD
            oid = base.get_oid('@')
            tree_from = base.get_tree(oid and base.get_commit(oid).tree)
    else:
        tree_to = base.get_working_tree()
        if not args.commit:
            # If no commit was provided, diff from index
            tree_from = base.get_index_tree()
    # compare the "working tree" with the tree of some commit. 
    # The "working tree" is a dictionary that describes the files in the working directory.
    result = diff.diff_trees(tree_from, tree_to)
    sys.stdout.flush()
    sys.stdout.buffer.write(result)
    
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
        for parent in commit.parents:
            dot += f'"{oid}" -> "{parent}"\n'
    
    dot += '}'
    print (dot)
    
    with subprocess.Popen (
            ['dot', '-Txlib', '/dev/stdin'],
            stdin=subprocess.PIPE) as proc:
        proc.communicate (dot.encode ())
    
def branch(args):
    """
    print all branches
    point a branch to a specific OID(args.start_point)
    """
    if not args.name:
        current = base.get_branch_name()
        for branch in base.iter_branch_names():
            # * current branch
            prefix = '*' if branch == current else ' '
            print(f'{prefix} {branch}')
        
    else:
        base.create_branch(args.name, args.start_point)
        print(f'Branch {args.name} created at {args.start_point[:10]}')
    
def status(args):
    """
    print useful information about our working directory
    """
    HEAD = base.get_oid('@') # default: HEAD
    branch = base.get_branch_name()
    if branch:
        print(f'On branch {branch}')
    else:
        print(f'HEAD detached at {HEAD[:10]}')
    
    # if MERGE_HEAD exist
    # helpfully inform the user when we're in the middle of a merge
    MERGE_HEAD = data.get_ref ('MERGE_HEAD').value
    if MERGE_HEAD:
        print (f'Merging with {MERGE_HEAD[:10]}')

    print ('\nChanges to be committed:\n')
    HEAD_tree = HEAD and base.get_commit(HEAD).tree
    # comparing HEAD and the index tree (show changed files)
    for path, action in diff.iter_change_files(base.get_tree(HEAD_tree),
                                                base.get_index_tree ()):
        print(f'{action:>12}: {path}')

    print('\nChanges not staged for commit:\n')
    # comparing the index tree and the working directory (show changed files)
    for path, action in diff.iter_changed_files(base.get_index_tree(),
                                                base.get_working_tree()):
        print(f'{action:>12}: {path}')

def reset(args):
    """
    move HEAD to an OID of our choice,
    which is useful to undo a commit.
    """
    
    """
    > the difference between checkout and reset?
        checkout leaves master at the previous place. 
        That's why we need reset, to move the actual branch and 
        not just HEAD.
    """
    base.reset(args.commit)
    
def merge(args):
    """
    bring the parallel branches back together
    """
    base.merge(args.commit)

def merge_base (args):
    """
    receive two commit OIDs and find their common ancestor
    """
    print(base.get_merge_base(args.commit1, args.commit2))

def fetch(args):
    """
    download refs and associated objects from a remote repository
    (only support remote repositories that are located on the same filesystem)
    """
    remote.fetch(args.remote)

def push(args):
    """
    uploads objects and synchronizes the local refs to the remote refs
    
    when you've added some commits and you'd like to update a remote repository 
    so that it's synchronized with your local version
    """
    remote.push(args.remote, f'refs/heads/{args.branch}')
    
def add(args):
    """
    add files that we want to commit to *index*, which can allow finer grained control over commited files
    """
    base.add(args.files)
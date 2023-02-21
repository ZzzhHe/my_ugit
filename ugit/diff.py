import subprocess

from collections import defaultdict
from tempfile import NamedTemporaryFile as Temp

from . import data

def compare_trees(*trees):
    """
    take a list of trees(*trees) 
    :return: trees grouped by filename
    for example, {dog.txt:[dog_oid_1, dog_oid_2], cat.txt:[cat_oid_1, cat_oid_2]}
    """
    # defaultdict is dict with default value 
    # default value:  a number of lists                
    #                       v 
    entries = defaultdict(lambda: [None] * len(trees))
    for i, tree in enumerate(trees):
        for path, oid in tree.items():
            entries[path][i] = oid
    for path, oids in entries.items():
        yield (path, *oids)       
    
def diff_trees(t_from, t_to):
    """
    takes two trees, compares them  
    :return: all entries(file_path) that have different OIDs
    """
    output = b''
    for path, o_form, o_to in compare_trees(t_from, t_to):
        if o_form != o_to:
            output += diff_blob(o_form, o_to, path)
    return output

def diff_blob(o_from, o_to, path='blob'):
    """
    take two blob OIDs 
    :return: the diff between them
    """
    with Temp() as f_from, Temp() as f_to:
        for oid, f in ((o_from, f_from), (o_to, f_to)):
            if oid:
                f.write(data.get_object(oid))
                f.flush()

        # use an external Unix utility called "diff". 
        # It receives two files as arguments and 
        # prints the differences between them in diff format
        with subprocess.Popen(
            ['diff', '--unified', '--show-c-function',
             '--label', f'a/{path}', f_from.name,
             '--label', f'b/{path}', f_to.name],
            stdout=subprocess.PIPE) as proc:
            output, _ = proc.communicate()

        return output

def iter_change_files(t_from, t_to):
    """
    take two trees and output all changed paths along with the change type 
    (deleted, created, modified)
    """
    for path, o_from, o_to in compare_trees(t_from, t_to):
        if o_from != o_to:
            action = (
                'new file' if not o_from else
                'deleted' if not o_to else
                'modified'
            )
            yield path, action
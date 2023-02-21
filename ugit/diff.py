import subprocess

from collections import defaultdict
from tempfile import NamedTemporaryFile as Temp

from . import data

def compare_trees(*trees):
    """
    take a list of trees(*trees) 
    :return: them grouped by filename
    """
    # The main difference between defaultdict and dict is that 
    # when you try to access or modify a key that’s not present in the dictionary, 
    # a default value is automatically given to that key. 
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
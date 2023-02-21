from collections import defaultdict

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
    output = ''
    for path, o_form, o_to in compare_trees(t_from, t_to):
        if o_form != o_to:
            output += f'change: {path}\n'
    
    return output
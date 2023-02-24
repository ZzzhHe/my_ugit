"""
Manages the data in .ugit directory. 
Here will be the code that actually touches files on disk.
"""
import os
import hashlib

from collections import namedtuple

GIT_DIR = ".ugit"

def init():
    os.makedirs(GIT_DIR)
    os.makedirs(f'{GIT_DIR}/objects')
    
def hash_object(data, type_='blob'):
    """ 
    refer to the file's object using its hash 
    and create a new byte file in 'objects' named by oid
    
    :type_: add a type tag for each object
    :return: hash id of 'type + data'
    """
    
    obj = type_.encode() + b'\x00' + data
    oid = hashlib.sha1(obj).hexdigest()
    with open(f'{GIT_DIR}/objects/{oid}', 'wb') as out:
        out.write(obj)
    return oid

def get_object(oid, expected='blob'):
    """ 
    get object by its OID
    
    :expected: expected type
    :return: object's content
    """
    with open(f'{GIT_DIR}/objects/{oid}', 'rb') as f:
        obj = f.read()
        
    type_, _, content = obj.partition(b'\x00')
    type_ = type_.decode()
    
    if expected is not None:
        # verify type_ is indeed the expected type
        # https://www.w3schools.com/python/ref_keyword_assert.asp
        assert type_ == expected, f'Expected {expected}, got {type_}'
    return content

# create a RefValue container to represent the value of a ref. 
# RefValue have a property symbolic that will say whether it's a symbolic or a direct ref.
"""
# https://git-scm.com/book/en/v2/Git-Internals-Git-References
> What is ref in git?
    A ref is an indirect way of referring to a commit. 
    You can think of it as a user-friendly alias for a commit hash. 
    This is Git's internal mechanism of representing branches and tags. 
    Refs are stored as normal text files in the .git/refs directory, 
        where .git is usually called .git.
> What is the symbolic in ref?
    Usually the HEAD file is a symbolic reference to the branch you’re currently on. 
    By symbolic reference, we mean that unlike a normal reference, 
        it contains a pointer to another reference
"""
RefValue = namedtuple('RefValue', ['symbolic', 'value'])

def update_ref(ref, value, deref=True):
    """
    recode the oid in .ugit/{ref} file
    ref == HEAD : make HEAD point to this oid
    ref == refs/tags/ : write oid in tags files to record tags that be provided by the user
    """
    # get last non-symbolic ref it needs to update by using _get_ref_internal
    ref = _get_ref_internal(ref, deref)[0]
    # write a symbolic value
    assert value.value
    if value.symbolic:
        value = f'ref: {value.value}'
    else:
        value = value.value
    ref_path = f'{GIT_DIR}/{ref}'
    
    os.makedirs(os.path.dirname(ref_path), exist_ok=True)
    with open(ref_path, 'w') as f:
        f.write(value)
        
def get_ref(ref, deref=True):
    """
    :deref: if True, dereference all symbolic refs; if False, raw value of a ref, not dereference
    
    :return: the value of the last ref pointed by a symbolic ref
    """
    return _get_ref_internal(ref, deref)[1]

def delete_ref(ref, deref=True):
    """
    removes an existing ref
    """
    ref = _get_ref_internal(ref, deref)[0]
    os.remove(f'{GIT_DIR}/{ref}')

def _get_ref_internal(ref, deref=True):
    """
    if deref is True:
    return the path and the value of the last non-symbolic ref pointed by a symbolic ref
    else:
    return the path and the value of the ref(passed in as parameter)
    """
    ref_path = f'{GIT_DIR}/{ref}'
    value = None
    if os.path.isfile(ref_path):
        with open(ref_path) as f:
            value = f.read().strip()

    # When given a symbolic ref, _get_ref_internal will dereference the ref recursively, 
    #   find the name of the last non-symbolic ref (that points to an OID) and return it,
    #   plus its value.
    symbolic = bool(value) and value.startswith('ref:')
    if symbolic:
        # "ref: path"
        #       value
        value = value.split(':', 1)[1].strip()
        if deref:
            # value is the path of the symbolic ref
            return _get_ref_internal(ref=value, deref=True)
    
    return ref, RefValue(symbolic=symbolic, value=value)
    
def iter_refs(prefix='', deref=True):
    """
    a generator which will iterate on all available refs (with prefix) 
    :return: HEAD from the ugit root directory and everything under .ugit/refs
    """
    refs = ['HEAD', 'MERGE_HEAD']
    for root, _, filenames in os.walk(f'{GIT_DIR}/refs/'):
        # root = root - GIT_DIR
        root = os.path.relpath(root, GIT_DIR)
        refs.extend(f'{root}/{name}' for name in filenames)
        
    for refname in refs:
        if not refname.startswith(prefix):
            continue
        ref = get_ref (refname, deref=deref)
        if ref.value:
            yield refname, ref

def debug_get_object(path):
    
    if os.path.isfile(path):
        with open(path) as f:
            value = f.read()
            return value
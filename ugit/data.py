"""
Manages the data in .ugit directory. 
Here will be the code that actually touches files on disk.
"""
import os
import hashlib

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

def update_ref(ref, oid):
    """
    recode the oid in .ugit/{ref} file
    ref == HEAD : make HEAD point to this oid
    ref == refs/tags/ : write oid in tags files to record tags that be provided by the user
    """
    with open(f'{GIT_DIR}/{ref}', 'w') as f:
        f.write(oid)

def get_ref(ref):
    """
    ref == HEAD: get oid from the HEAD file
    ref == refs/tags: get oid from the tag file
    """
    if os.path.isfile(f'{GIT_DIR}/{ref}'):
        with open(f'{GIT_DIR}/{ref}') as f:
            return f.read().strip()
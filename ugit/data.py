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
    
def hash_object(data):
    """ 
    refer to the file's object using its hash 
    and create a new oid path in 'objects'
    """
    oid = hashlib.sha1(data).hexdigest()
    with open(f'{GIT_DIR}/objects/{oid}', 'wb') as out:
        out.write(data)
    return oid

def get_object(oid):
    """ get object by its OID
    """
    with open(f'{GIT_DIR}/objects/{oid}', 'rb') as f:
        return f.read()
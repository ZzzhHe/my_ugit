"""
contain all remote synchronization code
"""

import os

from . import base
from . import data

REMOTE_REFS_BASE = 'refs/heads/'
LOCAL_REFS_BASE = 'refs/remote/'


def fetch (remote_path):
    """
    change GIT_DIR to point to the remote repository 
    and save all refs locally using our battle-tested iter_refs function
    """
    # Get refs from remote
    refs = _get_remote_refs(remote_path, REMOTE_REFS_BASE)

    # Fetch missing objects by iterating and fetching on demand
    for oid in base.iter_objects_in_commits(refs.values()):
        data.fetch_object_if_missing(oid, remote_path)
    
    # Update local refs to match remote
    for remote_name, value in refs.items():
        refname = os.path.relpath(remote_name, REMOTE_REFS_BASE)
        data.update_ref (f'{LOCAL_REFS_BASE}/{refname}',
                        data.RefValue (symbolic=False, value=value))

def _get_remote_refs (remote_path, prefix=''):
    """
    get all ref names and values from a remote repository
    """
    with data.change_git_dir(remote_path):
        return {refname: ref.value for refname, ref in data.iter_refs(prefix)}
    
def push(remote_path, refname):
    """
    push
    """
    # Get refs data from a branch_path
    remote_refs = _get_remote_refs(remote_path) # get refs from remote repository
    remote_ref = remote_refs.get(refname) #     
    local_ref = data.get_ref(refname).value
    assert local_ref
    
    """
    not remote_ref:
    The ref that we're pushing doesn't exist yet on the remote. 
    It means that it's a new branch and there is no risk of overwriting other's work.

    base.is_ancestor_of (local_ref, remote_ref):
    If the remote ref does exist, it must point to a commit that is an ancestor of the pushed ref. 
    This ancestry means that the local commit is based on the remote commit, 
    which means that the remote commit not getting overwritten, 
    since it's part of the history of the newly pushed commit.
    """
    
    # Don't allow force push
    assert not remote_ref or base.is_ancestor_of (local_ref, remote_ref)
    
    # Compute which objects the server doesn't have
    # Since the remote might have refs that point to branches that we didn't pull yet, 
    #   filter out all refs that point to unknown OIDs
    known_remote_refs = filter(data.object_exists, remote_refs)
    remote_objects = set(base.iter_objects_in_commits(known_remote_refs))
    local_objects = set(base.iter_objects_in_commits({local_ref}))
    
    objects_to_push = local_objects - remote_objects
    
    # Push all objects
    for oid in objects_to_push:
        data.push_object(oid, remote_path)
    
    # Update server ref to our value
    with data.change_git_dir(remote_path):
        data.update_ref(refname,
                        data.RefValue (symbolic=False, value=local_ref))
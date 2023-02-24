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
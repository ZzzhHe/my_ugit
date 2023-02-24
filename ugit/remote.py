from . import data


def fetch(remote_path):
    """
    change GIT_DIR to point to the remote repository 
    and list all refs using our battle-tested iter_refs function
    """
    # fetch: Print remote refs
    print('Will fetch the following refs:')
    for refname, _ in _get_remote_refs(remote_path, 'refs/heads').items ():
        print (f'- {refname}')

def _get_remote_refs (remote_path, prefix=''):
    """
    get all ref names and values from a remote repository
    """
    with data.change_git_dir(remote_path):
        return {refname: ref.value for refname, ref in data.iter_refs(prefix)}
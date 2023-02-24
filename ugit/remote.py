from . import data


def fetch(remote_path):
    """
    change GIT_DIR to point to the remote repository 
    and list all refs using our battle-tested iter_refs function
    """
    # fetch: Print remote refs
    print('Will fetch the following refs:')
    with data.change_git_dir(remote_path):
        for refname, _ in data.iter_refs('refs/heads'):
            print (f'- {refname}')
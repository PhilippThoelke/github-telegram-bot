import os
from github import Github

CREDENTIALS_FILE = '.credentials'

CREDENTIALS_FILE_MISSING_ERR = -1
UNKNOWN_MODIFIER_ERR = -2
REPOSITORY_NOT_FOUND_ERR = -3

def get_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'r') as credentials_file:
            return [line.strip() for line in credentials_file.readlines()]
    return None

def start_session():
    credentials = get_credentials()
    if credentials is None:
        return CREDENTIALS_FILE_MISSING_ERR

    return Github(credentials[0], credentials[1])

def list_repos(modifier='public', session=None):
    if session is None:
        g = start_session()
    else:
        g = session
    if type(g) is not Github:
        return g

    i = 0
    repos = []
    current = g.get_user().get_repos().get_page(i)
    while len(current) > 0:
        i += 1
        repos.extend(current)
        current = g.get_user().get_repos().get_page(i)

    if modifier == 'public':
        return [repo.name for repo in repos if not repo.private]
    elif modifier == 'private':
        return [repo.name for repo in repos if repo.private]
    elif modifier == 'all':
        return [repo.name for repo in repos]
    else:
        return UNKNOWN_MODIFIER_ERR

def get_clone_url(name):
    g = start_session()
    if type(g) is not Github:
        return g

    if not name in list_repos(modifier='all', session=g):
        return REPOSITORY_NOT_FOUND_ERR
    return g.get_user().get_repo(name).clone_url
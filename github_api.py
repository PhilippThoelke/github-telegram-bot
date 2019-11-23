import os
import base64
import pickle
from github import Github
import config_parser as parser

CREDENTIALS_FILE_MISSING_ERR = -1
UNKNOWN_MODIFIER_ERR = -2
REPOSITORY_NOT_FOUND_ERR = -3

def start_session():
    credentials = parser.get_value(parser.CREDENTIALS)
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
        return None

    if not name in list_repos(modifier='all', session=g):
        return REPOSITORY_NOT_FOUND_ERR
    return g.get_user().get_repo(name).clone_url

def get_repo(name):
    g = start_session()
    if type(g) is not Github:
        return None

    i = 0
    repos = g.get_user().get_repos().get_page(i)
    while len(repos) > 0:
        candidates = [curr for curr in repos if curr.name == name]
        if len(candidates) > 0:
            return candidates[0]

        i += 1
        repos = g.get_user().get_repos().get_page(i)

    return REPOSITORY_NOT_FOUND_ERR

def get_username():
    g = start_session()
    if type(g) is not Github:
        return None
    return g.get_user().login

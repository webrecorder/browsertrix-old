import click
import sys

import requests


# ============================================================================
class Settings:
    quiet_mode = False
    sesh = None

    server_prefix = None
    shepherd_prefix = None
    view_browsers_prefix = None


settings = Settings()


# ============================================================================
@click.group()
@click.option(
    '--server',
    metavar='<URL>',
    type=str,
    default='http://localhost:8000',
    help='The Browsertrix server url',
)
@click.option(
    '--shepherd',
    metavar='<URL>',
    type=str,
    default='http://localhost:9020',
    help='The Shepherd server url',
)
@click.option(
    '-q',
    '--quiet',
    is_flag=True,
    default=False,
    type=bool,
    help='quiet mode: print only crawl ids if success',
)
def cli(server, quiet, shepherd):
    settings.server_prefix = server

    settings.shepherd_prefix = shepherd
    settings.view_browsers_prefix = shepherd + '/attach/'

    settings.sesh = requests.session()

    settings.quiet_mode = quiet


# ============================================================================
def is_quiet():
    return settings.quiet_mode


# ============================================================================
def ensure_success(res, exit=True):
    """ Ensure API response is successful
        print error and exit if not

        :param res: Response from requests
        :param exit: Exit on any error
        :return: parsed JSON response as dict
    """
    if res.status_code == 200:
        json = res.json()
        return json

    if not is_quiet():
        print('Error response from API server')
        print('{0}: {1}'.format(res.status_code, res.text))

    if exit:
        sys.exit(1)


# ============================================================================
def conn_error_exit(url):
    if not is_quiet():
        print(
            'Unable to connect to {0}. Is Browsertrix container running in Docker?'.format(
                url
            )
        )
    sys.exit(2)


# ============================================================================
def sesh_get(url, prefix=None):
    url = (prefix or settings.server_prefix) + url
    try:
        res = settings.sesh.get(url)
        return ensure_success(res)
    except requests.exceptions.ConnectionError:
        conn_error_exit(url)


# ============================================================================
def sesh_post(url, json=None, prefix=None):
    url = (prefix or settings.server_prefix) + url
    try:
        res = settings.sesh.post(url, json=json)
        return ensure_success(res)
    except requests.exceptions.ConnectionError:
        conn_error_exit(url)


# ============================================================================
def sesh_delete(url, prefix=None):
    url = (prefix or settings.server_prefix) + url
    try:
        res = settings.sesh.delete(url)
        return ensure_success(res, exit=False)
    except requests.exceptions.ConnectionError:
        conn_error_exit(url)

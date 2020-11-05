import click
import docker
import sys
import time
import webbrowser


from browsertrix_cli.basecli import cli, is_quiet, sesh_get, settings


# ============================================================================
docker_api = None

PROFILE_PREFIX = 'oldwebtoday/profile:'

LABEL_BROWSERPROFILE = 'wr.browserprofile'
LABEL_BASEBROWSER = 'wr.basebrowser'


# ============================================================================
def get_profile_image(profile):
    """
    Get image image

    Args:
        profile: (str): write your description
    """
    try:
        global docker_api
        if not docker_api:
            docker_api = docker.from_env(version='auto')

        image_name = PROFILE_PREFIX + profile
        image = docker_api.images.get(image_name)
        assert image.labels.get(LABEL_BROWSERPROFILE) == profile
        return 'profile:' + profile

    except (docker.errors.ImageNotFound, AssertionError):
        if not is_quiet():
            print('Profile "{0}" not found'.format(profile))
        sys.exit(1)


# ============================================================================
@cli.group(help='Commands for creating/removing browser profiles')
def profile():
    """
    Create a docker profile.

    Args:
    """
    global docker_api
    docker_api = docker.from_env(version='auto')


# ============================================================================
@profile.command(name='list', help='List Profiles')
def list_profiles():
    """
    List all available docker images

    Args:
    """
    res = docker_api.images.list(filters={'label': LABEL_BROWSERPROFILE})

    format_str = '{profile: <16}  {base}'
    if not is_quiet():
        print(format_str.format(profile='PROFILE', base='BASE BROWSER'))

    for image in res:
        if not image.tags:
            continue

        if not image.tags[0].startswith(PROFILE_PREFIX):
            continue

        profile = image.tags[0][len(PROFILE_PREFIX) :]
        base_browser = image.labels.get(LABEL_BASEBROWSER, '(unknown)')

        if not is_quiet():
            print(format_str.format(profile=profile, base=base_browser))
        else:
            print(profile)

    if not is_quiet():
        print()


# ============================================================================
@profile.command(name='remove', help='Remove Profile')
@click.argument('profile', type=str)
def remove_profile(profile):
    """
    Remove a profile

    Args:
        profile: (str): write your description
    """
    full_tag = PROFILE_PREFIX + profile

    try:
        docker_api.images.remove(full_tag, force=True, noprune=False)
        if not is_quiet():
            print('Removed profile "{0}"!'.format(profile))

    except docker.errors.ImageNotFound:
        if not is_quiet():
            print('Profile "{0}" not found'.format(profile))
        sys.exit(1)


# ============================================================================
@profile.command(name='create', help='Create Profile')
@click.option(
    '--browser', default='chrome:73', type=str, help='Base Browser Image to Extend'
)
def create_profile(browser):
    """
    Create a new profile.

    Args:
        browser: (todo): write your description
    """
    res = sesh_get(
        '/api/request/{0}/about:blank'.format(browser), prefix=settings.shepherd_prefix
    )

    reqid = res.get('reqid')

    curr_browser = None

    webbrowser.open(settings.view_browsers_prefix + reqid)

    print('A new browser window should have been opened')
    print(
        'You can use the browser to log-in to accounts or otherwise prepare the browser profile'
    )
    print('(The content will not be recorded to WARC)')

    while True:
        profile_name = click.prompt(
            'When done, please enter a new name to save the browser profile', type=str
        )

        if not curr_browser:
            curr_browser = docker_api.containers.get('browser-' + reqid)

        # exit_code, output = curr_browser.exec_run('/app/prep-commit.sh')
        exit_code, output = curr_browser.exec_run('pkill -f "/usr/bin/google-chrome"')
        if not is_quiet():
            print('Killed Chrome to Save Profile for Commit')
            print('Result: {0}'.format(exit_code))
            print(output.decode('utf-8'))

        time.sleep(1.5)

        conf = {
            'Labels': {LABEL_BROWSERPROFILE: profile_name, LABEL_BASEBROWSER: browser}
        }

        res = curr_browser.commit(
            repository=PROFILE_PREFIX[:-1],
            tag=profile_name,
            message='Browser Profile',
            conf=conf,
        )

        if not is_quiet():
            print('Created Image: {0} ({1})'.format(res.tags[0], res.short_id))

        print('The browser should have restarted to about:blank')
        if not click.confirm('Continue browsing to create another profile?'):
            break

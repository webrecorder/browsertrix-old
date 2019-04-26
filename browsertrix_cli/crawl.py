import click
import datetime
import docker
import sys
import time
import yaml
import webbrowser

from collections import defaultdict


from browsertrix_cli.basecli import (
    cli,
    is_quiet,
    sesh_get,
    sesh_post,
    sesh_delete,
    settings,
)
from browsertrix_cli.profile import get_profile_image


COLUMNS = [
    ('id', 'CRAWL ID', 12),
    ('name', 'NAME', 12),
    ('start_time', 'STARTED', 12),
    ('finish_time', 'DURATION', 12),
    ('status', 'STATUS', 7),
    ('crawl_type', 'CRAWL TYPE', 12),
    ('coll', 'COLL', 16),
    ('mode', 'MODE', 8),
    ('num_queue', 'TO CRAWL', 8),
    ('num_pending', 'PENDING', 8),
    ('num_seen', 'SEEN', 8),
    ('num_browsers', 'BROWSERS', 9),
    ('num_tabs', 'TABS', 3),
]


# ============================================================================
@cli.group(help='Commands for working with crawls')
def crawl():
    pass


# ============================================================================
def format_duration(start_time, finish_time):
    """ Format duration of crawl

    :param start_time: start time of crawl
    :param finish_time: finish time of crawl
    :return: string text for time elapsed since timestr
    """
    try:
        if start_time == 0:
            return '-'

        if not finish_time:
            finish = datetime.datetime.now()
        else:
            finish = datetime.datetime.fromtimestamp(int(finish_time))

        start = datetime.datetime.fromtimestamp(int(start_time))
        elapsed = finish - start
        return str(elapsed).split('.', 1)[0]
    except Exception:
        return start_time


# ============================================================================
def print_logs(browsers, follow=False, wait=False):
    docker_api = docker.from_env(version='auto')

    if follow is None:
        follow = False

    for browser in browsers:
        skip = False
        print('**** Logs for Browser {0} ****'.format(browser))
        while True:
            try:
                container = docker_api.containers.get('autobrowser-' + browser)
                break
            except docker.errors.NotFound:
                if not wait:
                    skip = True
                    print('Crawler not found, already finished?')
                    break

                print('Waiting for Logs...')
                time.sleep(0.25)
                continue

        if skip:
            continue

        res = container.logs(follow=follow, stream=True)
        for line in res:
            sys.stdout.write(line.decode('utf-8'))


# ============================================================================
def open_browsers(browsers, crawl_id, tabs_done=None, num_tabs=-1):
    count = 1
    for reqid in browsers:
        if tabs_done and tabs_done.get(reqid) != num_tabs:
            msg = 'Opening Browser {0} of {1} ({2}) for crawl {3}'
        else:
            msg = 'Skipping Finished Browser {0} of {1}, ({2}) for crawl {3}'

        if not is_quiet():
            print(msg.format(count, len(browsers), reqid, crawl_id))

        webbrowser.open(settings.view_browsers_prefix + reqid)
        count += 1


# ============================================================================
@crawl.command(name='list', help='List all crawls')
def list_crawls():
    """ List all available crawls
    """
    res = sesh_get('/crawls')

    sorted_list = sorted(res['crawls'], key=lambda x: x['start_time'], reverse=True)

    if is_quiet():
        for crawl in sorted_list:
            print(crawl['id'])

        return

    format_str = '{value: <{size}}  '

    for _, text, size in COLUMNS:
        sys.stdout.write(format_str.format(value=text, size=size))
    print()

    for crawl in sorted_list:
        for field, _, size in COLUMNS:
            value = crawl[field]
            if field == 'start_time':
                value = format_duration(value, None) + ' ago'
            elif field == 'finish_time':
                value = format_duration(crawl['start_time'], value)

            sys.stdout.write(format_str.format(value=value, size=size))
        print()
    print()


# ============================================================================
@crawl.command(
    name='create', help='Create (and optionally start) new crawl from yaml crawl spec'
)
@click.option(
    '--start/--no-start',
    default=True,
    help="Start/Don't start crawl immediately after creation",
)
@click.option(
    '--browser',
    type=str,
    default=None,
    help='Browser Docker image to use for crawling, (overrides setting in spec)',
)
@click.option(
    '--profile',
    type=str,
    default=None,
    help='Browser Profile Docker image to use for crawling (overrides "browser" option)',
)
@click.option(
    '--coll',
    type=str,
    default=None,
    help='Set the collection (overrides setting in spec)',
)
@click.option(
    '--mode',
    type=str,
    default=None,
    help='Set the capture mode (overrides setting in spec)',
)
@click.option(
    '--screenshot_coll',
    type=str,
    default=None,
    help='Set the collection to save screenshots (overrides setting in spec)',
)
@click.option(
    '--headless',
    type=bool,
    is_flag=True,
    help='Use headless mode. Browsers can not be opened for watching the crawl',
)
@click.option(
    '--behavior-time',
    default=None,
    type=int,
    help='Max duration to run each in-page behavior',
)
@click.option(
    '--watch',
    is_flag=True,
    default=False,
    type=bool,
    help='Watch all started browsers in a local browser (only if starting crawl)',
)
@click.option(
    '--log',
    is_flag=True,
    default=False,
    type=bool,
    help='Tail the log for the browser crawler',
)
@click.argument('crawl_spec_file', type=click.File('rt'))
def create_crawl(
    crawl_spec_file,
    start,
    browser,
    profile,
    coll,
    mode,
    screenshot_coll,
    headless,
    behavior_time,
    watch,
    log,
):
    """ Create a new crawl!

        :param crawl_spec_file: YAML file with one or more crawls in 'crawls' key
        :param start: If true, start crawl immediately after creation
        :param browser: Browser Docker image to use for crawling (overrides setting in spec)
        :param profile: Browser Profile Docker image to use for crawling (overrides "browser" setting)
        :param coll: Set the collection (overrides setting in spec)
        :param mode: Set the capture mode (overrides setting in spec)
        :param screenshot_coll: Set the collection to save screenshots (overrides setting in spec)
        :param headless: Use headless mode. Browsers can not be opened for watching the crawl
        :param behavior_time: Max duration (in seconds) to run each in-page behavior
        :param watch: Watch all started browsers in a local browser (only if starting crawl)

    """
    root = yaml.load(crawl_spec_file, Loader=yaml.Loader)

    for crawl_spec in root['crawls']:
        if not start:
            msg = 'Created'
        else:
            msg = 'Created and Started'

        if headless is not None:
            crawl_spec['headless'] = headless

        if behavior_time is not None:
            crawl_spec['behavior_time'] = behavior_time

        if profile is not None:
            browser = get_profile_image(profile)

        if browser is not None:
            crawl_spec['browser'] = browser

        if coll is not None:
            crawl_spec['coll'] = coll

        if mode is not None:
            crawl_spec['mode'] = mode

        if screenshot_coll is not None:
            crawl_spec['screenshot_coll'] = screenshot_coll

        res = sesh_post('/crawls', json=crawl_spec)

        if is_quiet():
            print(res['id'])
        else:
            print('Crawl {0}: {1}'.format(msg, res['id']))
            print('Status: {0}'.format(res['status']))

        if watch:
            if not start:
                if not is_quiet():
                    print("Can't watch, crawl not started")

            elif headless:
                if not is_quiet():
                    print("Can't watch, crawl is running in headless mode")

            else:
                open_browsers(res['browsers'], res['id'])

        if log:
            print_logs(res['browsers'], follow=True, wait=True)


# ============================================================================
@crawl.command(name='start', help='Start an existing crawl')
@click.argument('crawl_id', nargs=-1)
def start_crawl(crawl_id, browser, headless, behavior_time):
    """ Start an existing crawl

        :param crawl_id: list of crawl ids to start
    """
    for id_ in crawl_id:
        res = sesh_post('/crawl/{0}/start'.format(id_))

        if is_quiet():
            print(res['id'])
        else:
            print('Started Crawl: {0}'.format(res['id']))


# ============================================================================
@crawl.command(name='info', help='Get info on an existing crawl(s)')
@click.argument('crawl_id', nargs=-1)
@click.option(
    '--urls/--no-urls',
    default=False,
    help='Get detailed info on crawl, listing all urls',
)
def get_info(crawl_id, urls):
    """ Get info on existing crawl(s)

        :param crawl_id: list of crawl ids to get info on
        :param urls: Get detailed info on crawl, listing all urls
    """
    for id_ in crawl_id:
        if urls:
            res = sesh_get('/crawl/{0}/info'.format(id_))
        else:
            res = sesh_get('/crawl/{0}'.format(id_))

        print(yaml.dump(res))


# ============================================================================
@crawl.command(name='watch', help='Watch crawling browsers in local browser')
@click.argument('crawl_id', nargs=-1)
def watch_crawl(crawl_id):
    """ Watch crawling browsers in local browser

        :param crawl_id: list of crawl ids to watch
    """
    for id_ in crawl_id:
        res = sesh_get('/crawl/{0}'.format(id_))

        if res.get('headless'):
            if not is_quiet():
                print("Can not watch, crawl is running in headless mode")
                continue

        if res.get('status') != 'running':
            if not is_quiet():
                print('Crawl not running: {0}'.format(id_))
                continue

        browsers = res['browsers']

        done_count = defaultdict(int)

        for info in res.get('tabs_done'):
            done_count[info['id']] += 1

        if not browsers:
            if not is_quiet():
                print('No Browsers')
                continue

        print(done_count, res['num_tabs'])
        open_browsers(browsers, id_, done_count, res['num_tabs'])


# ============================================================================
@crawl.command(name='stop', help='Stop one or more existing crawls')
@click.argument('crawl_id', nargs=-1)
def stop_crawl(crawl_id):
    """ Stop one or more existing crawls

        :param crawl_id: list of crawl ids to stop
    """
    for id_ in crawl_id:
        res = sesh_post('/crawl/{0}/stop'.format(id_))

        if not res.get('success'):
            print('Error stopping: ' + res)
            return

        if is_quiet():
            print(id_)
        else:
            print('Stopped Crawl: {0}'.format(id_))


# ============================================================================
@crawl.command(name='remove', help='Remove one or more existing crawls')
@click.argument('crawl_id', nargs=-1)
def remove_crawl(crawl_id):
    """ Remove one or more existing crawls

        :param crawl_id: list of crawl ids to stop
    """
    for id_ in crawl_id:
        res = sesh_delete('/crawl/{0}'.format(id_))

        if not res.get('success'):
            print('Error removing: ' + res)
            return

        if is_quiet():
            print(id_)
        else:
            print('Removed Crawl: {0}'.format(id_))


# ============================================================================
@crawl.command(name='remove-all', help='Stop and remove all crawls')
def remove_all():
    """ Stop and remove all crawls
    """
    res = sesh_get('/crawls')

    crawls = res['crawls']

    for crawl in crawls:
        id_ = crawl['id']
        res = sesh_delete('/crawl/{0}'.format(id_))
        if not is_quiet():
            print('Removed Crawl: {0}'.format(id_))


# ============================================================================
@crawl.command(name='logs', help='View crawl logs for one or all crawlers')
@click.argument('crawl_id', nargs=1)
@click.option(
    '-b',
    '--browser',
    type=int,
    default=0,
    help='1-based index of browser to show logs for, or 0 for all (default)',
)
@click.option(
    '-f',
    '--follow',
    type=bool,
    default=False,
    is_flag=True,
    help='follow crawl log in real-time',
)
def logs(crawl_id, browser, follow):
    """ View crawl logs for one or all crawlers
    :param crawl_id: The crawl_id to view logs for
    :param browser: 1-based index of browser to show logs for, or 0 for all (default)
    :param follow: follow crawl log in real-time (for one browser only)
    """
    res = sesh_get('/crawl/{0}'.format(crawl_id))


    num_browsers = len(res['browsers'])
    if browser <= 0:
        print_logs(res['browsers'], follow=follow)
    elif browser > num_browsers:
        print(
            'Crawl has {0} browsers. Index must be 1 to {0}'.format(
                num_browsers, num_browsers
            )
        )
    else:
        print_logs([res['browsers'][browser - 1]], follow=follow)

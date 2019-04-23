import click
import datetime
import sys
import webbrowser
import yaml

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
    ('status', 'STATUS', 7),
    ('crawl_type', 'CRAWL TYPE', 12),
    ('coll', 'COLL', 8),
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
def format_elapsed(timestr):
    """ Format given time as elapsed from now

    :param timestr: Time in seconds as str or int
    :return: string text for time elapsed since timestr
    """
    try:
        if timestr == 0:
            return '-'
        text = datetime.datetime.fromtimestamp(int(timestr))
        elapsed = datetime.datetime.now() - text
        return str(elapsed).split('.', 1)[0] + ' ago'
    except Exception:
        return timestr


# ============================================================================
def open_browsers(browsers, browsers_done, crawl_id):
    count = 1
    for reqid in browsers:
        if reqid not in browsers_done:
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
                value = format_elapsed(value)

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
@click.argument('crawl_spec_file', type=click.File('rt'))
def create_crawl(
    crawl_spec_file, start, browser, profile, coll, mode, headless, behavior_time, watch
):
    """ Create a new crawl!

        :param crawl_spec_file: YAML file with one or more crawls in 'crawls' key
        :param start: If true, start crawl immediately after creation
        :param browser: Browser Docker image to use for crawling (overrides setting in spec)
        :param profile: Browser Profile Docker image to use for crawling (overrides "browser" setting)
        :param coll: Set the collection (overrides setting in spec)
        :param mode: Set the capture mode (overrides setting in spec)
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
                open_browsers(res['browsers'], [], res['id'])


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
        browsers_done = res.get('browsers_done', [])

        if not browsers:
            if not is_quiet():
                print('No Browsers')
                continue

        open_browsers(browsers, browsers_done, id_)


# ============================================================================
@crawl.command(
    name='stop', help='Stop one or more existing crawls (and optionally remove)'
)
@click.argument('crawl_id', nargs=-1)
@click.option(
    '--remove',
    type=bool,
    default=False,
    is_flag=True,
    help='Crawl should be removed, not just stopped',
)
def stop_crawl(crawl_id, remove=False):
    """ Stop one or more existing crawls (and optionally remove)

        :param crawl_id: list of crawl ids to stop
        :param remove: Crawl should be removed, not just stopped
    """
    for id_ in crawl_id:
        if remove:
            res = sesh_delete('/crawl/{0}'.format(id_))
        else:
            res = sesh_post('/crawl/{0}/stop'.format(id_))

        if not res.get('success'):
            print('Error stopping: ' + res)
            return

        if is_quiet():
            print(id_)
        elif remove:
            print('Stopped and Removed Crawl: {0}'.format(id_))
        else:
            print('Stopped Crawl: {0}'.format(id_))


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

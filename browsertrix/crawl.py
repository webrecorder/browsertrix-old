from __future__ import annotations

import logging
import os
import time
import uuid
from asyncio import AbstractEventLoop, gather as aio_gather, get_event_loop
from functools import partial
from typing import Dict, List, Optional, Union

import ujson as json
from aiohttp import AsyncResolver, ClientSession, TCPConnector
from aioredis import Redis
from starlette.exceptions import HTTPException

from .schema import CacheMode, CaptureMode, CrawlInfo, CrawlType, CreateCrawlRequest
from .utils import env, extract_domain, init_redis

__all__ = ['Crawl', 'CrawlManager']


DEFAULT_REDIS_URL = 'redis://localhost'

logger = logging.getLogger('browsertrix')


# ============================================================================
class CrawlManager:
    """A simple class for managing crawls"""

    def __init__(self) -> None:
        self.redis: Redis = None
        self.session: ClientSession = None
        self.loop: AbstractEventLoop = None
        self.depth: int = env('DEFAULT_DEPTH', type_=int, default=1)
        self.same_domain_depth: int = env(
            'DEFAULT_SAME_DOMAIN_DEPTH', type_=int, default=100
        )

        self.num_browsers: int = env('DEFAULT_NUM_BROWSERS', type_=int, default=2)

        self.flock: str = env('DEFAULT_FLOCK', default='browsers')

        self.shepherd_host: str = env(
            'DEFAULT_SHEPHERD', default='http://shepherd:9020'
        )

        self.browser_api_url: str = f'{self.shepherd_host}/api'
        self.pool: str = env('DEFAULT_POOL', default='')

        self.scan_key: str = 'a:*:info'

        self.container_environ: Dict[str, str] = {
            'URL': 'about:blank',
            'REDIS_URL': env('REDIS_URL', default=DEFAULT_REDIS_URL),
            'WAIT_FOR_Q': '10',
            'TAB_TYPE': 'CrawlerTab',
            'CRAWL_NO_NETCACHE': '0',
            'VNC_PASS': 'pass',
            'IDLE_TIMEOUT': '',
            'BEHAVIOR_API_URL': 'http://behaviors:3030',
            'SCREENSHOT_API_URL': env('SCREENSHOT_API_URL'),
            'EXTRACTED_RAW_DOM_API_URL': env('EXTRACTED_RAW_DOM_API_URL'),
        }

        self.default_browser = None

        if os.environ.get('DEBUG'):
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

    async def startup(self) -> None:
        """Initialize the crawler manager's redis connection and
        http session used to make requests to shepherd
        """
        self.loop = get_event_loop()
        self.redis = await init_redis(
            env('REDIS_URL', default=DEFAULT_REDIS_URL), self.loop
        )
        self.session = ClientSession(
            connector=TCPConnector(
                resolver=AsyncResolver(loop=self.loop), loop=self.loop
            ),
            json_serialize=partial(json.dumps, ensure_ascii=False),
            loop=self.loop,
        )

    async def shutdown(self) -> None:
        """Closes the redis connection and http session"""
        try:
            self.redis.close()
            await self.redis.wait_closed()
        except Exception:
            pass

        try:
            await self.session.close()
        except Exception:
            pass

    def new_crawl_id(self) -> str:
        """Creates an id for a new crawl

        :return: The new id for a crawl
        """
        return uuid.uuid4().hex[-12:]

    async def create_new(
        self, crawl_request: CreateCrawlRequest
    ) -> Dict[str, Union[bool, str]]:
        """Creates a new crawl

        :param crawl_request: The body of the api request
        for the /crawls endpoint
        :return: A dictionary indicating success and the id of the new crawl
        """
        return await Crawl.create(self, crawl_request)

    async def load_crawl(self, crawl_id: str) -> Crawl:
        """Returns the crawl information for the supplied crawl id

        :param crawl_id: The id of the crawl to load
        :return: The loaded crawl
        """
        crawl = await Crawl.load(crawl_id, self)
        if not crawl.model:
            raise HTTPException(404, detail='crawl not found')
        return crawl

    async def get_crawl_info(self, crawl_id: str) -> Dict:
        """Retrieves and returns a crawls info

        :param crawl_id: The id of the crawl to retrieve the info for
        :return: A dictionary containing the crawls info
        """
        crawl = await self.load_crawl(crawl_id)
        return await crawl.get_info()

    async def get_full_crawl_info(self, crawl_id: str) -> Dict:
        """Retrieves and returns a crawls full details

        :param crawl_id: The id of the crawl to retrieve full details for
        :return: A dictionary containing the crawls full details
        """
        crawl = await self.load_crawl(crawl_id)
        info, urls = await aio_gather(
            crawl.get_info(count_urls=False), crawl.get_info_urls(), loop=self.loop
        )
        return dict(**info, **urls, success=True)

    async def get_crawl_urls(self, crawl_id: str) -> Dict:
        """Retrieves and returns a crawls URLs

        :param crawl_id: The id of the crawl to retrieve URLs for
        :return: A dictionary containing the crawls URL info
        """
        crawl = await self.load_crawl(crawl_id)
        return await crawl.get_info_urls()

    async def queue_crawl_urls(self, crawl_id: str, url_list: List[str]) -> Dict:
        """Queues the supplied list of URLs for the crawl associated with the supplied id

        :param crawl_id: The id of the crawl the URLs will be queued for
        :param url_list: The list of URL to be queued
        :return: A dictionary containing the results of this operation
        """
        crawl = await self.load_crawl(crawl_id)
        return await crawl.queue_urls(url_list)

    async def start_crawl(self, crawl_id: str) -> Dict:
        """Starts the crawl associated with the supplied id

        :param crawl_id: The id of the crawl to be started
        :return: A dictionary containing the results of this operation
        """
        crawl = await self.load_crawl(crawl_id)
        return await crawl.start()

    async def stop_crawl(self, crawl_id: str) -> Dict:
        """Stop the crawl associated with the supplied id

        :param crawl_id: The id of the crawl to be stopped
        :return: A dictionary containing the results of this operation
        """
        crawl = await self.load_crawl(crawl_id)
        return await crawl.stop()

    async def delete_crawl(self, crawl_id: str) -> Dict:
        """Stops and deletes the crawl associated with the supplied id

        :param crawl_id: The id of the crawl to be stopped and deleted
        :return: A dictionary containing the results of this operation
        """
        crawl = await self.load_crawl(crawl_id)
        return await crawl.delete()

    async def is_crawl_done(self, crawl_id: str) -> Dict:
        """Checks to see if the crawl associated with the supplied id
        is done

        :param crawl_id: The id of the crawl to be checked
        :return: A dictionary containing the results of this operation
        """
        crawl = await self.load_crawl(crawl_id)
        return await crawl.is_done()

    async def do_request(self, url_path: str, post_data: Optional[Dict] = None) -> Dict:
        """Makes an HTTP post request to the supplied URL/path

        :param url_path: The URL or path for the post request
        :param post_data: Optional post request body
        :return: The response body
        """
        try:
            url = self.browser_api_url + url_path
            async with self.session.post(url, json=post_data) as res:
                res = await res.json()
                logger.debug(str(res))
                return res
        except Exception as e:
            print(e)
            print(post_data)
            text = str(e)
            logger.debug(text)
            raise HTTPException(400, text)

    async def get_all_crawls(self) -> Dict[str, List[Dict]]:
        """Returns crawl info for all crawls

        :return: The list of all crawl info
        """
        all_infos = []

        async for key in self.redis.iscan(match=self.scan_key):
            _, crawl_id, _2 = key.split(':', 2)

            try:
                # crawl = Crawl(crawl_id, self)
                crawl = await self.load_crawl(crawl_id)
                info = await crawl.get_info()
                all_infos.append(info)
            except HTTPException:
                continue

        return {'crawls': all_infos}

    async def request_flock(self, opts: Dict) -> Dict:
        """Requests a flock from shepherd using the supplied options

        :param opts: The options for the requested flock
        :return: The response from shepherd
        """
        response = await self.do_request(
            f'/flock/request/{self.flock}?pool={self.pool}', opts
        )
        return response

    async def start_flock(self, reqid: str) -> Dict:
        """Requests that shepherd start the flock identified by the
        supplied request id

        :param reqid: The request id of the flock to be started
        :return: The response from shepherd
        """
        response = await self.do_request(
            f'/flock/start/{reqid}', {'environ': {'REQ_ID': reqid}}
        )
        return response

    async def stop_flock(self, reqid: str) -> Dict:
        """Requests that shepherd stop, but not remove, the flock
        identified by the supplied request id

        :param reqid: The request id of the flock to be stopped
        :return: The response from shepherd
        """
        response = await self.do_request(f'/flock/stop/{reqid}')
        return response

    async def remove_flock(self, reqid: str) -> Dict:
        """Requests that shepherd stop and remove the flock
        identified by the supplied request id

        :param reqid: The request id of the flock to be stopped
        :return: The response from shepherd
        """
        response = await self.do_request(f'/flock/remove/{reqid}')
        return response


# ============================================================================
class Crawl:
    """Simple class representing information about a crawl
    and the operations on it
    """

    __slots__ = [
        'crawl_id',
        'manager',
        'model',
        'browser_key',
        'frontier_q_key',
        'info_key',
        'pending_q_key',
        'scopes_key',
        'seen_key',
        'tabs_done_key',
    ]

    @classmethod
    async def create(
        cls, manager: CrawlManager, crawl_request: CreateCrawlRequest
    ) -> Dict:
        """Creates a crawl using the supplied create crawl request

        :param manager: The CrawlManager instance to be used
        :param crawl_request: The crawl creation request
        :return: A dictionary containing information about the results of this operation
        """
        crawl_id = manager.new_crawl_id()
        crawl = cls(crawl_id, manager)
        return await crawl.init_crawl(crawl_request)

    @classmethod
    async def load(cls, crawl_id: str, manager: CrawlManager) -> Crawl:
        """Loads the supplied crawl_id's info, if it exists, and
        returns an instance of Crawl

        :param crawl_id: The id of the crawl to be loaded
        :param manager: The CrawlManager instance to be used
        :return: The created instance of Crawl
        """
        crawl = cls(crawl_id, manager)
        info = await manager.redis.hgetall(crawl.info_key)
        if info:
            if 'browser_overrides' in info:
                info['browser_overrides'] = json.loads(info['browser_overrides'])
            crawl.model = CrawlInfo.parse_obj(info)
        return crawl

    def __init__(
        self, crawl_id: str, manager: CrawlManager, model: Optional[CrawlInfo] = None
    ) -> None:
        """Create a new crawl object

        :param crawl_id: The id of the crawl
        :param manager: The crawl manager instance
        """
        self.manager: CrawlManager = manager
        self.crawl_id: str = crawl_id

        self.info_key: str = f'a:{crawl_id}:info'

        self.frontier_q_key: str = f'a:{crawl_id}:q'
        self.pending_q_key: str = f'a:{crawl_id}:qp'

        self.seen_key: str = f'a:{crawl_id}:seen'
        self.scopes_key: str = f'a:{crawl_id}:scope'

        self.browser_key: str = f'a:{crawl_id}:br'
        self.tabs_done_key: str = f'a:{crawl_id}:br:done'

        self.model: Optional[CrawlInfo] = model

    @property
    def redis(self) -> Redis:
        """Retrieve the redis instance of the crawl manager

        :return: The redis instance of the crawl manager
        """
        return self.manager.redis

    @property
    def loop(self) -> AbstractEventLoop:
        """Retrieve the running event loop

        :return: The running event loop
        """
        return self.manager.loop

    async def delete(self) -> Dict[str, bool]:
        """Delete this crawl

        :return: An dictionary indicating if this operation
        was successful
        """
        await self.stop(remove=True)

        await self.redis.delete(self.info_key)

        await self.redis.delete(self.frontier_q_key)
        await self.redis.delete(self.pending_q_key)

        await self.redis.delete(self.seen_key)
        await self.redis.delete(self.scopes_key)

        await self.redis.delete(self.browser_key)
        await self.redis.delete(self.tabs_done_key)

        return {'success': True}

    async def _init_domain_scopes(self, urls: List[str]) -> None:
        """Initializes this crawls domain scopes

        :param urls: A list of URLs that define this crawls domain scope
        """

        for url in urls:
            if type(url) != str:
                url = url['url']

            await self.redis.sadd(
                self.scopes_key, json.dumps({'domain': extract_domain(url)})
            )

    async def queue_urls(self, urls: List[str]) -> Dict[str, bool]:
        """Adds the supplied list of URLs to this crawls queue

        :param urls: The list of URLs to be queued
        :return: An dictionary indicating if this operation
        was successful
        """
        if len(urls) == 0:
            return {'success': True}

        for url in urls:
            if type(url) == str:
                url_req = {'url': url, 'depth': 0}
            else:
                url_req = url.copy()
                url_req['depth'] = 0
                url = url_req['url']

            await self.redis.rpush(self.frontier_q_key, json.dumps(url_req))

            # add to seen list to avoid dupes
            await self.redis.sadd(self.seen_key, url)

        if self.model.crawl_type == CrawlType.SAME_DOMAIN:
            await self._init_domain_scopes(urls)

        return {'success': True}

    async def get_info(self, count_urls=True) -> Dict:
        """Returns this crawls information

        :param count_urls: If true, include count of frontier queue, pending set, seen set
        :return: The crawl information
        """
        try:
            await self.is_done()
        except Exception as e:
            logger.exception(str(e))

        data, browsers, tabs_done = await aio_gather(
            self.redis.hgetall(self.info_key),
            self.redis.smembers(self.browser_key),
            self.redis.lrange(self.tabs_done_key, 0, -1),
            loop=self.loop,
        )
        if 'browser_overrides' in data:
            data['browser_overrides'] = json.loads(data['browser_overrides'])

        data['browsers'] = list(browsers)
        data['tabs_done'] = [json.loads(elem) for elem in tabs_done]

        # do a count of the url keys
        if count_urls:
            num_queue, num_pending, num_seen = await aio_gather(
                self.redis.llen(self.frontier_q_key),
                self.redis.scard(self.pending_q_key),
                self.redis.scard(self.seen_key),
                loop=self.loop,
            )

            data['num_queue'] = num_queue
            data['num_pending'] = num_pending
            data['num_seen'] = num_seen

        return data

    async def get_info_urls(self) -> Dict:
        """Returns this crawls URL information

        :return: The crawls URL information
        """
        scopes, queue, pending, seen = await aio_gather(
            self.redis.smembers(self.scopes_key),
            self.redis.lrange(self.frontier_q_key, 0, -1),
            self.redis.smembers(self.pending_q_key),
            self.redis.smembers(self.seen_key),
            loop=self.loop,
        )

        queue = [json.loads(elem) for elem in queue]
        scopes = [json.loads(scope) for scope in scopes]

        data = {
            'scopes': scopes,
            'queue': queue,
            'pending': list(pending),
            'seen': seen,
        }

        return data

    async def start(self) -> Dict:
        if self.model.status == 'running':
            raise HTTPException(400, detail='already running')

        browsers = list(await self.redis.smembers(self.browser_key))
        errors = []

        for reqid in browsers:
            res = await self.manager.start_flock(reqid)

            if 'error' in res:
                errors.append(res['error'])

        if errors:
            raise HTTPException(400, detail=errors)

        await self.redis.hset(self.info_key, 'status', 'running')
        await self.redis.hset(self.info_key, 'start_time', int(time.time()))

        return {
            'success': True,
            'browsers': browsers,
            'status': 'running',
            'id': self.crawl_id,
        }

    async def init_crawl_browsers(
        self, browser_init_opts: Dict, start: bool = False
    ) -> Dict:
        """Initializes this crawls browsers and if start is true starts each browser in the crawl

        :param browser_init_opts: Browser initialization options
        :param start: T/F indicating if the the intialized browser should be started
        :return: A dictionary containing information about the results of this operation
        """
        errors = []
        browsers = []

        for _ in range(self.model.num_browsers):
            res = await self.manager.request_flock(browser_init_opts)
            reqid = res.get('reqid')
            if not reqid:
                if 'error' in res:
                    errors.append(res['error'])
                continue

            if start:
                res = await self.manager.start_flock(reqid)

            if 'error' in res:
                errors.append(res['error'])
            else:
                browsers.append(reqid)
                await self.redis.sadd(self.browser_key, reqid)

        if errors:
            raise HTTPException(400, detail=errors)

        if start:
            self.model.status = 'running'
            await self.redis.hset(self.info_key, 'status', 'running')

        return {
            'success': True,
            'browsers': browsers,
            'status': self.model.status,
            'id': self.crawl_id,
        }

    async def init_crawl(self, crawl_request: CreateCrawlRequest) -> Dict:
        """Initialize the crawl (and optionally start)

        :param crawl_request: Information about the crawl to be started
        :return: An dictionary that includes an indication if this operation
        was successful and a list of browsers in the crawl
        """
        # init base crawl data
        if crawl_request.crawl_type == CrawlType.ALL_LINKS:
            crawl_depth = crawl_request.crawl_depth or 1
        elif crawl_request.crawl_type == CrawlType.SAME_DOMAIN:
            crawl_depth = crawl_request.crawl_depth or self.manager.same_domain_depth
        elif crawl_request.crawl_type == CrawlType.SINGLE_PAGE:
            crawl_depth = 0
        elif crawl_request.crawl_type == CrawlType.CUSTOM:
            crawl_depth = crawl_request.crawl_depth

            for scope in crawl_request.scopes:
                await self.redis.sadd(self.scopes_key, json.dumps(scope))

        mode = crawl_request.mode.value
        if crawl_request.screenshot_coll == '':
            screenshot_coll = ''
        else:
            screenshot_coll = (
                crawl_request.screenshot_coll
                or (mode == 'record' and crawl_request.coll)
                or ''
            )

        if crawl_request.text_coll == '':
            text_coll = ''
        else:
            text_coll = (
                crawl_request.text_coll or (mode == 'record' and crawl_request.coll) or ''
            )

        self.model = CrawlInfo(
            id=self.crawl_id,
            coll=crawl_request.coll,
            screenshot_coll=screenshot_coll,
            text_coll=text_coll,
            mode=mode,
            name=crawl_request.name,
            num_browsers=crawl_request.num_browsers,
            num_tabs=crawl_request.num_tabs,
            crawl_type=crawl_request.crawl_type.value,
            status='new',
            crawl_depth=crawl_depth,
            start_time=int(time.time()) if crawl_request.start else 0,
            finish_time=0,
            headless=crawl_request.headless,
            cache=crawl_request.cache.value,
            browser_overrides=crawl_request.browser_overrides,
        )
        redis_crawl_info = self.model.dict(exclude={'browser_overrides', 'headless'})
        redis_crawl_info['headless'] = 1 if self.model.headless else 0
        if self.model.browser_overrides is not None:
            redis_crawl_info['browser_overrides'] = self.model.browser_overrides.json(
                skip_defaults=True
            )
        await self.redis.hmset_dict(self.info_key, redis_crawl_info)

        # init seeds
        if crawl_request.seed_urls is not None:
            await self.queue_urls(crawl_request.seed_urls)

        # init browser user params and environ
        browser = crawl_request.browser or self.manager.default_browser

        user_params = crawl_request.user_params
        user_params['auto_id'] = self.crawl_id
        user_params['mode'] = self.model.mode
        user_params['coll'] = self.model.coll
        user_params['cache'] = crawl_request.cache.value

        environ = self.manager.container_environ.copy()
        environ['AUTO_ID'] = self.crawl_id
        environ['NUM_TABS'] = self.model.num_tabs

        if crawl_request.mode != CaptureMode.LIVE:
            environ['PROXY_HOST'] = os.environ.get('PROXY_HOST', 'pywb')

        if crawl_request.cache == CacheMode.NEVER:
            environ['CRAWL_NO_NETCACHE'] = '1'

        if crawl_request.behavior_max_time > 0:
            environ['BEHAVIOR_RUN_TIME'] = crawl_request.behavior_max_time

        screenshot_api = environ['SCREENSHOT_API_URL']
        if self.model.screenshot_coll != '' and screenshot_api:
            environ['SCREENSHOT_API_URL'] = screenshot_api.format(
                coll=self.model.screenshot_coll
            )
        else:
            environ.pop('SCREENSHOT_API_URL', '')

        raw_dom_api = environ['EXTRACTED_RAW_DOM_API_URL']
        if self.model.text_coll != '' and raw_dom_api:
            environ['EXTRACTED_RAW_DOM_API_URL'] = raw_dom_api.format(
                coll=self.model.text_coll
            )
        else:
            environ.pop('EXTRACTED_RAW_DOM_API_URL', '')

        deferred = {'autobrowser': False}
        if crawl_request.headless:
            environ['DISPLAY'] = ''
            deferred['xserver'] = True

        opts = dict(
            overrides={
                'browser': 'oldwebtoday/' + browser,
                'xserver': 'oldwebtoday/remote-desktop-server',
            },
            deferred=deferred,
            user_params=crawl_request.user_params,
            environ=environ,
        )

        return await self.init_crawl_browsers(opts, crawl_request.start)

    async def is_done(self) -> Dict[str, bool]:
        """Is this crawl done

        :return: An dictionary that indicates if the crawl is done
        """
        if self.model.status == 'done':
            return {'done': True}

        # if not running, won't be done
        if self.model.status != 'running':
            return {'done': False}

        # if frontier not empty, not done
        # if await self.redis.llen(self.frontier_q_key) > 0:
        #    return {'done': False}

        # if pending q not empty, not done
        # if await self.redis.scard(self.pending_q_key) > 0:
        #    return {'done': False}

        # if not all browsers are done, not done
        tabs_done = await self.redis.lrange(self.tabs_done_key, 0, -1)

        if self.model.num_tabs * self.model.num_browsers != len(tabs_done):
            return {'done': False}

        if tabs_done:
            finish_time = int(json.loads(tabs_done[0])['time'])
        else:
            finish_time = 0

        update = {'status': 'done', 'finish_time': finish_time}

        await self.redis.hmset_dict(self.info_key, update)
        return {'done': True}

    async def stop(self, remove=False) -> Dict[str, bool]:
        """Stops the crawl

        :param remove: remove the crawl (if its stopped or not)
        :return: An dictionary indicating if the operation was successful
        """
        if not remove and self.model.status != 'running':
            raise HTTPException(400, detail='not running')

        errors = []

        browsers = await self.redis.smembers(self.browser_key)

        for reqid in browsers:
            if remove:
                res = await self.manager.remove_flock(reqid)
            else:
                res = await self.manager.stop_flock(reqid)

            if 'error' in res:
                errors.append(res['error'])

        if errors:
            raise HTTPException(400, detail=errors)

        await self.redis.hset(self.info_key, 'status', 'stopped')

        return {'success': True}

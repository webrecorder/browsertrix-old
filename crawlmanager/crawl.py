from __future__ import annotations

import uuid
from asyncio import AbstractEventLoop, gather as aio_gather, get_event_loop
from functools import partial
from typing import Dict, List, Optional, Union
from urllib.parse import urlsplit

from aiohttp import AsyncResolver, ClientSession, TCPConnector
from aioredis import Redis
from starlette.exceptions import HTTPException
from ujson import dumps as ujson_dumps

from .schema import CrawlInfo, CreateCrawlRequest, StartCrawlRequest
from .utils import env, init_redis

__all__ = ['Crawl', 'CrawlManager']


DEFAULT_REDIS_URL = 'redis://localhost'


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
            'WAIT_FOR_Q': '5',
            'TAB_TYPE': 'CrawlerTab',
            'VNC_PASS': 'pass',
            'IDLE_TIMEOUT': '',
            'BEHAVIOR_API_URL': 'http://behaviors:3030',
            'SCREENSHOT_API_URL': env('SCREENSHOT_API_URL'),
        }

        self.default_browser = None

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
            json_serialize=partial(ujson_dumps, ensure_ascii=False),
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
        self, create_request: CreateCrawlRequest
    ) -> Dict[str, Union[bool, str]]:
        """Creates a new crawl

        :param create_request: The body of the api request
        for the /crawls endpoint
        :return: A dictionary indicating success and the id of the new crawl
        """
        crawl_id = self.new_crawl_id()

        crawl_depth = create_request.depth
        if crawl_depth is None:
            if create_request.crawl_type == 'all-links':
                crawl_depth = 1
            elif create_request.crawl_type == 'same-domain':
                crawl_depth = self.same_domain_depth
            else:
                crawl_depth = 0

        data = {
            'id': crawl_id,
            'num_browsers': create_request.num_browsers,
            'num_tabs': create_request.num_tabs,
            # 'owner': collection.my_id,
            'crawl_type': create_request.crawl_type,
            'status': 'new',
            'depth': crawl_depth,
        }

        await Crawl.create(self, crawl_id, data, create_request.seed_urls)

        return {'success': True, 'id': crawl_id}

    async def load_crawl(self, crawl_id: str) -> Crawl:
        """Returns the crawl information for the supplied crawl id

        :param crawl_id: The id of the crawl to load
        :return: The information about a crawl
        """
        crawl = Crawl(crawl_id, self)
        data = await self.redis.hgetall(crawl.info_key)
        if not data:
            raise HTTPException(404, detail='not found')

        crawl.model = CrawlInfo(**data)

        return crawl

    async def do_request(self, url_path: str, post_data: Optional[Dict] = None) -> Dict:
        """Makes an HTTP post request to the supplied URL/path

        :param url_path: The URL or path for the post request
        :param post_data: Optional post request body
        :return: The response body
        """
        try:
            url = self.browser_api_url + url_path
            async with self.session.post(url, json=post_data) as res:
                return await res.json()
        except Exception as e:
            print(e)
            text = str(e)
            raise HTTPException(400, text)

    async def get_all_crawls(self) -> Dict[str, List[Dict]]:
        """Returns crawl info for all crawls

        :return: The list of all crawl info
        """
        all_infos = []

        async for key in self.redis.iscan(match=self.scan_key):
            _, crawl_id, _2 = key.split(':', 2)

            try:
                crawl = Crawl(crawl_id, self)
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
            f'/request_flock/{self.flock}?pool={self.pool}', opts
        )
        return response

    async def start_flock(self, reqid: str) -> Dict:
        """Requests that shepherd start the flock identified by the
        supplied request id

        :param reqid: The request id of the flock to be started
        :return: The response from shepherd
        """
        response = await self.do_request(
            f'/start_flock/{reqid}', {'environ': {'REQ_ID': reqid}}
        )
        return response

    async def stop_flock(self, reqid: str) -> Dict:
        """Requests that shepherd stop the flock identified by the
        supplied request id

        :param reqid: The request id of the flock to be stopped
        :return: The response from shepherd
        """
        response = await self.do_request(f'/stop_flock/{reqid}')
        return response


# ============================================================================
class Crawl:
    """Simple class representing information about a crawl
    and the operations on it
    """

    __slots__ = [
        'browser_done_key',
        'browser_key',
        'crawl_id',
        'frontier_q_key',
        'info_key',
        'manager',
        'model',
        'pending_q_key',
        'scopes_key',
        'seen_key',
    ]

    @classmethod
    async def create(
        cls,
        manager: CrawlManager,
        crawl_id: str,
        info: Dict,
        seed_urls: Optional[List[str]] = None,
    ) -> Crawl:
        """Creates a new crawl and returns it

        :param manager: The crawl manager instance
        :param crawl_id: The id for the new crawl
        :param info: The crawl info object created from the CreateCrawlRequest
        :param seed_urls: Optional list of URLs to be queued for this crawl
        :return: The newly created or updated crawl
        """
        crawl = Crawl(crawl_id, manager)
        await crawl.update_info(info)
        if seed_urls is not None:
            await crawl.queue_urls(seed_urls)
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
        self.browser_done_key: str = f'a:{crawl_id}:br:done'

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
        if self.model and self.model.status == 'running':
            await self.stop()

        await self.redis.delete(self.info_key)

        await self.redis.delete(self.frontier_q_key)
        await self.redis.delete(self.pending_q_key)

        await self.redis.delete(self.seen_key)
        await self.redis.delete(self.scopes_key)

        await self.redis.delete(self.browser_key)
        await self.redis.delete(self.browser_done_key)

        return {'success': True}

    async def _init_domain_scopes(self, urls: List[str]) -> None:
        """Initializes this crawls domain scopes

        :param urls: A list of URLs that define this crawls domain scope
        """
        domains = set()

        for url in urls:
            domain = urlsplit(url).netloc
            domains.add(domain)

        if not domains:
            return

        for domain in domains:
            await self.redis.sadd(self.scopes_key, ujson_dumps({'domain': domain}))

    async def queue_urls(self, urls: List[str]) -> Dict[str, bool]:
        """Adds the supplied list of URLs to this crawls queue

        :param urls: The list of URLs to be queued
        :return: An dictionary indicating if this operation
        was successful
        """
        if len(urls) == 0:
            return {'success': True}

        for url in urls:
            url_req = {'url': url, 'depth': 0}
            await self.redis.rpush(self.frontier_q_key, ujson_dumps(url_req))

            # add to seen list to avoid dupes
            await self.redis.sadd(self.seen_key, url)

        if self.model.crawl_type == 'same-domain':
            await self._init_domain_scopes(urls)

        return {'success': True}

    async def update_info(self, info: Dict) -> None:
        if self.model is None:
            self.model = CrawlInfo(**info)
        await self.redis.hmset_dict(self.info_key, info)

    async def get_info(self) -> Dict:
        """Returns this crawls information

        :return: The crawl information
        """
        data, browsers, browsers_done = await aio_gather(
            self.redis.hgetall(self.info_key),
            self.redis.smembers(self.browser_key),
            self.redis.smembers(self.browser_done_key),
            loop=self.loop,
        )

        data['browsers'] = list(browsers)
        data['browsersDone'] = list(browsers_done)

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

        data = {
            'scopes': list(scopes),
            'queue': queue,
            'pending': list(pending),
            'seen': seen,
        }

        return data

    async def start(self, start_request: StartCrawlRequest) -> Dict:
        """Starts the crawl

        :param start_request: Information about the crawl to be started
        :return: An dictionary that includes an indication if this operation
        was successful and a list of browsers in the crawl
        """
        if self.model.status == 'running':
            raise HTTPException(400, detail='already running')

        browser = start_request.browser or self.manager.default_browser

        start_request.user_params['auto_id'] = self.crawl_id

        environ = self.manager.container_environ.copy()
        environ['AUTO_ID'] = self.crawl_id
        environ['NUM_TABS'] = self.model.num_tabs
        if start_request.behavior_run_time > 0:
            environ['BEHAVIOR_RUN_TIME'] = start_request.behavior_run_time

        if start_request.screenshot_target_uri:
            environ['SCREENSHOT_TARGET_URI'] = start_request.screenshot_target_uri
            environ['SCREENSHOT_FORMAT'] = 'png'

        deferred = {'autodriver': False}
        if start_request.headless:
            deferred['xserver'] = True

        opts = dict(
            overrides={
                'browser': 'oldwebtoday/' + browser,
                'xserver': 'oldwebtoday/vnc-webrtc-audio',
            },
            deferred=deferred,
            user_params=start_request.user_params,
            environ=environ,
        )

        errors = []

        for _ in range(self.model.num_browsers):
            res = await self.manager.request_flock(opts)
            reqid = res.get('reqid')
            if not reqid:
                if 'error' in res:
                    errors.append(res['error'])
                continue

            res = await self.manager.start_flock(reqid)

            if 'error' in res:
                errors.append(res['error'])
            else:
                await self.redis.sadd(self.browser_key, reqid)

        if errors:
            raise HTTPException(400, detail=errors)

        await self.redis.hset(self.info_key, 'status', 'running')

        browsers = list(await self.redis.smembers(self.browser_key))

        return {'success': True, 'browsers': browsers}

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
        if await self.redis.llen(self.frontier_q_key) > 0:
            return {'done': False}

        # if pending q not empty, not done
        if await self.redis.scard(self.pending_q_key) > 0:
            return {'done': False}

        # if not all browsers are done, not done
        browsers = await self.redis.smembers(self.browser_key)
        browsers_done = await self.redis.smembers(self.browser_done_key)
        if browsers != browsers_done:
            return {'done': False}

        await self.redis.hset(self.info_key, 'status', 'done')
        return {'done': True}

    async def stop(self) -> Dict[str, bool]:
        """Stops the crawl

        :return: An dictionary indicating if the operation was successful
        """
        if self.model.status != 'running':
            raise HTTPException(400, detail='not running')

        errors = []

        browsers = await self.redis.smembers(self.browser_key)

        for reqid in browsers:
            res = await self.manager.stop_flock(reqid)
            if 'error' in res:
                errors.append(res['error'])

        if errors:
            raise HTTPException(400, detail=errors)

        await self.redis.hset(self.info_key, 'status', 'stopped')

        return {'success': True}

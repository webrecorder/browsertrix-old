from urllib.parse import urlsplit
from crawlmanager.schema import CrawlInfo
from starlette.exceptions import HTTPException

import os
import asyncio
import aioredis
import aiohttp
import uuid
import json


DEFAULT_REDIS_URL = 'redis://localhost'

redis = None


# ============================================================================
def init_redis():
    async def init():
        global redis
        redis = await aioredis.create_redis(
            os.environ.get('REDIS_URL', DEFAULT_REDIS_URL), encoding='utf-8')

    try:
        return asyncio.get_running_loop().create_task(init())
    except RuntimeError as er:
        return asyncio.run(init())


# ============================================================================
class CrawlManager(object):
    def __init__(self):
        self.depth = os.environ.get('DEFAULT_DEPTH', 1)
        self.same_domain_depth = os.environ.get('DEFAULT_SAME_DOMAIN_DEPTH', 100)

        self.num_browsers = os.environ.get('DEFAULT_NUM_BROWSERS', 2)

        self.flock = os.environ.get('DEFAULT_FLOCK', 'browsers')

        self.shepherd_host = os.environ.get('DEFAULT_SHEPHERD', 'http://shepherd:9020')

        self.browser_api_url = f'{self.shepherd_host}/api'
        self.pool = os.environ.get('DEFAULT_POOL', '')

        self.scan_key = 'a:*:info'

        self.container_environ = {
            'URL': 'about:blank',
            'REDIS_URL': os.environ.get('REDIS_URL', DEFAULT_REDIS_URL),
            'WAIT_FOR_Q': '5',
            'TAB_TYPE': 'CrawlerTab',
            'VNC_PASS': 'pass',
            'IDLE_TIMEOUT': '',
            'BEHAVIOR_API_URL': 'http://behaviors:3030',
            'SCREENSHOT_API_URL': os.environ.get('SCREENSHOT_API_URL')
        }

    def new_crawl_id(self):
        return uuid.uuid4().hex[-12:]

    async def create_new(self, create_request):
        crawl_id = self.new_crawl_id()

        if create_request.scope_type == 'all-links':
            crawl_depth = 1
        elif create_request.scope_type == 'same-domain':
            crawl_depth = self.same_domain_depth
        else:
            crawl_depth = 0

        data = {
            'id': crawl_id,

            'num_browsers': create_request.num_browsers,
            'num_tabs': create_request.num_tabs,
                     #'owner': collection.my_id,
            'scope_type': create_request.scope_type,
            'status': 'new',
            'crawl_depth': crawl_depth
        }

        await redis.hmset_dict(f'a:{crawl_id}:info', data)

        return {'success': True, 'id': crawl_id}

    async def load_crawl(self, crawl_id):
        crawl = Crawl(crawl_id)
        data = await redis.hgetall(crawl.info_key)
        if not data:
            raise HTTPException(404, detail='not_found')

        crawl.model = CrawlInfo(**data)

        return crawl

    async def do_request(self, url_path, post_data=None):
        err = None
        try:
            url = self.browser_api_url + url_path
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=post_data) as res:
                    return await res.json()
        except Exception as e:
            print(e)
            text = str(e)
            raise HTTPException(400,  text)

    async def get_all_crawls(self):
        all_infos = []

        async for key in redis.iscan(match=self.scan_key):
            _, crawl_id, _2 = key.split(':', 2)

            try:
                crawl = Crawl(crawl_id)
                info = await crawl.get_info()
                all_infos.append(info)
            except HTTPException:
                continue

        return {'crawls': all_infos}


# ============================================================================
class Crawl(object):
    def __init__(self, crawl_id):
        self.crawl_id = crawl_id

        self.info_key = f'a:{crawl_id}:info'

        self.frontier_q_key = f'a:{crawl_id}:q'
        self.pending_q_key = f'a:{crawl_id}:qp'

        self.seen_key = f'a:{crawl_id}:seen'
        self.scopes_key = f'a:{crawl_id}:scope'

        self.browser_key = f'a:{crawl_id}:br'
        self.browser_done_key = f'a:{crawl_id}:br:done'

        self.model = None

    async def delete(self):
        if self.model and self.model.status == 'running':
            await self.stop()

        await redis.delete(self.info_key)

        await redis.delete(self.frontier_q_key)
        await redis.delete(self.pending_q_key)

        await redis.delete(self.seen_key)
        await redis.delete(self.scopes_key)

        await redis.delete(self.browser_key)
        await redis.delete(self.browser_done_key)

        return {'success': True}

    async def _init_domain_scopes(self, urls):
        domains = set()

        for url in urls:
            domain = urlsplit(url).netloc
            domains.add(domain)

        if not domains:
            return

        for domain in domains:
            await redis.sadd(self.scopes_key, json.dumps({'domain': domain}))

    async def queue_urls(self, urls):
        for url in urls:
            url_req = {'url': url, 'depth': 0}
            await redis.rpush(self.frontier_q_key, json.dumps(url_req))

            # add to seen list to avoid dupes
            await redis.sadd(self.seen_key, url)

        if self.model.scope_type == 'same-domain':
            await self._init_domain_scopes(urls)

        return {'success': True}

    async def get_info(self):
        data = await redis.hgetall(self.info_key)

        data['browsers'] = list(await redis.smembers(self.browser_key))
        data['browsers_done'] = list(await redis.smembers(self.browser_done_key))

        return data

    async def get_info_urls(self):
        data = {}

        data['scopes'] = list(await redis.smembers(self.scopes_key))

        data['queue'] = await redis.lrange(self.frontier_q_key, 0, -1)
        data['pending'] = list(await redis.smembers(self.pending_q_key))
        data['seen'] = await redis.smembers(self.seen_key)

        return data

    async def start(self, start_request):
        if self.model.status == 'running':
            raise HTTPException(400, detail='already_running')

        browser = start_request.browser or crawl_man.default_browser

        start_request.user_params['auto_id'] = self.crawl_id

        environ = crawl_man.container_environ.copy()
        environ['AUTO_ID'] = self.crawl_id
        environ['NUM_TABS'] = self.model.num_tabs
        if start_request.behavior_timeout > 0:
            environ['BEHAVIOR_RUN_TIME'] = start_request.behavior_timeout

        if start_request.screenshot_target_uri:
            environ['SCREENSHOT_TARGET_URI'] = start_request.screenshot_target_uri
            environ['SCREENSHOT_FORMAT'] = 'png'

        deferred = {'autodriver': False}
        if start_request.headless:
            deferred['xserver'] = True

        opts = dict(overrides={'browser': 'oldwebtoday/' + browser,
                               'xserver': 'oldwebtoday/vnc-webrtc-audio'},
                    deferred=deferred,
                    user_params=start_request.user_params,
                    environ=environ)

        errors = []

        for x in range(self.model.num_browsers):
            request_url = f'/request_flock/{crawl_man.flock}?pool={crawl_man.pool}'
            res = await crawl_man.do_request(request_url, opts)
            reqid = res.get('reqid')
            if not reqid:
                if 'error' in res:
                    errors.append(res['error'])
                continue

            res = await crawl_man.do_request('/start_flock/' + reqid,
                                             {'environ': {'REQ_ID': reqid}})

            if 'error' in res:
                errors.append(res['error'])
            else:
                await redis.sadd(self.browser_key, reqid)

        if errors:
            raise HTTPException(400, detail=errors)

        await redis.hset(self.info_key, 'status', 'running')

        browsers = list(await redis.smembers(self.browser_key))

        return {'success': True,
                'browsers':  browsers}

    async def is_done(self):
        if self.model.status == 'done':
            return {'done': True}

        # if not running, won't be done
        if self.model.status != 'running':
            return {'done': False}

        # if frontier not empty, not done
        if await redis.llen(self.frontier_q_key) > 0:
            return {'done': False}

        # if pending q not empty, not done
        if await redis.scard(self.pending_q_key) > 0:
            return {'done': False}

        # if not all browsers are done, not done
        browsers = await redis.smembers(self.browser_key)
        browsers_done = await redis.smembers(self.browser_done_key)
        if browsers != browsers_done:
            return {'done': False}

        await redis.hset(self.info_key, 'status', 'done')
        return {'done': True}

    async def stop(self):
        if self.model.status != 'running':
            raise HTTPException(400, detail='not_running')

        errors = []

        browsers = await redis.smembers(self.browser_key)

        for reqid in browsers:
            res = await crawl_man.do_request('/stop_flock/' + reqid)
            if 'error' in res:
                errors.append(res['error'])

        if errors:
            raise HTTPException(400, detail=errors)

        await redis.hset(self.info_key, 'status', 'stopped')

        return {'success': True}


# ============================================================================
crawl_man = CrawlManager()


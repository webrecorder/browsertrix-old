from gevent.monkey import patch_all; patch_all()

from pywb.apps.frontendapp import FrontEndApp
from pywb.apps.wbrequestresponse import WbResponse

from warcio.timeutils import http_date_to_datetime, timestamp_now

from pywb.manager.manager import main as manager_main

from tempfile import SpooledTemporaryFile
from werkzeug.routing import Map, Rule
from urllib.parse import parse_qs

import os
import redis
import logging
import traceback
import requests


# ============================================================================
class CrawlProxyApp(FrontEndApp):
    def __init__(self, config_file=None, custom_config=None):
        super(CrawlProxyApp, self).__init__(config_file='./config.yaml',
                                            custom_config=custom_config)

        self.redis = redis.StrictRedis.from_url(os.environ['REDIS_URL'],
                                                decode_responses=True)

        self.collections_checked = set()

        self.screenshot_recorder_path = self.recorder_path + '&put_record=resource&url={url}'

    def ensure_coll_exists(self, coll):
        if coll == 'live':
            return

        if coll in self.collections_checked:
            return

        try:
            manager_main(['init', coll])
        except FileExistsError:
            pass

        self.collections_checked.add(coll)

    def proxy_route_request(self, url, environ):
        try:
            key = 'up:' + environ['REMOTE_ADDR']
            timestamp = self.redis.hget(key, 'TIMESTAMP') or timestamp_now()
            environ['pywb_redis_key'] = key
            environ['pywb_proxy_default_timestamp'] = timestamp

            coll = self.redis.hget(key, 'coll')
            mode = self.redis.hget(key, 'mode')

            if coll:
                self.ensure_coll_exists(coll)

                if mode == 'replay' or coll == 'live':
                    proxy_prefix = '/' + coll + '/bn_/'
                else:
                    proxy_prefix = '/' + coll + '/record/bn_/'
            else:
                proxy_prefix = self.proxy_prefix

        except Exception as e:
            traceback.print_exc()

        return proxy_prefix + url

    def _init_routes(self):
        super(CrawlProxyApp, self)._init_routes()
        self.url_map.add(Rule('/screenshot/<coll>', endpoint=self.put_screenshot,
                         methods=['PUT']))

    def put_screenshot(self, environ, coll):
        self.ensure_coll_exists(coll)

        headers = {'Content-Type': environ.get('CONTENT_TYPE', 'text/plain')}

        query_data = parse_qs(environ.get('QUERY_STRING'))

        url = query_data.get('target_uri', [])
        if url:
            url = url[0]

        if not url:
            return WbResponse.json_response({'error': 'no target_uri'})

        put_url = self.screenshot_recorder_path.format(url=url, coll=coll)

        res = requests.put(put_url,
                           headers=headers,
                           data=environ['wsgi.input'])

        res = res.json()
        return WbResponse.json_response(res)


#=============================================================================
application = CrawlProxyApp()


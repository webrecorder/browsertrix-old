from gevent.monkey import patch_all; patch_all()

from pywb.apps.frontendapp import FrontEndApp
from warcio.timeutils import http_date_to_datetime, timestamp_now

from pywb.manager.manager import main as manager_main

from tempfile import SpooledTemporaryFile

import os
import redis
import logging
import traceback


# ============================================================================
class CrawlProxyApp(FrontEndApp):
    def __init__(self, config_file=None, custom_config=None):
        super(CrawlProxyApp, self).__init__(config_file='./config.yaml',
                                            custom_config=custom_config)

        self.redis = redis.StrictRedis.from_url(os.environ['REDIS_URL'],
                                                decode_responses=True)

        self.collections_checked = set()

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

        print(proxy_prefix + url)
        return proxy_prefix + url


#=============================================================================
application = CrawlProxyApp()


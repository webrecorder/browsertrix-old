# fmt: off
from gevent.monkey import patch_all; patch_all()
# fmt: on
import base64
import hashlib
import json
import os
import traceback
from itertools import chain
from urllib.parse import parse_qsl

import redis
import requests
from pywb.apps.frontendapp import FrontEndApp
from pywb.apps.wbrequestresponse import WbResponse
from pywb.manager.manager import main as manager_main
from pywb.rewrite.templateview import BaseInsertView
from warcio.timeutils import timestamp_now, timestamp_to_iso_date
from werkzeug.routing import Rule

EMPTY_LIST = []
EMPTY_DICT = {}
SKIPPED_NODES = {'script', 'style'}
TEXT_OR_TITLE = {'#text', 'title'}


def extract_text(node, metadata=None):
    nname = node.get('nodeName', '').lower()
    if nname not in SKIPPED_NODES:
        if nname in TEXT_OR_TITLE:
            text_value = node.get('nodeValue', '').strip()
            if text_value:
                if nname == 'title' and metadata is not None:
                    metadata['title'] = text_value
                yield text_value
        kids = node.get('children', EMPTY_LIST)
        if kids:
            for t in chain.from_iterable(extract_text(child, metadata) for child in kids):
                yield t
        content_doc = node.get('contentDocument')
        if content_doc:
            for t in extract_text(content_doc, None):
                yield t


# ============================================================================
class CrawlProxyApp(FrontEndApp):
    def __init__(self, config_file=None, custom_config=None):
        super(CrawlProxyApp, self).__init__(
            config_file='./config.yaml', custom_config=custom_config
        )

        self.redis = redis.StrictRedis.from_url(
            os.environ['REDIS_URL'], decode_responses=True
        )

        self.collections_checked = set()

        self.custom_record_path = (
            self.recorder_path + '&put_record={rec_type}&url={url}'
        )

        self.solr_ingester = FullTextIngester()

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
            timestamp, coll, mode, cache = self.redis.hmget(
                key, 'timestamp', 'coll', 'mode', 'cache'
            )

            # environ['pywb_redis_key'] = key
            environ['pywb_proxy_default_timestamp'] = timestamp or timestamp_now()
            environ['pywb_cache'] = cache

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
        self.url_map.add(
            Rule(
                '/api/screenshot/<coll>', endpoint=self.put_screenshot, methods=['PUT']
            )
        )

        self.url_map.add(
            Rule('/api/dom/<coll>', endpoint=self.put_raw_dom, methods=['PUT'])
        )

        self.url_map.add(
            Rule('/api/search/<coll>', endpoint=self.page_search, methods=['GET'])
        )

        self.url_map.add(
            Rule('/<coll>/search', endpoint=self.serve_orig_coll_page, methods=['GET'])
        )

    def serve_orig_coll_page(self, environ, coll='$root'):
        return super(CrawlProxyApp, self).serve_coll_page(environ, coll)

    def serve_coll_page(self, environ, coll='$root'):
        if not self.is_valid_coll(coll):
            self.raise_not_found(environ, 'No handler for "/{0}"'.format(coll))

        self.setup_paths(environ, coll)

        view = BaseInsertView(self.rewriterapp.jinja_env, 'fullsearch.html')

        wb_prefix = environ.get('SCRIPT_NAME', '')
        if wb_prefix:
            wb_prefix += '/'

        content = view.render_to_string(environ, wb_prefix=wb_prefix, coll=coll)

        return WbResponse.text_response(
            content, content_type='text/html; charset="utf-8"'
        )

    def page_search(self, environ, coll):
        params = dict(parse_qsl(environ.get('QUERY_STRING')))

        result = self.solr_ingester.query_solr(coll, params)

        return WbResponse.json_response(result)

    def put_screenshot(self, environ, coll):
        data = environ['wsgi.input'].read()
        params = dict(parse_qsl(environ.get('QUERY_STRING')))

        return self.put_record(
            environ, coll, 'urn:screenshot:{url}', 'resource', params, data
        )

    def put_raw_dom(self, environ, coll):
        text = environ['wsgi.input'].read()
        params = dict(parse_qsl(environ.get('QUERY_STRING')))

        res = self.put_record(environ, coll, 'urn:dom:{url}', 'metadata', params, text)

        self.solr_ingester.ingest(coll, text, params)
        return res

    def put_record(self, environ, coll, target_uri_format, rec_type, params, data):
        self.ensure_coll_exists(coll)

        headers = {'Content-Type': environ.get('CONTENT_TYPE', 'text/plain')}

        url = params.get('url')

        if not url:
            return WbResponse.json_response({'error': 'no url'})

        timestamp = params.get('timestamp')
        if timestamp:
            headers['WARC-Date'] = timestamp_to_iso_date(timestamp)

        target_uri = target_uri_format.format(url=url)
        put_url = self.custom_record_path.format(
            url=target_uri, coll=coll, rec_type=rec_type
        )
        res = requests.put(put_url, headers=headers, data=data)

        res = res.json()

        return WbResponse.json_response(res)

    def serve_content(self, environ, *args, **kwargs):
        res = super(CrawlProxyApp, self).serve_content(environ, *args, **kwargs)

        if (
            environ.get('pywb_cache') == 'always'
            and res.status_headers.statusline.startswith('200')
            and environ.get('HTTP_REFERER')
        ):

            res.status_headers.headers.append(
                ('Cache-Control', 'public, max-age=31536000, immutable')
            )

        return res


# =============================================================================
class FullTextIngester:
    def __init__(self):
        self.solr_api = 'http://solr:8983/solr/browsertrix/update/json/docs?commit=true'
        self.solr_update_api = 'http://solr:8983/solr/browsertrix/update?commit=true'
        self.solr_select_api = 'http://solr:8983/solr/browsertrix/select'

        self.page_query = '?q=title_t:*&fq=coll_s:{coll}&fl=title_t,url_s,timestamp_ss,has_screenshot_b&rows={rows}&start={start}&sort=timestamp_ss+{sort}'
        self.text_query = '?q={q}&fq={fq}&fl=id,title_t,url_s,timestamp_ss,has_screenshot_b&hl=true&hl.fl=content_t&hl.snippets=3&rows={rows}&start={start}'

    def update_if_dupe(self, digest, coll, url, timestamp, timestamp_dt):
        try:
            query = 'digest_s:"{0}" AND coll_s:{1} AND url_s:"{2}"'.format(
                digest, coll, url
            )
            resp = requests.get(self.solr_select_api, params={'q': query, 'fl': 'id'})

            resp = resp.json()
            resp = resp.get('response')
            if not resp:
                return False

            docs = resp.get('docs')
            if not docs:
                return False

            id_ = docs[0].get('id')
            if not id_:
                return False

            add_cmd = {
                'add': {
                    'doc': {
                        'id': id_,
                        'timestamp_ss': {'add': timestamp},
                        'timestamp_dts': {'add': timestamp_dt},
                    }
                }
            }

            resp = requests.post(self.solr_update_api, json=add_cmd)
            return True

        except Exception as e:
            print(e)
            return False

    def ingest(self, coll, text, params):
        parsed = json.loads(text)
        mdata = {}
        content = "\n".join(text for text in extract_text(parsed["root"], mdata))
        title = mdata.get('title')
        url = params.get('url')
        timestamp_ss = params.get('timestamp')
        timestamp_dts = timestamp_to_iso_date(timestamp_ss)
        has_screenshot_b = params.get('hasScreenshot') == '1'

        title = title or url

        digest = self.get_digest(content)

        if self.update_if_dupe(digest, coll, url, timestamp_ss, timestamp_dts):
            return

        data = {
            'coll_s': coll,
            'title_t': title,
            'content_t': content,
            'url_s': url,
            'digest_s': digest,
            'timestamp_ss': timestamp_ss,
            'timestamp_dts': timestamp_dts,
            'has_screenshot_b': has_screenshot_b,
        }

        result = requests.post(self.solr_api, json=data)

    def get_digest(self, text):
        m = hashlib.sha1()
        m.update(text.encode('utf-8'))
        return 'sha1:' + base64.b32encode(m.digest()).decode('utf-8')

    def query_solr(self, coll, params):
        search = params.get('search')

        start = int(params.get('start', 0))

        rows = int(params.get('limit', 10))

        sort = params.get('sort', 'asc')

        if not search:
            qurl = self.solr_select_api + self.page_query.format(
                coll=coll, start=start, rows=rows, sort=sort
            )
            res = requests.get(qurl)

            res = res.json()
            resp = res.get('response', {})
            docs = resp.get('docs')

            return {
                'total': resp.get('numFound'),
                'results': [
                    {
                        'title': doc.get('title_t'),
                        'url': doc.get('url_s'),
                        'timestamp': doc.get('timestamp_ss'),
                        'has_screenshot': doc.get('has_screenshot_b'),
                    }
                    for doc in docs
                ],
            }

        else:
            query = 'content_t:"{q}" OR title_t:"{q}" OR url_s:"*{q}*"'.format(
                q=search, coll=coll
            )
            res = requests.get(
                self.solr_select_api
                + self.text_query.format(
                    q=query, start=start, rows=rows, fq='coll_s:' + coll
                )
            )

            res = res.json()
            resp = res.get('response', {})
            docs = resp.get('docs')
            hl = res.get('highlighting', {})

            return {
                'total': resp.get('numFound'),
                'results': [
                    {
                        'title': doc.get('title_t'),
                        'url': doc.get('url_s'),
                        'timestamp': doc.get('timestamp_ss'),
                        'has_screenshot': doc.get('has_screenshot_b'),
                        'matched': hl.get(doc.get('id'), {}).get('content_t'),
                    }
                    for doc in docs
                ],
            }


# =============================================================================
application = CrawlProxyApp()

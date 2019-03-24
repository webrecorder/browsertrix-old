from starlette.testclient import TestClient

from mock import patch
from collections import defaultdict
import uuid
import fakeredis
import crawlmanager.crawl


# ============================================================================
class AwaitFakeRedis(object):
    """ async adapter for fakeredis
    """
    def __init__(self):
        self.redis = fakeredis.FakeStrictRedis(decode_responses=True)

    def __getattr__(self, name):
        async def func(*args, **kwargs):
            return getattr(self.redis, name)(*args, **kwargs)

        return func

    async def hmset_dict(self, key, kwargs):
        return self.redis.hmset(key, kwargs)


# ============================================================================
def init():
    async def mock_await_none(*args, **kwargs):
        return None

    with patch('aioredis.create_redis', mock_await_none):
        from crawlmanager.api import app

    crawlmanager.crawl.redis = AwaitFakeRedis()

    return TestClient(app)

client = init()


# ============================================================================
shepherd_api_urls = defaultdict(list)
shepherd_api_post_datas = defaultdict(list)
reqid_counter = 0


async def mock_shepherd_api(self, url_path, post_data=None, use_pool=True):
    global shepherd_api_urls
    global shepherd_api_post_datas
    global reqid_counter

    if 'request_flock' in url_path:
        type_ = 'request'
        reqid_counter += 1
        resp = {'reqid': 'ID_' + str(reqid_counter)}

    elif 'start_flock' in url_path:
        type_ = 'start'
        resp = {'success': True}

    elif 'stop_flock' in url_path:
        type_ = 'stop'
        resp = {'success': True}

    shepherd_api_urls[type_].append(url_path)
    shepherd_api_post_datas[type_].append(post_data)
    return resp


# ============================================================================
class TestCrawlAPI(object):
    crawl_id = None
    crawl_id_2 = None

    def test_crawl_create(self):
        res = client.post('/crawls', json={'num_tabs': 2, 'scope_type': 'all-links'})

        res = res.json()
        assert res['success']
        TestCrawlAPI.crawl_id = res['id']

    def test_crawl_queue_urls(self):
        urls = {'urls': ['https://example.com/',
                         'http://iana.org/']
               }

        res = client.put(f'/crawl/{self.crawl_id}/urls', json=urls)
        assert res.json()['success']

    def test_get_crawl(self):
        res = client.get(f'/crawl/{self.crawl_id}')

        res = res.json()

        assert res['id'] == self.crawl_id
        assert res['num_browsers'] == 2
        assert res['num_tabs'] == 2
        assert res['scope_type'] == 'all-links'
        assert res['status'] == 'new'
        assert res['crawl_depth'] == 1

        assert len(res) == 8

    def test_get_crawl_details(self):
        res = client.get(f'/crawl/{self.crawl_id}/urls')

        res = res.json()

        assert res['queue'] == ['{"url": "https://example.com/", "depth": 0}',
                                '{"url": "http://iana.org/", "depth": 0}']

        assert res['scopes'] == []

        assert set(res['seen']) == set(['http://iana.org/', 'https://example.com/'])

        assert res['pending'] == []

    def test_crawl_same_domain_scopes(self):
        res = client.post('/crawls', json={'num_tabs': 2, 'scope_type': 'same-domain'})
        assert res.json()['success'] == True

        crawl_id = res.json()['id']

        urls = {'urls': ['https://example.com/',
                         'http://iana.org/']
               }

        res = client.put(f'/crawl/{crawl_id}/urls', json=urls)
        assert res.json()['success']

        res = client.get(f'/crawl/{crawl_id}/urls')
        assert set(res.json()['scopes']) == set(['{"domain": "example.com"}', '{"domain": "iana.org"}'])

        # save for deletion
        TestCrawlAPI.crawl_id_2 = crawl_id

    def test_invalid_crawl(self):
        res = client.get(f'/crawl/x-invalid')

        assert res.status_code == 404

        assert res.json() == {'detail': 'not_found'}

    def test_invalid_request_body(self):
        res = client.put(f'/crawl/x-another-invalid/urls', json={})

        assert res.status_code == 422

        assert res.json()['detail']

    def test_invalid_crawl_2(self):
        res = client.put(f'/crawl/x-another-invalid/urls', json={'urls': []})

        assert res.status_code == 404

        assert res.json() == {'detail': 'not_found'}

    @patch('crawlmanager.crawl.CrawlManager.do_request', mock_shepherd_api)
    def test_start_crawl(self):

        global shepherd_api_urls
        shepherd_api_urls.clear()

        global shepherd_api_post_datas
        shepherd_api_post_datas.clear()

        params = {
            'browser': 'chrome:67',
            'screenshot_target_uri': 'file://test',
            'user_params': {'some': 'value', 'some_int': 7},
            'behavior_timeout': 30
        }

        res = client.post(f'/crawl/{self.crawl_id}/start', json=params)
        res = res.json()

        assert res['success']

        # two browsers started
        assert set(res['browsers']) == set(['ID_1', 'ID_2'])

        # shepherd api urls
        assert shepherd_api_urls['request'] == [
            '/request_flock/browsers',
            '/request_flock/browsers',
        ]

        assert set(shepherd_api_urls['start']) == set([
            '/start_flock/ID_1',
            '/start_flock/ID_2'
        ])

        # shepherd api post data
        for data in shepherd_api_post_datas['request']:
            assert data['overrides'] == {
                'browser': 'oldwebtoday/chrome:67',
                'xserver': 'oldwebtoday/vnc-webrtc-audio'
            }

            assert data['deferred'] == {'autodriver': False}

            assert data['environ']['SCREENSHOT_TARGET_URI'] == 'file://test'

            assert data['user_params']['some'] == 'value'
            assert data['user_params']['some_int'] == 7

        assert shepherd_api_post_datas['start'] == [
            {'environ': {'REQ_ID': 'ID_1'}},
            {'environ': {'REQ_ID': 'ID_2'}}
        ]

    def test_is_done(self):
        res = client.get(f'/crawl/{self.crawl_id}/done')
        res = res.json()

        assert res['done'] == False

    @patch('crawlmanager.crawl.CrawlManager.do_request', mock_shepherd_api)
    def test_stop_crawl(self):
        res = client.post(f'/crawl/{self.crawl_id}/stop')
        res = res.json()

        assert res['success']

        # stop calls
        assert set(shepherd_api_urls['stop']) == set([
            '/stop_flock/ID_1',
            '/stop_flock/ID_2'
        ])

        # no post data for stop
        assert shepherd_api_post_datas['stop'] == [None, None]

        res = client.get(f'/crawl/{self.crawl_id}')

        res = res.json()

        assert res['status'] == 'stopped'

    def test_delete_crawl(self):
        res = client.delete(f'/crawl/{self.crawl_id}')

        assert res.json()['success'] == True

        res = client.delete(f'/crawl/{self.crawl_id_2}')

        assert res.json()['success'] == True

        assert fakeredis.FakeStrictRedis().keys('a:*') == []


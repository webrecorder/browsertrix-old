from collections import defaultdict

import fakeredis
import pytest
import os
from mock import patch

from .utils import convert_list_str_to_list, convert_list_str_to_set

# ============================================================================
shepherd_api_urls = defaultdict(list)
shepherd_api_post_datas = defaultdict(list)
reqid_counter = 0

os.environ['DEFAULT_POOL'] = 'test-pool'


# ============================================================================
async def mock_shepherd_api(self, url_path, post_data=None, use_pool=True):
    global shepherd_api_urls
    global shepherd_api_post_datas
    global reqid_counter

    type_ = None
    resp = None
    if 'flock/request' in url_path:
        type_ = 'request'
        reqid_counter += 1
        resp = {'reqid': 'ID_' + str(reqid_counter)}

    elif 'flock/start' in url_path:
        type_ = 'start'
        resp = {'success': True}

    elif 'flock/stop' in url_path:
        type_ = 'stop'
        resp = {'success': True}

    else:
        assert False, 'Unknown API call'

    shepherd_api_urls[type_].append(url_path)
    shepherd_api_post_datas[type_].append(post_data)
    return resp


# ============================================================================
@patch('browsertrix.crawl.CrawlManager.do_request', mock_shepherd_api)
@pytest.mark.usefixtures('browsertrix_use_fake_redis', 'api_test_client')
class TestCrawlAPI:
    crawl_id = None
    crawl_id_2 = None

    params = {
            'browser': 'chrome:67',
            'screenshot_target_uri': 'file://test',
            'user_params': {'some': 'value', 'some_int': 7},
            'behavior_run_time': 30,
            'headless': False,
            'start': False,
            'num_tabs': 2,
    }

    def test_crawl_create(self):
        params = self.params.copy()
        params['crawl_type'] = 'all-links'
        params['name'] = 'First Crawl!'

        res = self.client.post(
            '/crawls', json=params
        )

        res = res.json()
        assert res['success']
        TestCrawlAPI.crawl_id = res['id']

        # shepherd api urls
        assert shepherd_api_urls['request'] == [
            '/flock/request/browsers?pool=test-pool',
            '/flock/request/browsers?pool=test-pool',
        ]

    def test_crawl_queue_urls(self):
        urls = {'urls': ['https://example.com/', 'http://iana.org/']}

        res = self.client.put(f'/crawl/{self.crawl_id}/urls', json=urls)
        assert res.json()['success']

    def test_get_crawl(self):
        res = self.client.get(f'/crawl/{self.crawl_id}')

        json = res.json()

        assert json['id'] == self.crawl_id
        assert json['name'] == 'First Crawl!'
        assert json['num_browsers'] == 2
        assert json['num_tabs'] == 2
        assert json['crawl_type'] == 'all-links'
        assert json['status'] == 'new'
        assert json['crawl_depth'] == 1
        assert json['start_time'] == 0
        assert json['coll'] == 'live'
        assert json['mode'] == 'record'
        assert json['num_queue'] == 2
        assert json['num_seen'] == 2
        assert json['num_pending'] == 0
        assert json['headless'] == False
        assert json['screenshot_coll'] == ''

        assert len(json) == 17

    def test_get_crawl_details(self):
        res = self.client.get(f'/crawl/{self.crawl_id}/urls')

        json = res.json()

        assert convert_list_str_to_list(json['queue']) == [
            {'url': 'https://example.com/', 'depth': 0},
            {'url': 'http://iana.org/', 'depth': 0},
        ]

        assert json['scopes'] == []

        assert set(json['seen']) == {'http://iana.org/', 'https://example.com/'}

        assert json['pending'] == []

    def test_crawl_same_domain_scopes(self):
        params = self.params.copy()
        params['crawl_type'] = 'same-domain'
        res = self.client.post(
            '/crawls', json=params
        )
        assert res.json()['success'] == True

        crawl_id = res.json()['id']

        urls = {'urls': ['https://example.com/', 'http://iana.org/']}

        res = self.client.put(f'/crawl/{crawl_id}/urls', json=urls)
        assert res.json()['success']

        res = self.client.get(f'/crawl/{crawl_id}/urls')
        scopes = convert_list_str_to_set(res.json()['scopes'], lambda x: x['domain'])
        assert scopes == {'example.com', 'iana.org'}

        # save for deletion
        TestCrawlAPI.crawl_id_2 = crawl_id

        # shepherd api urls
        assert shepherd_api_urls['request'] == [
            '/flock/request/browsers?pool=test-pool',
            '/flock/request/browsers?pool=test-pool',
            '/flock/request/browsers?pool=test-pool',
            '/flock/request/browsers?pool=test-pool',
        ]



    def test_get_all_crawls(self):
        res = self.client.get(f'/crawls')
        res = res.json()

        assert len(res['crawls']) == 2

        expected_crawls = {
            (self.crawl_id, 'all-links'),
            (self.crawl_id_2, 'same-domain'),
        }

        assert (
            set((crawl['id'], crawl['crawl_type']) for crawl in res['crawls'])
            == expected_crawls
        )

    def test_invalid_crawl(self):
        res = self.client.get(f'/crawl/x-invalid')

        assert res.status_code == 404

        assert res.json() == {'detail': 'not found'}

    def test_invalid_request_body(self):
        res = self.client.put(f'/crawl/x-another-invalid/urls', json={})

        assert res.status_code == 422

        assert res.json()['detail']

    def test_invalid_crawl_2(self):
        res = self.client.put(f'/crawl/x-another-invalid/urls', json={'urls': []})

        assert res.status_code == 404

        assert res.json() == {'detail': 'not found'}

    def test_start_crawl(self):
        res = self.client.post(f'/crawl/{self.crawl_id}/start')
        json = res.json()

        assert json['success']

        # two browsers started
        assert set(json['browsers']) == {'ID_1', 'ID_2'}

        assert set(shepherd_api_urls['start']) == {'/flock/start/ID_1', '/flock/start/ID_2'}

        # shepherd api post data
        for data in shepherd_api_post_datas['request']:
            assert data['overrides'] == {
                'browser': 'oldwebtoday/chrome:67',
                'xserver': 'oldwebtoday/vnc-webrtc-audio',
            }

            assert data['deferred'] == {'autobrowser': False}

            assert data['environ']['SCREENSHOT_TARGET_URI'] == 'file://test'

            assert data['user_params']['some'] == 'value'
            assert data['user_params']['some_int'] == 7

        assert {'environ': {'REQ_ID': 'ID_1'}} in shepherd_api_post_datas['start']
        assert {'environ': {'REQ_ID': 'ID_2'}} in shepherd_api_post_datas['start']

    def test_is_done(self):
        res = self.client.get(f'/crawl/{self.crawl_id}/done')
        res = res.json()

        assert res['done'] == False

    def test_get_crawl_start_running(self):
        res = self.client.get(f'/crawl/{self.crawl_id}')

        json = res.json()

        assert json['id'] == self.crawl_id
        assert json['name'] == 'First Crawl!'
        assert json['status'] == 'running'
        assert json['start_time'] > 0
        assert json['headless'] == False
        assert json['num_queue'] == 2
        assert json['num_seen'] == 2
        assert json['num_pending'] == 0

        assert len(json) == 17

    @patch('browsertrix.crawl.CrawlManager.do_request', mock_shepherd_api)
    def test_stop_crawl(self):
        res = self.client.post(f'/crawl/{self.crawl_id}/stop')
        json = res.json()

        assert json['success']

        # stop calls
        assert set(shepherd_api_urls['stop']) == {
            '/flock/stop/ID_1',
            '/flock/stop/ID_2',
        }

        # no post data for stop
        assert shepherd_api_post_datas['stop'] == [None, None]

        res = self.client.get(f'/crawl/{self.crawl_id}')

        json = res.json()

        assert json['status'] == 'stopped'

    @patch('browsertrix.crawl.CrawlManager.do_request', mock_shepherd_api)
    def test_delete_crawl(self):
        res = self.client.delete(f'/crawl/{self.crawl_id}')

        assert res.json()['success'] == True

        res = self.client.delete(f'/crawl/{self.crawl_id_2}')

        assert res.json()['success'] == True

        assert fakeredis.FakeStrictRedis().keys('a:*') == []

        res = self.client.delete(f'/crawl/{self.crawl_id_2}')

        assert res.json()['detail'] == 'not found'

    @patch('browsertrix.crawl.CrawlManager.do_request', mock_shepherd_api)
    def test_create_and_start(self):
        res = self.client.post(
            '/crawls', json={'num_tabs': 2,
                             'crawl_type': 'all-links',
                             'name': 'Second Crawl Auto Start!',
                             'num_browsers': 3,
                             'coll': 'custom',
                             'screenshot_coll': 'screen-coll',
                             'seed_urls':
                                [
                                  'https://example.com/',
                                  'https://iana.org/'
                                ],
                             'browser': 'chrome:67',
                             'screenshot_target_uri': 'file://test',
                             'user_params': {'some': 'value', 'some_int': 7},
                             'behavior_run_time': 30,
                             'headless': True,
                             'start': True,
                             }

        )

        json = res.json()
        assert 'success' in json
        assert len(json['browsers']) == 3
        assert json['status'] == 'running'

        TestCrawlAPI.crawl_id = json['id']

    def test_second_crawl_info(self):
        res = self.client.get(f'/crawl/{self.crawl_id}')
        json = res.json()
        assert json['coll'] == 'custom'
        assert json['screenshot_coll'] == 'screen-coll'
        assert json['headless'] == True

        assert len(shepherd_api_post_datas['request']) == 7

        # assert last 3 shepherd api requests were headless
        for data in shepherd_api_post_datas['request'][-3:]:
            data = shepherd_api_post_datas['request'][-1]
            assert data['deferred'] == {'autobrowser': False, 'xserver': True}

    @patch('browsertrix.crawl.CrawlManager.do_request', mock_shepherd_api)
    def test_stop_and_delete_second_crawl(self):
        res = self.client.post(f'/crawl/{self.crawl_id}/stop')
        json = res.json()

        assert json['success']

        # stop calls
        assert set(shepherd_api_urls['stop']) == {
            '/flock/stop/ID_1',
            '/flock/stop/ID_2',
            '/flock/stop/ID_5',
            '/flock/stop/ID_6',
            '/flock/stop/ID_7',
        }

        # no post data for stop
        assert shepherd_api_post_datas['stop'] == [None, None, None, None, None]

        res = self.client.get(f'/crawl/{self.crawl_id}')

        json = res.json()

        assert json['status'] == 'stopped'

        res = self.client.delete(f'/crawl/{self.crawl_id}')

        assert res.json()['success'] == True

        assert fakeredis.FakeStrictRedis().keys('a:*') == []




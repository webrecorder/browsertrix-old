from collections import defaultdict

import fakeredis
import pytest
from mock import patch

from .utils import convert_list_str_to_list, convert_list_str_to_set

# ============================================================================
shepherd_api_urls = defaultdict(list)
shepherd_api_post_datas = defaultdict(list)
reqid_counter = 0


async def mock_shepherd_api(self, url_path, post_data=None, use_pool=True):
    global shepherd_api_urls
    global shepherd_api_post_datas
    global reqid_counter

    type_ = None
    resp = None
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
@pytest.mark.usefixtures('crawlmanager_use_fake_redis', 'api_test_client')
class TestCrawlAPI:
    crawl_id = None
    crawl_id_2 = None

    def test_crawl_create(self):
        res = self.client.post(
            '/crawls', json={'num_tabs': 2, 'crawl_type': 'all-links'}
        )

        res = res.json()
        assert res['success']
        TestCrawlAPI.crawl_id = res['id']

    def test_crawl_queue_urls(self):
        urls = {'urls': ['https://example.com/', 'http://iana.org/']}

        res = self.client.put(f'/crawl/{self.crawl_id}/urls', json=urls)
        assert res.json()['success']

    def test_get_crawl(self):
        res = self.client.get(f'/crawl/{self.crawl_id}')

        json = res.json()

        assert json['id'] == self.crawl_id
        assert json['num_browsers'] == 2
        assert json['num_tabs'] == 2
        assert json['crawl_type'] == 'all-links'
        assert json['status'] == 'new'
        assert json['crawl_depth'] == 1

        assert len(json) == 8

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
        res = self.client.post(
            '/crawls', json={'num_tabs': 2, 'crawl_type': 'same-domain'}
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
            'behavior_run_time': 30,
        }

        res = self.client.post(f'/crawl/{self.crawl_id}/start', json=params)
        json = res.json()

        assert json['success']

        # two browsers started
        assert set(json['browsers']) == {'ID_1', 'ID_2'}

        # shepherd api urls
        assert shepherd_api_urls['request'] == [
            '/request_flock/browsers?pool=',
            '/request_flock/browsers?pool=',
        ]

        assert set(shepherd_api_urls['start']) == {'/start_flock/ID_1', '/start_flock/ID_2'}

        # shepherd api post data
        for data in shepherd_api_post_datas['request']:
            assert data['overrides'] == {
                'browser': 'oldwebtoday/chrome:67',
                'xserver': 'oldwebtoday/vnc-webrtc-audio',
            }

            assert data['deferred'] == {'autodriver': False}

            assert data['environ']['SCREENSHOT_TARGET_URI'] == 'file://test'

            assert data['user_params']['some'] == 'value'
            assert data['user_params']['some_int'] == 7

        assert shepherd_api_post_datas['start'] == [
            {'environ': {'REQ_ID': 'ID_1'}},
            {'environ': {'REQ_ID': 'ID_2'}},
        ]

    def test_is_done(self):
        res = self.client.get(f'/crawl/{self.crawl_id}/done')
        res = res.json()

        assert res['done'] == False

    @patch('crawlmanager.crawl.CrawlManager.do_request', mock_shepherd_api)
    def test_stop_crawl(self):
        res = self.client.post(f'/crawl/{self.crawl_id}/stop')
        json = res.json()

        assert json['success']

        # stop calls
        assert set(shepherd_api_urls['stop']) == {
            '/stop_flock/ID_1',
            '/stop_flock/ID_2',
        }

        # no post data for stop
        assert shepherd_api_post_datas['stop'] == [None, None]

        res = self.client.get(f'/crawl/{self.crawl_id}')

        json = res.json()

        assert json['status'] == 'stopped'

    def test_delete_crawl(self):
        res = self.client.delete(f'/crawl/{self.crawl_id}')

        assert res.json()['success'] == True

        res = self.client.delete(f'/crawl/{self.crawl_id_2}')

        assert res.json()['success'] == True

        assert fakeredis.FakeStrictRedis().keys('a:*') == []

        res = self.client.delete(f'/crawl/{self.crawl_id_2}')

        assert res.json()['detail'] == 'not found'

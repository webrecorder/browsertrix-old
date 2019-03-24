import requests
import webbrowser
import time
import pytest
import yaml
import os


crawls = None
with open(os.path.join(os.path.dirname(__file__), 'crawl_tests.yaml')) as fh:
    crawls = yaml.load(fh.read())


crawl_map = {crawl['name']: crawl for crawl in crawls['crawls'] if not crawl.get('skip')}


@pytest.fixture(scope='module', params=crawl_map.keys())
def crawl(request):
    return crawl_map[request.param]


class TestCrawls(object):
    crawl_id = None
    api_host = 'http://localhost:8000'
    seen = []
    browsers = []

    @classmethod
    def teardown_class(cls):
        if cls.crawl_id:
            res = requests.delete(cls.api_host + '/crawl/' + cls.crawl_id)
            assert res.json()['success']

    def test_crawl_create(self, crawl):
        res = requests.post(self.api_host + '/crawls', json=crawl['spec'])

        res = res.json()
        assert res['success']
        TestCrawls.crawl_id = res['id']

    def test_crawl_queue_urls(self, crawl):
        urls = {'urls': crawl['urls']}

        res = requests.put(self.api_host + f'/crawl/{self.crawl_id}/urls', json=urls)
        assert res.json()['success']

    def test_start_crawl(self, crawl):
        params = {
            'browser': crawl.get('browser', 'chrome:67'),
            'behavior_timeout': crawl.get('behavior_timeout', 60)
        }

        res = requests.post(self.api_host + f'/crawl/{self.crawl_id}/start', json=params)
        res = res.json()

        assert res['success']
        assert len(res['browsers']) == crawl['spec'].get('num_browsers', 1)

        TestCrawls.browsers = res['browsers']

    def test_load_browsers(self, crawl):
        for reqid in self.browsers:
            webbrowser.open(f'http://localhost:9020/attach/{reqid}')

    def test_sleep_wait(self, crawl):
        start_time = time.time()
        sleep_time = 5
        max_time = crawl.get('max_timeout', 600)
        done = False
        while True:
            res = requests.get(self.api_host + f'/crawl/{self.crawl_id}/done')
            if res.json()['done']:
                done = True
                break

            if time.time() - start_time > max_time:
                break

            time.sleep(sleep_time)

        assert done

    def test_get_stats(self, crawl):
        res = requests.get(self.api_host + f'/crawl/{self.crawl_id}/urls')
        res = res.json()
        assert len(res['queue']) == 0
        assert len(res['pending']) == 0

        assert len(res['seen']) >= len(crawl['urls'])
        if crawl.get('expected_seen'):
            assert len(res['seen']) == crawl.get('expected_seen')

        TestCrawls.seen = res['seen']

    def test_delete(self, crawl):
        res = requests.delete(self.api_host + '/crawl/' + self.crawl_id)
        assert res.json()['success']
        TestCrawls.crawl_id = None

    def test_replay(self, crawl):
        for seen_url in self.seen:
            res = requests.get(f'http://localhost:8180/coll/mp_/{seen_url}', allow_redirects=True)
            assert 'URL Not Found' not in res.text


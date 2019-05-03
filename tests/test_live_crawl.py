import requests
import webbrowser
import time


class TestCrawls(object):
    crawl_id = None
    api_host = 'http://localhost:8000'
    default_browser = 'chrome:73'
    seen = []
    browsers = []

    all_crawl_ids = []

    @classmethod
    def teardown_class(cls):
        for crawl_id in cls.all_crawl_ids:
            res = requests.delete(cls.api_host + '/crawl/' + crawl_id)
            res = res.json()
            assert res.get('success') or res.get('detail') == 'crawl not found'

    def test_crawl_create_and_start(self, crawl, headless):
        crawl['headless'] = headless
        if 'browser' not in crawl:
            crawl['browser'] = self.default_browser

        res = requests.post(self.api_host + '/crawls', json=crawl)
        res = res.json()

        assert res.get('success'), res
        assert len(res['browsers']) == crawl.get('num_browsers', 1)

        TestCrawls.crawl_id = res['id']
        TestCrawls.all_crawl_ids.append(res['id'])
        TestCrawls.browsers = res['browsers']

    def test_load_browsers(self, crawl, headless):
        if not headless:
            for reqid in self.browsers:
                webbrowser.open(f'http://localhost:9323/attach/{reqid}')

    def test_sleep_wait(self, crawl):
        start_time = time.time()
        sleep_time = 5
        max_time = crawl.get('ignore_extra', {}).get('test_max_timeout', 600) + 30
        done = False
        while True:
            res = requests.get(self.api_host + f'/crawl/{self.crawl_id}/done')
            if res.json()['done']:
                done = True
                break

            if time.time() - start_time > max_time:
                break

            print('Waiting for crawl done')
            time.sleep(sleep_time)

        assert done

    def test_get_stats(self, crawl):
        res = requests.get(self.api_host + f'/crawl/{self.crawl_id}/urls')
        res = res.json()
        assert len(res['queue']) == 0
        assert len(res['pending']) == 0

        assert len(res['seen']) >= len(crawl['seed_urls'])
        expected_seen = crawl.get('ignore_extra', {}).get('test_expected_seen')
        if expected_seen:
            assert len(res['seen']) == expected_seen

        TestCrawls.seen = res['seen']

    def test_delete(self, crawl):
        res = requests.delete(self.api_host + '/crawl/' + self.crawl_id)
        res = res.json()
        assert res.get('success'), res
        TestCrawls.crawl_id = None

    def test_replay(self, crawl):
        for seen_url in self.seen:
            res = requests.get(f'http://localhost:8181/coll/mp_/{seen_url}', allow_redirects=True)
            assert 'URL Not Found' not in res.text


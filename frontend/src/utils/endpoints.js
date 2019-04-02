function getEndpointConfig() {
  if (typeof window !== 'undefined' && window.__crawlmanEndpoints != null) {
    return window.__crawlmanEndpoints;
  }
  return {
    crawls: {
      ep: 'http://localhost:8000/crawls',
      retrieve: { method: 'GET' },
      create: {
        defaults: { crawl_type: 'single-page', num_browsers: 2, num_tabs: 1 },
        method: 'POST'
      }
    },
    crawl: {
      ep: 'http://localhost:8000/crawl/',
      info: { path: '/info', method: 'GET' },
      remove: { method: 'DELETE' },
      start: {
        defaults: {
          browser: 'chrome:67',
          behavior_run_time: 60,
          headless: false
        },
        method: 'POST',
        path: '/start'
      },
      stop: { method: 'POST', path: '/stop' },
      done: { method: 'GET', path: '/done' },
      retrieveURLS: { method: 'GET', path: '/urls' },
      addURLS: { method: 'POST', path: '/urls' }
    }
  };
}

class Endpoints {
  constructor({ crawls, crawl }) {
    this.crawls = crawls;
    this.crawl = crawl;
  }

  /**
   * @param {Object} [newCrawlConfig]
   * @return {{body: Object, request: Request}}
   */
  createNewCrawl(newCrawlConfig) {
    const { defaults = {}, method } = this.crawls.create;
    const body = Object.assign(defaults, newCrawlConfig.crawlInfo);

    if (Array.isArray(newCrawlConfig.crawlRunInfo.seed_urls)) {
      body.seed_urls = newCrawlConfig.crawlRunInfo.seed_urls;
    }
    return {
      body,
      request: new Request(this.crawls.ep, {
        method,
        body: JSON.stringify(body)
      })
    };
  }

  /**
   * @return {Request}
   */
  retrieveAllCrawls() {
    const { method } = this.crawls.retrieve;
    return new Request(this.crawls.ep, { method });
  }

  /**
   * @param {string} id
   * @return {Request}
   */
  crawlInfo(id) {
    const { path = '', method } = this.crawl.info;
    const url = `${this.crawl.ep}${id}${path}`;
    return new Request(url, { method });
  }

  /**
   * @param {string} id
   * @return {Request}
   */
  crawlDone(id) {
    const { path = '', method } = this.crawl.done;
    const url = `${this.crawl.ep}${id}${path}`;
    return new Request(url, { method });
  }

  /**
   * @param {string} id
   * @return {Request}
   */
  getCrawlURLs(id) {
    const { path = '', method } = this.crawl.retrieveURLS;
    const url = `${this.crawl.ep}${id}${path}`;
    return new Request(url, { method });
  }

  /**
   * @param {string} id
   * @param {Array<string>} urls
   * @return {{body: Object, request: Request}}
   */
  addCrawlURLs(id, urls) {
    const { path = '', method } = this.crawl.addURLS;
    const url = `${this.crawl.ep}${id}${path}`;
    const body = { urls };
    return {
      body,
      request: new Request(url, {
        method,
        body: JSON.stringify(body)
      })
    };
  }

  /**
   * @param {string} id
   * @return {Request}
   */
  removeCrawl(id) {
    const { path = '', method } = this.crawl.remove;
    const url = `${this.crawl.ep}${id}${path}`;
    return new Request(url, { method });
  }

  /**
   * @param {string} id
   * @param {Object} [config]
   * @return {{body: Object, request: Request}}
   */
  startCrawl(id, config) {
    const { path = '', method, defaults = {} } = this.crawl.start;
    const url = `${this.crawl.ep}${id}${path}`;
    const body = Object.assign(defaults, config);
    return {
      body,
      request: new Request(url, {
        method,
        body: JSON.stringify(body)
      })
    };
  }

  /**
   * @param {string} id
   * @return {Request}
   */
  stopCrawl(id) {
    const { path = '', method } = this.crawl.stop;
    const url = `${this.crawl.ep}${id}${path}`;
    return new Request(url, { method });
  }
}

export const EndpointRequests = new Endpoints(getEndpointConfig());

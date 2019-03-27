const { root, crawl } =
  typeof window !== 'undefined'
    ? window.__crawlmanEndpoints != null
      ? window.__crawlmanEndpoints
      : {
          root: 'http://localhost:8001',
          crawl: 'http://localhost:8001/crawl/'
        }
    : {
        root: 'http://localhost:8001',
        crawl: 'http://localhost:8001/crawl/'
      };

/**
 * @type {{crawls: {retrieve: {method: string, ep: string}, create: {method: string, ep: string}}, crawl: {urls: {add: {method: string, ep: (function(*): string)}, retrieve: {method: string, ep: (function(*): string)}}, stop: {method: string, ep: (function(*): string)}, start: {method: string, ep: (function(*): string)}, done: {method: string, ep: (function(*): string)}, remove: {method: string, ep: (function(*): string)}, info: {method: string, ep: (function(*): string)}}}}
 */
export const Endpoints = {
  crawls: {
    retrieve: {
      ep: `${root}/crawls`,
      method: 'GET'
    },
    create: {
      ep: `${root}/crawls`,
      method: 'POST'
    }
  },
  crawl: {
    info: {
      ep: id => `${crawl}${id}`,
      method: 'GET'
    },
    remove: {
      ep: id => `${crawl}${id}`,
      method: 'DELETE'
    },
    start: {
      ep: id => `${crawl}${id}/start`,
      method: 'POST'
    },
    stop: {
      ep: id => `${crawl}${id}/stop`,
      method: 'POST'
    },
    done: {
      ep: id => `${crawl}${id}/done`,
      method: 'GET'
    },
    urls: {
      retrieve: {
        ep: id => `${crawl}${id}/urls`,
        method: 'GET'
      },
      add: {
        ep: id => `${crawl}${id}/urls`,
        method: 'POST'
      }
    }
  }
};

export class EndPointRequests {
  /**
   * @return {Request}
   */
  static retrieveAllCrawls() {
    const {
      retrieve: { ep, method }
    } = Endpoints.crawls;
    return new Request(ep, {
      method
    });
  }

  /**
   * @param body
   * @return {Request}
   */
  static createNewCrawl(body) {
    const {
      create: { ep, method }
    } = Endpoints.crawls;
    return new Request(ep, {
      method,
      body: JSON.stringify(body)
    });
  }

  /**
   *
   * @param {string} id
   * @return {Request}
   */
  static crawlInfo(id) {
    const { info } = Endpoints.crawl;
    return new Request(info.ep(id), {
      method: info.method
    });
  }

  /**
   *
   * @param {string} id
   * @return {Request}
   */
  static removeCrawl(id) {
    const { remove } = Endpoints.crawl;
    return new Request(remove.ep(id), {
      method: remove.method
    });
  }

  /**
   *
   * @param {string} id
   * @param {Object} body
   * @return {Request}
   */
  static startCrawl(id, body) {
    const { start } = Endpoints.crawl;
    return new Request(start.ep(id), {
      method: start.method,
      body: JSON.stringify(body)
    });
  }

  /**
   *
   * @param {string} id
   * @return {Request}
   */
  static stopCrawl(id) {
    const { stop } = Endpoints.crawl;
    return new Request(stop.ep(id), {
      method: stop.method
    });
  }

  /**
   *
   * @param {string} id
   * @return {Request}
   */
  static isCrawlDone(id) {
    const { done } = Endpoints.crawl;
    return new Request(done.ep(id), {
      method: done.method
    });
  }

  /**
   *
   * @param {string} id
   * @return {Request}
   */
  static getCawlUrls(id) {
    const { retrieve } = Endpoints.crawl.urls;
    return new Request(retrieve.ep(id), {
      method: retrieve.method
    });
  }

  /**
   *
   * @param {string} id
   * @param {Array<string>} urls
   * @return {Request}
   */
  static addCawlUrls(id, urls) {
    const { retrieve } = Endpoints.crawl;
    return new Request(retrieve.ep(id), {
      method: retrieve.method,
      body: JSON.stringify(urls)
    });
  }
}

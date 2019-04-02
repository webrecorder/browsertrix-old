import { toast } from 'react-toastify';
import { makeHTTPRequest } from './httpRequests';
import { EndpointRequests } from '../utils';

export const ActionTypes = {
  getAll: Symbol('crawl-get-all'),
  gotAll: Symbol('crawl-got-all'),
  gotAllInit: Symbol('crawl-got-all-init'),
  create: Symbol('crawl-create'),
  urls: Symbol('crawl-get-urls'),
  addURLs: Symbol('crawl-add-urls'),
  updateURLInfo: Symbol('crawl-update-url-info'),
  info: Symbol('crawl-get-info'),
  stop: Symbol('crawl-stop'),
  start: Symbol('crawl-start'),
  isDone: Symbol('crawl-is-done'),
  deleteCrawl: Symbol('crawl-delete'),
  updateInfo: Symbol('crawl-update-info')
};

export function getAllCrawls(init = false) {
  const request = EndpointRequests.retrieveAllCrawls();
  return makeHTTPRequest(request, {
    onError({ error }) {
      toast(`Failed to retrieve info about all crawls: ${error}`, {
        type: toast.TYPE.ERROR
      });
    },
    async onResponse({ response }) {
      if (!response.ok) {
        toast(
          `Failed to retrieve info about all crawls: Details 
        HTTP ${response.status}`,
          {
            type: toast.TYPE.ERROR
          }
        );
        return;
      }
      return {
        type: init ? ActionTypes.gotAllInit : ActionTypes.gotAll,
        payload: await response.json()
      };
    }
  });
}

export function getCrawlInfo(id) {
  const request = EndpointRequests.crawlInfo(id);
  return makeHTTPRequest(request, {
    onError({ error }) {
      toast(`Failed to retrieve the info for crawl - ${id}: ${error}`, {
        type: toast.TYPE.ERROR
      });
    },
    async onResponse({ response }) {
      const json = await response.json();
      if (!response.ok) {
        toast(
          `Failed to get the crawl info - ${id}: Details 
        ${json.detail}`,
          {
            type: toast.TYPE.ERROR
          }
        );
        return;
      }
      return {
        type: ActionTypes.info,
        payload: json
      };
    }
  });
}

export function addCrawlURLs(id, urls) {
  const { request } = EndpointRequests.addCrawlURLs(id, urls);
  return makeHTTPRequest(request, {
    onError({ error }) {
      toast(`Failed to add the urls to the crawl - ${id}: ${error}`, {
        type: toast.TYPE.ERROR
      });
    },
    async onResponse({ response }) {
      const json = await response.json();
      if (!response.ok) {
        toast(
          `Failed to add urls to the crawl - ${id}: Details 
        ${json.detail}`,
          {
            type: toast.TYPE.ERROR
          }
        );
        return;
      }
      return {
        type: ActionTypes.addURLs,
        payload: {
          id,
          urls
        }
      };
    }
  });
}

export function getCrawlURLs(id) {
  const { request } = EndpointRequests.getCrawlURLs(id);
  return makeHTTPRequest(request, {
    onError({ error }) {
      toast(`Failed to retrieve the crawls URLs - ${id}: ${error}`, {
        type: toast.TYPE.ERROR
      });
    },
    async onResponse({ response }) {
      const json = await response.json();
      if (!response.ok) {
        toast(
          `Failed to retrieve the crawls URLs - ${id}: Details 
        ${json.detail}`,
          {
            type: toast.TYPE.ERROR
          }
        );
        return;
      }
      return {
        type: ActionTypes.updateURLInfo,
        payload: Object.assign(
          {
            id
          },
          json
        )
      };
    }
  });
}

/**
 *
 * @param {Object} [newCrawlConfig]
 */
export function createCrawl(newCrawlConfig) {
  const { body, request } = EndpointRequests.createNewCrawl(newCrawlConfig);
  return makeHTTPRequest(request, {
    onError({ error }) {
      toast(`Failed to create the new crawl ${error}`, {
        type: toast.TYPE.ERROR
      });
    },
    async onResponse({ dispatch, response }) {
      const json = await response.json();
      if (!response.ok) {
        toast(
          `Failed to create the crawl - ${json.id}: Details 
        ${json.detail}`,
          {
            type: toast.TYPE.ERROR
          }
        );
        return;
      }
      const request = EndpointRequests.crawlInfo(json.id);
      const infoResponse = await fetch(request);
      const result = infoResponse.ok
        ? await infoResponse.json()
        : Object.assign(
            {
              id: json.id
            },
            body,
            newCrawlConfig.crawlRunInfo
          );

      console.log('newly created crawl info', result);
      return {
        type: ActionTypes.create,
        payload: result
      };
    }
  });
}

/**
 *
 * @param {string} id
 * @param {Object} [startConfig]
 */
export function startCrawl(id, startConfig) {
  const { body, request } = EndpointRequests.startCrawl(id, startConfig);
  return makeHTTPRequest(request, {
    onError({ error }) {
      toast(`Failed to start the crawl - ${id}: ${error}`, {
        type: toast.TYPE.ERROR
      });
    },
    async onResponse({ response }) {
      const json = await response.json();
      if (!response.ok) {
        toast(
          `Failed to start the crawl - ${id}: Details 
        ${json.detail}`,
          {
            type: toast.TYPE.ERROR
          }
        );
        return;
      }
      const result = {
        id,
        ...body
      };
      console.log('started crawl info', result);
      return {
        type: ActionTypes.start,
        payload: result
      };
    }
  });
}

export function stopCrawl(id) {
  const request = EndpointRequests.stopCrawl(id);
  return makeHTTPRequest(request, {
    onError({ error }) {
      toast(`Failed to remove the crawl - ${id}: ${error}`, {
        type: toast.TYPE.ERROR
      });
    },
    async onResponse({ dispatch, response }) {
      const json = await response.json();
      if (!response.ok) {
        toast(
          `Failed to stop the crawl - ${id}: Details 
        ${json.detail}`,
          {
            type: toast.TYPE.ERROR
          }
        );
        return;
      }
      return {
        type: ActionTypes.stop,
        payload: { id }
      };
    }
  });
}

export function removeCrawl(id) {
  const request = EndpointRequests.removeCrawl(id);
  return makeHTTPRequest(request, {
    onError({ error }) {
      toast(`Failed to remove the crawl - ${id}: ${error}`, {
        type: toast.TYPE.ERROR
      });
    },
    async onResponse({ dispatch, response }) {
      const json = await response.json();
      if (!response.ok) {
        toast(
          `Failed to remove the crawl - ${id}: Details 
        ${json.detail}`,
          {
            type: toast.TYPE.ERROR
          }
        );
        return;
      }
      return {
        type: ActionTypes.deleteCrawl,
        payload: { id }
      };
    }
  });
}

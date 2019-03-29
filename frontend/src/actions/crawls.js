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
      return {
        type: ActionTypes.info,
        payload: await response.json()
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
      return {
        type: ActionTypes.create,
        payload: {
          id: json.id,
          ...body
        }
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
      console.log(json);
      return {
        type: ActionTypes.start,
        payload: {
          id,
          ...body
        }
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
      console.log(json);
      return {
        type: ActionTypes.deleteCrawl,
        payload: { id }
      };
    }
  });
}

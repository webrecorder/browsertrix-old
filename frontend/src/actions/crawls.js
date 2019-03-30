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
          `Failed to create the crawl - ${id}: Details 
        ${json.detail}`,
          {
            type: toast.TYPE.ERROR
          }
        );
        return;
      }
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
      console.log(json);
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
      console.log(json);
      return {
        type: ActionTypes.deleteCrawl,
        payload: { id }
      };
    }
  });
}

import { Crawls, HTTPRequests } from '../utils/keys';
import { FetchStates, makeRequestRequest } from '../utils/makeHTTPRequest';
import { EndPointRequests } from '../utils/endpoints';
import { toast } from 'react-toastify';

export function getAllCrawls(init = false) {
  const request = EndPointRequests.retrieveAllCrawls();
  return makeRequestRequest(request, {
    init: () => ({ type: HTTPRequests.make }),
    async responseOrError({ dispatch, response, error }) {
      if (error) {
        toast('Failed to retrieve info about all crawls', {
          type: toast.TYPE.ERROR
        });
        return {
          type: HTTPRequests.done,
          payload: {
            fetchState: FetchStates.error,
            error
          }
        };
      }
      return {
        type: init ? Crawls.gotAllInit : Crawls.gotAll,
        payload: await response.json()
      };
    }
  });
}

export function updateCrawlInfo(info) {
  return {
    type: Crawls.updateInfo,
    payload: info
  };
}

export function getCrawlInfo(id) {
  const request = EndPointRequests.crawlInfo(id);
  return makeRequestRequest(request, {
    init: () => ({ type: HTTPRequests.make }),
    async responseOrError({ dispatch, response, error }) {
      if (error) {
        toast(`Failed to retrieve the info for crawl ${id}`, {
          type: toast.TYPE.ERROR
        });
        return {
          type: Crawls.done,
          payload: {
            forAction: Crawls.info,
            id,
            fetchState: FetchStates.error,
            error
          }
        };
      }
      return {
        type: Crawls.info,
        payload: await response.json()
      };
    }
  });
}

export function createCrawl(newCrawl = {}) {
  const { scope = 'single-page', browsers = 2, tabs = 2, urls = [] } = newCrawl;
  const body = {
    crawlType: scope,
    numBrowsers: browsers,
    numTabs: tabs,
    seedURLs: urls
  };
  const request = EndPointRequests.createNewCrawl(body);
  return makeRequestRequest(request, {
    init: () => ({ type: HTTPRequests.make }),
    async responseOrError({ dispatch, response, error }) {
      if (error) {
        toast(`Failed to create the crawl ${error}`, {
          type: toast.TYPE.ERROR
        });
        return {
          type: HTTPRequests.done,
          payload: {
            fetchState: FetchStates.error,
            error
          }
        };
      }
      const json = await response.json();
      return {
        type: Crawls.create,
        payload: {
          id: json.id,
          ...body
        }
      };
    }
  });
}

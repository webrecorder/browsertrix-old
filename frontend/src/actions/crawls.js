import { Crawls, HTTPRequests } from '../utils/keys';
import { FetchStates, makeRequestRequest } from '../utils/makeHTTPRequest';
import { EndPointRequests } from '../utils/endpoints';

export function getAllCrawls() {
  const request = EndPointRequests.retrieveAllCrawls();
  return makeRequestRequest(request, {
    init: () => ({
      type: HTTPRequests.make,
      payload: {
        fetchState: FetchStates.inflight
      }
    }),
    async responseOrError({ dispatch, response, error }) {
      if (error) {
        return {
          type: HTTPRequests.done,
          payload: {
            fetchState: FetchStates.error,
            error
          }
        };
      }
      return {
        type: Crawls.gotAll,
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
  const { scope = 'single-page', browsers = 2, tabs = 2 } = newCrawl;
  const body = {
    scope_type: scope,
    num_browsers: browsers,
    num_tabs: tabs
  };
  const request = EndPointRequests.createNewCrawl(body);
  return makeRequestRequest(request, {
    init: () => ({ type: HTTPRequests.make }),
    async responseOrError({ dispatch, response, error }) {
      if (error) {
        return {
          forAction: Crawls.create,
          type: HTTPRequests.done,
          payload: {
            fetchState: FetchStates.error,
            error
          }
        };
      }
      const { id } = await response.json();
      Promise.resolve().then(() => {
        dispatch(getCrawlInfo(id));
      });
      return {
        type: Crawls.create,
        payload: {
          id,
          ...body
        }
      };
    }
  });
}

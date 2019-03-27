export const Crawls = {
  getAll: 'CRAWL_GET_ALL',
  gotAll: 'CRAWL_GOT_ALL',
  gotAllInit: 'CRAWL_GOT_ALL',
  create: 'CRAWL_CREATE',
  urls: 'CRAWL_GET_URLS',
  addURLs: 'CRAWL_ADD_URLS',
  info: 'CRAWL_GET_INFO',
  stop: 'CRAWL_STOP',
  isDone: 'CRAWL_IS_DONE',
  deleteCrawl: 'CRAWL_DELETE',
  updateInfo: 'CRAWL_UPDATE_INFO',
  _fetched: 'ALL_CRAWLS_INIT'
};

const makeHTTPRequest = 'HTTP_REQUEST_MAKE';
const httpRequestDone = 'HTTP_REQUEST_DONE';

export const HTTPRequests = {
  make: makeHTTPRequest,
  done: httpRequestDone,
  actions: new Set([makeHTTPRequest, httpRequestDone])
};

export const HTTPRequestAction = 'MAKE_HTTP_REQUEST';

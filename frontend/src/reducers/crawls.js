import { List, Map, Record } from 'immutable';
import { ActionTypes } from '../actions/crawls';

export class CrawlRecord extends Record({
  crawl_type: '',
  num_browsers: 0,
  num_tabs: 0,
  depth: 0,
  seed_urls: [],
  id: '',
  browser: '',
  running: false,
  status: ''
}) {
  updateURLS(urls) {
    return this.updateIn(['seed_urls'], seed_urls => seed_urls.concat(urls));
  }
}

export function crawlsFetchedReducer(state = false, action) {
  if (action.type === ActionTypes.gotAllInit) {
    return true;
  }
  return state;
}

export function crawlIds(state = List([]), { type, payload, meta }) {
  switch (type) {
    case ActionTypes.deleteCrawl:
      const idx = state.indexOf(payload.id);
      return state.delete(idx);
    case ActionTypes.gotAllInit:
    case ActionTypes.gotAll:
      return state.withMutations(mutable => {
        const { crawls } = payload;
        for (let i = 0; i < crawls.length; i++) {
          mutable.push(crawls[i].id);
        }
        return mutable;
      });
    case ActionTypes.create:
      return state.push(payload.id);
  }
  return state;
}

export function crawlsReducer(state = Map({}), { type, payload, meta }) {
  switch (type) {
    case ActionTypes.deleteCrawl:
      return state.delete(payload.id);
    case ActionTypes.addURLs:
      if (!state.has(payload.id)) return state;
      return state.updateIn([id], crawl => crawl.updateURLS(payload.urls));
    case ActionTypes.gotAllInit:
    case ActionTypes.gotAll:
      return state.withMutations(mutable => {
        const { crawls } = payload;
        for (let i = 0; i < crawls.length; i++) {
          const rawCrawl = crawls[i];
          const crec = mutable.get(rawCrawl.id);
          if (!crec) {
            mutable.set(rawCrawl.id, new CrawlRecord(rawCrawl));
          } else {
            mutable.set(rawCrawl.id, crec.merge(rawCrawl));
          }
        }
        return mutable;
      });
    case ActionTypes.create:
      payload.seed_urls = List(payload.seed_urls);
      return state.set(payload.id, new CrawlRecord(payload));
    case ActionTypes.info:
      if (!state.has(payload.id)) return state;
      return state.updateIn([payload.id], crawl => crawl.merge(payload));
  }
  return state;
}

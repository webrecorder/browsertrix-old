import { List, Map, Record } from 'immutable';
import { ActionTypes } from '../actions/crawls';

export class CrawlRecord extends Record({
  crawl_type: '',
  num_browsers: 0,
  num_tabs: 0,
  depth: 0,
  scopes: [],
  queue: [],
  pending: [],
  seen: [],
  id: '',
  browser: 'chrome:67',
  browsers: [],
  browsersDone: [],
  running: false,
  status: 'new',
  behavior_run_time: 60
}) {
  updateBrowsers(browsers) {
    const existingBrowsers = this.browsers;
    return this.set('browsers', existingBrowsers.concat(browsers));
  }

  crawlRunning(browsers) {
    const existingBrowsers = this.browsers;
    return this.merge({
      browsers: existingBrowsers.concat(browsers),
      running: true
    });
  }

  startCrawlConfig() {
    return {
      browser: this.browser,
      behavior_run_time: this.behavior_run_time,
      headless: this.headless
    };
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
    case ActionTypes.start:
      if (!state.has(payload.id)) return state;
      return state.updateIn([payload.id], crawl =>
        crawl.crawlRunning(payload.browsers)
      );
    case ActionTypes.deleteCrawl:
      return state.delete(payload.id);
    case ActionTypes.addURLs:
      if (!state.has(payload.id)) return state;
      return state.updateIn([payload.id], crawl => crawl.merge(payload));
    case ActionTypes.gotAllInit:
    case ActionTypes.gotAll:
      return state.withMutations(mutable => {
        const { crawls } = payload;
        for (let i = 0; i < crawls.length; i++) {
          const rawCrawl = crawls[i];
          const crec = mutable.get(rawCrawl.id);
          console.log(rawCrawl);
          if (!crec) {
            mutable.set(rawCrawl.id, new CrawlRecord(rawCrawl));
          } else {
            mutable.set(rawCrawl.id, crec.mergeDeep(rawCrawl));
          }
        }
        return mutable;
      });
    case ActionTypes.create:
      return state.set(payload.id, new CrawlRecord(payload));
    case ActionTypes.updateURLInfo:
      if (!state.has(payload.id)) return state;
      return state.updateIn([payload.id], crawl => crawl.mergeDeep(payload));
    case ActionTypes.info:
      if (!state.has(payload.id)) return state;
      return state.updateIn([payload.id], crawl => crawl.mergeDeep(payload));
  }
  return state;
}

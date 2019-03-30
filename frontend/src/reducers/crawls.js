import { List, Map, Record } from 'immutable';
import { ActionTypes } from '../actions/crawls';

export const CrawlRecord = Record(
  {
    crawl_type: '',
    num_browsers: 0,
    num_tabs: 0,
    depth: 0,
    seed_urls: List([]),
    id: '',
    browsers: List([]),
    browsers_done: List([]),
    running: false,
    status: ''
  },
  'CrawlRecord'
);

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
    case ActionTypes.gotAllInit:
    case ActionTypes.gotAll:
      return state.withMutations(mutable => {
        const { crawls } = payload;
        for (let i = 0; i < crawls.length; i++) {
          const crawl = crawls[i];
          const crec = mutable.get(crawl.id);
          if (!crec) {
            mutable.set(crawl.id, CrawlRecord(crawl));
          } else {
            mutable.set(crawl.id, crec.merge(crawl));
          }
        }
        return mutable;
      });
    case ActionTypes.create:
    case ActionTypes.info:
      return state.update(payload.id, null, crawl =>
        crawl == null ? CrawlRecord(payload) : crawl.merge(payload)
      );
  }
  return state;
}

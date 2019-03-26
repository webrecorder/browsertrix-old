import { List, Map, Record } from 'immutable';
import { Crawls } from '../utils/keys';

const Crawl = Record(
  {
    scope_type: ' ',
    num_browsers: 0,
    num_tabs: 0,
    id: '',
    browsers: List([]),
    browsers_done: List([]),
    running: false
  },
  'Crawl'
);

export default function crawlsReducer(state = Map({}), { type, payload }) {
  switch (type) {
    case Crawls.gotAll: {
      return state.withMutations(mutable => {
        for (let i = 0; i < payload.length; i++) {
          const crawl = payload[i];
          mutable.set(crawl.id, Crawl(crawl));
        }
      });
    }
    case Crawls.create: {
      if (state.has(payload.id)) return state;
      return state.set(payload.id, Crawl(payload));
    }
    case Crawls.info: {
      return state.update(payload.id, null, crawl =>
        crawl == null ? Crawl(payload) : crawl.merge(payload)
      );
    }
    default:
      return state;
  }
}

import { List, Map, Record } from 'immutable';
import { Crawls } from '../utils/keys';

export const Crawl = Record(
  {
    crawl_type: '',
    num_browsers: 0,
    num_tabs: 0,
    id: '',
    browsers: List([]),
    browsers_done: List([]),
    running: false,
    status: ''
  },
  'Crawl'
);

export function crawlsFetchedReducer(state = false, action) {
  if (action.type === Crawls.gotAllInit) {
    return true;
  }
  return state;
}

export default function crawlsReducer(
  state = Map({}),
  { type, payload, meta }
) {
  switch (type) {
    case Crawls.gotAllInit:
    case Crawls.gotAll:
      return state.withMutations(mutable => {
        const { crawls } = payload;
        for (let i = 0; i < crawls.length; i++) {
          const crawl = crawls[i];
          const crec = mutable.get(crawl.id);
          if (!crec) {
            mutable.set(crawl.id, Crawl(crawl));
          } else {
            mutable.set(crawl.id, crec.merge(crawl));
          }
        }
        return mutable;
      });
    case Crawls.create:
    case Crawls.info:
      return state.update(payload.id, null, crawl =>
        crawl == null ? Crawl(payload) : crawl.merge(payload)
      );
    default:
      return state;
  }
}

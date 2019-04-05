import { combineReducers } from 'redux-immutable';
import { reducer as reduxFormReducer } from 'redux-form/immutable';
import { crawlIds, crawlsFetchedReducer, crawlsReducer } from './crawls';

const rootReducer = combineReducers({
  crawlIds,
  crawls: crawlsReducer,
  crawlsFetched: crawlsFetchedReducer,
  form: reduxFormReducer
});

export default rootReducer;

import { combineReducers } from 'redux-immutable';
import { combineReducers as oCR } from 'redux';
import { reducer as reduxFormReducer } from 'redux-form/immutable';
import { crawlsReducer, crawlsFetchedReducer, crawlIds } from './crawls';

const rootReducer = oCR({
  crawlIds,
  crawls: crawlsReducer,
  crawlsFetched: crawlsFetchedReducer,
  form: reduxFormReducer
});

export default rootReducer;

import { combineReducers } from 'redux-immutable';
import { reducer as reduxFormReducer } from 'redux-form/immutable';
import crawls, { crawlsFetchedReducer } from './crawls';

const rootReducer = combineReducers({
  crawls,
  crawlsFetched: crawlsFetchedReducer,
  form: reduxFormReducer
});

export default rootReducer;

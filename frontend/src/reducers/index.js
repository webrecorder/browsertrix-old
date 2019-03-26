import { combineReducers } from 'redux-immutable';
import crawls from './crawls';

const rootReducer = combineReducers({ crawls });

export default rootReducer;

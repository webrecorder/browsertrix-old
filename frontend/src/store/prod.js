import { createStore } from 'redux';
import rootReducer from '../reducers';
import middleWare from './middleware';
import { Map } from 'immutable';

export default function configureStore() {
  return createStore(rootReducer, Map({}), middleWare);
}

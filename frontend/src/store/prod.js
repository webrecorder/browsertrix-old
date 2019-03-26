import { createStore } from 'redux';
import { Map } from 'immutable/dist/immutable.es';
import rootReducer from '../reducers';
import middleWare from './middleware';

export default function configureStore() {
  return createStore(rootReducer, Map({}), middleWare);
}

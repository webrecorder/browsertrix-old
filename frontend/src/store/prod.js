import { createStore } from 'redux';
import rootReducer from '../reducers';
import middleWare from './middleware';

export default function configureStore() {
  return createStore(rootReducer, {}, middleWare);
}

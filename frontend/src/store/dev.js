import { createStore } from 'redux';
import { composeWithDevTools } from 'redux-devtools-extension';
import Immutable from 'immutable';
import * as actionCreators from '../actions';
import rootReducer from '../reducers';
import middleWare from './middleware';

const composer = composeWithDevTools({
  actionCreators,
  serialize: {
    immutable: Immutable
  }
});

export default function configureStore() {
  return createStore(rootReducer, Immutable.Map({}), composer(middleWare));
}

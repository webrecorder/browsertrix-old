import React from 'react';
import { Provider } from 'react-redux';
import * as PropTypes from 'prop-types';
import createStore from './store';

export default function WrapWithProvider({ element }) {
  const store = createStore();
  return <Provider store={store}>{element}</Provider>;
};

WrapWithProvider.propTypes = {
  element: PropTypes.element.isRequired
};

import './styles/global.scss';
import './utils/rhlConfig';
import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { HashRouter } from 'react-router-dom';
import Icons from 'uikit/dist/js/uikit-icons';
import Uikit from 'uikit';
import createStore from './store';
import App from './containers/App';

window.Uikit = Uikit;
Uikit.use(Icons);
const store = createStore();

ReactDOM.render(
  <Provider store={store}>
    <HashRouter>
      <App />
    </HashRouter>
  </Provider>,
  document.getElementById('mount')
);

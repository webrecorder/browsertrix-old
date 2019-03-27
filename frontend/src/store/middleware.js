import { applyMiddleware } from 'redux';
import thunkMiddleware from 'redux-thunk';
import promiseMiddleware from 'redux-promise';
import { HTTPRequests } from '../utils/keys';

function getRequestTracker() {
  if (typeof window !== 'undefined') {
    if (window.__requestTrack == null) {
      window.__requestTrack = {};
    }
    return window.__requestTrack;
  }
  return {};
}

function isURLTracked(url) {
  const requests = getRequestTracker();
  return requests[url] != null;
}

function trackURL(url) {
  const requests = getRequestTracker();
  return requests[url] != null;
}

function untrackURL(url) {
  const requests = getRequestTracker();
  delete requests[url];
}

function createRequestMiddleware() {
  return store => next => action => {
    if (!HTTPRequests.actions.has(action.type)) return next(action);
    if (action.meta && action.meta.httpRequest) {
      if (!action.meta.httpRequest.done) {
        if (isURLTracked(action.meta.httpRequest.url)) return;
        trackURL(action.meta.httpRequest.url);
      } else {
        untrackURL(action.meta.httpRequest.url);
      }
    }
    return next(action);
  };
}

export default applyMiddleware(
  thunkMiddleware,
  createRequestMiddleware(),
  promiseMiddleware
);

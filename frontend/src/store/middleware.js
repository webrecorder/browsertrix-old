import { applyMiddleware } from 'redux';
import thunkMiddleware from 'redux-thunk';
import promiseMiddleware from 'redux-promise';
import { FetchStates } from '../actions/httpRequests';

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
  requests[url] = true;
}

function untrackURL(url) {
  const requests = getRequestTracker();
  delete requests[url];
}

function createRequestMiddleware() {
  return store => next => action => {
    if (action.meta && action.meta.httpRequest) {
      const httpRequest = action.meta.httpRequest;
      switch (httpRequest.state) {
        case FetchStates.preflight:
          if (isURLTracked(action.meta.httpRequest.url)) return;
          trackURL(action.meta.httpRequest.url);
          break;
        case FetchStates.done:
        case FetchStates.error:
          untrackURL(action.meta.httpRequest.url);
          break;
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

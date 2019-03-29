export const HTTPRequestAction = Symbol('http-request-maker');

export const FetchStates = {
  preflight: Symbol('http-request-preflight'),
  inflight: Symbol('http-request-inflight'),
  done: Symbol('http-request-done'),
  error: Symbol('http-request-errored')
};

export function requestErrorAction({ error, payload }) {
  return {
    type: HTTPRequestAction,
    payload: Object.assign({ error }, payload)
  };
}

/**
 * @typedef {Object} MakeHTTPRequestInit
 * @property {function ({dispatch: Function, response: Response}): *} onResponse
 * @property {function ({dispatch: Function, error: Error}): *} onError
 */

function requestComplete(nextAction, wasError, url) {
  nextAction.meta = nextAction.meta || {};
  nextAction.meta.httpRequest = {
    url,
    state: wasError ? FetchStates.error : FetchStates.done
  };
  return nextAction;
}

/**
 *
 * @param {Request} request
 * @param {MakeHTTPRequestInit} init
 */
export function makeHTTPRequest(request, { onResponse, onError }) {
  return dispatch => {
    const init = {
      type: HTTPRequestAction,
      meta: {
        httpRequest: {
          state: FetchStates.preflight,
          url: request.url
        }
      }
    };
    if (!dispatch(init)) return; // no op, this is a duplicate request
    let wasError = false;
    dispatch(
      fetch(request)
        .then(response => onResponse({ dispatch, response }))
        .catch(error => {
          wasError = true;
          return onError({ dispatch, error });
        })
        .then(requestFinished =>
          requestComplete(
            requestFinished || { type: HTTPRequestAction },
            wasError,
            request.url
          )
        )
    );
  };
}

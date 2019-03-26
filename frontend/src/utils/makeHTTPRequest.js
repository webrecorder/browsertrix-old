/**
 *
 * @param {Request} request
 * @param {{init: function(): Object, responseOrError: function ({response?: Response, error?: Error}): Promise<*>}} actions
 */
export function makeRequestRequest(request, actions) {
  return dispatch => {
    const initAction = { ...actions.init() };
    initAction.meta = initAction.meta || {};
    initAction.meta.httpRequest = { url: request.url, done: false };
    if (!dispatch(initAction)) {
      return; // bail out here if the middleware cancelled the dispatch
    }
    dispatch(
      fetch(request)
        .then(response => actions.responseOrError({ dispatch, response }))
        .catch(error => actions.responseOrError({ dispatch, error }))
        .then(successAction => {
          successAction.meta = successAction.meta || {};
          successAction.meta.httpRequest = { url: request.url, done: true };
          return successAction;
        })
    );
  };
}

export const FetchStates = {
  inflight: Symbol('http-request-inflight'),
  done: Symbol('http-request-done'),
  error: Symbol('http-request-errored'),
  notMade: Symbol('http-request-not-made')
};

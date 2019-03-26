export const RequestStates = {
  begin: Symbol('WR-HTTP-REQUEST-BEGIN'),
  inflight: Symbol('WR-HTTP-REQUEST-INFLIGHT'),
  done: Symbol('WR-HTTP-REQUEST-DONE'),
};

export const HTTPRequestAT = 'MAKE_HTTP_REQUEST';
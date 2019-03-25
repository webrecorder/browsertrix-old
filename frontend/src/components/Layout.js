import 'bootstrap/dist/css/bootstrap.min.css';
import React, { Fragment } from 'react';

export default function Layout({ location, children }) {
  return (
    <Fragment>
      <div className="container">{children}</div>
    </Fragment>
  );
}

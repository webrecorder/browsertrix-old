import '../styles/global.scss';
import React, { Fragment } from 'react';
import * as PropTypes from 'prop-types';
import { Container } from 'reactstrap';
import Header from './Header';

export default function Layout({ location, children, fluid }) {
  return (
    <Fragment>
      <Header location={location} />
      <Container fluid={fluid}>{children}</Container>
    </Fragment>
  );
}

Layout.propTypes = {
  fluid: PropTypes.bool
};

Layout.defaultProps = {
  fluid: false
};

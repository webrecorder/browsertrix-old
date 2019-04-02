import React from 'react';
import * as PropTypes from 'prop-types';
import { Link } from 'react-router-dom';

export default function HeaderLink({ to, location, children, button }) {
  if (button) {
    return (
      <Link className='uk-button uk-button-default' to={to}>
        {children}
      </Link>
    );
  }
  return (
    <li className={to === location.pathname ? 'uk-active' : undefined}>
      <Link to={to}>{children}</Link>
    </li>
  );
}

HeaderLink.propTypes = {
  button: PropTypes.bool,
  to: PropTypes.string.isRequired
};

HeaderLink.defaultProps = {
  button: false
};

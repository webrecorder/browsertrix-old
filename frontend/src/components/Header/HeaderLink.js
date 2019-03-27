import React from 'react';
import NavItem  from 'react-bootstrap/NavItem';
import { Link } from 'gatsby';

export default function HeaderLink({ to, location, children }) {
  return (
    <NavItem>
      <Link to={to} className='nav-link' activeClassName={'active'}>
        {children}
      </Link>
    </NavItem>
  );
}

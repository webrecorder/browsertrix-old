import React from 'react';
import { NavItem } from 'reactstrap';
import { Link } from 'gatsby';

export default function HeaderLink({ to, location, children }) {
  return (
    <NavItem active={location.pathname === to}>
      <Link to={to} className='nav-link' activeClassName={'active'}>
        {children}
      </Link>
    </NavItem>
  );
}

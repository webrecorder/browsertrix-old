import React from 'react';
import { Link } from 'react-router-dom';

export default function HeaderLink({ to, location, children }) {
  return (
    <li className={to === location.pathname ? 'uk-active' : undefined}>
      <Link to={to}>{children}</Link>
    </li>
  );
}

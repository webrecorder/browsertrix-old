import React from 'react';
import { Container, Nav, Navbar } from 'reactstrap';
import HeaderLink from './HeaderLink';

export default function Header({ location }) {
  return (
    <Container fluid>
      <Navbar className='navbar-expand-lg navbar-dark bg-dark' dark>
        <Nav navbar>
          <HeaderLink to='/' location={location}>
            Create Crawl
          </HeaderLink>
          <HeaderLink to='/crawlInfo' location={location}>
            Crawl Info
          </HeaderLink>
        </Nav>
      </Navbar>
    </Container>
  );
}

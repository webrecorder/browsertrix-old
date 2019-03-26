import React from 'react';
import { Container, Nav, Navbar } from 'react-bootstrap';
import HeaderLink from './HeaderLink';

export default function Header({ location }) {
  return (
    <Container fluid>
      <Navbar className='navbar-expand-lg navbar-dark bg-dark' variant='dark'>
        <Nav navbar>
          <HeaderLink to='/' location={location}>
            Crawls
          </HeaderLink>
          <HeaderLink to='/crawlInfo' location={location}>
            Crawl Info
          </HeaderLink>
        </Nav>
      </Navbar>
    </Container>
  );
}

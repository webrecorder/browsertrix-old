import React from 'react';
import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import HeaderLink from './HeaderLink';

export default function Header({ location }) {
  return (
    <Container>
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

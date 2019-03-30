import React from 'react';
import PropTypes from 'prop-types';
import { withRouter } from 'react-router-dom';
import HeaderLink from './HeaderLink';

function Header({ location }) {
  return (
    <div className='uk-container uk-container-small'>
      <nav className='uk-navbar-container' data-uk-navbar='' data-uk-sticky=''>
        <div className='uk-navbar-center'>
          <ul className='uk-navbar-nav'>
            <HeaderLink location={location} to='/'>
              Crawls
            </HeaderLink>
            <HeaderLink location={location} to='/createCrawl'>
              Create Crawl
            </HeaderLink>
          </ul>
        </div>
      </nav>
    </div>
  );
}

Header.propTypes = {
  match: PropTypes.object.isRequired,
  location: PropTypes.object.isRequired,
  history: PropTypes.object.isRequired
};

export default withRouter(Header);

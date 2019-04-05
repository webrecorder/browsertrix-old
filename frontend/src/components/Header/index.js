import React from 'react';
import * as PropTypes from 'prop-types';
import { withRouter } from 'react-router-dom';
import HeaderLink from './HeaderLink';

function Header(props) {
  return (
    <div className='uk-container uk-container-small'>
      <nav className='uk-navbar-container' data-uk-navbar='' data-uk-sticky=''>
        <div className='uk-navbar-center'>
          <ul className='uk-navbar-nav'>
            <HeaderLink location={props.location} to='/'>
              Crawl Select
            </HeaderLink>
          </ul>
        </div>
        <div className='uk-navbar-right'>
          <div className='uk-navbar-item'>
            <HeaderLink button location={location} to='/createCrawl'>
              Create Crawl
            </HeaderLink>
          </div>
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

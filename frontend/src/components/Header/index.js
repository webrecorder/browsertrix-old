import React from 'react';
import * as PropTypes from 'prop-types';
import { withRouter } from 'react-router-dom';
import HeaderLink from './HeaderLink';

function Header(props) {
  return (
    <div className='uk-container'>
      <img className='logo' src="/static/browsertrix-logo.svg"/>
      <nav className='uk-navbar-container' uk-navbar="true">
        <div className="uk-navbar-left">
        <ul className="uk-nav uk-tab uk-flex-left">
            <HeaderLink location={props.location} to='/'>
              View All Crawls
            </HeaderLink>
            <HeaderLink location={props.location} to='/createCrawl'>
              Create New Crawl
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

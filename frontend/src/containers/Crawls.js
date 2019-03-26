import React, { Component } from 'react';
import { connect } from 'react-redux';
import * as PropTypes from 'prop-types';
import { Map } from 'immutable';
import CreateOrFetchAllCrawls from '../components/CreateOrFetchAllCrawls';

class Crawls extends Component {
  render() {
    let component;
    if (this.props.crawls.size === 0) {
      component = <CreateOrFetchAllCrawls numCrawls={this.props.crawls.size} />;
    }
    return component;
  }
}

Crawls.propTypes = {
  crawls: PropTypes.instanceOf(Map).isRequired
};

function mapStateToProps(state, ownProps) {
  return {
    crawls: state.get('crawls')
  };
}

const ConnectedCrawls = connect(mapStateToProps)(Crawls);

export default ConnectedCrawls;

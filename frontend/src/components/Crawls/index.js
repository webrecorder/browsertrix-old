import React, { Component } from 'react';
import { connect } from 'react-redux';
import * as PropTypes from 'prop-types';
import { List, Map } from 'immutable';
import { getAllCrawls, removeCrawl } from '../../actions/crawls';
import LoadingCrawls from './LoadingCrawls';
import SelectCrawl from './SelectCrawl';
import CrawlCreator from '../CrawlCreator';

class Crawls extends Component {
  static propTypes = {
    crawls: PropTypes.instanceOf(Map).isRequired,
    crawlsFetched: PropTypes.bool.isRequired,
    init: PropTypes.func.isRequired,
    removeCrawl: PropTypes.func.isRequired
  };

  componentDidMount() {
    if (!this.props.crawlsFetched) {
      this.props.init();
    }
  }

  render() {
    let component;
    if (!this.props.crawlsFetched) {
      component = <LoadingCrawls />;
    } else if (this.props.crawls.size === 0) {
      component = <CrawlCreator message={'There are no pre-existing crawls'} />;
    } else {
      component = (
        <SelectCrawl
          removeCrawl={this.props.removeCrawl}
          crawls={this.props.crawls}
        />
      );
    }
    return <div className='uk-container'>{component}</div>;
  }
}

const mapDispatchToProps = (dispatch, ownProps) => ({
  init() {
    dispatch(getAllCrawls(true));
  },
  removeCrawl(id) {
    dispatch(removeCrawl(id));
  }
});

const mapStateToProps = (state, ownProps) => ({
  crawls: state.get('crawls'),
  crawlsFetched: state.get('crawlsFetched')
});

const ConnectedCrawls = connect(
  mapStateToProps,
  mapDispatchToProps
)(Crawls);

export default ConnectedCrawls;

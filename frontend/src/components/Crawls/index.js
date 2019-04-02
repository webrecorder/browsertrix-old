import React, { Component } from 'react';
import { connect } from 'react-redux';
import * as PropTypes from 'prop-types';
import { List } from 'immutable';
import { getAllCrawls } from '../../actions/crawls';
import LoadingCrawls from './LoadingCrawls';
import SelectCrawl from './SelectCrawl';
import CrawlCreator from '../CrawlCreator';

class Crawls extends Component {
  static propTypes = {
    crawlIds: PropTypes.instanceOf(List).isRequired,
    crawlsFetched: PropTypes.bool.isRequired,
    init: PropTypes.func.isRequired
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
    } else if (this.props.crawlIds.size === 0) {
      component = (
        <CrawlCreator message={'There are no pre-existing crawls!'} />
      );
    } else {
      component = <SelectCrawl crawlIds={this.props.crawlIds} />;
    }
    return <div className='uk-container'>{component}</div>;
  }
}

const mapDispatchToProps = (dispatch, ownProps) => ({
  init() {
    dispatch(getAllCrawls(true));
  }
});

const mapStateToProps = (state, ownProps) => ({
  crawlIds: state.get('crawlIds'),
  crawlsFetched: state.get('crawlsFetched')
});

const ConnectedCrawls = connect(
  mapStateToProps,
  mapDispatchToProps
)(Crawls);

export default ConnectedCrawls;

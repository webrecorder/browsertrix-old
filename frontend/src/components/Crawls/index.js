import React, { Component } from 'react';
import { connect } from 'react-redux';
import * as PropTypes from 'prop-types';
import { Map } from 'immutable';
import {
  createCrawl,
  getAllCrawls,
  getCrawlInfo,
  removeCrawl
} from '../../actions/crawls';
import LoadingCrawls from './LoadingCrawls';
import CrawlCreator from '../CrawlCreator';
import ViewAllCrawls from './ViewAllCrawls';

class Crawls extends Component {
  static propTypes = {
    crawls: PropTypes.instanceOf(Map).isRequired,
    crawlsFetched: PropTypes.bool.isRequired,
    init: PropTypes.func.isRequired,
    crawlActions: PropTypes.shape({
      createCrawl: PropTypes.func.isRequired,
      getAllCrawls: PropTypes.func.isRequired,
      getCrawlInfo: PropTypes.func.isRequired,
      removeCrawl: PropTypes.func.isRequired
    })
  };

  componentDidMount() {
    if (!this.props.crawls.get('fetched')) {
      this.props.init();
    }
  }

  // shouldComponentUpdate(nextProps, nextState, nextContext) {
  //   return (
  //     this.props.crawlsFetched !== nextProps.crawlsFetched ||
  //     this.props.crawls !== nextProps.crawls
  //   );
  // }

  createCrawl = values => {
    this.props.crawlActions.createCrawl(values.toJS());
  };

  updateCrawlInfo = id => {
    this.props.crawlActions.getCrawlInfo(id);
  };

  removeCrawl = id => {
    this.props.crawlActions.removeCrawl(id);
  };

  render() {
    if (!this.props.crawlsFetched) {
      return <LoadingCrawls />;
    } else if (this.props.crawls.size === 0) {
      return (
        <>
          <h1 className='display-4'>There were no pre-existing crawls</h1>
          <CrawlCreator onSubmit={this.createCrawl} />
        </>
      );
    }
    return (
      <>
        <ViewAllCrawls
          crawls={this.props.crawls}
          crawlActions={this.props.crawlActions}
        />
      </>
    );
  }
}

const mapDispatchToProps = (dispatch, ownProps) => ({
  init() {
    dispatch(getAllCrawls(true));
  },
  crawlActions: {
    createCrawl(crawlInfo) {
      dispatch(createCrawl(crawlInfo));
    },
    getAllCrawls() {
      dispatch(getAllCrawls());
    },
    getCrawlInfo(id) {
      dispatch(getCrawlInfo(id));
    },
    removeCrawl(id) {
      dispatch(removeCrawl(id));
    }
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

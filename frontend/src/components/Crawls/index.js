import React, { PureComponent } from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import * as PropTypes from 'prop-types';
import { Map } from 'immutable';
import * as crawlActions from '../../actions/crawls';
import LoadingCrawls from './LoadingCrawls';
import CrawlCreator from '../CrawlCreator';
import ViewAllCrawls from './ViewAllCrawls';

class Crawls extends PureComponent {
  componentDidMount() {
    if (!this.props.crawls.get('fetched')) {
      this.props.init();
    }
  }

  createCrawl = values => {
    this.props.createCrawl(values.toJS());
  };

  render() {
    if (!this.props.crawlsFetched) {
      return <LoadingCrawls />;
    } else if (this.props.crawls.size === 1) {
      return (
        <>
          <h1 className='display-4'>There were no pre-existing crawls</h1>
          <CrawlCreator onSubmit={this.createCrawl} />
        </>
      );
    }
    return (
      <ViewAllCrawls
        crawls={this.props.crawls}
        crawlActions={this.props.crawlActions}
      />
    );
  }
}

Crawls.propTypes = {
  crawls: PropTypes.instanceOf(Map).isRequired,
  crawlsFetched: PropTypes.bool.isRequired,
  init: PropTypes.func.isRequired,
  crawlActions: PropTypes.object.isRequired,
};

const mapDispatchToProps = (dispatch, ownProps) => ({
  init() {
    dispatch(crawlActions.getAllCrawls(true));
  },
  crawlActions: bindActionCreators(crawlActions, dispatch)
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

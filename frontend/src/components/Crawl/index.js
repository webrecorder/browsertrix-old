import React, { Component } from 'react';
import * as PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Redirect } from 'react-router-dom';
import { CrawlRecord } from '../../reducers/crawls';
import {
  getCrawlInfo,
  removeCrawl,
  startCrawl,
  stopCrawl
} from '../../actions';
import Info from './Info';
import Control from './Control';

class Crawl extends Component {
  static propTypes = {
    location: PropTypes.object.isRequired,
    match: PropTypes.object.isRequired,
    crawl: PropTypes.instanceOf(CrawlRecord),
    getCrawlInfo: PropTypes.func.isRequired,
    startCrawl: PropTypes.func.isRequired,
    stopCrawl: PropTypes.func.isRequired,
    removeCrawl: PropTypes.func.isRequired
  };

  render() {
    if (this.props.crawl == null) return <Redirect to='/' />;
    const {
      crawl,
      getCrawlInfo,
      removeCrawl,
      stopCrawl,
      startCrawl
    } = this.props;
    return (
      <div className='uk-container uk-container-small'>
        <div
          className='uk-grid uk-flex-center uk-margin-bottom'
          data-uk-grid=''
        >
          <div>
            <h1>Crawl Id - {crawl.id}</h1>
          </div>
          <div>
            <span className='uk-label uk-label-info'>
              {crawl.running ? '' : 'Not'} Running
            </span>
          </div>
        </div>
        <Control
          crawl={crawl}
          getCrawlInfo={getCrawlInfo}
          removeCrawl={removeCrawl}
          startCrawl={startCrawl}
          stopCrawl={stopCrawl}
        />
        <Info crawl={crawl} />
      </div>
    );
  }
}

const mapStateToProps = (state, ownProps) => ({
  crawl: state.get('crawls').get(ownProps.match.params.crawlid)
});

const mapDispatchToProps = (dispatch, ownProps) => ({
  getCrawlInfo() {
    dispatch(getCrawlInfo(ownProps.match.params.crawlid));
  },
  startCrawl(config) {
    dispatch(startCrawl(ownProps.match.params.crawlid, config));
  },
  stopCrawl() {
    dispatch(stopCrawl(ownProps.match.params.crawlid));
  },
  removeCrawl() {
    dispatch(removeCrawl(ownProps.match.params.crawlid));
  }
});

const ConnectedCrawl = connect(
  mapStateToProps,
  mapDispatchToProps
)(Crawl);

export default ConnectedCrawl;

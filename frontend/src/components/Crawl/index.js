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
    if (this.props.crawl == null) return <Redirect to={'/'} />;
    const {
      crawl,
      getCrawlInfo,
      removeCrawl,
      startCrawl,
      stopCrawl
    } = this.props;
    return (
      <>
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
          <table className='uk-table uk-table-middle'>
            <thead>
              <tr>
                <th>Type</th>
                <th>Status</th>
                <th>Num Browsers</th>
                <th>Num Tabs</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>{crawl.crawl_type}</td>
                <td>{crawl.status || 'new'}</td>
                <td>{crawl.num_browsers}</td>
                <td>{crawl.num_tabs}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div className='uk-container uk-container-small'>
          <div
            className='uk-grid uk-flex-center  uk-margin-top'
            data-uk-grid=''
          >
            <div>
              <button
                onClick={startCrawl}
                disabled={crawl.running || crawl.seed_urls.length === 0}
                className='uk-button uk-button-default'
              >
                Start Crawl
              </button>
            </div>
            <div>
              <button
                onClick={stopCrawl}
                disabled={!crawl.running}
                className='uk-button uk-button-default'
              >
                Stop Crawl
              </button>
            </div>
            <div>
              <button
                className='uk-button uk-button-default'
                onClick={getCrawlInfo}
              >
                Update
              </button>
            </div>
            <div>
              <button
                className='uk-button uk-button-default'
                onClick={removeCrawl}
              >
                Remove
              </button>
            </div>
          </div>
        </div>
      </>
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
  startCrawl() {
    dispatch(startCrawl(ownProps.match.params.crawlid));
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

import React from 'react';
import * as PropTypes from 'prop-types';
import { CrawlRecord } from '../../reducers/crawls';
import { connect } from 'react-redux';
import {
  getCrawlInfo,
  removeCrawl,
  startCrawl,
  stopCrawl
} from '../../actions';

function Crawl({ crawl, getCrawlInfo, removeCrawl, startCrawl, stopCrawl }) {
  return (
    <li>
      <div className='uk-card uk-card-default uk-card-small'>
        <div className='uk-card-header'>
          <div className='uk-card-badge uk-label'>
            {crawl.running ? '' : 'Not'} Running
          </div>
          <h3 className='uk-card-title uk-margin-remove-bottom'>
            Crawl: {crawl.id}
          </h3>
        </div>
        <div className='uk-card-body'>
          <table className='uk-table'>
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
        <div className='uk-card-footer'>
          <a
            href='#'
            className='uk-button uk-button-text uk-margin-right'
            onClick={getCrawlInfo}
          >
            Update
          </a>
          <a
            href='#'
            className='uk-button uk-button-text uk-margin-right'
            onClick={removeCrawl}
          >
            Remove
          </a>
          <a
            href='#'
            onClick={startCrawl}
            className='uk-button uk-button-text uk-margin-right'
          >
            Start Crawl
          </a>
          <a
            href='#'
            onClick={stopCrawl}
            className='uk-button uk-button-text uk-margin-right'
          >
            Stop Crawl
          </a>
        </div>
      </div>
    </li>
  );
}

Crawl.propTypes = {
  crawlId: PropTypes.string.isRequired,
  crawl: PropTypes.instanceOf(CrawlRecord),
  getCrawlInfo: PropTypes.func.isRequired,
  startCrawl: PropTypes.func.isRequired,
  stopCrawl: PropTypes.func.isRequired,
  removeCrawl: PropTypes.func.isRequired
};

const mapStateToProps = (state, ownProps) => ({
  crawl: state.crawls.get(ownProps.crawlId)
});

const mapDispatchToProps = (dispatch, ownProps) => ({
  getCrawlInfo() {
    dispatch(getCrawlInfo(ownProps.crawlId));
  },
  startCrawl() {
    dispatch(startCrawl(ownProps.crawlId));
  },
  stopCrawl() {
    dispatch(stopCrawl(ownProps.crawlId));
  },
  removeCrawl() {
    dispatch(removeCrawl(ownProps.crawlId));
  }
});

const ConnectedCrawl = connect(
  mapStateToProps,
  mapDispatchToProps
)(Crawl);

export default ConnectedCrawl;

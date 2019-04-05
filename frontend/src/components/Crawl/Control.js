import React, { Component } from 'react';
import * as PropTypes from 'prop-types';
import { CrawlRecord } from '../../reducers/crawls';

export default class Control extends Component {
  static propTypes = {
    crawl: PropTypes.instanceOf(CrawlRecord).isRequired,
    getCrawlInfo: PropTypes.func.isRequired,
    startCrawl: PropTypes.func.isRequired,
    stopCrawl: PropTypes.func.isRequired,
    removeCrawl: PropTypes.func.isRequired
  };

  startCrawl() {
    const { crawl } = this.props;
    this.props.startCrawl(crawl.startCrawlConfig());
  }

  constructor(props) {
    super(props);
    this.startCrawl = this.startCrawl.bind(this);
  }

  render() {
    const { crawl, getCrawlInfo, removeCrawl, stopCrawl } = this.props;
    return (
      <div className='uk-grid uk-flex-center uk-margin-bottom' data-uk-grid=''>
        <div>
          <button
            onClick={this.startCrawl}
            disabled={crawl.running}
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
          <button className='uk-button uk-button-default' onClick={removeCrawl}>
            Remove
          </button>
        </div>
      </div>
    );
  }
}

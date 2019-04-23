import React, { Component } from 'react';
import * as PropTypes from 'prop-types';
import { CrawlRecord } from '../../reducers/crawls';

export default class Info extends Component {
  static propTypes = {
    crawl: PropTypes.instanceOf(CrawlRecord).isRequired
  };

  renderQueue() {
    const crawlId = this.props.crawl.id;
    const queue = this.props.crawl.queue;
    const q = new Array(queue.length);
    for (let i = 0; i < queue.length; i++) {
      const qinfo = JSON.parse(queue[i]);
      q[i] = (
        <li key={`${crawlId}-seeds-${i}`}>
          <p>
            {qinfo.url} @ depth {qinfo.depth}
          </p>
        </li>
      );
    }
    return (
      <>
        <h4 className='uk-text-center'>Queue</h4>
        <ul className='uk-list uk-flex uk-flex-column uk-flex-center uk-flex-middle'>{q}</ul>
      </>
    );
  }

  renderBrowsers() {
    const crawlId = this.props.crawl.id;
    const browsers = this.props.crawl.browsers;
    const b = new Array(browsers.length);
    for (let i = 0; i < browsers.length; i++) {
      console.log(browsers[i]);
      b[i] = (
        <li key={`${crawlId}-browsers-${i}`}>
          <a
            href={`http://localhost:9020/attach/${browsers[i]}`}
            target='_blank'
          >
            View {browsers[i]}
          </a>
        </li>
      );
    }
    return (
      <>
        <h4 className='uk-text-center'>View Running Crawl</h4>
        <ul className='uk-list uk-flex uk-flex-center'>{b}</ul>
      </>
    );
  }

  render() {
    const { crawl } = this.props;
    console.log('Viewing crawl info', crawl.toJS());
    return (
      <>
        <table className='uk-table uk-table-middle uk-table-justify'>
          <thead>
            <tr>
              <th>Type</th>
              <th>Status</th>
              <th>Num Browsers</th>
              <th>Num Tabs</th>
              <th>Crawl Depth</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{crawl.crawl_type}</td>
              <td>{crawl.status || 'new'}</td>
              <td>{crawl.num_browsers}</td>
              <td>{crawl.num_tabs}</td>
              <td>{crawl.crawl_depth}</td>
            </tr>
          </tbody>
        </table>
        {crawl.browsers.length > 0 && this.renderBrowsers()}
        {crawl.queue.length > 0 && this.renderQueue()}
      </>
    );
  }
}

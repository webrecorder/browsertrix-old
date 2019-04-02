import React, { Component } from 'react';
import * as PropTypes from 'prop-types';
import { Link } from 'react-router-dom';

export default class CrawlLi extends Component {
  static propTypes = {
    removeCrawl: PropTypes.func.isRequired,
    crawlId: PropTypes.string.isRequired
  };

  constructor(props) {
    super(props);
    this.removeCrawl = this.removeCrawl.bind(this);
  }

  removeCrawl() {
    this.props.removeCrawl(this.props.crawlId);
  }

  render() {
    return (
      <li>
        <h1>
          <Link
            className='uk-button uk-button-text'
            to={`/crawl/${this.props.crawlId}`}
          >
            {this.props.crawlId}
          </Link>
          <span
            className='removeCrawlFromListIcon'
            onClick={this.removeCrawl}
            data-uk-icon='close'
          />
        </h1>
      </li>
    );
  }
}

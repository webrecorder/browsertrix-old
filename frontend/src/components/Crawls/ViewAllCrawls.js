import React from 'react';
import * as PropTypes from 'prop-types';
import { List } from 'immutable';
import ListGroup from 'react-bootstrap/ListGroup';
import Crawl from './Crawl';

export default function ViewAllCrawls({ crawls, crawlActions }) {
  const allCrawls = [];
  for (const [id, crawl] of crawls) {
    allCrawls.push(
      <Crawl key={`crawl-${id}`} crawlActions={crawlActions} crawl={crawl} />
    );
  }
  return <ListGroup>{allCrawls}</ListGroup>;
}

ViewAllCrawls.propTypes = {
  crawlIds: PropTypes.instanceOf(List).isRequired,
  crawlActions: PropTypes.shape({
    createCrawl: PropTypes.func.isRequired,
    getAllCrawls: PropTypes.func.isRequired,
    getCrawlInfo: PropTypes.func.isRequired,
    removeCrawl: PropTypes.func.isRequired
  })
};

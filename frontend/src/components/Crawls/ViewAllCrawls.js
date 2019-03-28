import React from 'react';
import * as PropTypes from 'prop-types';
import { Map } from 'immutable';
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
  crawls: PropTypes.instanceOf(Map).isRequired,
  crawlActions: PropTypes.shape({
    getAllCrawls: PropTypes.func.isRequired,
    getCrawlInfo: PropTypes.func.isRequired
  })
};

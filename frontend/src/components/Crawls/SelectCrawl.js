import React from 'react';
import * as PropTypes from 'prop-types';
import { List } from 'immutable';
import CrawlLi from './CrawlLi';

export default function SelectCrawls({ crawlIds, removeCrawl }) {
  const crawls = new Array(crawlIds.size);
  for (let i = 0; i < crawlIds.size; i++) {
    const id = crawlIds.get(i);
    crawls[i] = (
      <CrawlLi
        key={`crawl-${i}-${id}`}
        removeCrawl={removeCrawl}
        crawlId={id}
      />
    );
  }
  return (
    <>
      <h1 className='uk-text-center'>Select Crawl To View</h1>
      <div className='uk-container uk-container-small'>
        <div className='uk-flex uk-flex-center'>
          <ul className='uk-list uk-list-divider'>{crawls}</ul>
        </div>
      </div>
    </>
  );
}

SelectCrawls.propTypes = {
  crawlIds: PropTypes.instanceOf(List).isRequired,
  removeCrawl: PropTypes.func.isRequired
};

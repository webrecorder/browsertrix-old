import React from 'react';
import * as PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import { List } from 'immutable';

export default function SelectCrawls({ crawlIds }) {
  const crawls = new Array(crawlIds.size);
  for (let i = 0; i < crawlIds.size; i++) {
    const id = crawlIds.get(i);
    crawls[i] = (
      <div key={`crawl-${i}-${id}`}>
        <h1>
          <Link className='uk-button uk-button-text' to={`/crawl/${id}`}>
            Crawl Id - {id}
          </Link>
        </h1>
      </div>
    );
  }
  return (
    <>
      <h1 className='uk-text-center'>Select Crawl To View</h1>
      <div className='uk-container uk-container-small'>
        <div
          className='uk-grid uk-child-width-1-3 uk-flex-center'
          data-uk-grid=''
        >
          {crawls}
        </div>
      </div>
    </>
  );
}

SelectCrawls.propTypes = {
  crawlIds: PropTypes.instanceOf(List).isRequired
};

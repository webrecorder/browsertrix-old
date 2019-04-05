import React from 'react';

export default function LoadingCrawls() {
  return (
    <div className='uk-flex uk-flex-column uk-flex-middle'>
      <h1 className='uk-heading-primary'>Retrieving Crawl Info</h1>
      <span data-uk-spinner='ratio: 4.5' />
    </div>
  );
}

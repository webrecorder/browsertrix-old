import React from 'react';
import Spinner from 'react-bootstrap/Spinner';

export default function LoadingCrawls() {
  return (
    <div className='d-flex flex-column justify-content-center'>
      <h1 className='display-5 align-self-center'>Retrieving Crawl Info</h1>
      <Spinner
        className='align-self-center'
        animation='border'
        variant='info'
      />
    </div>
  );
}

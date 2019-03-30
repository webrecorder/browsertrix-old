import React from 'react';
import * as PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { createCrawl } from '../../actions';
import CrawlCreationForm from './CreationForm';

function validate(values, props) {
  if (!props.initialized) return;
  const errors = {};
  if (values.get('numBrowsers') <= 0) {
    errors.numBrowsers =
      'The number of browser to be used cannot be less than or equal to zero';
  }
  if (values.get('numTabs') <= 0) {
    errors.numTabs =
      'The number of tabs to be used cannot be less than or equal to zero';
  }
  if (values.get('depth') <= 0) {
    errors.depth = 'The depth of crawl cannot be less than or equal to zero';
  }
  return errors;
}

function CrawlCreator({ message, createCrawl }) {
  return (
    <>
      <h1 className='display-4 uk-text-center'>{message}</h1>
      <CrawlCreationForm
        initialValues={{
          crawlType: 'single-page',
          numBrowsers: 1,
          numTabs: 1,
          depth: 1,
          urls: []
        }}
        validate={validate}
        onSubmit={createCrawl}
      />
    </>
  );
}

CrawlCreator.propTypes = {
  message: PropTypes.string.isRequired,
  createCrawl: PropTypes.func.isRequired
};

const mapDispatchToProps = (dispatch, ownProps) => ({
  createCrawl(crawlInfo) {
    dispatch(createCrawl(crawlInfo.toJS()));
  }
});

const ConnectedCrawlCreator = connect(
  null,
  mapDispatchToProps
)(CrawlCreator);

export default ConnectedCrawlCreator;

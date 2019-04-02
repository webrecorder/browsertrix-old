import React from 'react';
import * as PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { createCrawl } from '../../actions';
import CrawlCreationForm, { initialValues } from './CreationForm';

function CrawlCreator({ message, createCrawl }) {
  return (
    <>
      <h1 className='display-4 uk-text-center'>{message}</h1>
      <CrawlCreationForm initialValues={initialValues} onSubmit={createCrawl} />
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

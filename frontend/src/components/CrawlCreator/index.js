import React from 'react';
import * as PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { formValueSelector } from 'redux-form/immutable';
import { withRouter } from 'react-router-dom';
import { createCrawl } from '../../actions';
import CrawlCreationForm, { initialValues } from './CreationForm';

function CrawlCreator({ crawlType, createCrawl }) {
  return (
    <>
      <h3 className='display-4 uk-text-center'>New Crawl</h3>
      <CrawlCreationForm
        crawlType={crawlType}
        initialValues={initialValues}
        onSubmit={createCrawl} />
    </>
  );
}

CrawlCreator.propTypes = {
  createCrawl: PropTypes.func.isRequired
};

const selector = formValueSelector('CreateCrawl');
const mapStateToProps = state => {
  return {
    crawlType: selector(state, 'crawlInfo.crawl_type')
  };
};

const mapDispatchToProps = (dispatch, ownProps) => ({
  createCrawl(crawlInfo) {
    ownProps.history.push('/');
    dispatch(createCrawl(crawlInfo.toJS()));
  }
});

const ConnectedCrawlCreator = connect(
  mapStateToProps,
  mapDispatchToProps
)(CrawlCreator);

export default withRouter(ConnectedCrawlCreator);

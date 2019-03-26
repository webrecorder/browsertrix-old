import React from 'react';
import * as PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { createCrawl, getAllCrawls } from '../../actions/crawls';
import CrawlCreator from './CrawlCreator';

function CreateOrFetchAllCrawls({ numCrawls, getAll, createCrawl }) {
  return (
    <CrawlCreator createCrawl={createCrawl}/>
  );
}

function mapDispatchToProps(dispatch, ownProps) {
  return {
    createCrawl() {
      dispatch(createCrawl());
    },
    getAll() {
      dispatch(getAllCrawls());
    }
  };
}

CreateOrFetchAllCrawls.propTypes = {
  numCrawls: PropTypes.number.isRequired,
  getAll: PropTypes.func.isRequired,
  createCrawl: PropTypes.func.isRequired
};

export default connect(
  null,
  mapDispatchToProps
)(CreateOrFetchAllCrawls);

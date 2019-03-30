import React from 'react';
import Field from 'redux-form/lib/immutable/Field';
import FieldArray from 'redux-form/lib/immutable/FieldArray';
import reduxForm from 'redux-form/lib/immutable/reduxForm';
import {
  CrawlDepthField,
  NumBrowsersField,
  NumTabsField,
  ScopeField,
  URLFields
} from './fields';

function validate(values, props) {
  if (!props || !props.initialized) return;
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

function CrawlCreationForm({ handleSubmit, valid, submitting }) {
  const submitDisabled = !valid || submitting;
  return (
    <form className='uk-form-stacked' onSubmit={handleSubmit} autoComplete='on'>
      <div className='uk-flex uk-flex-middle uk-flex-center'>
        <button
          className='uk-button uk-button-default uk-margin-bottom'
          type='submit'
          disabled={submitDisabled}
        >
          Create Crawl
        </button>
      </div>
      <div className='uk-child-width-1-4' data-uk-grid=''>
        <Field name='crawlType' component={ScopeField} />
        <Field name='numBrowsers' component={NumBrowsersField} />
        <Field name='numTabs' component={NumTabsField} />
        <Field name='depth' component={CrawlDepthField} />
      </div>
      <FieldArray name='urls' component={URLFields} />
    </form>
  );
}

export default reduxForm({
  form: 'CreateCrawl',
  enableReinitialize: true,
  destroyOnUnmount: false,
  initialValues: {
    crawlType: 'single-page',
    numBrowsers: 1,
    numTabs: 1,
    depth: 1,
    urls: []
  },
  validate
})(CrawlCreationForm);

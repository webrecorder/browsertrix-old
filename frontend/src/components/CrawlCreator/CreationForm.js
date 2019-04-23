import React from 'react';
import FormSection from 'redux-form/lib/FormSection';
import Field from 'redux-form/lib/immutable/Field';
import FieldArray from 'redux-form/lib/immutable/FieldArray';
import reduxForm from 'redux-form/lib/immutable/reduxForm';
import {
  CrawlConfigInputField,
  CrawlConfigSelectField,
  URLFields
} from './fields';

export function validate(values, props) {
  const errors = {
    crawlInfo: {},
    crawlRunInfo: {}
  };
  const crawlInfo = values.get('crawlInfo');
  if (!crawlInfo) {
    errors.crawlInfo = 'required';
  } else {
    if (crawlInfo.get('num_browsers') <= 0) {
      errors.crawlInfo.num_browsers =
        'The number of browser to be used cannot be less than or equal to zero';
    }
    if (values.get('num_tabs') <= 0) {
      errors.crawlInfo.num_tabs =
        'The number of tabs to be used cannot be less than or equal to zero';
    }
    if (values.get('crawl_depth') <= 0) {
      errors.crawlInfo.crawl_depth =
        'The depth of crawl cannot be less than or equal to zero';
    }
  }
  const cinfo = values.get('crawlRunInfo');
  if (!cinfo) {
    errors.crawlRunInfo = 'Required';
  } else {
    if (cinfo.get('behavior_run_time') <= 0) {
      errors.crawlRunInfo.behavior_run_time =
        'The runtime of behaviors must be greater than zero';
    }
    const seeds = cinfo.get('seed_urls');
    if (!seeds || seeds.size <= 0) {
      errors.crawlRunInfo.seed_urls = 'Must include seed urls';
    }
  }
  return errors;
}

function seedURLsRequired(value, allValues, props) {
  if (!value) return 'Required';
  if (value.size === 0) return 'Required';
}

function CrawlCreationForm({ crawlType, handleSubmit, valid, submitting }) {
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
      <FormSection name='crawlInfo'>
        <div className='uk-grid uk-child-width-1-4' data-uk-grid=''>
          <Field
            name='crawl_type'
            label='Crawl Type'
            component={CrawlConfigSelectField}
          >
            <option value='single-page'>Single Page</option>
            <option value='same-domain'>Same Domain Links</option>
            <option value='all-links'>All Links on Page</option>
            <option value='custom'>Custom Depth</option>
          </Field>
          <Field
            name='crawl_depth'
            type='number'
            label='Crawl Depth'
            props={{ disabled: crawlType !== 'custom', min: 1 }}
            component={CrawlConfigInputField}
          />
          <Field
            name='num_browsers'
            type='number'
            label='How Many Browsers'
            component={CrawlConfigInputField}
          />
          <Field
            name='num_tabs'
            type='number'
            label='How Many Tabs'
            component={CrawlConfigInputField}
          />
        </div>
      </FormSection>
      <FormSection name='crawlRunInfo'>
        <>
          <div
            className='uk-grid uk-child-width-1-3 uk-margin-top'
            data-uk-grid=''
          >
            <Field
              name='browser'
              label='Which Browser'
              component={CrawlConfigSelectField}
            >
              <option value='chrome:67'>Chrome 67</option>
            </Field>
            <Field
              name='headless'
              label='Headless'
              component={CrawlConfigSelectField}
            >
              <option value={false}>No</option>
              <option value={true}>Yes</option>
            </Field>
            <Field
              name='behavior_run_time'
              type='number'
              label='How Long Should Behaviors Run (Seconds)'
              component={CrawlConfigInputField}
            />
          </div>
          <FieldArray
            name='seed_urls'
            component={URLFields}
            validate={seedURLsRequired}
          />
        </>
      </FormSection>
    </form>
  );
}

export const initialValues = {
  crawlInfo: {
    crawl_type: 'single-page',
    num_browsers: 1,
    num_tabs: 1,
    crawl_depth: 1
  },
  crawlRunInfo: {
    headless: false,
    browser: 'chrome:67',
    behavior_run_time: 60,
    urls: []
  }
};

export default reduxForm({
  form: 'CreateCrawl',
  enableReinitialize: true,
  destroyOnUnmount: false,
  initialValues,
  validate
})(CrawlCreationForm);

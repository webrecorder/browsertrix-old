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
  };
  const crawlInfo = values.get('crawlInfo');
  if (!crawlInfo) {
    errors.crawlInfo = 'required';
  } else {
    if (values.get('num_browsers') <= 0) {
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

    if (values.get('behavior_max_time') <= 0) {
      errors.crawlInfo.behavior_max_time =
        'The runtime of behaviors must be greater than zero';
    }
    const seeds = crawlInfo.get('seed_urls');
    if (!seeds || seeds.size <= 0) {
      errors.crawlInfo.seed_urls = 'Must include seed urls';
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
      <FormSection name='crawlInfo'>
        <div uk-child-width-expands="true" uk-grid="true">
          <div className='uk-width-1-2'>
            <div className='uk-column-1-2'>
              <Field
                name='name'
                type='text'
                label='Name'
                component={CrawlConfigInputField}
              />
              <Field
                name='coll'
                type='text'
                label='Collection'
                component={CrawlConfigInputField}
              />
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
              <Field
                name='behavior_max_time'
                type='number'
                label='Behaviors Runtime (Seconds)'
                title='How Long Should Behaviors run for, in seconds.'
                component={CrawlConfigInputField}
              />
            </div>
            <ul uk-accordion="true">
              <li className="">
                <a className="uk-accordion-title" href="#">More Options...</a>
                <div className="uk-accordion-content uk-column-1-2">
                  <Field
                  name='crawl_depth'
                  type='number'
                  label='Crawl Depth'
                  props={{ disabled: crawlType === 'single-page', min: 1 }}
                  component={CrawlConfigInputField}
                  />
                  <Field
                    name='browser'
                    label='Which Browser'
                    component={CrawlConfigSelectField}
                  >
                    <option value='chrome:73'>Chrome 73</option>
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
                    name='cache'
                    label='Cache Settings'
                    component={CrawlConfigSelectField}
                  >
                    <option value='always'>Always</option>
                    <option value='never'>Never</option>
                    <option value='default'>Default</option>
                  </Field>
                </div>
              </li>
            </ul>
          </div>
          <div className="uk-width-1-2">
            <FieldArray
              name='seed_urls'
              component={URLFields}
              validate={seedURLsRequired}
            />
          </div>
        </div>
        <div className='uk-flex uk-flex-middle uk-flex-center'>
          <button
            className='uk-button uk-button-default uk-button-primary uk-margin-bottom'
            type='submit'
            disabled={submitDisabled}
          >
            Create Crawl
          </button>
        </div>
      </FormSection>
    </form>
  );
}

export const initialValues = {
  crawlInfo: {
    crawl_type: 'single-page',
    num_browsers: 1,
    num_tabs: 1,
    name: 'test crawl',
    coll: 'test',
    crawl_depth: 1,
    headless: false,
    cache: 'always',
    browser: 'chrome:73',
    behavior_max_time: 60,
    seed_urls: [],
  }
};

export default reduxForm({
  form: 'CreateCrawl',
  enableReinitialize: true,
  destroyOnUnmount: false,
  initialValues,
  validate
})(CrawlCreationForm);

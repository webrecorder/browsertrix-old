import React from 'react';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import { Field, FieldArray, reduxForm } from 'redux-form/immutable';
import { NumBrowsersField, NumTabsField, ScopeField, URLFields } from './fields';
import validate from './validate';

function CrawlCreator({ handleSubmit, pristine, reset, submitting }) {
  return (
    <Form onSubmit={handleSubmit} className='form-border' autoComplete='on'>
      <Form.Row>
        <Field name='scope' component={ScopeField} />
        <Field name='browsers' component={NumBrowsersField} />
        <Field name='tabs' component={NumTabsField} />
      </Form.Row>
      <FieldArray name='urls' component={URLFields} />
      <Button
        type='submit'
        variant='outline-primary'
        disabled={submitting || !pristine}
      >
        Create Crawl
      </Button>
    </Form>
  );
}

export default reduxForm({
  form: 'CreateCrawl',
  initialValues: {
    scope: 'single-page',
    browsers: 1,
    tabs: 1,
    urls: []
  },
  validate
})(CrawlCreator);

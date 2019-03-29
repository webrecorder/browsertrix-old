import React from 'react';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import Field from 'redux-form/lib/immutable/Field';
import FieldArray from 'redux-form/lib/immutable/FieldArray';
import reduxForm from 'redux-form/lib/immutable/reduxForm';
import {
  NumBrowsersField,
  NumTabsField,
  ScopeField,
  CrawlDepthField,
  URLFields
} from './fields';

function CrawlCreator(props) {
  return (
    <Form
      onSubmit={props.handleSubmit}
      className='form-border'
      autoComplete='on'
    >
      <Form.Row>
        <Field name='crawlType' component={ScopeField} />
        <Field name='numBrowsers' component={NumBrowsersField} />
        <Field name='numTabs' component={NumTabsField} />
        <Field name='depth' component={CrawlDepthField} />
      </Form.Row>
      <FieldArray required name='urls' component={URLFields} />
      <Button
        type='submit'
        variant='outline-primary'
        disabled={!props.valid || props.submitting}
      >
        Create Crawl
      </Button>
    </Form>
  );
}

export default reduxForm({
  form: 'CreateCrawl',
  destroyOnUnmount: true,
  initialValues: {
    crawlType: 'single-page',
    numBrowsers: 1,
    numTabs: 1,
    depth: 1,
    urls: []
  }
})(CrawlCreator);

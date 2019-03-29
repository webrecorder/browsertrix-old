import React, { Component } from 'react';
import * as PropTypes from 'prop-types';
import Button from 'react-bootstrap/Button';
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';
import Feedback from 'react-bootstrap/Feedback';
import FormControl from 'react-bootstrap/FormControl';
import FormGroup from 'react-bootstrap/FormGroup';
import FormLabel from 'react-bootstrap/FormLabel';
import ListGroup from 'react-bootstrap/ListGroup';
import ListGroupItem from 'react-bootstrap/ListGroupItem';
import Field from 'redux-form/lib/immutable/Field';
import urlRegx from 'url-regex';

export function ScopeField({ input: { value, onChange } }) {
  return (
    <FormGroup as={Col} sm='3'>
      <FormLabel htmlFor='crawlScope'>Crawl Type</FormLabel>
      <FormControl
        size='sm'
        id='crawlScope'
        value={value}
        as='select'
        onChange={onChange}
      >
        <option value='single-page'>Single Page</option>
        <option value='same-domain'>Same Domain</option>
        <option value='all-links'>All Pages</option>
      </FormControl>
    </FormGroup>
  );
}

export function NumBrowsersField({ input: { value, onChange } }) {
  return (
    <FormGroup as={Col} sm='3'>
      <FormLabel htmlFor='numBrowsers'>Browsers</FormLabel>
      <FormControl
        size='sm'
        id='numBrowsers'
        as='input'
        type='number'
        value={value}
        onChange={onChange}
      />
    </FormGroup>
  );
}

export function NumTabsField({ input: { value, onChange } }) {
  return (
    <FormGroup as={Col} sm='3'>
      <FormLabel htmlFor='numTabs'>Tabs</FormLabel>
      <FormControl
        size='sm'
        id='numTabs'
        as='input'
        type='number'
        value={value}
        onChange={onChange}
      />
    </FormGroup>
  );
}

export function CrawlDepthField({ input: { value, onChange } }) {
  return (
    <FormGroup as={Col} sm='3'>
      <FormLabel htmlFor='crawlDepth'>Depth</FormLabel>
      <FormControl
        size='sm'
        id='crawlDepth'
        as='input'
        type='number'
        value={value}
        onChange={onChange}
      />
    </FormGroup>
  );
}

const isURLRe = urlRegx({ exact: true, strict: false });

const isURLTest = url => (isURLRe.test(url) ? null : 'Not a URL');

class URLToCrawl extends Component {
  static propTypes = {
    idx: PropTypes.number.isRequired,
    remove: PropTypes.func.isRequired
  };

  constructor(props) {
    super(props);
    this.renderURL = this.renderURL.bind(this);
    this.remove = this.remove.bind(this);
  }

  className(inputValue, meta) {
    const invalid = !!(meta && meta.touched && meta.error) || !inputValue;
    return `form-control form-control-sm ${
      invalid ? 'is-invalid' : 'is-valid'
    }`;
  }

  renderURL({ input, meta }) {
    const classes = `form-control form-control-sm ${
      meta.valid ? 'is-valid' : 'is-invalid'
    }`;
    return (
      <>
        <input
          className={classes}
          type='url'
          id={input.name}
          value={input.value}
          onChange={input.onChange}
          onBlur={input.onBlur}
          placeholder='Seed URL'
        />
        {!meta.valid && (
          <Feedback as='span' type='invalid'>
            {meta.error}
          </Feedback>
        )}
      </>
    );
  }

  remove() {
    this.props.remove(this.props.idx);
  }

  render() {
    return (
      <ListGroupItem>
        <Row>
          <Col>
            <Field
              component={this.renderURL}
              validate={isURLTest}
              name={`urls.${this.props.idx}`}
            />
          </Col>
          <Col sm='1'>
            <Button
              size='sm'
              variant='outline-warning'
              type='button'
              onClick={this.remove}
            >
              Remove
            </Button>
          </Col>
        </Row>
      </ListGroupItem>
    );
  }
}

export class URLFields extends Component {
  constructor(props) {
    super(props);
    this.renderURLs = this.renderURLs.bind(this);
    this.addURL = this.addURL.bind(this);
    this.removeURL = this.removeURL.bind(this);
  }

  addURL() {
    this.props.fields.push('');
  }

  removeURL(idx) {
    this.props.fields.remove(idx);
  }

  renderURLs() {
    const { fields } = this.props;
    const urls = new Array(fields.length);
    for (let i = 0; i < fields.length; i++) {
      urls[i] = (
        <URLToCrawl
          key={`crawl-url-input-${i}`}
          idx={i}
          remove={this.removeURL}
        />
      );
    }
    return urls;
  }

  render() {
    const haveURLS = this.props.fields.length >= 1;
    return (
      <>
        <div className='d-flex justify-content-center'>
          <Button size='sm' variant='outline-secondary' onClick={this.addURL}>
            Add Seed URL
          </Button>
        </div>
        <ListGroup variant='flush' className='create-crawl-seedlist'>
          {haveURLS && this.renderURLs()}
        </ListGroup>
      </>
    );
  }
}

import React, { Component } from 'react';
import * as PropTypes from 'prop-types';
import { Button, Col, Form } from 'react-bootstrap';

export default class CrawlCreator extends Component {
  static propTypes = {
    createCrawl: PropTypes.func.isRequired
  };

  constructor(props) {
    super(props);
    this.formRefs = {
      scope: React.createRef(),
      browsers: React.createRef(),
      tabs: React.createRef()
    };
    this.createCrawl = this.createCrawl.bind(this);
  }

  createCrawl(e) {
    e.preventDefault();
    console.log('create crawl');
    console.log(e.target);
    this.props.createCrawl({

    });
  }

  render() {
    return (
      <Form onSubmit={this.createCrawl}>
        <Form.Row>
          <Form.Group as={Col}>
            <Form.Label htmlFor='crawlScope'>Scope</Form.Label>
            <Form.Control
              size='sm'
              id='crawlScope'
              defaultValue='single-page'
              as='select'
              ref={this.formRefs.scope}
            >
              <option value='single-page'>Single Page</option>
              <option value='same-domain'>Same Domain</option>
              <option value='all-links'>All Pages</option>
            </Form.Control>
          </Form.Group>
          <Form.Group as={Col}>
            <Form.Label htmlFor='numBrowsers'>Num Browsers</Form.Label>
            <Form.Control
              size='sm'
              id='numBrowsers'
              as='input'
              type='number'
              defaultValue={2}
              ref={this.formRefs.browsers}
            />
          </Form.Group>
          <Form.Group as={Col}>
            <Form.Label htmlFor='numTabs'>Num Tabs</Form.Label>
            <Form.Control
              size='sm'
              id='numTabs'
              as='input'
              type='number'
              defaultValue={2}
              ref={this.formRefs.tabs}
            />
          </Form.Group>
        </Form.Row>
        <Button type='submit'>Create Crawl</Button>
      </Form>
    );
  }
}

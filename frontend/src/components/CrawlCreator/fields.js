import React, { Component, Fragment } from 'react';
import * as PropTypes from 'prop-types';
import Button from 'react-bootstrap/Button';
import Col from 'react-bootstrap/Col';
import FormControl from 'react-bootstrap/FormControl';
import FormGroup from 'react-bootstrap/FormGroup';
import FormLabel from 'react-bootstrap/FormLabel';
import ListGroup from 'react-bootstrap/ListGroup';
import ListGroupItem from 'react-bootstrap/ListGroupItem';
import Row from 'react-bootstrap/Row';

export function ScopeField({ input: { value, onChange } }) {
  return (
    <FormGroup as={Col} sm='4'>
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
    <FormGroup as={Col} sm='4'>
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
    <FormGroup as={Col} sm='4'>
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

class URLToBeCrawled extends Component {
  static propTypes = {
    idx: PropTypes.number,
    remove: PropTypes.func,
    empty: PropTypes.bool,
    url: PropTypes.string
  };

  remove = () => {
    this.props.remove(this.props.idx);
  };

  render() {
    if (this.props.empty) {
      return <ListGroupItem as='li'>No URLs To Crawl</ListGroupItem>;
    }
    return (
      <ListGroupItem as='li'>
        {this.props.url}
        <Button
          className='float-right'
          size='sm'
          variant='outline-danger'
          onClick={this.remove}
        >
          X
        </Button>
      </ListGroupItem>
    );
  }
}

export class URLFields extends Component {
  constructor(props) {
    super(props);
    this.addURL = this.addURL.bind(this);
    this.removeURL = this.removeURL.bind(this);
    this.inputRef = React.createRef();
  }

  addURL() {
    const url = this.inputRef.current.value.trim();
    if (url) {
      this.props.fields.push(url);
      this.inputRef.current.value = '';
    }
  }

  removeURL(idx) {
    this.props.fields.remove(idx);
  }

  renderURLS() {
    const { fields } = this.props;
    const urls = new Array(fields.length);
    for (let i = 0; i < fields.length; i++) {
      urls[i] = (
        <URLToBeCrawled
          key={`seed-url-${i}`}
          url={fields.get(i)}
          idx={i}
          remove={this.removeURL}
        />
      );
    }
    if (urls.length === 0) {
      urls.push(<URLToBeCrawled key='no-urls-to-crawl' empty />);
    }
    return urls;
  }

  render() {
    return (
      <Fragment>
        <Row>
          <Col>
            <FormControl
              size='sm'
              as='input'
              type='url'
              placeholder='Seed URL'
              ref={this.inputRef}
            />
          </Col>
          <Col sm='2'>
            <Button size='sm' variant='outline-secondary' onClick={this.addURL}>
              Add Seed URL
            </Button>
          </Col>
        </Row>
        <ListGroup className='create-crawl-seedlist' as='ul'>
          {this.renderURLS()}
        </ListGroup>
      </Fragment>
    );
  }
}

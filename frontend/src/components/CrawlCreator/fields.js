import React, { Component } from 'react';
import * as PropTypes from 'prop-types';
import Field from 'redux-form/lib/immutable/Field';
import urlRegx from 'url-regex';

export function ScopeField({ input }) {
  return (
    <div>
      <label className='uk-form-label' htmlFor='crawlScope'>
        Crawl Type
      </label>
      <select className='uk-select' id='crawlScope' {...input}>
        <option value='single-page'>Single Page</option>
        <option value='same-domain'>Same Domain</option>
        <option value='all-links'>All Pages</option>
      </select>
    </div>
  );
}

export function NumBrowsersField({ input, meta }) {
  const className = `uk-input ${meta.valid ? '' : 'uk-form-danger'}`;
  return (
    <div>
      <label htmlFor='numBrowsers'>Browsers</label>
      <input className={className} id='numBrowsers' type='number' {...input} />
    </div>
  );
}

export function NumTabsField({ input, meta }) {
  const className = `uk-input ${meta.valid ? '' : 'uk-form-danger'}`;
  return (
    <div>
      <label htmlFor='numTabs'>Tabs</label>
      <input className={className} id='numTabs' type='number' {...input} />
    </div>
  );
}

export function CrawlDepthField({ input, meta }) {
  const className = `uk-input ${meta.valid ? '' : 'uk-form-danger'}`;
  return (
    <div>
      <label htmlFor='crawlDepth'>Depth</label>
      <input
        className={className}
        size='sm'
        id='crawlDepth'
        type='number'
        {...input}
      />
    </div>
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

  renderURL({ input, meta }) {
    const className = `uk-input ${meta.valid ? '' : 'uk-form-danger'}`;
    return (
      <input
        className={className}
        type={input.type}
        id={input.name}
        value={input.value}
        onChange={input.onChange}
        onBlur={input.onBlur}
        placeholder='Seed URL'
      />
    );
  }

  remove() {
    this.props.remove(this.props.idx);
  }

  render() {
    return (
      <div className='uk-inline uk-form-controls uk-width-1-1 uk-margin-small'>
        <a
          className='uk-form-icon uk-form-icon-flip'
          onClick={this.remove}
          data-uk-icon='icon: close'
        />
        <Field
          component={this.renderURL}
          validate={isURLTest}
          type='url'
          name={`urls.${this.props.idx}`}
        />
      </div>
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
      <div
        className='uk-grid uk-grid-large'
        data-uk-grid=''
        style={{ marginTop: 30 }}
      >
        <div>
          <button className='uk-button uk-button-default' onClick={this.addURL}>
            Add Seed URL
          </button>
        </div>
        <div className='uk-width-expand uk-overflow-auto uk-height-medium'>
          <ul className='uk-list'>{haveURLS && this.renderURLs()}</ul>
        </div>
      </div>
    );
  }
}

import React, { Component } from 'react';
import * as PropTypes from 'prop-types';
import Field from 'redux-form/lib/immutable/Field';
import urlRegx from 'url-regex';
import UIKit from 'uikit';

export function CrawlConfigSelectField({ label, input, meta, children }) {
  const id = input.name;
  return (
    <div>
      <label className='uk-form-label' htmlFor={id}>
        {label}
      </label>
      <select className='uk-select' id={id} {...input}>
        {children}
      </select>
    </div>
  );
}

export function CrawlConfigInputField({ disabled, label, min, type, input, meta }) {
  const id = `${input.name}-${type}`;
  const className = `uk-input ${meta.valid ? '' : 'uk-form-danger'}`;
  return (
    <div>
      <label className='uk-form-label' htmlFor={id}>
        {label}
      </label>
      <input disabled={disabled} className={className} type={type} min={min} size='sm' id={id} {...input} />
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
          name={`seed_urls.${this.props.idx}`}
        />
      </div>
    );
  }
}

export class BulkURLInput extends Component {
  static propTypes = {
    addURL: PropTypes.func.isRequired
  };

  constructor(props) {
    super(props);
    this.textAreaRef = React.createRef();
    this.addURLs = this.addURLs.bind(this);
    this.close = this.close.bind(this);
  }

  componentWillUnmount() {
    UIKit.modal('#bulk-seed-input').$destroy(true);
  }

  addURLs() {
    const value = this.textAreaRef.current.value;
    if (value) {
      const rawValues = value.split('\n');
      let added = false;
      for (let i = 0; i < rawValues.length; i++) {
        const value = rawValues[i].trim();
        if (isURLRe.test(value)) {
          added = true;
          this.props.addURL(value);
        }
      }
      if (added) {
        this.close();
      }
    }
  }

  close() {
    this.textAreaRef.current.value = '';
    UIKit.modal('#bulk-seed-input').hide();
  }

  render() {
    return (
      <div id='bulk-seed-input' className='uk-flex-top' data-uk-modal=''>
        <div className='uk-modal-dialog'>
          <div className='uk-modal-header'>
            <h2 className='uk-modal-title'>Enter URLs On A Single Line</h2>
          </div>
          <div className='uk-modal-body uk-margin-auto-vertical'>
            <textarea
              ref={this.textAreaRef}
              className='uk-textarea'
              rows='10'
              placeholder='Seed URLs'
            />
          </div>
          <div className='uk-modal-footer uk-text-right'>
            <button
              className='uk-button uk-button-small uk-button-danger uk-margin-right'
              type='button'
              onClick={this.close}
            >
              Cancel
            </button>
            <button
              className='uk-button uk-button-small uk-button-default'
              type='button'
              onClick={this.addURLs}
            >
              Save
            </button>
          </div>
        </div>
      </div>
    );
  }
}

export class URLFields extends Component {
  static propTypes = {
    fields: PropTypes.object.isRequired
  };

  constructor(props) {
    super(props);
    this.renderURLs = this.renderURLs.bind(this);
    this.addURL = this.addURL.bind(this);
    this.removeURL = this.removeURL.bind(this);
  }

  addURL(maybeURL) {
    this.props.fields.push(typeof maybeURL === 'string' ? maybeURL : '');
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
        <div
          className='uk-grid uk-grid-small uk-flex uk-flex-center uk-margin-top uk-margin-bottom'
          data-uk-grid=''
        >
          <div>
            <button
              className='uk-button uk-button-default'
              onClick={this.addURL}
            >
              Add Seed URL
            </button>
          </div>
          <div>
            <button
              className='uk-button uk-button-default'
              data-uk-toggle='target: #bulk-seed-input'
            >
              Bulk Add Seeds
            </button>
          </div>
        </div>
        {this.props.meta.error && (
          <div
            className='uk-flex uk-flex-middle uk-flex-center'
            style={{ color: '#f0506e' }}
          >
            <span
              className='uk-margin-small-right uk-icon'
              data-uk-icon='warning'
            />
            Seed URLs Required
          </div>
        )}
        <BulkURLInput addURL={this.addURL} />
        <div className='uk-width-expand uk-overflow-auto uk-height-medium'>
          <ul className='uk-list'>{haveURLS && this.renderURLs()}</ul>
        </div>
      </>
    );
  }
}

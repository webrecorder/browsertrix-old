import React, { Component } from 'react';
import { connect } from 'react-redux';
import * as PropTypes from 'prop-types';
import { List, Map } from 'immutable';
import { getAllCrawls, removeCrawl } from '../../actions/crawls';
import LoadingCrawls from './LoadingCrawls';
import SelectCrawl from './SelectCrawl';
import CrawlCreator from '../CrawlCreator';

class Crawls extends Component {
  static propTypes = {
    crawls: PropTypes.instanceOf(Map).isRequired,
    crawlsFetched: PropTypes.bool.isRequired,
    init: PropTypes.func.isRequired,
    removeCrawl: PropTypes.func.isRequired
  };

  constructor(props) {
    super(props);

    this.handle = null;
  }

  componentDidMount() {
    if (!this.props.crawlsFetched) {
      this.props.loadCrawls(true);
    }

    if (this.props.crawls.size > 0) {
      this.autoUpdate();
    }
  }

  componentDidUpdate() {
    if (this.props.crawls.size > 0 && !this.handle) {
      this.autoUpdate();
    } else if (this.props.crawls.size === 0 && this.handle) {
      clearInterval(this.handle);
      this.handle = null;
    }
  }

  componentWillUnmount() {
    clearInterval(this.handle);
  }

  autoUpdate = () => {
    this.handle = setInterval(this.props.loadCrawls, 1000);
  }

  render() {
    let component;
    if (!this.props.crawlsFetched) {
      component = <LoadingCrawls />;
    } else if (this.props.crawls.size === 0) {
      component = <CrawlCreator message={'There are no pre-existing crawls'} />;
    } else {
      component = (
        <SelectCrawl
          removeCrawl={this.props.removeCrawl}
          crawls={this.props.crawls}
        />
      );
    }
    return <div className='uk-container'>{component}</div>;
  }
}

const mapDispatchToProps = (dispatch, ownProps) => ({
  loadCrawls(init = false) {
    dispatch(getAllCrawls(init));
  },
  removeCrawl(id) {
    dispatch(removeCrawl(id));
  }
});

const mapStateToProps = (state, ownProps) => ({
  crawls: state.get('crawls'),
  crawlsFetched: state.get('crawlsFetched')
});

const ConnectedCrawls = connect(
  mapStateToProps,
  mapDispatchToProps
)(Crawls);

export default ConnectedCrawls;

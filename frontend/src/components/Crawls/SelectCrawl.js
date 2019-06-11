import React from 'react';
import ReactTable from "react-table";
import * as PropTypes from 'prop-types';
import { List, Map } from 'immutable';
import { Link } from 'react-router-dom';

export default function SelectCrawls({ crawls, removeCrawl }) {


  function doRemove(id) {
    //this.props.removeCrawl(this.props.crawlId);
    console.log(id);
    removeCrawl(id);
  }

  function formatTimeDiff(from, to) {
    to = to ? new Date(to * 1000) : new Date();
    from = new Date(from * 1000);

    var delta = Math.abs(to - from) / 1000;

    var hours = Math.floor(delta / 3600);
    delta -= hours * 3600;

    var minutes = Math.floor(delta / 60) % 60;
    delta -= minutes * 60;

    var seconds = Math.floor(delta % 60);

    hours = hours.toString().padStart(2, '0');
    minutes = minutes.toString().padStart(2, '0');
    seconds = seconds.toString().padStart(2, '0');

    return `${hours}:${minutes}:${seconds}`;
}


  const columns = [
  {
    Header: 'Name (Id)',
    accessor: 'id',
    Cell: props => <Link className='uk-button uk-button-text' to={`/crawl/${props.value}`}>{props.original.name ? props.original.name + ' (' + props.value + ')': props.value}</Link>
  },
  {
    Header: 'Started',
    accessor: 'start_time',
    Cell: props => <span>{`${formatTimeDiff(props.value)} ago`}</span>
  },
  {
    Header: 'Duration',
    accessor: 'finish_time',
    Cell: props => <span>{`${formatTimeDiff(props.original.start_time, props.value)}`}</span>
  },
  {
    Header: 'Status',
    accessor: 'status'
  },
  {
    Header: 'Crawl Type',
    accessor: 'crawl_type'
  },
  {
    Header: 'Collection',
    accessor: 'coll',
    Cell: props => <a href={`${window.location.protocol + "//" + window.location.hostname}:8180/${props.value}`}>{props.value}</a>
  },
  {
    Header: 'Mode',
    accessor: 'mode'
  },
  {
    Header: 'To Crawl',
    accessor: 'num_queue'
  },
  {
    Header: 'Have Crawled',
    accessor: 'num_seen'
  },
  {
    Header: 'Remove Crawl',
    id: 'remove_crawl',
    Cell: props => (<span
            className='removeCrawlFromListIcon' style={{'textAlign': 'center'}}
            data-uk-icon='close'
          />)
  },
  ];

  function resolveData(data) {
    return data.valueSeq().toArray();
  }

  function getTdProps(state, rowInfo, column, instance) {
    return {
      onClick: (e, handleOriginal) => {
        if (column.id === "remove_crawl") {
          doRemove(rowInfo.row.id);
        }
      }
    };
  }

  const crawlTable = (<ReactTable data={crawls}
                                  columns={columns}
                                  resolveData={resolveData}
                                  defaultSorted={[{'id': 'start_time', 'desc': true}]}
                                  getTdProps={getTdProps}/>);

  return (
    <div>
      <h3 className='uk-text-center'>All Crawls</h3>
      {crawlTable}
    </div>
  );
}

SelectCrawls.propTypes = {
  crawls: PropTypes.instanceOf(Map).isRequired,
  removeCrawl: PropTypes.func.isRequired
};



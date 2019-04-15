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

  const columns = [
  {
    Header: 'Id',
    accessor: 'id',
    Cell: props => <Link className='uk-button uk-button-text' to={`/crawl/${props.value}`}>{props.value}</Link>
  },
  { Header: 'Crawl Type',
    accessor: 'crawl_type'
  },
  {
    Header: 'Status',
    accessor: 'status'
  },
  {
    Header: 'Browsers',
    accessor: 'num_browsers',
  },
  {
    Header: 'Tabs',
    accessor: 'num_tabs',
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
                                  getTdProps={getTdProps}/>);

  return (
    <div>
      <h1 className='uk-text-center'>Select Crawl To View</h1>
      {crawlTable}
    </div>
  );
}

SelectCrawls.propTypes = {
  crawls: PropTypes.instanceOf(Map).isRequired,
  removeCrawl: PropTypes.func.isRequired
};



import React from 'react';
import * as PropTypes from 'prop-types';
import { Crawl as CrawlRecord } from '../../reducers/crawls';
import ListGroupItem from 'react-bootstrap/ListGroupItem';
import Table from 'react-bootstrap/Table';
import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';

export default function Crawl({ crawl, crawlActions }) {
  return (
    <ListGroupItem>
      <Card>
        <Card.Header>Crawl: {crawl.id}</Card.Header>
        <Card.Body>
          <Table>
            <thead>
              <tr>
                <th>Type</th>
                <th>Running</th>
                <th>Status</th>
                <th>Num Browsers</th>
                <th>Num Tabs</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>{crawl.crawlType}</td>
                <td>{crawl.running ? 'yes' : 'no'}</td>
                <td>{crawl.numBrowsers}</td>
                <td>{crawl.numTabs}</td>
                <td>{crawl.status}</td>
              </tr>
            </tbody>
          </Table>
        </Card.Body>
        <Card.Body>
          <Button onClick={() => crawlActions.getCrawlInfo(crawl.id)}>
            Update
          </Button>
        </Card.Body>
      </Card>
    </ListGroupItem>
  );
}

Crawl.propTypes = {
  crawl: PropTypes.instanceOf(CrawlRecord).isRequired,
  crawlActions: PropTypes.object.isRequired
};

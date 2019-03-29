import React, { Component } from 'react';
import * as PropTypes from 'prop-types';
import { CrawlRecord } from '../../reducers/crawls';
import ListGroupItem from 'react-bootstrap/ListGroupItem';
import Table from 'react-bootstrap/Table';
import Card from 'react-bootstrap/Card';
import Button from 'react-bootstrap/Button';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

export default class Crawl extends Component {
  static propTypes = {
    crawl: PropTypes.instanceOf(CrawlRecord).isRequired,
    crawlActions: PropTypes.object.isRequired
  };

  updateInfo = () => this.props.crawlActions.getCrawlInfo(this.props.crawl.id);
  removeCrawl = () => this.props.crawlActions.removeCrawl(this.props.crawl.id);

  // shouldComponentUpdate(nextProps, nextState, nextContext) {
  //   return this.props.crawl !== nextProps.crawl;
  // }

  render() {
    const { crawl } = this.props;
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
                  <td>{crawl.crawl_type}</td>
                  <td>{crawl.running ? 'yes' : 'no'}</td>
                  <td>{crawl.status || 'new'}</td>
                  <td>{crawl.num_browsers}</td>
                  <td>{crawl.num_tabs}</td>
                </tr>
              </tbody>
            </Table>
          </Card.Body>
          <Card.Body>
            <Row>
              <Col>
                <Button onClick={this.updateInfo}>Update</Button>
              </Col>
              <Col>
                <Button onClick={this.removeCrawl}>Remove</Button>
              </Col>
            </Row>
          </Card.Body>
        </Card>
      </ListGroupItem>
    );
  }
}

import React from 'react';
import Layout from '../components/Layout';
import { Row } from 'reactstrap';

export default function Home({ location }) {
  return (
    <Layout location={location} fluid>
      <Row>
        <p>hi</p>
      </Row>
    </Layout>
  );
}

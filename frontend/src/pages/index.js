import React from 'react';
import { Row, Col } from 'reactstrap';
import Layout from '../containers/Layout';
import Crawls from '../containers/Crawls';

export default function Home({ location }) {
  return (
    <Layout location={location}>
      <Crawls />
    </Layout>
  );
}

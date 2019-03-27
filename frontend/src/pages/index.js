import React from 'react';
import Layout from '../components/Layout';
import Crawls from '../components/Crawls';

export default function Home({ location }) {
  return (
    <Layout location={location}>
      <Crawls />
    </Layout>
  );
}

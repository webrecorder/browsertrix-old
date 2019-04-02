import { hot } from 'react-hot-loader/root';
import React from 'react';
import { Route, Switch } from 'react-router-dom';
import Header from '../components/Header';
import Crawls from '../components/Crawls';
import CrawlCreator from '../components/CrawlCreator';
import Crawl from '../components/Crawl';

function AllCrawls(props) {
  return <Crawls {...props} />;
}

function CreateCrawl(props) {
  return (
    <div className='uk-container'>
      <CrawlCreator message={'Create a new crawl!'} />
    </div>
  );
}

function viewCrawl(props) {
  return <Crawl {...props} />;
}

function App() {
  return (
    <>
      <Header />
      <div className='route-container'>
        <Switch>
          <Route exact path='/' render={AllCrawls} />
          <Route exact path='/createCrawl' render={CreateCrawl} />
          <Route exact path='/crawl/:crawlid' render={viewCrawl} />
        </Switch>
      </div>
    </>
  );
}

let ExportedApp = App;

if (process.env.NODE_ENV === 'development') {
  ExportedApp = hot(App);
}

export default ExportedApp;

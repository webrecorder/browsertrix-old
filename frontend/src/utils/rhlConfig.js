import { setConfig, hot } from 'react-hot-loader';
if (process.env.NODE_ENV === 'development') {
  setConfig({
    logLevel: 'debug'
    // ignoreSFC: true, // RHL will be __completely__ disabled for SFC
    // pureRender: true // RHL will not change render method
  });
}

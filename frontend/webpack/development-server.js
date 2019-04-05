const path = require('path');
const createServer = require('fastify');
const webpack = require('webpack');
const HMR = require('fastify-webpack-hmr');
const config = require('./webpack.config');

const fastify = createServer({
  logger: false
});

const staticPath = path.join(__dirname, '..', 'public');

fastify
  .register(HMR, {
    compiler: webpack(config),
    webpackDev: {
      logLevel: 'debug'
    }
  })
  .register(require('fastify-static'), {
    root: staticPath,
    prefix: '/'
  });

async function run() {
  const listeningOn = await fastify.listen(8001);
  console.log(
    `Dev server listening on\n${
      listeningOn.startsWith('http://127.0.0.1')
        ? listeningOn.replace('http://127.0.0.1', 'http://localhost')
        : listeningOn
    }`
  );
  console.log(fastify.printRoutes());
}

run().catch(error => {
  console.error(error);
});

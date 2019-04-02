const path = require('path');
const webpack = require('webpack');

const rootPath = path.join(__dirname, '..');
const staticPath = path.join(path.join(rootPath, '..'), 'static');
const srcPath = path.join(rootPath, 'src');
const entryPath = path.join(srcPath, 'root.js');
const hotConf =
  'webpack-hot-middleware/client?path=__webpack_hmr&reload=true&overlay=false';

const mode = process.env.NODE_ENV || 'development';
const production = mode === 'production';

const plugins = [
  new webpack.NamedModulesPlugin(),
  new webpack.IgnorePlugin({
    contextRegExp: /moment$/
  }),
  new webpack.DefinePlugin({
    'process.env.NODE_ENV': JSON.stringify(mode),
    __DEV__: JSON.stringify(!production)
  }),
  new webpack.NoEmitOnErrorsPlugin()
];

const jsLoader = {
  loader: 'babel-loader',
  options: {
    cacheDirectory: true,
    babelrc: false,
    presets: [
      '@babel/preset-react',
      [
        '@babel/preset-env',
        {
          loose: true,
          debug: false,
          modules: false,
          useBuiltIns: false,
          targets: {
            chrome: '70',
            firefox: '66'
          }
        }
      ]
    ],
    plugins: [['@babel/plugin-proposal-class-properties', { loose: true }]]
  }
};

if (mode === 'development') {
  plugins.push(new webpack.HotModuleReplacementPlugin());
  jsLoader.options.plugins.unshift('react-hot-loader/babel');
} else {
  jsLoader.options.plugins.push([
    'transform-react-remove-prop-types',
    {
      ignoreFilenames: ['node_modules']
    }
  ]);
}

module.exports = {
  mode: mode,
  context: rootPath,
  entry: production ? entryPath : [entryPath, hotConf],
  output: {
    path: production ? staticPath : path.join(rootPath, 'public'),
    filename: 'app.js',
    publicPath: '/'
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        use: [jsLoader]
      },
      {
        test: /\.s[ac]ss$/,
        use: [
          {
            loader: 'style-loader',
            options: {
              hmr: true
            }
          },
          {
            loader: 'css-loader'
          },
          {
            loader: 'sass-loader',
            options: {
              includePaths: [
                'node_modules/uikit/src/scss',
                'node_modules/react-toastify/scss/main'
              ],
              precision: 8
            }
          }
        ]
      },
      {
        test: /\.(eot|otf|ttf|woff(2)?)(\?.*)?$/,
        use: [
          {
            loader: 'url-loader'
          }
        ]
      }
    ]
  },
  resolve: {
    extensions: ['.mjs', '.js', '.jsx', '.wasm', '.json', '.ts', '.tsx'],
    alias: {
      'react-dom': require.resolve('@hot-loader/react-dom')
    }
  },
  plugins
};

const path = require('path');
const webpack = require('webpack');

const rootPath = path.join(__dirname, '..');
const srcPath = path.join(rootPath, 'src');
const entryPath = path.join(srcPath, 'root.js');
const hotConf =
  'webpack-hot-middleware/client?path=__webpack_hmr&reload=true&overlay=false';

const mode = process.env.NODE_ENV || 'development';
const production = mode === 'production';

module.exports = {
  mode: 'development',
  context: rootPath,
  entry: [entryPath, hotConf],
  output: {
    path: path.join(rootPath, 'public'),
    filename: 'app.js',
    publicPath: '/'
    // devtoolModuleFilenameTemplate: info =>
    //   path.resolve(info.absoluteResourcePath).replace(/\\/g, '/')
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        use: [
          {
            loader: 'babel-loader',
            options: {
              cacheDirectory: true
            }
          }
        ]
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
  plugins: [
    new webpack.NamedModulesPlugin(),
    new webpack.IgnorePlugin({
      contextRegExp: /moment$/
    }),
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': JSON.stringify(mode),
      __DEV__: JSON.stringify(!production)
    }),
    new webpack.HotModuleReplacementPlugin(),
    new webpack.NoEmitOnErrorsPlugin()
  ]
};

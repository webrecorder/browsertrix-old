module.exports = {
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
  plugins: [
    // ['@babel/plugin-proposal-decorators', { legacy: true }],
    'react-hot-loader/babel',
    ['@babel/plugin-proposal-class-properties', { loose: true }]
  ]
};

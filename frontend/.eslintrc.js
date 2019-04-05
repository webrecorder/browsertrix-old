module.exports = {
  extends: ['plugin:prettier/recommended', 'prettier/react'],
  parser: 'babel-eslint',
  parserOptions: {
    ecmaVersion: 10
  },
  env: {
    browser: true,
    node: true
  }
};

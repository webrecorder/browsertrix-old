module.exports = {
  siteMetadata: {
    title: 'things',
    siteUrl: 'https://blah.io',
    description: 'stuff',
    author: 'more stuff'
  },
  plugins: [
    {
      resolve: 'gatsby-plugin-sass',
      options: {
        includePaths: ['node_modules/bootstrap/scss'],
        precision: 10
      }
    },
  ]
};

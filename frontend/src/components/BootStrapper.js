import 'bootstrap/dist/css/bootstrap.min.css';
import React from 'react'
import * as PropTypes from 'prop-types'

export default function BootStrapper ({
  meta,
  image,
  title,
  description,
  slug
}) {
  const {
    site: { siteMetadata }
  } = useStaticQuery(query)
  const metaDescription = description || siteMetadata.description
  const metaImage = image ? `${siteMetadata.siteUrl}/${image}` : null
  const url = `${siteMetadata.siteUrl}${slug}`
  const hMeta = [
    { name: 'description', content: metaDescription },
    { property: 'og:url', content: url },
    { property: 'og:title', content: title || siteMetadata.title },
    { property: 'og:description', content: metaDescription },
    { name: 'twitter:card', content: 'summary' },
    { name: 'twitter:creator', content: siteMetadata.social.twitter.handle },
    { name: 'twitter:title', content: title || siteMetadata.title },
    { name: 'twitter:description', content: metaDescription }
  ]
  if (metaImage) {
    hMeta.push(
      { property: 'og:image', content: metaImage },
      { name: 'twitter:image', content: metaImage }
    )
  }
  const hTitle = title
    ? {
        titleTemplate: `%s — ${siteMetadata.title}`,
        title
      }
    : { title: siteMetadata.title }
  return (
    <Helmet
      htmlAttributes={{ lang: 'en' }}
      {...hTitle}
      meta={hMeta.concat(meta)}
    />
  )
}

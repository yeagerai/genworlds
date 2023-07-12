import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import classnames from 'classnames';
import HubspotForm from 'react-hubspot-form'

import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <div class="row">
          <div className={classnames("col","col--8", styles.heroText)}>
            <h1 className="hero__title">{siteConfig.title}</h1>
            <p className="hero__subtitle">{siteConfig.tagline}</p>
            <div className={styles.buttons}>
              <Link
                className="button button--secondary button--lg"
                to="/docs/getting-started">
                Getting Started
              </Link>
            </div>
          </div>
          <div class="col col--4">
            <div className={classnames("card", styles.heroCard)}>
              <div className={classnames("card__header", styles.heroCardHeader)}>
                <h3>Join Now</h3>
                <p>We are building an ecosystem of Generative AI applications. Join the community to be the first to learn about what others are building.</p>
              </div>
              <div class="card__body">

                <HubspotForm
                  portalId='20388104'
                  formId='74307b02-d32b-4668-a125-a80460ae4428'
                  onSubmit={() => console.log('Submit!')}
                  onReady={(form) => console.log('Form ready!')}
                  loading={<div>Loading...</div>}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="{siteConfig.tagline}">
      <HomepageHeader />
      <main className={styles.content}>
        <section className={styles.description}>
          <div className={classnames("row", styles.descriptionRow)}>
            <div className="col col--6">
              <h3>Use Case Highlight: All-In RoundTable</h3>
              <p>Imagine summoning history’s brightest minds for a group discussion on anything. Ask them for help or bounce ideas off them. RoundTable is not just a Chatgpt wrapper, it's a team of AI agents acting independently with specific personalities, memories and expertise.</p>
              <Link
                className="button button--primary button--lg"
                to="/docs/getting-started">
                Try now! 
              </Link>
            </div>
            <div className={classnames("col col--6", styles.imgColumn)}>
              <div className={styles.videoContainer}>
                <iframe src="https://yeager.proj.nakimasolutions.com/?tankId=123" frameborder="0" allowtransparency="true" scrolling="no" data-dashlane-frameid="575"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen></iframe>
              </div>
            </div>
          </div>
        </section>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}

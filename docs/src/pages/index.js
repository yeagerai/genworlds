import React from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import classnames from 'classnames';
import HubspotForm from 'react-hubspot-form'

import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import HomepageQuotes from '@site/src/components/HomepageQuotes';

import styles from './index.module.css';
// Import slick-carousel css
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <div className="row">
          <div className={classnames("col", "col--8", styles.heroText)}>
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
          <div className="col col--4">
            <div className={classnames("card", styles.heroCard)}>
              <div className={classnames("card__header", styles.heroCardHeader)}>
                <h3>Join Now</h3>
                <p>We are building an ecosystem of Generative AI applications. Join the community to be the first to learn about what others are building.</p>
              </div>
              <div className="card__body">

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
  const { siteConfig } = useDocusaurusContext();
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
                to="https://replit.com/@jmlago/GenworldsBase?v=1">
                Try now!
              </Link>
            </div>
            <div className={classnames("col col--6", styles.imgColumn)}>
              <div className={styles.videoContainer}>
                <iframe src="https://yeager.proj.nakimasolutions.com/?tankId=123" allowtransparency="true" scrolling="no" data-dashlane-frameid="575"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen></iframe>
              </div>
            </div>
          </div>
        </section>
        <HomepageFeatures />
        <section className={styles.features}>
          <div className="container">
            <div class="alert alert--warning margin-vert--md" role="alert">
              🧬🌍 GenWorlds is an early stage product in active development.  If you spot any issues or bugs


              <div className={styles.buttons}>
                <Link
                  className="button button--primary button--xs margin-top--md"
                  to="https://github.com/yeagerai/genworlds/issues">
                  Let us know
                </Link>
              </div>

            </div></div>

        </section>


        <section className={styles.features}>
          <div className="card">
            <div className="card__header">
              <div class="row">
                <div class="col col--12">
                  <h4 class="fs-2x text-gray-800 w-bolder mt-8">Join our Community 🚀</h4>
                  <div class="my-4">

                    <p class="fw-semibold fs-4 text-gray-600 mb-2">GenWorlds is not just an AI platform;
                      it's a vibrant community of developers, AI enthusiasts, and innovators who are
                      shaping the future of AI. We value collaboration, innovation, knowledge sharing, and
                      mutual growth.
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <div className="card__body">
              <div className="row">
                <div className={classnames("col col--6", styles.quotesContainer)}>
                  <HomepageQuotes />
                </div>
                <div className={classnames("col col--6", styles.quotesContainer)}>
                  <div className="row">

                    <div className="col col--6 padding-horiz--10 margin-top--10">
                      <h4>Contribute on GitHub</h4>
                      <p>Love GenWorlds? Help us make it better! Our GitHub repository is always open for
                        contributions. You can help us improve GenWorlds, create new GenAI applications,
                        or
                        even
                        develop new features.</p>
                      <div className={styles.buttons}>
                        <Link
                          className="button button--secondary button--lg"
                          to="/docs/getting-started">
                          Getting Started
                        </Link>
                      </div>
                    </div>

                    <div className="col col--6 padding-horiz--10  margin-top--10">
                      <h4>Discord Community</h4>
                      <p>Join our Discord Community! Engage in stimulating discussions, get updates about
                        the
                        latest GenWorlds features, participate in hackathons, and learn from the shared
                        knowledge of a global community.</p>
                      <div className={styles.buttons}>
                        <Link
                          className="button button--secondary button--lg"
                          to="/docs/getting-started">
                          Getting Started
                        </Link>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}

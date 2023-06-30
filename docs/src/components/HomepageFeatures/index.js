import React from 'react';
import clsx from 'clsx';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Customizable Interactive Environments',
    Svg: require('@site/static/img/openmoji_globe_with_meridians.svg').default,
    description: (
      <>
        Design unique GenWorld environments, tailored to your project's needs, 
        filled with interactive objects and potential actions for your agents.
      </>
    ),
  },
  {
    title: 'Goal-Oriented Generative Autonomous Agents',
    Svg: require('@site/static/img/openmoji_bullseye.svg').default,
    description: (
      <>
        Utilize AI agents powered by Langchain that are driven by specific objectives 
        and can be easily extended and programmed to simulate complex behaviors 
        and solve intricate problems.
      </>
    ),
  },
  {
    title: 'Scalability',
    Svg: require('@site/static/img/openmoji_high_voltage.svg').default,
    description: (
      <>
        Benefit from threading and WebSocket communication for real-time interaction between agents, 
        ensuring the platform can easily scale up as your needs grow.
      </>
    ),
  },
];

function Feature({Svg, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}

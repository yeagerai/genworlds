import React from 'react';
import clsx from 'clsx';
import styles from './styles.module.css';
import classnames from 'classnames';

const FeatureList = [
  {
    title: 'Customizable Environments',
    Svg: require('@site/static/img/emojis/openmoji_bullseye.svg').default,
    description: (
      <>
        Design every aspect of your world, from the AI Agents and objects to their goals and memories.
      </>
    ),
  },
  {
    title: 'Scalable Architecture',
    Svg: require('@site/static/img/emojis/1F3D7.svg').default,
    description: (
      <>
        Our architecture adjusts with your needs. From WebSocket to multiple interfaces, we scale for optimal performance regardless of the task at hand.
      </>
    ),
  },
  {
    title: 'Plug-n-Play',
    Svg: require('@site/static/img/emojis/openmoji_bricks.svg').default,
    
    description: (
      <>
        A repository of ready-made memories and tools at your disposal designed to be easily deployed within your GenWorld.
      </>
    ),
  },
  {
    title: ' Cognitive Processes',
    Svg: require('@site/static/img/emojis/openmoji_brain.svg').default,
    description: (
      <>
        Choose the brain for your agents. From Tree of Thoughts to Chain of Thoughts and AutoGPT, each agent can think differently, aligning with their purpose.
      </>
    ),
  },
  {
    title: 'Coordination Protocols',
    Svg: require('@site/static/img/emojis/openmoji_heart.svg').default,
    description: (
      <>
        Pick from a range of organization processes for agent coordination, such as token-bearer or serialized processing, ensuring efficient task execution.


      </>
    ),
  },
  {
    title: '3rd Party GenWorld Integration',
    Svg: require('@site/static/img/emojis/openmoji_alien_monster.svg').default,
    description: (
      <>
        Leverage the power of the marketplace. Seamlessly connect existing agents and worlds to amplify your GenWorld's capabilities.
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
        
        <div className= {styles.title}>
          <h2>Features</h2>
        </div>
        <div className="row text--center">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}

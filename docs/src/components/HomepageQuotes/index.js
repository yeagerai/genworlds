import React from 'react';
import clsx from 'clsx';
import styles from './styles.module.css';
import classnames from 'classnames';
import Slider from "react-slick";

import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";

const QuoteList = [
  {
    name: 'Harrison Chase',
    avatar: "https://avatars.githubusercontent.com/u/11986836?v=4",
    title: 'Founder @ LangChain',
    quote: (
      <>
        The Yeager.ai team keeps shipping.  Really exciting to see how their GenWorlds framework brings coordinating AI agents to life built on LangChain.  Coordinating Agents are a paradigm shift in GenAI and I'm pleased to see the Yeager team using LangChain to do it
      </>
    ),
  },
  {
    name: 'Andre Zayarni',
    avatar: "https://avatars.githubusercontent.com/u/926368?v=4",
    title: 'CEO of Qdrant',
    quote: (
      <>
        We are thrilled that Qdrant is Yeager's vector database and similarity search engine of choice. Now, GenWorlds' AI Agents can be trained on specific sources of data, such as Youtube transcripts. It is fantastic to see how they optimize LLM context windows by using Qdrant vector stores for long-term memory and LLMs for short-term memory. This is exactly how we envisioned our platform would be used in robust GenAI Applications.
      </>
    ),
  },
];

const Quote = ({ avatar, name, title, quote }) => (
  <div className="container">
    <div className="row padding--md ">
      <div className={classnames("avatar", styles.quoteAvatar)}>
        <img className="avatar__photo avatar__photo--xl" src={avatar} alt={name} />
        <div className="avatar__intro">
          <div className="avatar__name">{name}</div>
          <small className="avatar__subtitle">
            {title}
          </small>
        </div>
      </div>
      <div className="card__body">
        {quote}
      </div>
    </div>
  </div>
);


export default function HomepageQuotes() {
  var settings = {
    dots: true,
    infinite: true,
    speed: 5000,
    slidesToShow: 1,
    slidesToScroll: 1,
    initialSlide: 1,
    autoplay: true,
  };

  return (

    <div className={classnames("col col--12", styles.quotesContainer)}>
      <div className="card shadow--lw">
        <Slider {...settings}>
          {QuoteList.map((props, idx) => (
            <Quote key={idx} {...props} />
          ))}
        </Slider>
      </div>
    </div>
  );
}

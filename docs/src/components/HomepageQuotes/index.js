import React from 'react';
import clsx from 'clsx';
import styles from './styles.module.css';
import classnames from 'classnames';
import Slider from "react-slick";

import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";

const QuoteList = [
  {
    name: 'Harrisson Chase',
    avatar: "https://avatars.githubusercontent.com/u/11986836?v=4",
    title: 'Founder @ LangChain',
    quote: (
      <>
        Our users so far have mostly been developers, but we're excited for yAgents to bring the LangChain ecosystem to a whole new audience. We are excited for Yeager.ai to be building on our framework and can't wait to see what they release next. This partnership is a perfect example of how collaboration and composability can drive innovation and make cutting-edge technology accessible to a wider audience.</>
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
    speed: 500,
    slidesToShow: 1,
    slidesToScroll: 1,
    initialSlide: 0,

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

import logging
import os
import colorlog


class LoggingFactory:
    colors = ["red", "yellow", "blue", "purple", "cyan", "green", "white"]
    color_index = 0
    loggers = {}

    @classmethod
    def get_logger(cls, name, level=None):
        # If a logger with this name already exists, return it
        if name in cls.loggers:
            return cls.loggers[name]

        # Create a handler for the logger
        handler = colorlog.StreamHandler()
        handler.setFormatter(
            colorlog.ColoredFormatter(
                # f'%(log_color)s%(levelname)-8s%(reset)s %({cls.colors[cls.color_index]})s[%(name)s] %(message)s'
                f"%({cls.colors[cls.color_index]})s[%(name)s] %(message)s"
            )
        )

        # Create a logger
        logger = colorlog.getLogger(name)
        logger.addHandler(handler)

        # Set the logging level
        if level == None:
            level = os.getenv("LOGGING_LEVEL", logging.INFO)
        logger.setLevel(level)
        logger.debug(f"Created logger {name} with level {logger.level}")

        # Cache the logger instance
        cls.loggers[name] = logger

        # Update color index for next logger
        cls.color_index = (cls.color_index + 1) % len(cls.colors)

        return logger

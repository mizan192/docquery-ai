import logging
import sys


def setup_logging():
    # create logger for entire app
    logger = logging.getLogger("docquery")
    logger.setLevel(logging.INFO)

    # log format - shows time, level, and message
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # log to terminal
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


# single logger instance used across entire app
logger = setup_logging()

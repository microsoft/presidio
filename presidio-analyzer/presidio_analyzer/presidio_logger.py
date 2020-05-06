import logging
import os
import sys


class PresidioLogger:
    """A wrapper class for logger"""
    def __init__(self, logger_name="presidio", default_level="INFO"):
        if logger_name:
            logger = logging.getLogger(logger_name)
        else:
            logger = logging.getLogger()

        if not logger.handlers:
            loglevel = os.environ.get("LOG_LEVEL", default_level)
            ch = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '[%(asctime)s][%(name)s][%(levelname)s]%(message)s')
            ch.setFormatter(formatter)
            logger.addHandler(ch)
            logger.setLevel(loglevel)

        self.__logger = logger

    def set_level(self, level):
        self.__logger.setLevel(level)

    def debug(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'DEBUG'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)
        """
        self.__logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'INFO'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.info("Houston, we have a %s", "interesting problem", exc_info=1)
        """
        self.__logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'WARNING'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.warning("Houston, we have a %s", "bit of a problem", exc_info=1)
        """
        self.__logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'ERROR'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.error("Houston, we have a %s", "major problem", exc_info=1)
        """
        self.__logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'CRITICAL'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.critical("Houston, we have a %s", "major disaster", exc_info=1)
        """
        self.__logger.critical(msg, *args, **kwargs)

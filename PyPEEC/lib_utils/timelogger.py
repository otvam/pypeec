"""
Module for handle the logging (with timer for elapsed time).
Provide a class for timing (and logging) code blocks.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) 2023 - Dartmouth College"

import time
import datetime
import logging
from PyPEEC import config

# get config
LOGGING_LEVEL = config.LOGGING_LEVEL
LOGGING_INDENTATION = config.LOGGING_INDENTATION
LOGGING_COLOR = config.LOGGING_COLOR
LOGGING_CL_DEBUG = config.LOGGING_CL_DEBUG
LOGGING_CL_INFO = config.LOGGING_CL_INFO
LOGGING_CL_WARNING = config.LOGGING_CL_WARNING
LOGGING_CL_ERROR = config.LOGGING_CL_ERROR
LOGGING_CL_CRITICAL = config.LOGGING_CL_CRITICAL
LOGGING_CL_RESET = config.LOGGING_CL_RESET

# global timestamp (constant over the complete run)
LOGGING_GLOBAL_TIMESTAMP = time.time()

# logging indentation level (updated inside the blocks)
LOGGING_CURRENT_LEVEL = 0


def _get_format_timestamp(timestamp):
    """
    Format a timestamp into a string.
    """

    timestamp = datetime.datetime.fromtimestamp(timestamp)
    timestamp = timestamp.strftime("%H:%M:%S,%f")[:-3]

    return timestamp


def _get_format_duration(timestamp):
    """
    Compute the elapsed time and format the duration into a string.
    """

    duration = time.time()-timestamp
    duration = datetime.datetime.utcfromtimestamp(duration)
    duration = duration.strftime("%H:%M:%S,%f")[:-3]

    return duration


class _DeltaTimeFormatter(logging.Formatter):
    """
    Class for adding elapsed time to a logger.
    """

    def __init__(self, fmt):
        """
        Constructor.
        Create a timer.
        """

        # call parent constructor
        super().__init__(fmt)

        # define the color formatters
        self.fmt_color = {
            logging.DEBUG: logging.Formatter(LOGGING_CL_DEBUG + fmt + LOGGING_CL_RESET),
            logging.INFO: logging.Formatter(LOGGING_CL_INFO + fmt + LOGGING_CL_RESET),
            logging.WARNING: logging.Formatter(LOGGING_CL_WARNING + fmt + LOGGING_CL_RESET),
            logging.ERROR: logging.Formatter(LOGGING_CL_ERROR + fmt + LOGGING_CL_RESET),
            logging.CRITICAL: logging.Formatter(LOGGING_CL_CRITICAL + fmt + LOGGING_CL_RESET),
        }

        # define the black formatter
        self.fmt_black = logging.Formatter(fmt)

    def format(self, record):
        """
        Format a record to a string.
        Add the elapsed time.
        """

        # get log
        lvl = record.levelno
        msg = record.msg

        # add the elapsed time to the log record
        record.timestamp = _get_format_timestamp(LOGGING_GLOBAL_TIMESTAMP)
        record.duration = _get_format_duration(LOGGING_GLOBAL_TIMESTAMP)

        # get the message padding for the desired indentation
        pad = " " * (LOGGING_CURRENT_LEVEL*LOGGING_INDENTATION)

        # add the padding to the message
        record.msg = pad + msg

        # get the formatter
        if LOGGING_COLOR:
            msg = self.fmt_color[lvl].format(record)
        else:
            msg = self.fmt_black.format(record)

        return msg


class BlockTimer:
    """
    Class for timing block of code.
    Uses enter and exit magic methods.
    Display the results with a logger.
    """

    def __init__(self, logger, name):
        """
        Constructor.
        Assign block name and logger.
        Create a timer.
        """

        self.logger = logger
        self.name = name
        self.timestamp = None

    def __enter__(self):
        """
        Enter magic method.
        Reset the timer and log the results.
        """

        # start the timer and display
        self.timestamp = time.time()
        self.logger.info(self.name + " : enter : timing")

        # increase the indentation of the block
        global LOGGING_CURRENT_LEVEL
        LOGGING_CURRENT_LEVEL += 1

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Exit magic method.
        Get the elapsed time and log the results.
        """

        # restore the indentation to the previous state
        global LOGGING_CURRENT_LEVEL
        LOGGING_CURRENT_LEVEL -= 1

        # stop the timer and display
        duration = _get_format_duration(self.timestamp)
        self.logger.info(self.name + " : exit : " + duration)


def log_exception(logger, ex):
    """
    Log an exception (type, message, and trace).
    Remove the context from the exception before the logging.
    """

    # remove the expression context
    ex.__context__ = None

    # get the exception data
    ex_type = type(ex)
    ex_trace = ex.__traceback__
    ex_name = ex.__class__.__name__

    # log the exception
    logger.error("check error : " + ex_name, exc_info=(ex_type, ex, ex_trace))


def get_logger(name):
    """
    Get a logger with a name.
    Display elapsed time, time, name, level, and message.

    The elapsed time can be measured with respect to:
        - the time the module is imported
        - the time the logger is called/created

    The elapsed time measurement method and the logging level are specified in the config.
    """

    # get the logger (only one logger per name is allowed)
    logger = logging.getLogger(name)
    if len(logger.handlers) != 0:
        raise RuntimeError("duplicated logger name")

    # get the formatter
    fmt = _DeltaTimeFormatter("%(duration)s : %(name)-12s: %(levelname)-12s : %(message)s")

    # get the handle
    handler = logging.StreamHandler()
    handler.setFormatter(fmt)

    # get the logger
    logger.setLevel(LOGGING_LEVEL)
    logger.addHandler(handler)

    return logger

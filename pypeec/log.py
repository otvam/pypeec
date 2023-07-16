"""
Module for handling the logging.
    - Use a global timer to measure the elapsed time.
    - Provide a class for timing (and logging) code blocks.
    - Measure duration with local timers.
    - Log exceptions.

"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os
import time
import datetime
import threading
import logging
from pypeec import config

# get config
FORMAT = config.LOGGING_OPTIONS.FORMAT
LEVEL = config.LOGGING_OPTIONS.LEVEL
INDENTATION = config.LOGGING_OPTIONS.INDENTATION
EXCEPTION_TRACE = config.LOGGING_OPTIONS.EXCEPTION_TRACE
USE_COLOR = config.LOGGING_OPTIONS.USE_COLOR
DEF_COLOR = config.LOGGING_OPTIONS.DEF_COLOR

# global timestamp (constant over the complete run)
GLOBAL_TIMESTAMP = time.time()

# logging indentation level (updated inside the blocks)
CURRENT_LEVEL = 0


def _get_fmt(color, reset):
    """
    Get a logging formatter.
    """

    if (color is None) and (reset is None):
        fmt = logging.Formatter(FORMAT["LOGGER"])
    else:
        fmt = logging.Formatter("\x1b" + color + FORMAT["LOGGER"] + "\x1b" + reset)

    return fmt


def _get_compute_timestamp():
    """
    Get the current time.
    """

    timestamp = datetime.datetime.today()

    return timestamp


def _get_compute_duration(timestamp):
    """
    Compute the elapsed time.
    """

    duration = time.time()-timestamp
    duration = datetime.timedelta(seconds=duration)

    return duration


def _get_format_timestamp(timestamp):
    """
    Format a timestamp into a string.
    """

    timestamp_str = timestamp.strftime(FORMAT["TIMESTAMP_FMT"])
    timestamp_str = timestamp_str[0:len(timestamp_str)-FORMAT["TIMESTAMP_TRC"]]

    return timestamp_str


def _get_format_duration(duration):
    """
    Format the duration into a string.
    """

    # get reference timestamp
    timestamp = datetime.datetime.utcfromtimestamp(0)

    # convert timestamp to duration
    timestamp = timestamp+duration

    # format timestamp
    duration_str = timestamp.strftime(FORMAT["DURATION_FMT"])
    duration_str = duration_str[0:len(duration_str)-FORMAT["DURATION_TRC"]]

    return duration_str


class _DeltaTimeFormatter(logging.Formatter):
    """
    Class for adding elapsed time to a logger.
    """

    def __init__(self):
        """
        Constructor.
        Create a timer.
        """

        # call parent constructor
        super().__init__()

        # define the color formatters
        self.fmt_color = {
            logging.DEBUG: _get_fmt(DEF_COLOR["CL_DEBUG"], DEF_COLOR["CL_RESET"]),
            logging.INFO: _get_fmt(DEF_COLOR["CL_INFO"], DEF_COLOR["CL_RESET"]),
            logging.WARNING: _get_fmt(DEF_COLOR["CL_WARNING"], DEF_COLOR["CL_RESET"]),
            logging.ERROR: _get_fmt(DEF_COLOR["CL_ERROR"], DEF_COLOR["CL_RESET"]),
            logging.CRITICAL: _get_fmt(DEF_COLOR["CL_CRITICAL"], DEF_COLOR["CL_RESET"]),
        }

        # define the black formatter
        self.fmt_black = _get_fmt(None, None)

    def format(self, record):
        """
        Format a record to a string.
        Add the elapsed time.
        """

        # get log
        lvl = record.levelno
        msg = record.msg

        # add the elapsed time to the log record
        timestamp = _get_compute_timestamp()
        duration = _get_compute_duration(GLOBAL_TIMESTAMP)
        record.timestamp = _get_format_timestamp(timestamp)
        record.duration = _get_format_duration(duration)

        # add the process and thread id to the log record
        record.process_id = os.getpid()
        record.thread_id = threading.get_native_id()

        # get the message padding for the desired indentation
        pad = " " * (CURRENT_LEVEL*INDENTATION)

        # add the padding to the message
        record.msg = pad + msg

        # get the formatter
        if USE_COLOR:
            msg = self.fmt_color[lvl].format(record)
        else:
            msg = self.fmt_black.format(record)

        return msg


class BlockTimer:
    """
    Class for timing a block of code.
        - Uses enter and exit magic methods.
        - Display the results with a logger.

    Parameters
    ----------
    logger : logger
        Logger object instance.
    name : string
        Name of the code block.
    """

    def __init__(self, logger, name):
        """
        Constructor.
        Set the logger.
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
        global CURRENT_LEVEL
        CURRENT_LEVEL += 1

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Exit magic method.
        Get the elapsed time and log the results.
        """

        # restore the indentation to the previous state
        global CURRENT_LEVEL
        CURRENT_LEVEL -= 1

        # stop the timer and display
        duration = _get_compute_duration(self.timestamp)
        duration = _get_format_duration(duration)
        self.logger.info(self.name + " : exit : " + duration)


class BlockIndent:
    """
    Class for indenting a block of code.
        - Uses enter and exit magic methods.
        - Display the results with a logger.
    """

    def __init__(self):
        """
        Constructor.
        """

        pass

    def __enter__(self):
        """
        Enter magic method.
        Increase the indentation of the block.
        """

        global CURRENT_LEVEL
        CURRENT_LEVEL += 1

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Exit magic method.
        Restore the indentation to the previous state.
        """

        global CURRENT_LEVEL
        CURRENT_LEVEL -= 1


def log_exception(logger, ex):
    """
    Log an exception.
        - Log the exception type, message, and trace.
        - Remove the context from the exception before the logging.

    Parameters
    ----------
    logger : logger
        Logger object instance.
    ex : exception
        Exception to be logged.
    """

    # remove the expression context
    ex.__context__ = None

    # get the exception data
    name = ex.__class__.__name__

    # log the exception
    if EXCEPTION_TRACE:
        logger.error("exception error : " + name, exc_info=ex)
    else:
        logger.error("exception error : " + name + "\n" + str(ex))


def get_timer():
    """
    Get a timestamp with the current time.

    Returns
    -------
    timestamp : timestamp
        Timestamp with the current time.
    """

    timestamp = time.time()

    return timestamp


def get_duration(timestamp):
    """
    Get the elapsed time with respect to a timestamp.

    Parameters
    ----------
    timestamp : timestamp
        Timestamp with the reference time.

    Returns
    -------
    duration : duration
        Duration object with the elapsed time.
    fmt : string
        String with the formatted elapsed time.
    """

    duration = _get_compute_duration(timestamp)
    fmt = _get_format_duration(duration)

    return duration, fmt


def get_logger(name):
    """
    Get a logger with a specified name.

    Parameters
    ----------
    name : string
        Name of the logger to be returned.
        If the logger does not exist, the logger is created.
        If the logger does exist, the logger is returned.

    Returns
    -------
    logger : logger
        Logger object instance.
    """

    # get the logger
    logger = logging.getLogger(name)

    # create the logger (if not already done)
    if len(logger.handlers) == 0:
        # get the formatter
        fmt = _DeltaTimeFormatter()

        # get the handle
        handler = logging.StreamHandler()
        handler.setFormatter(fmt)

        # prevent duplicated log messages
        logger.propagate = False

        # set the level
        logger.setLevel(LEVEL)

        # get the logger
        logger.addHandler(handler)

    return logger

"""
Module for handle the logging (with timer for elapsed time).
Provide a class for timing (and logging) code blocks.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import time
import datetime
import logging
from pypeec.lib_utils import config

# get config
LEVEL = config.LOGGING_OPTIONS["LEVEL"]
INDENTATION = config.LOGGING_OPTIONS["INDENTATION"]
FORMAT = config.LOGGING_OPTIONS["FORMAT"]
EXCEPTION_TRACE = config.LOGGING_OPTIONS["EXCEPTION_TRACE"]
USE_COLOR = config.LOGGING_OPTIONS["USE_COLOR"]
CL_DEBUG = config.LOGGING_OPTIONS["CL_DEBUG"]
CL_INFO = config.LOGGING_OPTIONS["CL_INFO"]
CL_WARNING = config.LOGGING_OPTIONS["CL_WARNING"]
CL_ERROR = config.LOGGING_OPTIONS["CL_ERROR"]
CL_CRITICAL = config.LOGGING_OPTIONS["CL_CRITICAL"]
CL_RESET = config.LOGGING_OPTIONS["CL_RESET"]

# global timestamp (constant over the complete run)
GLOBAL_TIMESTAMP = time.time()

# logging indentation level (updated inside the blocks)
CURRENT_LEVEL = 0


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

    def __init__(self):
        """
        Constructor.
        Create a timer.
        """

        # call parent constructor
        super().__init__()

        # color escape
        ESC = "\x1b"

        # define the color formatters
        self.fmt_color = {
            logging.DEBUG: logging.Formatter(ESC + CL_DEBUG + FORMAT + ESC + CL_RESET),
            logging.INFO: logging.Formatter(ESC + CL_INFO + FORMAT + ESC + CL_RESET),
            logging.WARNING: logging.Formatter(ESC + CL_WARNING + FORMAT + ESC + CL_RESET),
            logging.ERROR: logging.Formatter(ESC + CL_ERROR + FORMAT + ESC + CL_RESET),
            logging.CRITICAL: logging.Formatter(ESC + CL_CRITICAL + FORMAT + ESC + CL_RESET),
        }

        # define the black formatter
        self.fmt_black = logging.Formatter(FORMAT)

    def format(self, record):
        """
        Format a record to a string.
        Add the elapsed time.
        """

        # get log
        lvl = record.levelno
        msg = record.msg

        # add the elapsed time to the log record
        record.timestamp = _get_format_timestamp(GLOBAL_TIMESTAMP)
        record.duration = _get_format_duration(GLOBAL_TIMESTAMP)

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
    name = ex.__class__.__name__

    # log the exception
    if EXCEPTION_TRACE:
        logger.error("exception error : " + name, exc_info=ex)
    else:
        logger.error("exception error : " + name + "\n" + str(ex))


def reset_timer():
    """
    Reset the global timer to the current time.
    """

    global GLOBAL_TIMESTAMP
    GLOBAL_TIMESTAMP = time.time()


def get_logger(name):
    """
    Get a logger with a name.
    Display elapsed time, time, name, level, and message.

    The elapsed time can be measured with respect to:
        - the time the module is imported
        - the time the logger is called/created

    The elapsed time measurement method and the logging level are specified in the config.
    """

    # get the logger
    logger = logging.getLogger(name)

    # prevent duplicated log messages
    logger.propagate = False

    # create the logger (if not already done)
    if len(logger.handlers) == 0:
        # get the formatter
        fmt = _DeltaTimeFormatter()

        # get the handle
        handler = logging.StreamHandler()
        handler.setFormatter(fmt)

        # get the logger
        logger.setLevel(LEVEL)
        logger.addHandler(handler)

    return logger

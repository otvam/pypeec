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
LOGGING_GLOBAL_TIMER = config.LOGGING_GLOBAL_TIMER

# global timestamp (constant over the complete run)
LOGGING_GLOBAL_TIMESTAMP = time.time()


class _DeltaTimeFormatter(logging.Formatter):
    """
    Class for adding elapsed time to a logger.
    """

    def __init__(self, fmt, timestamp, global_timer):
        """
        Constructor.
        Create a timer.
        """

        # call parent constructor
        super().__init__(fmt)

        # create a timer
        if global_timer:
            self.timestamp = timestamp
        else:
            self.timestamp = time.time()

    def _get_time_init(self):
        """
        Get the timer starting time (as a string).
        """

        init = datetime.datetime.fromtimestamp(self.timestamp)
        init = init.strftime("%H:%M:%S,%f")[:-3]

        return init

    def _get_time_duration(self):
        """
        Get the timer elapsed time (as a string).
        """

        duration = time.time()-self.timestamp
        duration = datetime.datetime.utcfromtimestamp(duration)
        duration = duration.strftime("%H:%M:%S,%f")[:-3]

        return duration

    def format(self, record):
        """
        Format a record to a string.
        Add the elapsed time.
        """

        # add the elapsed time to the log record
        record.init = self._get_time_init()
        record.duration = self._get_time_duration()

        # format the log record
        msg = super().format(record)

        return msg


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
    fmt = _DeltaTimeFormatter(
        fmt="%(duration)s : %(name)-12s: %(levelname)-12s : %(message)s",
        timestamp=LOGGING_GLOBAL_TIMESTAMP,
        global_timer=LOGGING_GLOBAL_TIMER,
    )

    # get the handle
    handler = logging.StreamHandler()
    handler.setFormatter(fmt)

    # get the logger
    logger.setLevel(LOGGING_LEVEL)
    logger.addHandler(handler)

    return logger

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
LOGGING_GLOBAL_TIMER = config.LOGGING_GLOBAL_TIMER

# global timestamp (constant over the complete run)
LOGGING_GLOBAL_TIMESTAMP = time.time()

# logging indentation level (updated inside the blocks)
LOGGING_CURRENT_LEVEL = 0


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

        # create a timer
        self.timer = _DeltaTiming()

        # ensure that all the logger share the same timer
        if LOGGING_GLOBAL_TIMER:
            self.timer.set_timestamp(LOGGING_GLOBAL_TIMESTAMP)
        else:
            self.timer.set_now()

    def format(self, record):
        """
        Format a record to a string.
        Add the elapsed time.
        """

        # add the elapsed time to the log record
        record.init = self.timer.get_init()
        record.duration = self.timer.get_duration()

        # get the message padding for the desired indentation
        pad = " " * (LOGGING_CURRENT_LEVEL*LOGGING_INDENTATION)

        # add the padding to the message
        record.msg = pad + record.msg

        # format the log record
        msg = super().format(record)

        return msg


class _DeltaTiming:
    """
    Simple class for computing elapsed time.
    The results are converted to string format.
    """

    def __init__(self):
        """
        Constructor.
        Initialize the timer.
        """

        self.timestamp = None

    def set_now(self):
        """
        Set the timer to the current time.
        """

        self.timestamp = time.time()

    def set_timestamp(self, timestamp):
        """
        Set the timer with a provided timestamp.
        """

        self.timestamp = timestamp

    def get_init(self):
        """
        Get the timer starting time (as a string).
        """

        init = datetime.datetime.fromtimestamp(self.timestamp)
        init = init.strftime("%H:%M:%S,%f")[:-3]

        return init

    def get_duration(self):
        """
        Get the timer elapsed time (as a string).
        """

        duration = time.time()-self.timestamp
        duration = datetime.datetime.utcfromtimestamp(duration)
        duration = duration.strftime("%H:%M:%S,%f")[:-3]

        return duration


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
        self.timer = _DeltaTiming()

    def __enter__(self):
        """
        Enter magic method.
        Reset the timer and log the results.
        """

        # start the timer and display
        self.timer.set_now()
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
        duration = self.timer.get_duration()
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

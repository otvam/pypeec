"""
Module for handling the logging.
    - Use a global timer to measure the elapsed time.
    - Provide a class for timing (and logging) code blocks.
    - Measure duration with local timers.
    - Log exceptions.

The log config is defined by the following files.
    - First the default configuration is loaded ("pypeec/data/logger.yaml").
    - Afterward, a custom file can be loaded with an environment variable ("PYTHONLOGGER").
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os
import sys
import datetime
import threading
import logging
import yaml
import importlib.resources

# global timestamp (constant over the complete run)
GLOBAL_TIMESTAMP = datetime.datetime.today()

# logging indentation level (updated inside the blocks)
GLOBAL_LEVEL = 0


def _check_boolean(name, data):
    """
    Check a boolean.
    """

    if not isinstance(data, bool):
        raise AssertionError("%s: should be a boolean" % name)


def _check_integer(name, data):
    """
    Check a integer.
    """

    # check type
    if not isinstance(data, int):
        raise AssertionError("%s: should be an integer" % name)

    # check value
    if data < 0:
        raise AssertionError("%s: should be positive" % name)


def _check_string(name, data,):
    """
    Check a string.
    """

    # check type
    if not isinstance(data, str):
        raise AssertionError("%s: should be a string" % name)
    if len(data) == 0:
        raise AssertionError("%s: cannot be empty" % name)


def _check_dict(name, data, key_list):
    """
    Check a dict.
    """

    # check type
    if not isinstance(data, dict):
        raise AssertionError("%s: should be a dict" % name)

    # check keys
    for tag in key_list:
        if tag not in data:
            raise AssertionError("%s: dict is incomplete: %s" % (name, tag))


def _check_config(data):
    """
    Check the integrity of the config file.
    """

    # check dict
    key_list = [
        "FORMAT",
        "LEVEL",
        "INDENTATION",
        "EXCEPTION_TRACE",
        "USE_COLOR",
        "DEF_COLOR",
    ]
    _check_dict("data", data, key_list)
    
    # check data
    _check_string("LEVEL", data["LEVEL"])
    _check_integer("INDENTATION", data["INDENTATION"])
    _check_boolean("EXCEPTION_TRACE", data["EXCEPTION_TRACE"])
    _check_boolean("USE_COLOR", data["USE_COLOR"])

    # check sub dict
    key_list = [
        "LOGGER",
        "TIMESTAMP_FMT",
        "DURATION_FMT",
        "TIMESTAMP_TRC",
        "DURATION_TRC",
    ]
    _check_dict("FORMAT", data["FORMAT"], key_list)
    _check_string("LOGGER", data["FORMAT"]["LOGGER"])
    _check_string("TIMESTAMP_FMT", data["FORMAT"]["TIMESTAMP_FMT"])
    _check_string("DURATION_FMT", data["FORMAT"]["DURATION_FMT"])
    _check_integer("TIMESTAMP_TRC", data["FORMAT"]["TIMESTAMP_TRC"])
    _check_integer("DURATION_TRC", data["FORMAT"]["DURATION_TRC"])

    # check sub dict
    key_list = [
        "CL_DEBUG",
        "CL_INFO",
        "CL_WARNING",
        "CL_ERROR",
        "CL_CRITICAL",
        "CL_RESET",
    ]
    _check_dict("DEF_COLOR", data["DEF_COLOR"], key_list)
    _check_string("CL_DEBUG", data["DEF_COLOR"]["CL_DEBUG"])
    _check_string("CL_INFO", data["DEF_COLOR"]["CL_INFO"])
    _check_string("CL_WARNING", data["DEF_COLOR"]["CL_WARNING"])
    _check_string("CL_ERROR", data["DEF_COLOR"]["CL_ERROR"])
    _check_string("CL_CRITICAL", data["DEF_COLOR"]["CL_CRITICAL"])
    _check_string("CL_RESET", data["DEF_COLOR"]["CL_RESET"])


def _get_fmt(color, reset):
    """
    Get a logging formatter.
    """

    if (color is None) and (reset is None):
        fmt = logging.Formatter(FORMAT["LOGGER"])
    else:
        fmt = logging.Formatter("\x1b" + color + FORMAT["LOGGER"] + "\x1b" + reset)

    return fmt


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
        timestamp = datetime.datetime.today()
        duration = timestamp-GLOBAL_TIMESTAMP
        record.timestamp = _get_format_timestamp(timestamp)
        record.duration = _get_format_duration(duration)

        # add the process and thread id to the log record
        record.process_id = os.getpid()
        record.thread_id = threading.get_native_id()

        # get the message padding for the desired indentation
        pad = " " * (GLOBAL_LEVEL*INDENTATION)

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
    level : string
        Logging level to be used.
    """

    def __init__(self, logger, name, level="INFO"):
        """
        Constructor.
        Set the logger.
        """

        self.logger = logger
        self.name = name
        self.level = logging.getLevelName(level)
        self.timestamp = None

    def __enter__(self):
        """
        Enter magic method.
        Reset the timer and log the results.
        """

        # start the timer and display
        self.timestamp = datetime.datetime.today()
        self.logger.log(self.level, self.name + " : enter : timing")

        # increase the indentation of the block
        global GLOBAL_LEVEL
        GLOBAL_LEVEL += 1

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Exit magic method.
        Get the elapsed time and log the results.
        """

        # restore the indentation to the previous state
        global GLOBAL_LEVEL
        GLOBAL_LEVEL -= 1

        # get timing
        duration = datetime.datetime.today()-self.timestamp
        duration = _get_format_duration(duration)

        # display exit message
        self.logger.log(self.level, self.name + " : exit : " + duration)


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

        global GLOBAL_LEVEL
        GLOBAL_LEVEL += 1

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Exit magic method.
        Restore the indentation to the previous state.
        """

        global GLOBAL_LEVEL
        GLOBAL_LEVEL -= 1


def log_exception(logger, ex, level="ERROR"):
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
    level : string
        Logging level to be used.
    """

    # remove the expression context
    ex.__context__ = None

    # get the exception data
    name = ex.__class__.__name__

    # get level
    level = logging.getLevelName(level)

    # log the exception
    if EXCEPTION_TRACE:
        logger.log(level, "exception : " + name, exc_info=ex)
    else:
        logger.log(level, "exception : " + name + "\n" + str(ex))


def get_timer():
    """
    Get a timestamp with the current time.

    Returns
    -------
    timestamp : timestamp
        Timestamp with the current time.
    """

    timestamp = datetime.datetime.today()

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
    seconds : float
        Float with the elapsed time in seconds.
    duration : string
        String with the formatted elapsed time.
    date : string
        String with the formatted initial timestamp.
    """

    # get timing
    duration = datetime.datetime.today()-timestamp

    # parse timing
    seconds = duration.total_seconds()
    duration = _get_format_duration(duration)
    date = _get_format_timestamp(timestamp)

    return seconds, duration, date


def set_global(timestamp, level):
    """
    Set the global variables.
        - timestamp (for the elapsed time)
        - indentation level (for log messages)

    Parameters
    ----------
    timestamp : timestamp
        Timestamp (for the elapsed time).
    level : integer
        Indentation level for the log messages.
    """

    global GLOBAL_TIMESTAMP
    global GLOBAL_LEVEL
    GLOBAL_TIMESTAMP = timestamp
    GLOBAL_LEVEL = level


def get_global():
    """
    Get the global variables.
        - timestamp (for the elapsed time)
        - indentation level (for log messages)

    Returns
    -------
    timestamp : timestamp
        Timestamp (for the elapsed time).
    level : integer
        Indentation level for the log messages.
    """

    return GLOBAL_TIMESTAMP, GLOBAL_LEVEL


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


# load the config file
try:
    # load the default file
    with importlib.resources.path("pypeec.data", "logger.yaml") as file:
        with open(file, 'r') as fid:
            data = yaml.safe_load(fid)

    # get file custom file
    file = os.getenv("PYTHONLOGGER")
    if file is not None:
        with open(file, 'r') as fid:
            data = yaml.safe_load(fid)

    # check file integrity
    _check_config(data)

    # set global variables
    FORMAT = data["FORMAT"]
    LEVEL = data["LEVEL"]
    INDENTATION = data["INDENTATION"]
    EXCEPTION_TRACE = data["EXCEPTION_TRACE"]
    USE_COLOR = data["USE_COLOR"]
    DEF_COLOR = data["DEF_COLOR"]
except Exception as ex:
    print("==========================", file=sys.stderr)
    print("INVALID CONFIGURATION FILE", file=sys.stderr)
    print("==========================", file=sys.stderr)
    print(str(ex), file=sys.stderr)
    print("==========================", file=sys.stderr)
    sys.exit(1)

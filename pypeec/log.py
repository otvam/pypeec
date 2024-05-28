"""
Module for handling the logging.
    - Use a global timer to measure the elapsed time.
    - Provide a class for timing (and logging) code blocks.
    - Measure duration with local timers.
    - Log exceptions.

The log config is defined by the following files.
    - First the default configuration is loaded ("pypeec/data/logger.ini").
    - Afterward, a custom file can be loaded with an environment variable ("PYTHONLOGGER").

Warning
-------
    - This logging module is based on the Python logging module.
    - The philosophy of this logging module is slightly different.
    - Be careful if you are mixing both modules.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os
import sys
import datetime
import threading
import logging
import configparser
import importlib.resources

# global timestamp (constant over the complete run)
GLOBAL_TIMESTAMP = datetime.datetime.today()

# logging indentation level (updated inside the blocks)
GLOBAL_LEVEL = 0


def _decode_escape(value):
    """
    Decode the escape sequence in a string.
    """

    value = bytes(value, "utf-8")
    value = value.decode("unicode_escape")

    return value


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


def _check_string(name, data):
    """
    Check a string.
    """

    # check type
    if not isinstance(data, str):
        raise AssertionError("%s: should be a string" % name)
    if len(data) == 0:
        raise AssertionError("%s: cannot be empty" % name)


def _check_dict(name, data):
    """
    Check a dict.
    """

    # check type
    if not isinstance(data, dict):
        raise AssertionError("%s: should be a dict" % name)

    # check keys
    for tag, value in data.items():
        _check_string(name, tag)
        _check_string(name, value)


def _check_config():
    """
    Check the integrity of the config file.
    """

    # check format data
    _check_string("FORMAT", FORMAT)
    _check_string("LEVEL_DEFAULT", LEVEL_DEFAULT)
    _check_boolean("EXCEPTION_TRACE", EXCEPTION_TRACE)
    _check_integer("INDENTATION", INDENTATION)

    # check color data
    _check_string("COLOR_RESET", COLOR_RESET)
    _check_string("COLOR_DEFAULT", COLOR_DEFAULT)
    _check_boolean("USE_COLOR", COLOR_USE)

    # check timing data
    _check_string("TIMESTAMP_FMT", TIMESTAMP_FMT)
    _check_string("DURATION_FMT", DURATION_FMT)
    _check_integer("TIMESTAMP_TRC", TIMESTAMP_TRC)
    _check_integer("DURATION_TRC", DURATION_TRC)

    # check color level
    _check_dict("COLOR_LEVEL", COLOR_LEVEL)

    # check module level
    _check_dict("MODULE_LEVEL", MODULE_LEVEL)


def _get_level(name):
    """
    Get the corresponding logging level.
    """

    # check for exact match
    if name in MODULE_LEVEL:
        return MODULE_LEVEL[name]

    # check for parent level
    split = name.rsplit(".", 1)
    if len(split) == 1:
        return LEVEL_DEFAULT
    else:
        return _get_level(split[0])


def _get_format_timestamp(timestamp):
    """
    Format a timestamp into a string.
    """

    timestamp_str = timestamp.strftime(TIMESTAMP_FMT)
    timestamp_str = timestamp_str[0:len(timestamp_str)-TIMESTAMP_TRC]

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
    duration_str = timestamp.strftime(DURATION_FMT)
    duration_str = duration_str[0:len(duration_str)-DURATION_TRC]

    return duration_str


class _DeltaTimeFormatter(logging.Formatter):
    """
    Class for adding elapsed time to a logger.
    """

    def __init__(self, tag):
        """
        Constructor.
        Create a timer.
        """

        # call parent constructor
        super().__init__(fmt=FORMAT)

        # assign
        self.tag = tag

    def _handle_record(self, record):
        """
        Add different information to a log record.
        The timing data (timestamp and duration) are added.
        The process and thread data are added.
        """

        # extract
        msg = record.msg
        name = record.name
        levelname = record.levelname
        exc_info = record.exc_info

        # add the elapsed time to the log record
        timestamp = datetime.datetime.today()
        duration = timestamp-GLOBAL_TIMESTAMP
        record.timestamp = _get_format_timestamp(timestamp)
        record.duration = _get_format_duration(duration)

        # add the process and thread id to the log record
        record.thread_id = threading.get_native_id()
        record.process_id = os.getpid()

        # add the custom tag
        record.tag = self.tag

        # cast to lower case
        record.name = name.lower()
        record.levelname = levelname.lower()

        return record, levelname, msg, exc_info

    def _handle_lines(self, record, levelname, text):
        """
        Format a multiline text with a given record.
        """

        # get the padding for the indentation
        pad = " " * (GLOBAL_LEVEL*INDENTATION)

        # array for the lines
        out_list = []

        # format the lines
        for line in text.splitlines():
            # set the line with padding
            record.msg = pad + line

            # format the line
            out_tmp = super(_DeltaTimeFormatter, self).format(record)

            # add color and padding
            if COLOR_USE:
                if levelname in COLOR_LEVEL:
                    out_tmp = COLOR_LEVEL[levelname] + out_tmp + COLOR_RESET
                else:
                    out_tmp = COLOR_DEFAULT + out_tmp + COLOR_RESET
            else:
                pass

            # add the line
            out_list.append(out_tmp)

        return out_list

    def formatException(self, exc_info):
        """
        Dummy function to prevent traceback formatting.
        Traceback is handled in the format method.
        """

        return None

    def format(self, record):
        """
        Format a record to a string.
        """

        # parse record
        (record, levelname, msg, exc_info) = self._handle_record(record)

        # array for the lines
        out_list = []

        # format log message (if any)
        if msg is not None:
            out_list += self._handle_lines(record, levelname, msg)

        # format the attached exception (if any)
        if exc_info is not None:
            err = super(_DeltaTimeFormatter, self).formatException(exc_info)
            out_list += self._handle_lines(record, levelname, err)

        # join the lines
        out = "\n".join(out_list)

        return out


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
    module = ex.__class__.__module__

    # get level
    level = logging.getLevelName(level)

    # log the exception
    logger.log(level, "exception : %s / %s" % (module, name))
    with BlockIndent():
        if EXCEPTION_TRACE:
            logger.log(level, None, exc_info=ex)
        else:
            logger.log(level, str(ex))
    logger.log(level, "exception : %s / %s" % (module, name))


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


def get_logger(name, tag=None):
    """
    Get a logger with a specified name.
    If the logger does not exist, the logger is created.
    If the logger does exist, the logger is returned.

    Parameters
    ----------
    name : string
        Name of the logger to be returned.
    tag : string
        Name of a non-unique tag assigned to the logger.

    Returns
    -------
    logger : logger
        Logger object instance.
    """

    # fix the tag if None
    tag = tag or name

    # get the logger
    logger = logging.getLogger(name)

    # create the logger (if not already done)
    if len(logger.handlers) == 0:
        # get the formatter
        fmt = _DeltaTimeFormatter(tag)

        # get the handle
        handler = logging.StreamHandler()
        handler.setFormatter(fmt)

        # prevent duplicated log messages
        logger.propagate = False

        # get the logging level
        level_tmp = _get_level(name)

        # set the level
        logger.setLevel(level_tmp)

        # get the logger
        logger.addHandler(handler)

    return logger


# load the config file
try:
    # init parser and set mode to case-sensitive
    config = configparser.ConfigParser()
    config.optionxform = str

    # load the default file
    with importlib.resources.path("pypeec.data", "logger.ini") as file:
        out = config.read(file)
        if len(out) != 1:
            raise RuntimeError("config file cannot be loaded: %s" % file)

    # get file custom file
    file = os.getenv("PYTHONLOGGER")
    if file is not None:
        out = config.read(file)
        if len(out) != 1:
            raise RuntimeError("config file cannot be loaded: %s" % file)

    # load format data
    FORMAT = config.get("GLOBAL", "FORMAT", raw=True)
    LEVEL_DEFAULT = config.get("GLOBAL", "LEVEL_DEFAULT", raw=True)
    EXCEPTION_TRACE = config.getboolean("GLOBAL", "EXCEPTION_TRACE")
    INDENTATION = config.getint("GLOBAL", "INDENTATION")

    # load color data
    COLOR_RESET = _decode_escape(config.get("GLOBAL", "COLOR_RESET", raw=True))
    COLOR_DEFAULT = _decode_escape(config.get("GLOBAL", "COLOR_DEFAULT", raw=True))
    COLOR_USE = config.getboolean("GLOBAL", "COLOR_USE")

    # load timing data
    TIMESTAMP_FMT = config.get("GLOBAL", "TIMESTAMP_FMT", raw=True)
    DURATION_FMT = config.get("GLOBAL", "DURATION_FMT", raw=True)
    TIMESTAMP_TRC = config.getint("GLOBAL", "TIMESTAMP_TRC")
    DURATION_TRC = config.getint("GLOBAL", "DURATION_TRC")

    # load color level
    COLOR_LEVEL = dict(config.items("COLOR_LEVEL", raw=True))
    for tag, value in COLOR_LEVEL.items():
        COLOR_LEVEL[tag] = _decode_escape(value)

    # load module level
    MODULE_LEVEL = dict(config.items("MODULE_LEVEL", raw=True))
    for tag, value in MODULE_LEVEL.items():
        MODULE_LEVEL[tag] = _decode_escape(value)

    # check file integrity
    _check_config()
except Exception as ex:
    print("==========================", file=sys.stderr)
    print("INVALID CONFIGURATION FILE", file=sys.stderr)
    print("==========================", file=sys.stderr)
    print(str(ex), file=sys.stderr)
    print("==========================", file=sys.stderr)
    sys.exit(1)

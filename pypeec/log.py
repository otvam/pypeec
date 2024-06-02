"""
Module for handling the logging.
    - Use a global timer to measure the elapsed time.
    - Provide a class for timing (and logging) code blocks.
    - Measure duration with local timers.
    - Log exceptions.

The log config is defined by the following files.
    - First the default configuration is loaded ("pypeec/data/logger.ini").
    - The logger configuration file is written as a Python ConfigParser INI file.
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
    _check_boolean("TIMESTAMP_UTC", TIMESTAMP_UTC)
    _check_string("TIMESTAMP_FMT", TIMESTAMP_FMT)
    _check_string("DURATION_FMT", DURATION_FMT)

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

    return timestamp_str


def _get_format_duration(duration):
    """
    Format the duration into a string.
    """

    # extract and parse
    days = duration.days
    seconds = duration.seconds
    microseconds = duration.microseconds
    hours, remainder = divmod(seconds, 3600)
    minutes, remainder = divmod(remainder, 60)
    seconds = remainder+microseconds/1e6

    # format duration
    duration_str = DURATION_FMT.format(
        days=days,
        hours=hours,
        minutes=minutes,
        seconds=seconds,
    )

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
        timestamp = get_timestamp()
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


class BlockIndent:
    """
    Class for timing a block of code.
        - Uses enter and exit magic methods.
        - Display the name of the block.
        - Indent the results inside the block.

    Parameters
    ----------
    logger : logger
        Logger object instance.
    name : string
        Name of the code block.
    level : string
        Logging level to be used.
    """

    def __init__(self, logger=None, name=None, level="INFO"):
        """
        Constructor.
        Set the logger.
        """

        # assign
        self.name = name

        # assign logger if provided
        if logger is None:
            self.logger = LOGGER
        else:
            self.logger = logger

        # parse level name
        self.level = logging.getLevelName(level)

    def __enter__(self):
        """
        Enter magic method.
        Display the block name.
        Increase the indentation.
        """

        # display log
        if self.name is not None:
            self.logger.log(self.level, self.name)

        # increase the indentation of the block
        global GLOBAL_LEVEL
        GLOBAL_LEVEL += 1

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Exit magic method.
        Restore the indentation.
        """

        # restore the indentation to the previous state
        global GLOBAL_LEVEL
        GLOBAL_LEVEL -= 1


class BlockTimer:
    """
    Class for timing a block of code.
        - Uses enter and exit magic methods.
        - Display the name of the block.
        - Display timing information.
        - Indent the results inside the block.

    Parameters
    ----------
    logger : logger
        Logger object instance.
    name : string
        Name of the code block.
    level : string
        Logging level to be used.
    """

    def __init__(self, logger=None, name=None, level="INFO"):
        """
        Constructor.
        Set the logger.
        """

        # assign
        self.name = name

        # assign logger if provided
        if logger is None:
            self.logger = LOGGER
        else:
            self.logger = logger

        # parse level name
        self.level = logging.getLevelName(level)

        # dummy timestamp
        self.timestamp = None

    def __enter__(self):
        """
        Enter magic method.
        Reset the timer and log the results.
        """

        # start the timer
        self.timestamp = get_timestamp()

        # get timing
        duration = datetime.timedelta(seconds=0)
        duration = _get_format_duration(duration)

        # display log
        if self.name is not None:
            self.logger.log(self.level, self.name + " : enter : " + duration)
        else:
            self.logger.log(self.level, "enter : " + duration)

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
        duration = get_timestamp()-self.timestamp
        duration = _get_format_duration(duration)

        # display log
        if self.name is not None:
            self.logger.log(self.level, self.name + " : exit : " + duration)
        else:
            self.logger.log(self.level, "exit : " + duration)


def log_exception(logger=None, ex=None, level="ERROR"):
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

    # if logger is not provided, use default
    if logger is None:
        logger = LOGGER

    # if exception is not provided, use default
    if ex is None:
        (_, ex, _) = sys.exc_info()

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
            logger.log(level, str(ex))
    logger.log(level, "exception : %s / %s" % (module, name))


def get_timestamp():
    """
    Get a timestamp with the current time.

    Returns
    -------
    timestamp : timestamp
        Timestamp with the current time.
    """

    if TIMESTAMP_UTC:
        timestamp = datetime.datetime.utcnow()
    else:
        timestamp = datetime.datetime.now()

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
    duration = get_timestamp()-timestamp

    # parse timing
    seconds = duration.total_seconds()
    duration = _get_format_duration(duration)
    date = _get_format_timestamp(timestamp)

    return seconds, duration, date


def reset_global():
    """
    Reset the global variables.
        - timestamp (for the elapsed time)
        - indentation level (for log messages)
    """

    # reset timestamp
    timestamp = get_timestamp()

    # reset indentation
    level = 0

    # set global
    global GLOBAL_TIMESTAMP
    global GLOBAL_LEVEL
    GLOBAL_TIMESTAMP = timestamp
    GLOBAL_LEVEL = level


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

    # set global
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
        Non-unique tag assigned to the logger.

    Returns
    -------
    logger : logger
        Logger object instance.
    """

    # fix the tag if not provided
    if tag is None:
        tag = name

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
    TIMESTAMP_UTC = config.getboolean("GLOBAL", "TIMESTAMP_UTC")
    TIMESTAMP_FMT = config.get("GLOBAL", "TIMESTAMP_FMT", raw=True)
    DURATION_FMT = config.get("GLOBAL", "DURATION_FMT", raw=True)

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

    # init default logger
    LOGGER = get_logger(__name__, "default")

    # global timestamp (constant over the complete run)
    GLOBAL_TIMESTAMP = get_timestamp()

    # logging indentation level (updated inside the blocks)
    GLOBAL_LEVEL = 0
except Exception as ex:
    print("==========================", file=sys.stderr)
    print("INVALID CONFIGURATION FILE", file=sys.stderr)
    print("==========================", file=sys.stderr)
    print(str(ex), file=sys.stderr)
    print("==========================", file=sys.stderr)
    sys.exit(1)

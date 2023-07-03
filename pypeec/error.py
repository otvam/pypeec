"""
Definition of the used exceptions.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"


class CheckError(Exception):
    """
    Exception used for signaling invalid input data.
    """

    pass


class RunError(Exception):
    """
    Exception used for an error during execution.
    """

    pass


class FileError(Exception):
    """
    Exception used for an error during loading/writing files.
    """

    pass

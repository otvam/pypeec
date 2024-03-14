"""
Set the package metadata.
"""

import importlib.resources

# set basic metadata
__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

# get the version number
try:
    with importlib.resources.open_text("pypeec.data", "version.txt") as file_version:
        __version__ = file_version.read()
except FileNotFoundError:
    __version__ = 'x.x.x'

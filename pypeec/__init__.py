import importlib.resources

# set basic metadata
__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

# get the version number
try:
    filename = importlib.resources.files("pypeec.data").joinpath("version.txt")
    with filename.open("r") as fid:
        __version__ = fid.read()
except FileNotFoundError:
    __version__ = "x.x.x"

# import the script method
from pypeec.script import *

# import the main method
from pypeec.main import *

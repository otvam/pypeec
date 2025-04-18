"""
Root level module (import main functions and set metadata).
"""

import importlib.resources

# set basic metadata
__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

# import the script method
from pypeec.script import run_script
from pypeec.script import run_arguments

# import the main method
from pypeec.main import run_extract_examples
from pypeec.main import run_extract_documentation
from pypeec.main import run_mesher_data, run_mesher_file
from pypeec.main import run_viewer_data, run_viewer_file
from pypeec.main import run_solver_data, run_solver_file
from pypeec.main import run_plotter_data, run_plotter_file

# get the version number
try:
    filename = importlib.resources.files("pypeec.data").joinpath("version.txt")
    with filename.open("r", encoding="utf-8") as fid:
        __version__ = fid.read()
except FileNotFoundError:
    __version__ = "x.x.x"

# get the banner text
filename = importlib.resources.files("pypeec.data").joinpath("banner.txt")
with filename.open("r", encoding="utf-8") as fid:
    __banner__ = fid.read()

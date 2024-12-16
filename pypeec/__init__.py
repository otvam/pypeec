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
    __version__ = 'x.x.x'

# import the script method
from pypeec.script import run_script as run_script
from pypeec.script import run_arguments as run_arguments

# import the main method
from pypeec.main import run_mesher_data as run_mesher_data
from pypeec.main import run_mesher_file as run_mesher_file
from pypeec.main import run_viewer_data as run_viewer_data
from pypeec.main import run_viewer_file as run_viewer_file
from pypeec.main import run_solver_data as run_solver_data
from pypeec.main import run_solver_file as run_solver_file
from pypeec.main import run_plotter_data as run_plotter_data
from pypeec.main import run_plotter_file as run_plotter_file

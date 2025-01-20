"""
Configuration file for the Sphinx documentation generator.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os
import sys
import datetime
import setuptools_scm

# define the package path
sys.path.insert(0, os.path.abspath(".."))

# get the version number
ver = setuptools_scm.get_version(
    root="..",
    relative_to=__file__,
    version_scheme="only-version",
    local_scheme="no-local-version",
)
release = ver
version = ver

# get date
date = datetime.datetime.today().strftime("%a, %b %d, %Y")

# project title and version
project = "PyPEEC - %s" % ver

# title for the html pages
html_title = "PyPEEC"

# project author
author = "Thomas Guillod"

# project copyright
copyright = "Thomas Guillod - Dartmouth College"

# add prolog
rst_epilog = """
.. |ver| replace:: {ver}
.. |date| replace:: {date}
"""
rst_epilog = rst_epilog.format(ver=ver, date=date)

# load extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
]

# allowed redirects for the external links
linkcheck_allowed_redirects = {
    "https://dartmouth.edu/*": ".*",
    "http://mozilla.org/*": ".*",
    "https://doi.org/*": ".*",
}

# define folder paths
templates_path = ["_templates"]
html_static_path = ["_static"]
html_theme_path = ["_static"]

# html base options
html_baseurl = "https://pypeec.otvam.ch"
html_theme = "sphinx_rtd_theme"
html_logo = "images/sphinx.png"
html_favicon = "images/icon.png"
html_show_sphinx = False
html_show_sourcelink = False
html_copy_source = False
html_use_index = False
html_domain_indices = False

# html theme options
html_theme_options = {
    "logo_only": False,
    "style_nav_header_background": "#7a9aa3",
    "prev_next_buttons_location": None,
    "collapse_navigation": True,
    "sticky_navigation": True,
    "navigation_depth": 2,
    "includehidden": True,
    "titles_only": False,
}

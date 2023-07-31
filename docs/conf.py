"""
Configuration file for the Sphinx documentation generator.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os
import sys
import setuptools_scm

# create the static folder
try:
    os.mkdir("_static")
except FileExistsError:
    pass

# create the template folder
try:
    os.mkdir("_templates")
except FileExistsError:
    pass

# define the package path
sys.path.insert(0, os.path.abspath('..'))

# get the version number
version = setuptools_scm.get_version(
    root='..',
    relative_to=__file__,
    version_scheme="guess-next-dev",
)

# project metadata
project = 'PyPEEC'
html_title = "PyPEEC"
copyright = 'Thomas Guillod'
author = 'Thomas Guillod'
release = version

# load extensions
extensions = [
    'sphinx.ext.githubpages',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
]

# autodoc order
autodoc_member_order = 'bysource'

# disable API file generation
autosummary_generate = False

# define paths
templates_path = ['_templates']
html_static_path = ['_static']
html_theme_path = ['_static']

# html options
html_baseurl = 'https://pypeec.otvam.ch'
html_theme = 'sphinx_rtd_theme'
html_logo = "images/header.png"
html_favicon = "images/icon.png"
html_show_sphinx = False
html_show_sourcelink = False
html_copy_source = False
html_use_index = False
html_domain_indices = False

# html theme
html_theme_options = {
    'logo_only': True,
    'display_version': True,
    'style_nav_header_background': '#2980B9',
    'prev_next_buttons_location': None,
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 2,
    'includehidden': True,
    'titles_only': False,
}

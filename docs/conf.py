# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import setuptools_scm

version = setuptools_scm.get_version(
    root='..',
    relative_to=__file__,
    version_scheme="guess-next-dev",
)

project = 'PyPEEC'
copyright = 'Thomas Guillod'
author = 'Thomas Guillod'
release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []
templates_path = ['_templates']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_title = "PyPEEC"

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_theme_path = ['_static']
html_logo = "images/header.png"
html_favicon = "images/icon.png"
html_show_sphinx = False

html_theme_options = {
    'logo_only': False,
    'display_version': True,
    'style_nav_header_background': '#2980B9',
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 2,
    'includehidden': True,
    'titles_only': False
}

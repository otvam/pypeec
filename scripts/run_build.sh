#!/bin/bash
# Script for building the documentation and the package:
#   - clean the generated files
#   - build the Sphinx documentation
#   - build the Python package
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

set -o nounset
set -o pipefail

function clean_data {
  echo "======================================================================"
  echo "CLEAN DATA"
  echo "======================================================================"

  # clean package
  rm -rf dist
  rm -rf build
  rm -rf pypeec.egg-info

  # clean generated files
  rm -rf pypeec/data/examples.zip
  rm -rf pypeec/data/documentation.zip
  rm -rf pypeec/data/version.txt

  # clean documentation
  rm -rf html
  rm -rf website
  rm -rf docs/_static
  rm -rf docs/_templates
}

function build_docs {
  echo "======================================================================"
  echo "BUILD DOCUMENTATION"
  echo "======================================================================"

  # create folders
  mkdir docs/_static
  mkdir docs/_templates

  # build documentation
  sphinx-build -W -b html docs html

  # update status
  ret=$(( ret || $? ))

  # check external links
  sphinx-build -W -b linkcheck docs html

  # update status
  ret=$(( ret || $? ))

  # clean data
  rm -rf html/.buildinfo
  rm -rf html/.doctrees
  rm -rf html/output.json
  rm -rf html/output.txt

  # copy html for website
  cp -r html website

  # add the hidden files
  touch website/.gitignore
  touch website/.nojekyll

  # get the timestamp for the sitemap
  export LASTMOD=$(date '+%Y-%m-%d')

  # substitute the timestamp for the sitemap
  cat docs/website/sitemap.xml | envsubst > website/sitemap.xml

  # copy metadata
  cp docs/website/CNAME website
  cp docs/website/README.md website
  cp docs/website/robots.txt website
  cp docs/website/googlec2be449c43987dd0.html website
}

function build_pkg {
  echo "======================================================================"
  echo "BUILD PACKAGE"
  echo "======================================================================"

  # backup the README file
  cp README.md README.md.bak

  # make the README compatible with PyPI
  sed -i '/\!\[[^]]*\]([^)]*)/d' README.md
  sed -i 'N;/^\n$/D;P;D;' README.md

  # pack examples
  (cd examples && git archive -o ../pypeec/data/examples.zip HEAD)

  # pack documentation
  (cd html && zip -qr ../pypeec/data/documentation.zip .)

  # build package
  python -m build

  # update status
  ret=$(( ret || $? ))

  # restore the README file
  mv README.md.bak README.md
}

# change to root directory
cd "$(dirname "$0")" && cd ..

# init status
ret=0

# build the documentation
clean_data
build_docs
build_pkg

exit $ret

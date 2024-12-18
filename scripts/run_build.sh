#!/bin/bash
# Script for building the documentation and the package:
#   - build the Sphinx documentation
#   - build the Python package
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

set -o nounset
set -o pipefail

function build_docs {
  echo "======================================================================"
  echo "============================== BUILD: DOCS"
  echo "======================================================================"

  # create folders
  mkdir -p docs/_static
  mkdir -p docs/_templates

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

  # get the timestamp for the substitution
  export LASTMOD=$(date '+%Y-%m-%d')

  # substitute the timestamp for sitemap.xml
  cat docs/website/sitemap.xml | envsubst > website/sitemap.xml

  # substitute the timestamp for robots.txt
  cat docs/website/robots.txt | envsubst > website/robots.txt

  # domain name description file
  echo "pypeec.otvam.ch" > website/CNAME

  # copy a simple README file
  cp docs/website/README.md website
}

function build_pkg {
  echo "======================================================================"
  echo "============================== BUILD: PKG"
  echo "======================================================================"

  # backup the README file
  cp README.md README.md.bak

  # make the README compatible with PyPI
  sed -i '/\!\[[^]]*\]([^)]*)/d' README.md
  sed -i 'N;/^\n$/D;P;D;' README.md

  # pack examples
  (cd examples && git archive HEAD | xz > ../pypeec/data/examples.tar.xz)

  # pack documentation
  (cd html && tar -cf - * | xz > ../pypeec/data/documentation.tar.xz)

  # build package
  python -m build

  # update status
  ret=$(( ret || $? ))

  # restore the README file
  mv README.md.bak README.md
}

function ret_collect {
  if [[ $ret == 0 ]]
  then
    status="SUCCESS"
  else
    status="FAILURE"
  fi

  echo "======================================================================"
  echo "============================== BUILD: $status"
  echo "======================================================================"
}

# change to root directory
cd "$(dirname "$0")" && cd ..

# init status
ret=0

# build the documentation
build_docs

# build the package
build_pkg

# collect status
ret_collect

exit $ret

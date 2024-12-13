#!/bin/bash
# Script for creating and uploading a release:
#   - create a tag and a release
#   - build the Sphinx documentation
#   - build the Python package
#   - run the all the tests
#   - upload the documentation
#   - upload the Python package
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

set -o nounset
set -o pipefail

function check_release {
  echo "======================================================================"
  echo "CHECK RELEASE"
  echo "======================================================================"

  # get the version and release message
  if [[ "$#" -eq 2 ]]
  then
    VER=$(echo $1 | awk '{$1=$1;print}')
    MSG=$(echo $2 | awk '{$1=$1;print}')
  else
    echo "error: usage : run_release.sh VER MSG"
    exit 1
  fi

  # init status
  ret=0

  # check the version number
  rx='^v([0-9]+)\.([0-9]+)\.([0-9]+)$'
  if ! [[ $VER =~ $rx ]]
  then
    echo "error: invalid version number format"
    ret=1
  fi

  # check the release message
  rx='^ *$'
  if [[ $MSG =~ $rx ]]
  then
    echo "error: invalid release message format"
    ret=1
  fi

  # check git branch name
  if [[ $(git rev-parse --abbrev-ref HEAD) != "main" ]]
  then
    echo "error: release should be done from main"
    ret=1
  fi

  # check git tag existence
  if [[ $(git tag -l $VER) ]]
  then
    echo "error: version number already exists"
    ret=1
  fi

  # check git repository status
  if ! [[ -z "$(git status --porcelain)" ]]
  then
    echo "error: git status is not clean"
    ret=1
  fi

  # abort in case of failure
  if [[ $ret != 0 ]]
  then
    echo "======================================================================"
    echo "RELEASE FAILURE"
    echo "======================================================================"
    exit $ret
  fi
}

function build_test {
  # init status
  ret=0

  # create a temporary tag
  git tag -a $VER -m "$MSG" > /dev/null

  # check build
  ./scripts/run_build.sh
  ret=$(( ret || $? ))

  # remove the temporary tag
  git tag -d $VER > /dev/null

  # check tests
  ./scripts/run_tests.sh
  ret=$(( ret || $? ))

  # abort in case of failure
  if [[ $ret != 0 ]]
  then
    echo "======================================================================"
    echo "RELEASE FAILURE"
    echo "======================================================================"
    exit $ret
  fi
}

function upload_docs {
  echo "======================================================================"
  echo "UPLOAD DOCUMENTATION"
  echo "======================================================================"

  # remove the documentation repository
  rm -rf pypeecdocs

  # clone the documentation repository
  git clone git@github.com:otvam/pypeecdocs.git

  # remove the existing data
  rm -rf pypeecdocs/*

  # copy the last version
  cp -r website/* pypeecdocs

  # add all the files to git
  git -C pypeecdocs add .

  # commit the new version
  git -C pypeecdocs commit -m "$VER / $MSG"

  # push the new version
  git -C pypeecdocs push

  # remove the documentation repository
  rm -rf pypeecdocs
}

function upload_pkg {
  echo "======================================================================"
  echo "UPLOAD PACKAGE"
  echo "======================================================================"

  # create a tag
  git tag -a $VER -m "$MSG"

  # push the tag
  git push origin --tags

  # create a release
  gh release create $VER --title $VER --notes "$MSG"

  # upload to PyPI
  twine upload dist/*
}

# change to root directory
cd "$(dirname "$0")" && cd ..

# parse the arguments
check_release "$@"

# run the code
build_test
upload_docs
upload_pkg

exit 0

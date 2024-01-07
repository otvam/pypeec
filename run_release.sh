#!/bin/bash
# Script for creating a release:
#   - create a tag
#   - build the documentation and the package
#   - run the tests and check the results
#   - create a release
#   - upload the documentation
#   - upload the package
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

set -o nounset
set -o pipefail

function check_release {
  echo "======================================================================"
  echo "CHECK RELEASE"
  echo "======================================================================"

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

  # check status
  if [[ $ret != 0 ]]
  then
    exit $ret
  fi
}

function run_build_test {
  # create a tag
  git tag -a $VER -m "$MSG"

  # init status
  ret=0

  # check build
  ./run_build.sh
  ret=$(( ret || $? ))

  # check tests
  ./run_tests.sh
  ret=$(( ret || $? ))

  if [[ $ret != 0 ]]
  then
    echo "======================================================================"
    echo "RELEASE FAILURE"
    echo "======================================================================"

    # clean tags
    git tag -d $VER

    # force quit
    exit $ret
  fi
}

function create_release {
  echo "======================================================================"
  echo "CREATE RELEASE"
  echo "======================================================================"

  # push the tags
  git push origin --tags

  # create a release
  gh release create $VER --title $VER --notes "$MSG"
}

function upload_documentation {
  echo "======================================================================"
  echo "UPLOAD DOCUMENTATION"
  echo "======================================================================"

  # init clean data
  rm -rf pypeecdocs/*

  # copy website
  cp -r html/* pypeecdocs

  # copy metadata
  cp docs/website/CNAME pypeecdocs
  cp docs/website/README.md pypeecdocs
  cp docs/website/googlec2be449c43987dd0.html pypeecdocs

  # add file in git
  git -C pypeecdocs add .

  # commit the new version
  git -C pypeecdocs commit -m "$VER / $MSG"

  # push the new version
  git -C pypeecdocs push
}

function upload_package {
  echo "======================================================================"
  echo "UPLOAD PACKAGE"
  echo "======================================================================"

  # upload to PyPi
  twine upload dist/*
}

# get the version and release message
if [[ "$#" -eq 2 ]]
then
  VER=$(echo $1 | awk '{$1=$1;print}')
  MSG=$(echo $2 | awk '{$1=$1;print}')
else
  echo "======================================================================"
  echo "error: usage : run_release.sh VER MSG"
  echo "======================================================================"
  exit 1
fi

# run the code
check_release
run_build_test
create_release
upload_documentation
upload_package

exit 0

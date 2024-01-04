#!/bin/bash
# Script for creating a release:
#   - create a tag
#   - create a release
#   - build the documentation and the package
#   - upload the documentation
#   - upload the package
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

set -o nounset
set -o pipefail

function create_tag {
  echo "======================================================================"
  echo "CREATE TAG"
  echo "======================================================================"

  # create a tag
  git tag -a $VER -m "$MSG"
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

function run_build_test {
  # init status
  ret=0

  # check build
  ./run_build.sh
  ret=$(( ret || $? ))

  # check tests
  ./run_tests.sh
  ret=$(( ret || $? ))

  if (( $ret != 0 ))
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

# get the version and release message
if [ "$#" -eq 2 ]
then
  VER=$(echo $1 | tr -d ' ')
  MSG=$(echo $2 | tr -d ' ')
else
  echo "error : usage : run_release.sh VER MSG"
  exit 1
fi

# check the version number
rx='^v([0-9]+)\.([0-9]+)\.([0-9]+)$'
if ! [[ $VER =~ $rx ]]
then
  echo "error : invalid version number"
  exit 1
fi

# check the release message
rx='^ *$'
if [[ $MSG =~ $rx ]]
then
  echo "error : invalid message"
  exit 1
fi

# run the code
create_tag
run_build_test
create_release
upload_documentation
upload_package

exit 0

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
  echo "Create tag"
  echo "======================================================================"

  # create a tag
  git tag -a $VER -m "$MSG"

  # push the tags
  git push origin --tags
}

function create_release {
  echo "======================================================================"
  echo "Create release"
  echo "======================================================================"

  # create a release
  gh release create $VER --title $VER --notes "$MSG"
}

function upload_documentation {
  echo "======================================================================"
  echo "Upload documentation"
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
  echo "Upload package"
  echo "======================================================================"

  # upload to PyPi
  twine upload dist/*
}

# get the version and commit message
if [ "$#" -eq 2 ]; then
  VER=$1
  MSG=$2
else
  echo "error : usage : run_release.sh VER MSG"
  exit 1
fi

# run the code
create_tag
create_release
./run_build.sh
upload_documentation
upload_package

exit 0

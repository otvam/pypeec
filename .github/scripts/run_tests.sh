#!/bin/bash
# Script for running and checking the tests.
#
# Thomas Guillod - Dartmouth College
# Mozilla Public License Version 2.0

set -e
set -u

# run test
git archive HEAD | xz > tmp.tar.xz

python aaa.py

ls
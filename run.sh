#!/bin/bash

# clean 
rm -rf jats

# convert figures
inkscape workflow.svg --export-area-page --export-filename=workflow.pdf
inkscape performance.svg --export-area-page --export-filename=performance.pdf

# run JOSS workflow
docker run --rm \
    --volume $PWD:/data \
    --user $(id -u):$(id -g) \
    --env JOURNAL=joss \
    openjournals/inara

# clean 
rm -rf jats

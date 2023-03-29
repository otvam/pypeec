#!/bin/bash
# Script for transforming GERBER files into PNG files:
#   - using "gerbv - Gerber Viewer" for parsing the GERBER files
#   - using "mogrify - ImageMagick" for trimming the PNG files
#
# (c) Thomas Guillod - Dartmouth College

set -o nounset
set -o pipefail

function convert_file {
  echo "================================================================"
  echo "CONVERT: $1"
  echo "================================================================"

  # render the GERBER files
  gerbv -p $1.gvp -o $1.png -x png --border 10 --dpi 1500 2>/dev/null
  
  # cut the border
  mogrify -trim $1.png
}

convert_file gerbv_front
convert_file gerbv_back
convert_file gerbv_via

exit 0

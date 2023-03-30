#!/bin/bash
# Script for transforming GERBER files into PNG files.
#
# The PCB is created with "KiCad - PCB" and the following files are exported:
#   - GERBER files for the conductor and the terminals
#   - Excellon files for the vias
#
# Afterwards, the files are combined with "gerbv - Gerber Viewer".
#
# Finally, this script is used to generate PNG files for the layers: 
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
convert_file gerbv_terminal

exit 0

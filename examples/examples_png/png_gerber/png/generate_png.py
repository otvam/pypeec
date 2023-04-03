"""
Generate PNG files for the example.

The PCB is created with "KiCad - PCB" and the following files are exported:
    - GERBER files for the conductor and the terminals
    - Excellon files for the vias

Finally, this script is used to generate PNG files for the layers:
    - using "gerbv - Gerber Viewer" for parsing the GERBER files
    - using "mogrify - ImageMagick" for trimming the PNG files
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import os
import subprocess


def get_gerbv_file(filename_gerbv, file_edge, stack):
    """
    Create a "gerbv - Gerber Viewer" project file.
    """

    with open(filename_gerbv, "w") as fid:
        # add header
        fid.write('(gerbv-file-version! "2.0A")\n')

        # add stack
        for i, stack_tmp in enumerate(stack):
            # extract data
            layer = i+1
            file = stack_tmp["file"]
            (cr, cg, cb) = stack_tmp["color"]

            # add layer
            fid.write('(define-layer! %d (cons \'filename "%s")\n' % (layer, file))
            fid.write('\t(cons \'visible #t)\n')
            fid.write('\t(cons \'color #(%d %d %d))\n' % (cr, cg, cb))
            fid.write('\t(cons \'alpha #(65535))\n')
            fid.write(')\n')

        # add board edges
        fid.write('(define-layer! 0 (cons \'filename "%s")\n' % file_edge)
        fid.write('\t(cons \'visible #t)\n')
        fid.write('\t(cons \'color #(0 0 0))\n')
        fid.write('\t(cons \'alpha #(65535))\n')
        fid.write(')\n')

        # add background
        fid.write('(define-layer! -1 (cons \'filename "%s")\n' % filename_gerbv)
        fid.write('\t(cons \'color #(65535 65535 65535))\n')
        fid.write(')\n')

        # add rendering settings
        fid.write('(set-render-type! 3)\n')


def get_png(name, border, resolution, file_edge, stack):
    """
    Transform GERBER files into a PNG file.
    """

    # create the file names
    filename_gerbv = name + ".gvp"
    filename_png = name + ".png"

    # get the project files with the GERBER files
    get_gerbv_file(filename_gerbv, file_edge, stack)

    # transform the GERBER files into a PNG file
    cmd = "gerbv -p %s -o %s -x png --border %d --dpi %d 2>/dev/null" % (
        filename_gerbv,
        filename_png,
        border,
        resolution,
    )
    subprocess.run(cmd, shell=True)

    # cut the border
    cmd = "mogrify -trim %s" % filename_png
    subprocess.run(cmd, shell=True)

    # remove the project file
    os.remove(filename_gerbv)


if __name__ == "__main__":
    # ######################## get the variables
    border = 10
    resolution = 1500
    file_edge = "gerber/generate_gerber-edge.gbr"

    # ######################## gerbv_front
    name = "gerbv_front"
    stack = [
        {"file": "gerber/generate_gerber-PTH.drl", "color": (65535, 65535, 65535)},
        {"file": "gerber/generate_gerber-front_copper.gbr", "color": (65535, 0, 0)},
    ]
    get_png(name, border, resolution, file_edge, stack)

    # ######################## gerbv_back
    name = "gerbv_back"
    stack = [
        {"file": "gerber/generate_gerber-PTH.drl", "color": (65535, 65535, 65535)},
        {"file": "gerber/generate_gerber-back_copper.gbr", "color": (65535, 0, 0)},
    ]
    get_png(name, border, resolution, file_edge, stack)

    # ######################## gerbv_terminal
    name = "gerbv_terminal"
    stack = [
        {"file": "gerber/generate_gerber-sink.gbr", "color": (0, 0, 65535)},
        {"file": "gerber/generate_gerber-src.gbr", "color": (0, 65535, 0)},
    ]
    get_png(name, border, resolution, file_edge, stack)

    # ######################## gerbv_via
    name = "gerbv_via"
    stack = [
        {"file": "gerber/generate_gerber-PTH.drl", "color": (65535, 65535, 65535)},
        {"file": "gerber/generate_gerber-VIA.drl", "color": (65535, 0, 0)},
    ]
    get_png(name, border, resolution, file_edge, stack)

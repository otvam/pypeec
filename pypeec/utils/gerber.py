"""
Module for generating PNG files from GERBER files.

The PCB is created with "KiCad - PCB" and the following files are exported:
    - GERBER files for the different layers (main layers)
    - GERBER files for the terminals (user layers)
    - Excellon files for the vias

Finally, this script is used to generate PNG files for the layers:
    - using "gerbv - Gerber Viewer 2.8" for parsing the GERBER files
    - using "mogrify - ImageMagick 6.9" for trimming the PNG files

Warning
-------
    - This code requires the following external tools: "gerbv" and "mogrify".
    - This code has only been tested on Linux (Ubuntu 22.04).
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os
import os.path
import subprocess


def _get_gerbv_file(filename_gerbv, folder_gerber, data_gerber, data_stack):
    """
    Create a "gerbv - Gerber Viewer" project file.
    """

    # extract the data
    gerber_edge = data_gerber["gerber_edge"]
    color_edge = data_gerber["color_edge"]
    color_background = data_gerber["color_background"]
    color_def = data_gerber["color_def"]
    gerber_def = data_gerber["gerber_def"]

    # get base color
    color_edge = tuple([257 * x for x in color_edge])
    color_background = tuple([257 * x for x in color_background])

    # get GERBER edge file
    gerber_edge = os.path.join(folder_gerber, gerber_edge)

    # get transparency value
    alpha_channel = 257 * 255

    # create the file
    with open(filename_gerbv, "w") as fid:
        # add header
        fid.write('(gerbv-file-version! "2.0A")\n')

        # add stack
        for i, data_stack_tmp in enumerate(data_stack):
            # extract the data
            layer = i + 1
            gerber = data_stack_tmp["gerber"]
            color = data_stack_tmp["color"]

            # get layer color
            color = color_def[color]
            color = tuple([257 * x for x in color])

            # get GERBER file
            gerber = gerber_def[gerber]
            gerber = os.path.join(folder_gerber, gerber)

            # add layer
            fid.write('(define-layer! %d (cons \'filename "%s")\n' % (layer, gerber))
            fid.write("\t(cons 'visible #t)\n")
            fid.write("\t(cons 'color #(%d %d %d))\n" % color)
            fid.write("\t(cons 'alpha #(%d))\n" % alpha_channel)
            fid.write(")\n")

        # add board edges
        fid.write('(define-layer! 0 (cons \'filename "%s")\n' % gerber_edge)
        fid.write("\t(cons 'visible #t)\n")
        fid.write("\t(cons 'color #(%d %d %d))\n" % tuple(color_edge))
        fid.write("\t(cons 'alpha #(%d))\n" % alpha_channel)
        fid.write(")\n")

        # add background
        fid.write('(define-layer! -1 (cons \'filename "%s")\n' % filename_gerbv)
        fid.write("\t(cons 'color #(%d %d %d))\n" % tuple(color_background))
        fid.write("\t(cons 'alpha #(%d))\n" % alpha_channel)
        fid.write(")\n")

        # add rendering settings
        fid.write("(set-render-type! 3)\n")


def _get_png_file(filename_gerbv, filename_png, margin, voxel, oversampling):
    """
    Transform GERBER project file into a PNG file for a given layer.
    """

    # get the resolution and margin
    resolution = round(25.4e-3 * oversampling / voxel)
    resize = 100 / oversampling
    border = 100 * margin

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

    # cut the border
    cmd = "mogrify -sample %.2f%% %s" % (resize, filename_png)
    subprocess.run(cmd, shell=True)


def _get_convert_layer(tag, data_export, data_gerber, data_stack):
    """
    Transform GERBER files into a PNG file for a given layer.
    """

    # extract the data
    margin = data_export["margin"]
    voxel = data_export["voxel"]
    oversampling = data_export["oversampling"]
    folder_gerber = data_export["folder_gerber"]
    folder_png = data_export["folder_png"]

    # get the absolute location
    folder_gerber = os.path.abspath(folder_gerber)
    folder_png = os.path.abspath(folder_png)

    # create the file names
    filename_gerbv = os.path.join(folder_png, "%s.gvp" % tag)
    filename_png = os.path.join(folder_png, "%s.png" % tag)

    # get the project file with the GERBER files
    _get_gerbv_file(filename_gerbv, folder_gerber, data_gerber, data_stack)

    # convert the project file into a PNG file
    _get_png_file(filename_gerbv, filename_png, margin, voxel, oversampling)

    # remove the project file
    os.remove(filename_gerbv)


def get_convert(data_export, data_gerber, data_stack):
    """
    Transform GERBER files into PNG files.
    """

    for tag, data_stack_tmp in data_stack.items():
        _get_convert_layer(tag, data_export, data_gerber, data_stack_tmp)

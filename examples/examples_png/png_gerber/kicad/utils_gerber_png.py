"""
Module for generating PNG files from GERBER files.

The PCB is created with "KiCad - PCB" and the following files are exported:
    - GERBER files for the different layers (main layers)
    - GERBER files for the terminals (user layers)
    - Excellon files for the vias

Finally, this script is used to generate PNG files for the layers:
    - using "gerbv - Gerber Viewer" for parsing the GERBER files
    - using "mogrify - ImageMagick" for trimming the PNG files
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import os
import os.path
import subprocess


def get_gerbv_file(filename_gerbv, folder_gerber, data_gerber, data_stack):
    """
    Create a "gerbv - Gerber Viewer" project file.
    """

    # extract the data
    gerber_edge = data_gerber["gerber_edge"]
    color_edge = data_gerber["color_edge"]
    color_none = data_gerber["color_none"]
    color_def = data_gerber["color_def"]
    gerber_def = data_gerber["gerber_def"]

    # get name
    color_edge = color_def[color_edge]
    color_none = color_def[color_none]
    gerber_edge = gerber_def[gerber_edge]
    gerber_edge = os.path.join(folder_gerber, gerber_edge)

    # convert color
    color_edge = tuple([257 * x for x in color_edge])
    color_none = tuple([257 * x for x in color_none])

    # get alpha
    alpha_channel = 257*255

    # create the file
    with open(filename_gerbv, "w") as fid:
        # add header
        fid.write('(gerbv-file-version! "2.0A")\n')

        # add stack
        for i, data_stack_tmp in enumerate(data_stack):
            # extract the data
            layer = i+1
            gerber = data_stack_tmp["gerber"]
            color = data_stack_tmp["color"]

            # get color
            color = color_def[color]
            gerber = gerber_def[gerber]
            gerber = os.path.join(folder_gerber, gerber)

            # convert color
            color = tuple([257*x for x in color])

            # add layer
            fid.write('(define-layer! %d (cons \'filename "%s")\n' % (layer, gerber))
            fid.write('\t(cons \'visible #t)\n')
            fid.write('\t(cons \'color #(%d %d %d))\n' % color)
            fid.write('\t(cons \'alpha #(%d))\n' % alpha_channel)
            fid.write(')\n')

        # add board edges
        fid.write('(define-layer! 0 (cons \'filename "%s")\n' % gerber_edge)
        fid.write('\t(cons \'visible #t)\n')
        fid.write('\t(cons \'color #(%d %d %d))\n' % tuple(color_edge))
        fid.write('\t(cons \'alpha #(%d))\n' % alpha_channel)
        fid.write(')\n')

        # add background
        fid.write('(define-layer! -1 (cons \'filename "%s")\n' % filename_gerbv)
        fid.write('\t(cons \'color #(%d %d %d))\n' % tuple(color_none))
        fid.write('\t(cons \'alpha #(%d))\n' % alpha_channel)
        fid.write(')\n')

        # add rendering settings
        fid.write('(set-render-type! 3)\n')


def get_layer_png(tag, data_export, data_gerber, data_stack):
    """
    Transform GERBER files into a PNG file for a given layer.
    """

    # extract the data
    margin = data_export["margin"]
    voxel = data_export["voxel"]
    oversampling = data_export["oversampling"]
    folder_gerber = data_export["folder_gerber"]
    folder_png = data_export["folder_png"]

    # create the file names
    filename_gerbv = "%s.gvp" % tag
    filename_png = "%s.png" % tag

    # get the project files with the GERBER files
    get_gerbv_file(filename_gerbv, folder_gerber, data_gerber, data_stack)

    # get the resolution and margin
    resolution = round(25.4e-3*oversampling/voxel)
    resize = 100/oversampling
    border = 100*margin

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

    # remove the project file
    os.remove(filename_gerbv)

    # move the PNG file
    os.rename(filename_png, os.path.join(folder_png, filename_png))


def get_convert(data_export, data_gerber, data_stack):
    """
    Transform GERBER files into PNG files.
    """

    for tag, data_stack_tmp in data_stack.items():
        get_layer_png(tag, data_export, data_gerber, data_stack_tmp)

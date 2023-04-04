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


def get_gerbv_file(filename_gerbv, data_base, stack):
    """
    Create a "gerbv - Gerber Viewer" project file.
    """

    # extract data
    gerber_edge = data_base["gerber_edge"]
    color_edge = data_base["color_edge"]
    color_none = data_base["color_none"]
    color_def = data_base["color_def"]
    gerber_def = data_base["gerber_def"]

    # get name
    color_edge = color_def[color_edge]
    color_none = color_def[color_none]
    gerber_edge = gerber_def[gerber_edge]

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
        for i, stack_tmp in enumerate(stack):
            # extract data
            layer = i+1
            gerber = stack_tmp["gerber"]
            color = stack_tmp["color"]

            # get color
            color = color_def[color]
            gerber = gerber_def[gerber]

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


def get_png(layer, name, margin, voxel, oversampling, data_base, stack):
    """
    Transform GERBER files into a PNG file for a given layer.
    """

    # create the file names
    filename_gerbv = name + "_" + layer + ".gvp"
    filename_png = name + "_" + layer + ".png"

    # get the project files with the GERBER files
    get_gerbv_file(filename_gerbv, data_base, stack)

    # get the resolution
    resolution = round(25.4e-3*oversampling/voxel)
    resize = 100/oversampling

    # get the margin
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


def get_layer(name, margin, voxel, oversampling, data_base):
    """
    Transform GERBER files into PNG files.
    """

    # front
    stack = [
        {"gerber": "drill", "color": "none"},
        {"gerber": "front", "color": "copper"},
    ]
    get_png("front", name, margin, voxel, oversampling, data_base, stack)

    # back
    stack = [
        {"gerber": "drill", "color": "none"},
        {"gerber": "back", "color": "copper"},
    ]
    get_png("back", name, margin, voxel, oversampling, data_base, stack)

    # terminal
    stack = [
        {"gerber": "drill", "color": "none"},
        {"gerber": "sink", "color": "sink"},
        {"gerber": "src", "color": "src"},
    ]
    get_png("terminal", name, margin, voxel, oversampling, data_base, stack)

    # via
    stack = [
        {"gerber": "drill", "color": "none"},
        {"gerber": "via", "color": "copper"},
    ]
    get_png("via", name, margin, voxel, oversampling, data_base, stack)


if __name__ == "__main__":
    # ######################## get the colors / GERBER files
    color_def = {
        "none":  (255, 255, 255),
        "edge":  (0, 0, 0),
        "copper": (255, 0, 0),
        "sink":  (0, 0, 255),
        "src": (0, 255, 0),
    }
    gerber_def = {
        "edge":  "gerber/generate_gerber-edge.gbr",
        "front": "gerber/generate_gerber-front_copper.gbr",
        "back": "gerber/generate_gerber-back_copper.gbr",
        "src": "gerber/generate_gerber-src.gbr",
        "sink": "gerber/generate_gerber-sink.gbr",
        "drill":  "gerber/generate_gerber-PTH.drl",
        "via":  "gerber/generate_gerber-VIA.drl",
    }
    data_base = {
        "gerber_edge": "edge",
        "color_edge": "edge",
        "color_none": "none",
        "color_def": color_def,
        "gerber_def": gerber_def
    }

    # ######################## get the variables
    name = "gerbv"
    margin = 0.1
    voxel = 17.0e-6
    oversampling = 1.0

    # ######################## run
    get_layer(name, margin, voxel, oversampling, data_base)

"""
Generate PNG files from the GERBER files for the example.
"""

__author__ = "Thomas Guillod"
__copyright__ = "(c) Thomas Guillod - Dartmouth College"

import utils_gerber_png


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
        "edge": "pcb-edge.gbr",
        "front": "pcb-front_copper.gbr",
        "back": "pcb-back_copper.gbr",
        "src": "pcb-src.gbr",
        "sink": "pcb-sink.gbr",
        "drill": "pcb-PTH.drl",
        "via":  "pcb-VIA.drl",
    }
    data_gerber = {
        "gerber_edge": "edge",
        "color_edge": "edge",
        "color_none": "none",
        "color_def": color_def,
        "gerber_def": gerber_def
    }

    # ######################## get the layer stack
    data_stack = {
        "front": [
            {"gerber": "drill", "color": "none"},
            {"gerber": "front", "color": "copper"},
        ],
        "back": [
            {"gerber": "drill", "color": "none"},
            {"gerber": "back", "color": "copper"},
        ],
        "terminal": [
            {"gerber": "drill", "color": "none"},
            {"gerber": "sink", "color": "sink"},
            {"gerber": "src", "color": "src"},
        ],
        "via": [
            {"gerber": "drill", "color": "none"},
            {"gerber": "via", "color": "copper"},
        ],
    }

    # ######################## get the export instructions
    data_export = {
        "margin": 0.1,
        "voxel": 17.0e-6,
        "oversampling": 1.0,
        "folder_gerber": "../gerber",
        "folder_png": "../png",
    }

    # ######################## run
    utils_gerber_png.get_convert(data_export, data_gerber, data_stack)

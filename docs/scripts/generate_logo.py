"""
Script for rendering the PyPEEC logo.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import json
import numpy as np
import pyvista as pv
import PIL.Image as pmg


def get_plotter(off_screen, logo_size, render_size):
    """
    Get a PyVista plotter object.
    """

    # setup plot
    pv.global_theme.transparent_background = True
    pv.global_theme.edge_color = "black"
    pv.global_theme.edge_opacity = 1.0

    # get size
    if off_screen:
        plotter_size = logo_size
    else:
        plotter_size = render_size

    # create plotter
    pl = pv.Plotter(
        off_screen=off_screen,
        window_size=plotter_size,
        line_smoothing=True,
        polygon_smoothing=True,
        lighting="none",
    )

    return pl


def set_camera(pl):
    """
    Set the camera for the plotter object.
    """

    # set the camera angle
    pl.camera_position = "xz"
    pl.camera.azimuth = -45
    pl.camera.elevation = +25

    # set the zoom
    pl.camera.zoom(1.0)

    # set the shift
    pl.camera.SetWindowCenter(0.0, -0.1)


def set_light(pl):
    """
    Set the lights for the plotter object.
    """

    # definition of the lights
    intensity_vec = np.array([0.80, 0.30, 0.40, 0.50])
    position_vec = np.array([[-5, -5, 5], [0, 0, 5], [-5, 0, 0], [0, -5, 0]])

    # add the lights
    for intensity, position in zip(intensity_vec, position_vec, strict=True):
        light = pv.Light(
            light_type="scenelight",
            position=position,
            intensity=intensity,
        )
        pl.add_light(light)


def get_voxel(pl):
    """
    Add the logo to the plotter object.
    """

    # load the voxel data
    with open("brick.json") as file:
        data = json.load(file)
        idx_vec = data["idx_vec"]
        col_vec = data["col_vec"]

    # load voxel shape
    mesh = pv.read("brick.stl")

    # add the voxels
    for col, idx in zip(col_vec, idx_vec, strict=True):
        pl.add_mesh(mesh.translate(idx), color=col)


if __name__ == "__main__":
    # interactive plot
    off_screen = True

    # set the filename
    filename_logo_png = "logo.png"
    filename_logo_icn = "icon.png"
    render_size = (800, 800)
    logo_size = (512, 512)
    icon_size = (96, 96)

    # get the plotter
    pl = get_plotter(off_screen, logo_size, render_size)

    # add the geometry
    get_voxel(pl)

    # set the view
    set_camera(pl)
    set_light(pl)

    # show/save the plot
    if off_screen:
        # save the PNG file
        pl.show(screenshot=filename_logo_png)

        # create the icon
        img = pmg.open(filename_logo_png)
        img = img.resize(icon_size, pmg.BICUBIC)
        img.save(filename_logo_icn)
    else:
        pl.show()

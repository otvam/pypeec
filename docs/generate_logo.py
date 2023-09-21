"""
Script for rendering the PyPEEC logo.

Three files are created:
    - logo.ply: 3D logo in PLY format
    - logo.png: 2D logo in PNG format
    - icon.png: 2D icon in PNG format
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import numpy as np
import pyvista as pv
import matplotlib.cm as cm
import PIL.Image as pmg


def get_voxel():
    """
    Create the voxel structure with the logo.
    """

    # voxel indices
    idx = [
        0,  1,  2,
        6,  7,  8,
        9, 11, 15,
        18, 20, 23,
        24, 25, 26,
    ]

    # voxel colors
    var = [
        0.85714286, 0.78571429, 0.71428571,
        0.14285714, 0.07142857, 0.00000000,
        0.92857143, 0.64285714, 0.21428571,
        1.00000000, 0.57142857, 0.50000000,
        0.28571429, 0.35714286, 0.42857143,
    ]

    # create a uniform grid for the complete structure
    grid = pv.ImageData()

    # set the array size and the voxel size
    grid.origin = (1.5, 1.5, 1.5)
    grid.dimensions = (4, 4, 4)
    grid.spacing = (1, 1, 1)

    # get the voxel structure
    voxel = grid.extract_cells(idx)
    voxel["var"] = var

    return voxel


def get_plotter(voxel):
    """
    Plotter for rendering the logo from the voxel structure.
    """

    # setup plot
    pv.rcParams['transparent_background'] = True
    pv.rcParams["edge_color"] = "black"

    # create plotter
    pl = pv.Plotter(
        window_size=(256, 256),
        off_screen=True,
        line_smoothing=True,
        polygon_smoothing=True,
        lighting="three lights"
    )

    # add content
    pl.add_mesh(
        voxel,
        scalars="var",
        show_scalar_bar=False,
        show_edges=True,
        edge_color="black",
        cmap="viridis",
        line_width=1.0,
    )

    # set camera
    pl.camera.SetWindowCenter(0, -0.1)
    pl.camera.roll = 0
    pl.camera.azimuth = 180
    pl.camera.elevation = 170

    return pl


def get_mesh(voxel):
    """
    Extract a surface mesh from the voxel structure.
    """

    # get mesh
    mesh = voxel.extract_surface()
    var = mesh["var"]

    # get the texture
    texture = cm.viridis(var)
    texture = 255*texture
    texture = texture.astype(np.uint8)

    return mesh, texture


if __name__ == "__main__":
    # get the data
    voxel = get_voxel()
    pl = get_plotter(voxel)
    (mesh, texture) = get_mesh(voxel)

    # set the filename
    filename_logo_ply = "logo.ply"
    filename_logo_png = "logo.png"
    filename_logo_icn = "icon.png"

    # save the PNG file
    pl.show(screenshot=filename_logo_png)

    # save the PLY file
    mesh.save(filename_logo_ply, texture=texture)

    # create the icon
    img = pmg.open(filename_logo_png, formats=["png"])
    img = img.resize((96, 96), pmg.BICUBIC)
    img.save(filename_logo_icn)

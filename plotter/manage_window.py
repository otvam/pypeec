import pyvista as pv


def get_plotter(subplot_shape):
    pl = pv.Plotter(shape=subplot_shape)

    return pl


def get_subplot(pl, pos):
    (row, col) = pos
    pl.subplot(row, col)


def get_flush(pl, title, window_size):
    pl.show(title=title, window_size=window_size)



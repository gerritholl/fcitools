"""Geolocation-related routines
"""

import math
import pyproj
import numpy
import matplotlib.colors
import satpy
import dask.array
import cv2
import PIL
import matplotlib.pyplot

def calc_heading_distance_accurate(lat1, lon1, lat2, lon2):
    """Calculating heading and distance, accurately

    Uses pyproj, assumes WGS84
    """
    geod = pyproj.geod.Geod(ellps="WGS84")
    (heading, _, distance) = geod.inv(lon1.compute(), lat1.compute(), lon2.compute(), lat2.compute())
    return heading, distance

    # should try to dask-ify at some point!
    # problem: https://stackoverflow.com/q/59270302/974555
    def wrap(lon1, lat1, lon2, lat2):
        tp = geod.inv(lon1, lat1, lon2, lat2)
        return dask.array.dstack([tp[0], tp[2]])
    rv = dask.array.map_blocks(
            wrap, lon1, lat1, lon2, lat2,
            dtype="f4",
            chunks=(128, 128, 2))
    heading = rv[:, :, 0]
    distance = rv[:, :, 1]
    return (heading, distance)


def calc_rgb_from_heading_distance(heading, distance, f=0.01):
    """Calculate RGB from heading and distance

    Heading shall be between ±pi/2
    """
    hsv = dask.array.concatenate([
            (heading[..., numpy.newaxis]+180)/360,
            dask.array.full(heading.shape + (1,), 1, dtype="f4"),
            dask.array.where(f*distance<1, f*distance, 1)[..., numpy.newaxis]],
            axis=2)
    rgb = matplotlib.colors.hsv_to_rgb(hsv)
    return rgb


def get_legend(n=1000, ang_range=(-180, 180),
               dist_range=(0, 100)):
    """Get an RGB to use for the legend

    Get an RGB image illustrating the colour as a function of distance and
    heading.  This is essentially a 2-dimensional colourbar.

    See also: :func:`plot_legend`.

    Args:
        n (Optional[int]):
            Number of steps to use for each axis.
        ang_range (Optional[Tuple]):
            Range of angles (in degrees) for which to visualise the legend.
            Defaults to (-180, 180).
        dist_range (Optional[Tuple])
            Range of distances (in metres) for which the visualise the legend.
            Defaults to (0, 100).
    Returns:
        ndarray [nx, ny, 3]
            RGB image illustrating the values per distance and heading.
    """
    head = dask.array.linspace(*ang_range, n)
    distance = dask.array.linspace(*dist_range, n)
    return calc_rgb_from_heading_distance(*dask.array.meshgrid(head, distance))


def plot_legend(rgb,
                ang_range=(-180, 180),
                dist_range=(0, 100)):
    """Plot a legend into a matplotlib axis

    Plot an RGB legend, obtained through :func:`get_legend`, into a matplotlib
    axis.

    Caution: the RGB legend is a pure ndarray with no coordinate or axes
    information.  Therefore, the user must be careful to pass the same
    ``ang_range`` and ``dist_range`` arguments to :func:`plot_legend` as to
    :func:`get_legend`.

    Args:
        rgb (ndarray)
            RGB image obtained through :func:`get_legend`
        ang_range (Optional[Tuple]):
            Range of angles (in degrees) for which to visualise the legend.
            Defaults to (-180, 180).
        dist_range (Optional[Tuple])
            Range of distances (in metres) for which the visualise the legend.
            Defaults to (0, 100).
    Returns:
        (Figure, Axes) matplotlib figure and axes objects that have been
        created and into which the legend has been plotted
    """
    (f, ax) = matplotlib.pyplot.subplots(1, 1)
    ax.imshow(rgb,
              extent=[*ang_range, *dist_range],
              origin="lower",
              aspect="auto")
    ax.set_xlabel("direction / degrees")
    ax.set_ylabel("distance / m")
    return (f, ax)


def compare_geolocation(sc, chan, _x_start=1, _y_start=1, _x_end=None, _y_end=None):
    """Compare pytroll and EUM geolocation

    Compare geolocation as calculated by satpy and the one provided by
    EUMETSAT.  Note that the EUMETSAT code is not publicly available.

    Args:
        sc (satpy.Scene)
            satpy Scene object to use for the calculations.
        chan (str)
            Channel (or otherwise satpy dataset) for which to calculate the
            geolocation.
    Returns:
        ndarray [n_x, n_y, 3] RGB image corresponding to the full disk size of
        the channel.  The hue of each pixel corresponds to the direction of the
        displacement between EUMETSAT and pytroll, the brightness value
        corresponds to the magnitude.  For a legend, call :func:`get_legend`.
    """

    ar = sc[chan].area
    _x_end = _x_end if _x_end is not None else ar.x_size + 1
    _y_end = _y_end if _y_end is not None else ar.y_size + 1
    xc = dask.array.arange(_x_start, _x_end, dtype="f4", chunks=128)
    yc = dask.array.arange(_y_start, _y_end, dtype="f4", chunks=128)
    (y, x) = dask.array.meshgrid(yc, xc)
    res = abs(int(ar.resolution[0]))
    from . import eumsecret
    (eum_lat, eum_lon) = eumsecret.pixcoord2geocoord(
            x, y, eumsecret.r_eq, eumsecret.f, eumsecret.h,
            eumsecret.lambda_d, eumsecret.grid_params[res]["lamb"],
            eumsecret.grid_params[res]["phi"],
            eumsecret.grid_params[res]["azimuth_grid_sampling"],
            eumsecret.grid_params[res]["elevation_grid_sampling"])
    (pyt_lon, pyt_lat) = ar.get_lonlats(chunks=128, dtype="f4")

    (heading, distance) = calc_heading_distance_accurate(
            eum_lat, eum_lon, pyt_lat, pyt_lon)

    rgb = calc_rgb_from_heading_distance(heading, distance)

    return rgb


def save_rgb(rgb, fl):
    """Save RGB to file

    Rescale an RGB and save it directly to a file.  This is primarily intended
    for the pure image, the legend is better plotted with :func:`plot_legend`.

    Args:
        rgb (ndarray)
            RGB image as returned by :func:`compare_geolocation`
        fl (str)
            Path or file to which to save the image
    """
    rescaled = (255*rgb).astype(numpy.uint8)
    im = PIL.Image.fromarray(rescaled)
    im.save(fl)

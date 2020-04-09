"""Geolocation-related routines.

This module contains routines related to geolocation calculations.  In
particular, it contains methods to calculate and visualise the difference
between the pytroll FCI geolocation and those provided by EUMETSAT.  The
EUMETSAT calculation however is not publicly available.

Example code of how to use this::

    import numpy
    from satpy import Scene
    from glob import glob
    from PIL import Image
    import fcitools.geo
    srcdir = "/media/nas/x21308/2020_04_MTG_unofficial_Testdata/20130804_RC72/"
    fciscene = Scene(sensor="fci", reader=["fci_l1c_fdhsi"],
                     filenames=glob(srcdir + "/*BODY*.nc"))
    fciscene.load(["vis_09"])
    rgb = fcitools.geo.compare_geolocation(fciscene, "vis_09")

    fcitools.geo.save_rgb(rgb, "/tmp/test.png")
    #fcitools.geo.save_rgb(fcitools.geo.get_legend(), "/tmp/legend.png")
    (f, ax) = fcitools.geo.plot_legend(fcitools.geo.get_legend())
    f.savefig("/tmp/legend.png")

    (pyt_lat, pyt_lon, eum_lat, eum_lon) = fcitools.geo.get_lat_lon_pair(
            fciscene, "vis_09")
    (heading, distance) = fcitools.geo.calc_heading_distance_accurate(
            eum_lat, eum_lon, pyt_lat, pyt_lon)
    distcomp = distance.compute()
    print(np.median(ma.masked_invalid(distcomp)))

This reveals that with the spring 2020 test data release, the median difference
between the two calculations is 8.628 metre.  For comparison, the distance
between (45N, 45E) and ((45+eps)N, 45E) is 42 cm in single precision and 1.1 nm
in double precision.  The cases with large difference are near the edge.  Among
the 100 pixels closest to the rim, the median is 73 metre, and 5% of those
pixels have more than 287 metre difference, in two opposite directions.  See
https://pytroll.slack.com/files/UGU1HTMUG/F011RMANGJD/grafik.png for a pretty
400% zoom visualising the differences near the edge.
"""

import pyproj
import numpy
import matplotlib.colors
import dask.array
import PIL
import matplotlib.pyplot


def calc_heading_distance_accurate(lat1, lon1, lat2, lon2):
    """Calculating heading and distance, accurately

    Uses pyproj, assumes WGS84

    Args:
        lat1 (float)
        lon1 (float)
        lat2 (float)
        lon2 (float)

    Returns:
        heading (degrees)
        distance (metre)
    """
    geod = pyproj.geod.Geod(ellps="WGS84")

    def _wrap(lon1, lat1, lon2, lat2):
        tp = geod.inv(lon1, lat1, lon2, lat2)
        return numpy.concatenate([
            tp[0][..., numpy.newaxis],
            tp[2][..., numpy.newaxis]],
            axis=lon1.ndim)
    if hasattr(lon1, "chunks"):
        rv = dask.array.map_blocks(
                _wrap, lon1, lat1, lon2, lat2,
                dtype="f4",
                chunks=lon1.chunks + (2,),
                new_axis=lon1.ndim)
        heading = rv[..., 0]
        distance = rv[..., 1]
        return (heading, distance)
    else:  # not a dask array
        (heading, _, distance) = geod.inv(lon1, lat1, lon2, lat2)
        return heading, distance


def calc_rgb_from_heading_distance(heading, distance, f=0.01):
    """Calculate RGB from heading and distance

    Calculate an RGB visualising the heading and the distance.  The heading
    will be mapped unto the hue in HSV space, and the distance will map onto
    the brightness, or value in HSV.  The saturation is always set to 1.
    This means that the resulting RGB will have those primary and secondary
    colours:

    * black if distance is zero
    * red [1, 0, 0] where the heading is straight south (180 degrees)
    * green [0, 1, 0] where the heading is WNW (-60 degrees)
    * blue [0, 0, 1] where the heading is ENE (60 degrees)
    * cyan [0, 1, 1] where the heading is straight north (0 degrees)
    * yellow [1, 1, 0] where heading is WSW (-120 degrees)
    * magenta [1, 0, 1] where heading is ESE (120 degrees)

    To get a legend illustrating the resulting angles and magnitudes, use
    :func:`get_legend` and :func:`plot_legend`.

    Args:
        heading (ndarray):
            Direction, where 0 is north, 90 is east, -90 is west, and ±180
            is south.
        distance (ndarray):
            Distance / magnitude
        f (Optional[float]):
            Scale factor.  After multiplication with this scale factor, any
            distances larger than 1 will be capped.  So if you pass in 0.01,
            the intensity will max out at 100.
    """
    hsv = dask.array.concatenate([
            (heading[..., numpy.newaxis] + 180) / 360,
            dask.array.full(heading.shape + (1,), 1, dtype="f4"),
            dask.array.where(f * distance < 1,
                             f * distance, 1)[..., numpy.newaxis]],
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


def get_lat_lon_pair(sc, chan, _x_start=1, _y_start=1,
                     _x_end=None, _y_end=None):
    """Get a pair of lat/lons

    Args:
        sc (satpy.Scene)
            satpy Scene object to use for the calculations.
        chan (str)
            Channel (or otherwise satpy dataset) for which to calculate the
            geolocation.  Channel must be loaded first.
    Returns:
        (lat_pyt, lon_pyt, lat_eum, lon_eum)
    """
    ar = sc[chan].area
    _x_end = _x_end if _x_end is not None else ar.x_size + 1
    _y_end = _y_end if _y_end is not None else ar.y_size + 1
    xc = dask.array.arange(_x_start, _x_end, dtype="f4", chunks=128)
    yc = dask.array.arange(_y_start, _y_end, dtype="f4", chunks=128)
    (y, x) = dask.array.meshgrid(yc, xc)
    res = abs(round(ar.resolution[0]))
    from . import eumsecret
    (eum_lat, eum_lon) = eumsecret.pixcoord2geocoord(
            x, y, eumsecret.r_eq, eumsecret.f, eumsecret.h,
            eumsecret.lambda_d, eumsecret.grid_params[res]["lamb"],
            eumsecret.grid_params[res]["phi"],
            eumsecret.grid_params[res]["azimuth_grid_sampling"],
            eumsecret.grid_params[res]["elevation_grid_sampling"])
    (pyt_lon, pyt_lat) = ar.get_lonlats(chunks=128, dtype="f4")

    return (pyt_lat, pyt_lon, eum_lat, eum_lon)


def compare_geolocation(sc, chan, _x_start=1, _y_start=1,
                        _x_end=None, _y_end=None):
    """Compare pytroll and EUM geolocation

    Compare geolocation as calculated by satpy and the one provided by
    EUMETSAT.  Note that the EUMETSAT code is not publicly available.

    Args:
        sc (satpy.Scene)
            satpy Scene object to use for the calculations.
        chan (str)
            Channel (or otherwise satpy dataset) for which to calculate the
            geolocation.  Channel must be already loaded.
    Returns:
        ndarray [n_x, n_y, 3] RGB image corresponding to the full disk size of
        the channel.  The hue of each pixel corresponds to the direction of the
        displacement between EUMETSAT and pytroll, the brightness value
        corresponds to the magnitude.  For a legend, call :func:`get_legend`.
    """

    (pyt_lat, pyt_lon, eum_lat, eum_lon) = get_lat_lon_pair(
            sc, chan, _x_start=_x_start, _y_start=_y_start,
            _x_end=_x_end, _y_end=_y_end)

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

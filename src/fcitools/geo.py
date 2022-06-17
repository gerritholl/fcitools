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

import dask.array

from sattools.geo import (calc_heading_distance_accurate,
                          calc_rgb_from_heading_distance)


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

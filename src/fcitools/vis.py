"""Routines related to visualisation
"""

import satpy
import glob
import pathlib
from .ioutil import unpack_tgz

def unpack_and_show_testdata(
        path_to_tgz,
        composites,
        channels,
        regions,
        d_out,
        fn_out="{area:s}_{dataset:s}.tiff",
        path_to_coastlines=None):
    """Unpack and show image from testdata

    Taking a ``.tar.gz``-archived file from the FCI test data, unpack such a
    file and write the desired composites and channels for each of the desired
    regions.

    Args:
        path_to_tgz (str):
            Path to ``.tar.gz`` file containing test data

        composites (List[str]):
            List of composites to be generated

        channels (List[str]):
            List of channels (datasets) to be generated

        regions (List[str]):
            List of regions/areas these shall be generated for

        d_out (str):
            Path to directory where output files shall be written.

        fn_out (Optional[str]):
            Pattern of filename in output directory.  Using Python's string
            formatting syntax, the fields ``area`` and ``dataset`` will be
            replaced by the region/area and the composite/channel.

        path_to_coastlines (Optional[Str]):
            If given, directory to use for coastlines.

    Returns:
        List of filenames written
    """

    td = unpack_tgz(path_to_tgz)
    p = pathlib.Path(path_to_tgz).stem.split(".")[0] # true stem

    names = show_testdata_from_dir(
            td.name + "/" + p,
            composites,
            channels,
            regions,
            d_out,
            fn_out,
            path_to_coastlines=path_to_coastlines)
    td.cleanup()
    return names

def show_testdata_from_dir(
        d,
        composites,
        channels,
        regions,
        d_out,
        fn_out,
        path_to_coastlines=None):
    """Visualise a directory of EUM FCI test data

    From a directory containing EUMETSAT FCI test data, visualise composites
    and channels for the given regions/areas, possibly adding coastlines.

    Args:
        d (str):
            Path to directory containing test data

        composites (List[str]):
            List of composites to be generated

        channels (List[str]):
            List of channels (datasets) to be generated

        regions (List[str]):
            List of regions/areas these shall be generated for

        d_out (str):
            Path to directory where output files shall be written.

        fn_out (Optional[str]):
            Pattern of filename in output directory.  Using Python's string
            formatting syntax, the fields ``area`` and ``dataset`` will be
            replaced by the region/area and the composite/channel.

        path_to_coastlines (Optional[Str]):
            If given, directory to use for coastlines.

    Returns:
        List of filenames written
    """
    L = []
    sc = satpy.Scene(
            sensor="fci",
            filenames=glob.glob(d + "/*BODY*.nc"),
            reader=["fci_l1c_fdhsi"])
    if path_to_coastlines is not None:
        overlay = {"coast_dir": path_to_coastlines, "color": "red"}
    else:
        overlay = None
    sc.load(channels)
    sc.load(composites)
    for nm in regions:
        ls = sc.resample(nm)
        for dn in composites + channels:
            fn = pathlib.Path(d_out) / fn_out.format(
                    area=nm, dataset=dn)
            ls.save_dataset(
                    dn,
                    filename=str(fn),
                    overlay=overlay)
            L.append(fn)
    return L

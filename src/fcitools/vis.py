"""Routines related to visualisation
"""

import numpy
import satpy
import pathlib
import xarray
from . import ioutil


def unpack_and_show_testdata(
        path_to_tgz,
        composites,
        channels,
        regions,
        d_out,
        fn_out="{area:s}_{dataset:s}.tiff",
        path_to_coastlines=None,
        show_only_coastlines=False):
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

        d_out (pathlib.Path):
            Path to directory where output files shall be written.

        fn_out (Optional[str]):
            Pattern of filename in output directory.  Using Python's string
            formatting syntax, the fields ``area`` and ``dataset`` will be
            replaced by the region/area and the composite/channel.

        path_to_coastlines (Optional[Str]):
            If given, directory to use for coastlines.

        show_only_coastlines (Optional[bool]):
            If true, prepare an image showing only coastlines.

    Returns:
        List of filenames written
    """

    paths = ioutil.unpack_tgz(path_to_tgz)
    areas = ioutil.get_all_areas()
    p = pathlib.Path(path_to_tgz).stem.split(".")[0]  # true stem

    names = show_testdata_from_dir(
            {str(p) for p in paths},
            composites,
            channels,
            [areas.get(nm) for nm in regions],
            d_out,
            fn_out,
            path_to_coastlines=path_to_coastlines,
            label=p,
            show_only_coastlines=show_only_coastlines)
    td.cleanup()
    return names


def show_testdata_from_dir(
        files,
        composites,
        channels,
        regions,
        d_out,
        fn_out,
        path_to_coastlines=None,
        label="",
        show_only_coastlines=False):
    """Visualise a directory of EUM FCI test data

    From a directory containing EUMETSAT FCI test data, visualise composites
    and channels for the given regions/areas, possibly adding coastlines.

    Args:
        files (List[pathlib.Path]):
            Paths to files

        composites (List[str]):
            List of composites to be generated

        channels (List[str]):
            List of channels (datasets) to be generated

        regions (List[str]):
            List of AreaDefinition objects these shall be generated for.
            The special region 'native' means no reprojection is applied.

        d_out (pathlib.Path):
            Path to directory where output files shall be written.

        fn_out (Optional[str]):
            Pattern of filename in output directory.  Using Python's string
            formatting syntax, the fields ``area`` and ``dataset`` will be
            replaced by the region/area and the composite/channel.

        path_to_coastlines (Optional[Str]):
            If given, directory to use for coastlines.

        label (Optiona[Str]):
            Additional label to substitute into fn_out.

        show_only_coastlines (Optional[bool]):
            If true, prepare images showing only coastlines.  Needs at least
            one channel to be loaded.  Backgrounds will be white, black, and
            transparent.

    Returns:
        List of filenames written
    """
    L = []
    sc = satpy.Scene(
            sensor="fci",
            filenames=files,
            reader=["fci_l1c_fdhsi"])
    if path_to_coastlines is not None:
        overlay = {"coast_dir": path_to_coastlines, "color": "red"}
    else:
        overlay = None
    sc.load(channels)
    sc.load(composites)
    if show_only_coastlines:
        sc["black"] = xarray.zeros_like(sc[(channels+composites).pop(0)])
        sc["white"] = xarray.ones_like(sc[(channels+composites).pop(0)])
        sc["nans"] = xarray.full_like(sc[(channels+composites).pop(0)],
                                      numpy.nan)
    for la in regions:
        ls = sc.resample(la)
        for dn in ls.keys():
            fn = pathlib.Path(d_out) / fn_out.format(
                    area=getattr(la, "area_id", "native"),
                    dataset=dn.name,
                    label=label)
            ls.save_dataset(
                    dn,
                    filename=str(fn),
                    overlay=overlay)
            L.append(fn)
    return L

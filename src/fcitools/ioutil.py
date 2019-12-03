"""Utilities related to IO
"""

import gzip
import tarfile
import tempfile
import pkg_resources
import pyresample

def unpack_tgz(path_to_tgz):
    """Unpack a .tar.gz archive to a temporary directory

    Unpack a .tar.gz archive to a named temporary directory.

    Args:

        path_to_tgz (str):
            Path to the ``.tar.gz`` file to be unpacked

    Returns:

        `TemporaryDirectory` object
    """

    with gzip.open(path_to_tgz) as fd:
        tf = tarfile.TarFile(fileobj=fd)
        od = tempfile.TemporaryDirectory()
        tf.extractall(od.name)
    return od

def get_all_areas():
    """Get a dictionary with all findable areas
    """

    D = {}
    for pkg in ["satpy", "fcitools"]:
        fn = pkg_resources.resource_filename(pkg, "etc/areas.yaml")
        areas = pyresample.area_config.load_area(fn)
        D.update({ar.area_id: ar for ar in areas})
    return D

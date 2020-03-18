"""Utilities related to IO
"""

import gzip
import tarfile
import tempfile
import pkg_resources
import pyresample
import sattools.ptc


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

    return sattools.ptc.get_all_areas(["satpy", "fcitools"])

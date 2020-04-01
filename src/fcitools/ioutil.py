"""Utilities related to IO
"""

import pathlib
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

        (`TemporaryDirectory` object, List[str] with names)
    """

    if path_to_tgz.suffix == ".tar":
        mode = "r"
    elif path_to_tgz.suffix in {".bz2", ".gz", ".xz"}:
        mode = "r:" + path_to_tgz.suffix[1:]
    else:
        raise ValueError(f"Not a gz/bz2/lzma file: {path_to_tgz!s}")

    with tarfile.open(path_to_tgz, mode) as tf:
        od = tempfile.TemporaryDirectory()
        names = tf.getnames()
        tf.extractall(od.name)
    return (od, names)


def get_all_areas():
    """Get a dictionary with all findable areas
    """

    return sattools.ptc.get_all_areas(["satpy", "fcitools"])

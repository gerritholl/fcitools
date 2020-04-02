"""Utilities related to IO
"""

import logging
import tarfile
import sattools.ptc
import sattools.io

logger = logging.getLogger(__name__)


def _get_path_to_unpack_to(p):
    cd = sattools.io.get_cache_dir(subdir="fcitools")
    return cd / p.name.replace(".", "_")


def unpack_tgz(path_to_tgz):
    """Unpack a .tar.gz archive to a cache directory

    Unpack a .tar.gz archive to a cache directory, unless a file from
    the same path had already been unpacked to this location.  The
    .tar.gz. must contain exactly one subdirectory.

    Args:

        path_to_tgz (str):
            Path to the ``.tar.gz`` file to be unpacked

    Returns:

        iterator with paths to files
    """

    if path_to_tgz.suffix == ".tar":
        mode = "r"
    elif path_to_tgz.suffix in {".bz2", ".gz", ".xz"}:
        mode = "r:" + path_to_tgz.suffix[1:]
    else:
        raise ValueError(f"Not a gz/bz2/lzma file: {path_to_tgz!s}")
    to = _get_path_to_unpack_to(path_to_tgz)
    if not to.exists():
        logger.debug(f"Unpacking {path_to_tgz!s} to {to!s}")
        to.mkdir(parents=True, exist_ok=False)
        with tarfile.open(path_to_tgz, mode) as tf:
            tf.extractall(to)
    else:
        logger.debug(f"Reading unpacked {path_to_tgz!s} from cache at {to!s}")
    subdirs = list(to.iterdir())
    if len(subdirs) != 1:
        raise ValueError(f"Found {len(subdirs):d} files, expected "
                         "exactly one")
    return subdirs[0].iterdir()


def get_all_areas():
    """Get a dictionary with all findable areas
    """

    return sattools.ptc.get_all_areas(["satpy", "fcitools"])

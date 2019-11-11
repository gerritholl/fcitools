"""Utilities related to IO
"""

import gzip
import tarfile
import tempfile

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

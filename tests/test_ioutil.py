import logging
import pathlib
import pytest
import types
import os
from unittest.mock import patch


def test_unpack_tgz(tmp_path, tfs, caplog):
    import fcitools.ioutil
    (tf1, tf2) = tfs
    os.environ["XDG_CACHE_HOME"] = str(tmp_path)
    exp = tmp_path / "fcitools" / "file_tar" / "subdir"
    with caplog.at_level(logging.DEBUG):
        paths1 = fcitools.ioutil.unpack_tgz(tf1)
        assert isinstance(paths1, types.GeneratorType)
        paths1 = set(paths1)
        assert all(p.exists() for p in paths1)
        assert "Unpacking" in caplog.text
        assert paths1 == {exp / f"file{i:d}.dat" for i in range(3)}
        paths2 = fcitools.ioutil.unpack_tgz(tf2)
        assert {p.name for p in paths1} == {p.name for p in paths2}
        paths3 = fcitools.ioutil.unpack_tgz(tf1)
        assert "Reading unpacked" in caplog.text
        assert set(paths1) == set(paths3)

    # test with bad cases

    with pytest.raises(ValueError):
        fcitools.ioutil.unpack_tgz(pathlib.Path("not.here"))

    import tarfile

    with tarfile.open(tmp_path / "bad.tar", "w"):
        pass

    with pytest.raises(ValueError):
        fcitools.ioutil.unpack_tgz(tmp_path / "bad.tar")

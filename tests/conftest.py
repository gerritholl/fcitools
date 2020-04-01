import pytest
import os
import tarfile


@pytest.fixture
def tfs(tmp_path):
    ptd = tmp_path / "tartest1"
    ptd.mkdir(exist_ok=True, parents=True)
    os.chdir(ptd)
    with open("file1.dat", "wb") as fp:
        fp.write(b"abcd")
    with open("file2.dat", "wb") as fp:
        fp.write(b"efgh")
    with tarfile.open(ptd / "file.tar", "w") as tf:
        tf.add("file1.dat")
        tf.add("file2.dat")
    with tarfile.open(ptd / "file.tar.gz", "w:gz") as tf:
        tf.add("file1.dat")
        tf.add("file2.dat")
    return (ptd / "file.tar", ptd / "file.tar.gz")


@pytest.fixture
def areas():
    import pyresample.geometry
    ad = pyresample.geometry.AreaDefinition(
            "shrubbery", "it is a good shrubbery", "shrub",
            {'ellps': 'WGS84', 'lat_0': '0', 'lat_ts': '0', 'lon_0': '0',
             'no_defs': 'None', 'proj': 'eqc', 'type': 'crs', 'units': 'm',
             'x_0': 0, 'y_0': 0},
            750, 300, (2500000, 4000000, 3000000, 40000000))
    return [ad]

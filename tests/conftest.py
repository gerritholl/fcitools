import pytest
import tarfile


@pytest.fixture
def tfs(tmp_path):
    ptd = tmp_path / "tartest1"
    sd = ptd / "subdir"
    sd.mkdir(exist_ok=False, parents=True)
    for i in range(3):
        with (sd / f"file{i:d}.dat").open("wb") as fp:
            fp.write(b"abcd")
    tfn1 = ptd / "file.tar"
    tfn2 = ptd / "file.tar.gz"
    with tarfile.open(tfn1, "w") as tf:
        tf.add(sd, arcname=sd.name)
    with tarfile.open(tfn2, "w:gz") as tf:
        tf.add(sd, arcname=sd.name)
    return (tfn1, tfn2)


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

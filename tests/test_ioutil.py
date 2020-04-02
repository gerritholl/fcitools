import pathlib
import pytest
from unittest.mock import patch


def test_unpack_tgz(tmp_path, tfs):
    import fcitools.ioutil
    for t in tfs:
        (od, names) = fcitools.ioutil.unpack_tgz(t)
        p = pathlib.Path(od.name)
        assert p.exists()
        assert p.is_dir()
        assert set(p.iterdir()) == {p / "file1.dat", p / "file2.dat"}
        assert names == ["file1.dat", "file2.dat"]
    with pytest.raises(ValueError):
        fcitools.ioutil.unpack_tgz(pathlib.Path("not.here"))


@patch("pyresample.area_config.load_area", autospec=True)
@patch("pkg_resources.resource_filename", autospec=True)
def test_get_areas(prf, pac, areas):
    # need to mock pkg_resources.resource_filename
    # and pyresample.area_config.load_area
    # such that I get a list of areas
    import fcitools.ioutil
    prf.return_value = "/dev/null"
    pac.return_value = areas
    D = fcitools.ioutil.get_all_areas()
    assert prf.call_count == 2
    assert pac.call_count == 2
    assert D == {"shrubbery": areas[0]}

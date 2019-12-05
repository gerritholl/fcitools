"""Test visualisation routines
"""

import pathlib
from unittest.mock import patch, Mock, call
import fcitools.vis
import fcitools.ioutil


@patch("fcitools.ioutil.unpack_tgz", autospec=True)
@patch("fcitools.ioutil.get_all_areas", autospec=True)
@patch("fcitools.vis.show_testdata_from_dir", autospec=True)
def test_unpack_and_show_testdata(st, ga, ut):
    ut.return_value.name = "/tmp/pinguin"
    ga.return_value = {"olympus_mons": "mountain"}
    fcitools.vis.unpack_and_show_testdata(
            "/whats/on/the/telly.tgz", ["mars_rgb"], ["vis_00"],
            ["olympus_mons"], "/out")
    ut.assert_called_once_with("/whats/on/the/telly.tgz")
    ga.assert_called_once_with()
    st.assert_called_once_with(
            "/tmp/pinguin/telly", ["mars_rgb"], ["vis_00"], ["mountain"],
            "/out", "{area:s}_{dataset:s}.tiff",
            label="telly", path_to_coastlines=None)


@patch("satpy.Scene", autospec=True)
@patch("glob.glob", autospec=True)
def test_show_testdata(gl, sc):
    m = Mock()
    m.area_id = "mountain"
    v = Mock()
    v.area_id = "valley"
    c = Mock()
    c.area_id = "crater"
    L = fcitools.vis.show_testdata_from_dir(
            "/tmp/pinguin/telly", ["mars_rgb", "venus_rgb"],
            ["vis_00", "ir_00", "uv_00"],
            [m, v, c],
            "/out", "{label:s}_{area:s}_{dataset:s}.tiff",
            path_to_coastlines="/coast", label="fish")
    assert sc.return_value.resample.return_value.save_dataset.call_count == 15
    assert set(L) == {pathlib.Path("/out") /
                      f"fish_{area:s}_{ds:s}.tiff"
                      for ds in ["mars_rgb", "venus_rgb",
                                 "vis_00", "ir_00", "uv_00"]
                      for area in ["mountain", "valley", "crater"]}
    sc.return_value.resample.return_value.save_dataset.assert_has_calls(
            [call("ir_00",
                  filename="/out/fish_mountain_ir_00.tiff",
                  overlay={"coast_dir": "/coast", "color": "red"})])
    L = fcitools.vis.show_testdata_from_dir(
            "/tmp/pinguin/telly", ["mars_rgb", "venus_rgb"],
            ["vis_00", "ir_00", "uv_00"],
            [m, v, c],
            "/out", "{label:s}_{area:s}_{dataset:s}.tiff",
            label="fish")
    sc.return_value.resample.return_value.save_dataset.assert_has_calls(
            [call("ir_00",
                  filename="/out/fish_mountain_ir_00.tiff",
                  overlay=None)])

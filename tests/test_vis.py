"""Test visualisation routines
"""

import pathlib
from unittest.mock import patch, call


@patch("satpy.Scene", autospec=True)
@patch("sattools.ptc.get_all_areas", autospec=True)
def test_unpack_and_show_testdata(ga, sS, tfs, tmp_path, areas):
    import fcitools.vis
    ga.return_value = {"shrubbery": areas[0]}
    fcitools.vis.unpack_and_show_testdata(
            tfs[0], ["mars_rgb"], ["vis_00"],
            ["shrubbery"], tmp_path)
    ga.assert_called_once_with()
    # more rigorous testing in test_show_testdata


@patch("satpy.Scene", autospec=True)
@patch("glob.glob", autospec=True)
def test_show_testdata(gl, sc, areas):
    import fcitools.vis
    from satpy.tests.utils import make_dataid
    comps = ["mars_rgb", "venus_rgb"]
    chans = ["vis_00", "ir_00", "uv_00"]
    D = {make_dataid(name=k): None for k in comps+chans}
    sc.return_value.resample.return_value.keys.side_effect = D.keys
    L = fcitools.vis.show_testdata_from_dir(
            "/tmp/pinguin/telly", comps, chans, areas,
            pathlib.Path("/out"), "{label:s}_{area:s}_{dataset:s}.tiff",
            path_to_coastlines="/coast", label="fish")
    assert sc.return_value.resample.return_value.save_dataset.call_count == 5
    assert set(L) == {pathlib.Path("/out") /
                      f"fish_{area:s}_{ds:s}.tiff"
                      for ds in ["mars_rgb", "venus_rgb",
                                 "vis_00", "ir_00", "uv_00"]
                      for area in ["shrubbery"]}
    sc.return_value.resample.return_value.save_dataset.assert_has_calls(
            [call(make_dataid(name="ir_00"),
                  filename="/out/fish_shrubbery_ir_00.tiff",
                  overlay={"coast_dir": "/coast", "color": "red"})])
    L = fcitools.vis.show_testdata_from_dir(
            "/tmp/pinguin/telly", ["mars_rgb", "venus_rgb"],
            ["vis_00", "ir_00", "uv_00"],
            areas,
            pathlib.Path("/out"), "{label:s}_{area:s}_{dataset:s}.tiff",
            label="fish")
    sc.return_value.resample.return_value.save_dataset.assert_has_calls(
            [call(make_dataid(name="ir_00"),
                  filename="/out/fish_shrubbery_ir_00.tiff",
                  overlay=None)])

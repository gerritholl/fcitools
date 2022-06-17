"""Test visualisation routines
"""

import pathlib

from unittest.mock import patch


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


@patch("sattools.vis.show", autospec=True)
@patch("glob.glob", autospec=True)
def test_show_testdata(gl, sc, areas):
    import fcitools.vis
    # just a thin wrapper…
    fcitools.vis.show_testdata_from_dir(
            "/tmp/pinguin/telly", "comps", "chans", "areas",
            pathlib.Path("/out"), "{label:s}_{area:s}_{dataset:s}.tiff",
            path_to_coastlines="/coast", label="fish")

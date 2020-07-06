"""Test visualisation routines
"""

import pathlib
from unittest.mock import patch, call


@patch("satpy.Scene", autospec=True)
@patch("fcitools.ioutil.get_all_areas", autospec=True)
def test_unpack_and_show_testdata(ga, sS, tfs, tmp_path, areas):
    import fcitools.vis
    ga.return_value = {"shrubbery": areas[0]}
    fcitools.vis.unpack_and_show_testdata(
            tfs[0], ["mars_rgb"], ["vis_00"],
            ["shrubbery"], tmp_path)
    ga.assert_called_once_with()
    # more rigorous testing in test_show_testdata

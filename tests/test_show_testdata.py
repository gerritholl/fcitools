"""Test the show_testdata script
"""

from unittest.mock import patch
import fcitools.processing.show_testdata

@patch("argparse.ArgumentParser", autospec=True)
def test_get_parser(ap):
    fcitools.processing.show_testdata.parse_cmdline()
    assert ap.return_value.add_argument.call_count == 7

@patch("satpy.utils.debug_on", autospec=True)
@patch("fcitools.processing.show_testdata.parse_cmdline", autospec=True)
@patch("fcitools.vis.unpack_and_show_testdata", autospec=True)
def test_main(us, pc, do):
    pc.return_value.path = "/"
    pc.return_value.composites = ["foo"]
    pc.return_value.channels = ["ir_00"]
    pc.return_value.areas = ["mars"]
    pc.return_value.outdir = "/out"
    pc.return_value.filename_pattern = "{label:s}_{area:s}_{dataset:s}.tiff"
    pc.return_value.coastline_dir = "/coast"
    fcitools.processing.show_testdata.main()
    do.assert_called_once_with()
    pc.assert_called_once_with()
    us.assert_called_once_with("/", ["foo"], ["ir_00"], ["mars"], "/out",
                               "{label:s}_{area:s}_{dataset:s}.tiff",
                               "/coast")

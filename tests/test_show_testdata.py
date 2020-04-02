"""Test the show_testdata script
"""

import os
from unittest.mock import patch


@patch("argparse.ArgumentParser", autospec=True)
def test_get_parser(ap):
    import fcitools.processing.show_testdata
    fcitools.processing.show_testdata.parse_cmdline()
    assert ap.return_value.add_argument.call_count == 7


@patch("satpy.Scene", autospec=True)
@patch("fcitools.processing.show_testdata.parse_cmdline", autospec=True)
def test_main(fpsp, sS, tfs, tmp_path):
    import fcitools.processing.show_testdata
    fpsp.return_value = fcitools.processing.show_testdata.\
        get_parser().parse_args([
                str(tfs[1]),
                str(tmp_path),
                "--composites", "overview", "natural_color", "fog",
                "--channels", "vis_04", "nir_13", "ir_38", "wv_87",
                "-a", "socotra", "bornholm"])

    os.environ["XDG_CACHE_HOME"] = str(tmp_path)
    fcitools.processing.show_testdata.main()
    sS.assert_called_once_with(
        sensor="fci",
        filenames={str(tmp_path / "fcitools" / "file_tar_gz"
                       / "subdir" / f"file{i:d}.dat")
                   for i in (1, 2, 0)},
        reader=["fci_l1c_fdhsi"])

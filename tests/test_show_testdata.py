"""Test the show_testdata script
"""

from unittest.mock import patch


@patch("argparse.ArgumentParser", autospec=True)
def test_get_parser(ap):
    import fcitools.processing.show_testdata
    fcitools.processing.show_testdata.parse_cmdline()
    assert ap.return_value.add_argument.call_count == 7


@patch("satpy.Scene", autospec=True)
@patch("fcitools.processing.show_testdata.parse_cmdline", autospec=True)
@patch("tempfile.TemporaryDirectory", autospec=True)
def test_main(tT, fpsp, sS, tfs, tmp_path):
    import fcitools.processing.show_testdata
    fpsp.return_value = fcitools.processing.show_testdata.\
        get_parser().parse_args([
                str(tfs[1]),
                str(tmp_path),
                "--composites", "overview", "natural_color", "fog",
                "--channels", "vis_04", "nir_13", "ir_38", "wv_87",
                "-a", "socotra", "bornholm"])
    tT.return_value.name = str(tmp_path / "raspberry")
    fcitools.processing.show_testdata.main()
    sS.assert_called_once_with(
        sensor="fci",
        filenames=[str(tmp_path / "raspberry" / "file1.dat"),
                   str(tmp_path / "raspberry" / "file2.dat")],
        reader=["fci_l1c_fdhsi"])

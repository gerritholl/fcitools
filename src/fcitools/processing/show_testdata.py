"""Display images based on FCI testdata from .tar.gz archives

From FCI testdata displayed in .tar.gz archives, display selected
channels and composites for selected areas.
"""

import pathlib
import argparse
from .. import vis


def get_parser():
    parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
            "path", action="store", type=pathlib.Path,
            help="Path to .tar.gz containing testdata")

    parser.add_argument(
            "outdir", action="store", type=pathlib.Path,
            help="Directory where to write resulting images.")

    parser.add_argument(
            "--composites", action="store", type=str,
            nargs="*",
            default=[],
            help="Composites to generate")

    parser.add_argument(
            "--channels", action="store", type=str,
            nargs="*",
            default=[],
            help="Channels to generate.  Should be FCI channel labels.")

    parser.add_argument(
            "-a", "--areas", action="store", type=str,
            nargs="+",
            help="Areas for which to generate those.")

    parser.add_argument(
            "--filename-pattern", action="store", type=str,
            default="{label:s}_{area:s}_{dataset:s}.tiff",
            help="Filename pattern for output files.")

    parser.add_argument(
            "--coastline-dir", action="store", type=str,
            help="Path to directory with coastlines.")

    parser.add_argument(
            "--show-only-coastlines", action="store_true",
            help="Prepare three blank images showing only coastlines.  "
                 "Backgrounds will be white, black, and transparent.")

    return parser


def parse_cmdline():
    return get_parser().parse_args()


def main():
    from satpy.utils import debug_on
    debug_on()
    p = parse_cmdline()
    fn = vis.unpack_and_show_testdata(
            p.path,
            p.composites,
            p.channels,
            p.areas,
            p.outdir,
            p.filename_pattern,
            p.coastline_dir,
            p.show_only_coastlines)
    print("Files written:", fn)

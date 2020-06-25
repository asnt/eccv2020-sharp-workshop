import argparse
import pathlib
import sys

from . import data


def _do_convert(args):
    mesh = data.load_mesh(args.input)
    data.save_mesh(args.output, mesh)


def _parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_convert = subparsers.add_parser("convert",
                                           help="convert between mesh formats")
    parser_convert.add_argument("input", type=pathlib.Path)
    parser_convert.add_argument("output", type=pathlib.Path)
    parser_convert.set_defaults(func=_do_convert)

    args = parser.parse_args()

    # Ensure help message is displayed when not command is provided.
    if "func" not in args:
        parser.print_help()
        sys.exit(1)

    return args


def main():
    args = _parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

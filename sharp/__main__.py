import argparse
import pathlib
import sys

from . import data
from . import utils


def _do_convert(args):
    mesh = data.load_mesh(args.input)
    data.save_mesh(args.output, mesh)


def _do_shoot(args):
    mesh = data.load_mesh(str(args.input))
    n_holes = (args.holes if args.holes is not None
               else (args.min_holes, args.max_holes))
    dropout = (args.dropout if args.dropout is not None
               else (args.min_dropout, args.max_dropout))
    point_indices = utils.shoot_holes(mesh.vertices, n_holes, dropout)
    shot = utils.remove_points(mesh, point_indices)
    shot.save(str(args.output))


def _parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_convert = subparsers.add_parser("convert",
                                           help="convert between mesh formats")
    parser_convert.add_argument("input", type=pathlib.Path)
    parser_convert.add_argument("output", type=pathlib.Path)
    parser_convert.set_defaults(func=_do_convert)

    parser_shoot = subparsers.add_parser(
        "shoot", help="generate partial data with the shooting method")
    parser_shoot.add_argument("input", type=pathlib.Path)
    parser_shoot.add_argument("output", type=pathlib.Path)
    parser_shoot.add_argument(
        "--holes", type=int, default=None,
        help="If not None, fixed number of holes to shoot, otherwise a random"
             " number between min_holes and max_holes is used.",
    )
    parser_shoot.add_argument(
        "--min-holes", type=int, default=3,
        help="Minimum number of holes to generate (default: 3).",
    )
    parser_shoot.add_argument(
        "--max-holes", type=int, default=10,
        help="Maximum number of holes to generate (default: 10).",
    )
    parser_shoot.add_argument(
        "--dropout", type=float, default=None,
        help="If not None, fixed proportion of points to remove in a single"
             " hole, otherwise a random proportion between min_dropout and"
             " max_dropout is used.",
    )
    parser_shoot.add_argument(
        "--min-dropout", type=float, default=0.01,
        help="minimum proportion of points to remove in a single hole"
             " (default: 0.01)",
    )
    parser_shoot.add_argument(
        "--max-dropout", type=float, default=0.05,
        help="maximum proportion of points to remove in a single hole"
             " (default: 0.05)",
    )
    parser_shoot.set_defaults(func=_do_shoot)

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

import argparse
from pathlib import Path

import numpy as np

import data
import utils


def cut(inpath, outpath):
    mesh = data.load_mesh(str(inpath))
    ldmpath = inpath.parent / 'landmarks3d.txt'
    if not ldmpath.exists():
        raise RuntimeError(f'landmarks not found {ldmpath}')
    ldmdict = data.read_3d_landmarks(str(ldmpath))
    pts = list(ldmdict.values())

    plausible_ldms = range(26)
    #get random subset of 3 landmarks
    #A, B, C = ldmdict['shoulder_right'],  ldmdict['shoulder_left'], ldmdict['hip_middle']
    indices = np.random.choice(plausible_ldms, 3, replace=False)
    A, B, C = pts[indices[0]], pts[indices[1]], pts[indices[2]]

    #estimate cutting plane parameters
    c, n = utils.estimate_plane(A, B, C)

    #get two slices
    slice1_indices, slice2_indices = utils.slice_by_plane(mesh, c, n)
    slice1 = utils.remove_points(mesh, slice1_indices)
    slice2 = utils.remove_points(mesh, slice2_indices)

    outpath1 = str(outpath) + '_slice1.obj'
    outpath2 = str(outpath) + '_slice2.obj'

    slice1.save(outpath1)
    slice2.save(outpath2)


def shoot(inpath, outpath, num_holes_range=(3, 10), dropout_range=(0.01, 0.05)):
    mesh = data.load_mesh(str(inpath))
    rm_indices = utils.shoot_holes(mesh.vertices, num_holes_range, dropout_range)
    shot = utils.remove_points(mesh, rm_indices)
    shot.save(str(outpath))


def get_args():
    arg_parser = argparse.ArgumentParser(description='Prepare the data')
    arg_parser.add_argument("method", choices=['cut', 'shoot'],
                            help="method to generate the partial data")
    arg_parser.add_argument("--inpath", type=Path, required=True)
    arg_parser.add_argument("--outpath", type=Path, required=True)
    return arg_parser.parse_args()


def main():
    args = get_args()
    inpath = args.inpath
    outpath = args.outpath
    method = args.method
    if method == 'cut':
        cut(inpath, outpath)
    elif method == 'shoot':
        shoot(inpath, outpath)


if __name__ == "__main__":
    main()

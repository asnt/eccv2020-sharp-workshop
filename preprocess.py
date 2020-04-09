import argparse
from utils import read_3d_landmarks, estimate_plane, Obj, shoot_holes, shoot_holes
from pathlib import Path
import numpy as np

def cut(inpath, outpath):
    mesh = Obj(str(inpath))
    ldmpath = inpath.parent / 'landmarks3d.txt'
    if ldmpath.exists():
        ldmdict = read_3d_landmarks(str(ldmpath))
        #print(ldmdict.keys(), ldmdict.values()) 
        pts = list(ldmdict.values())

        plausible_ldms = range(26)
        #get random subset of 3 landmarks
        #A, B, C = ldmdict['shoulder_right'],  ldmdict['shoulder_left'], ldmdict['hip_middle']
        indices = np.random.choice(plausible_ldms, 3, replace=False)
        A, B, C = pts[indices[0]], pts[indices[1]], pts[indices[2]]

        #estimate cutting plane parameters
        c, n = estimate_plane(A, B, C)

        #get two slices
        slice1_indices, slice2_indices = mesh.slice_by_plane(c, n)
        slice1 = mesh.remove_points(slice1_indices)
        slice2 = mesh.remove_points(slice2_indices)

        outpath1 = str(outpath) + '_slice1.obj'
        outpath2 = str(outpath) + '_slice2.obj'

        slice1.write(outpath1)
        slice2.write(outpath2)
    else:
        raise RuntimeError('no landmarks provided')

def shoot(inpath, outpath, num_holes_range=(3, 10), dropout_range=(0.01, 0.05)):
    mesh = Obj(str(inpath))
    rm_indices = shoot_holes(mesh.vertices, num_holes_range, dropout_range)
    shot = mesh.remove_points(rm_indices)
    shot.write(str(outpath))

def get_args():
    arg_parser = argparse.ArgumentParser(description='Prepare the data')
    arg_parser.add_argument("command", choices=['cut', 'shoot'], help="choose the type os partial data generation")
    arg_parser.add_argument("--inpath", type=Path, required=True)
    arg_parser.add_argument("--outpath", type=Path, required=True)
    return arg_parser.parse_args()

def main():    
    args = get_args()
    inpath = args.inpath
    outpath = args.outpath
    cmd = args.command
    if cmd == 'cut':
        cut(inpath, outpath)
    elif cmd == 'shoot':
        shoot(inpath, outpath)

if __name__ == "__main__":
    main()

import argparse
import copy
from pathlib import Path

import cv2
import numpy as np

import utils
from utils import read_3d_landmarks, estimate_plane, Obj, shoot_holes


def _slice_by_plane(mesh, center, n):
    c = np.dot(center, n)
    plane_side = lambda x: np.dot(x, n) >= c
    split = np.asarray([plane_side(v) for v in mesh.vertices])
    slice1_indices = np.argwhere(split == True)
    slice2_indices = np.argwhere(split == False)
    return slice1_indices, slice2_indices


def _remove_points(mesh, indices, blackoutTexture=True):
    cpy = copy.copy(mesh)
    cpy.vertices = np.delete(mesh.vertices, indices, axis=0)
    if mesh.vertex_colors is not None:
        cpy.vertex_colors = np.delete(mesh.vertex_colors, indices, axis=0)
    if mesh.vertex_normals is not None:
        cpy.vertex_normals = np.delete(
            mesh.vertex_normals, indices, axis=0)

    if mesh.faces is not None:
        face_indices = np.where(
            np.any(np.isin(mesh.faces[:], indices, assume_unique=False),
                   axis=1)
        )[0]
        cpy.faces = np.delete(mesh.faces, face_indices, axis=0)
        fix_indices = np.vectorize(
            lambda x: np.sum(x >= indices))(cpy.faces)
        cpy.faces -= fix_indices

        if mesh.face_normals is not None:
            cpy.face_normals = np.delete(
                mesh.face_normals, face_indices, axis=0)
        unused_uv = None
        if mesh.texture_indices is not None:
            cpy.texture_indices = np.delete(
                mesh.texture_indices, face_indices, axis=0)
            used_uv = np.unique(cpy.texture_indices.flatten())
            all_uv = np.arange(len(mesh.texcoords))
            unused_uv = np.setdiff1d(all_uv, used_uv, assume_unique=True)
            fix_uv_idx = np.vectorize(
                lambda x: np.sum(x >= unused_uv))(cpy.texture_indices)
            cpy.texture_indices -= fix_uv_idx
            cpy.texcoords = np.delete(mesh.texcoords, unused_uv, axis=0)

            #render texture
            if blackoutTexture:
                tri_indices = cpy.texture_indices
                tex_coords = cpy.texcoords
                mesh.read_texture()
                img = utils.render_texture(mesh.texture_image, tex_coords, tri_indices)
                #dilate the result to remove sewing
                kernel = np.ones((3, 3), np.uint8)
                cpy.texture_image = cv2.dilate(img, kernel, iterations=1)

        if mesh.faces_normal_indices is not None:
            cpy.faces_normal_indices = np.delete(
                mesh.faces_normal_indices, face_indices, axis=0)
            used_ni = np.unique(cpy.faces_normal_indices.flatten())
            all_ni = np.arange(len(mesh.face_normals))
            unused_ni = np.setdiff1d(all_ni, used_ni, assume_unique=True)
            fix_ni_idx = np.vectorize(lambda x: np.sum(
                x > unused_ni))(cpy.faces_normal_indices)
            cpy.faces_normal_indices -= fix_ni_idx
            cpy.face_normals = np.delete(
                mesh.face_normals, unused_ni, axis=0)

    return cpy


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
        slice1_indices, slice2_indices = _slice_by_plane(mesh, c, n)
        slice1 = _remove_points(mesh, slice1_indices)
        slice2 = _remove_points(mesh, slice2_indices)

        outpath1 = str(outpath) + '_slice1.obj'
        outpath2 = str(outpath) + '_slice2.obj'

        slice1.write(outpath1)
        slice2.write(outpath2)
    else:
        raise RuntimeError('no landmarks provided')


def shoot(inpath, outpath, num_holes_range=(3, 10), dropout_range=(0.01, 0.05)):
    mesh = Obj(str(inpath))
    rm_indices = shoot_holes(mesh.vertices, num_holes_range, dropout_range)
    shot = _remove_points(mesh, rm_indices)
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

import copy
import numbers

import cv2
import numpy as np
from scipy.spatial import cKDTree

from .trirender import UVTrianglesRenderer


def slice_by_plane(mesh, center, n):
    c = np.dot(center, n)
    plane_side = lambda x: np.dot(x, n) >= c
    split = np.asarray([plane_side(v) for v in mesh.vertices])
    slice1_indices = np.argwhere(split == True)
    slice2_indices = np.argwhere(split == False)
    return slice1_indices, slice2_indices


def remove_points(mesh, indices, blackoutTexture=True):
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

            # render texture
            if blackoutTexture:
                tri_indices = cpy.texture_indices
                tex_coords = cpy.texcoords
                img = render_texture(mesh.texture, tex_coords, tri_indices)
                # dilate the result to remove sewing
                kernel = np.ones((3, 3), np.uint8)
                cpy.texture = cv2.dilate(img, kernel, iterations=1)

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


def render_texture(texture, tex_coords, tri_indices):
    if len(texture.shape) == 3 and texture.shape[2] == 4:
        texture = texture[:, :, 0:3]
    elif len(texture.shape) == 2:
        texture = np.concatenate([texture, texture, texture], axis=2)

    renderer = UVTrianglesRenderer.with_standalone_ctx(
        (texture.shape[1], texture.shape[0])
    )

    return renderer.render(tex_coords, tri_indices, texture, True)


def estimate_plane(A, B, C):
    c = (A + B + C) / 3
    n = np.cross(B - A, C - A)
    assert(np.isclose(np.dot(B-A, n), np.dot(C-A, n)))
    return c, n


def shoot_holes(vertices, n_holes=(3, 10), dropout=(1e-2, 5e-2)):
    """Generate a partial shape by cutting holes of random location and size.

    Args:
        vertices: The vertices of the mesh.
        n_holes: int or (low, high), number of holes to shot, or bounds from
            which to randomly draw the number of holes.
        dropout: int or (low, high), proportion of points to remove in a single
            hole, or bounds from which to randomly draw the proportion.

    Returns:
        Array of indices of the points to remove.
    """
    n = vertices.shape[0]
    kdtree = cKDTree(vertices, leafsize=200)

    if not isinstance(n_holes, numbers.Integral):
        n_holes = np.random.randint(*n_holes)

    # Select random hole centers.
    center_indices = np.random.choice(len(vertices), size=n_holes)
    centers = vertices[center_indices]

    if isinstance(dropout, numbers.Number):
        hole_size = n * dropout
        hole_sizes = [hole_size] * n_holes
    else:
        hole_size_bounds = n * np.asarray(dropout)
        hole_sizes = np.random.randint(*hole_size_bounds, size=n_holes)

    # Crop holes of random size around the centers.
    to_crop = []
    for center, size in zip(centers, hole_sizes):
        _, indices = kdtree.query(center, k=size)
        to_crop.append(indices)
    to_crop = np.unique(np.concatenate(to_crop))

    return to_crop

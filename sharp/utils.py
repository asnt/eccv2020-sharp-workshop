import copy
import numbers

import cv2
import numpy as np
try:
    from scipy.spatial import cKDTree as KDTree
except ImportError:
    from scipy.spatial import KDTree

from . import data
from .trirender import UVTrianglesRenderer


def slice_by_plane(mesh, center, n):
    c = np.dot(center, n)
    plane_side = lambda x: np.dot(x, n) >= c
    split = np.asarray([plane_side(v) for v in mesh.vertices])
    slice1_indices = np.argwhere(split == True)
    slice2_indices = np.argwhere(split == False)
    return slice1_indices, slice2_indices


def remove_points(mesh, indices, blackoutTexture=True):
    submesh = data.Mesh()

    roi_vertices = np.ones(len(mesh.vertices), dtype=bool)
    roi_vertices[indices] = False
    submesh.vertices = mesh.vertices[roi_vertices]
    if mesh.vertex_colors is not None:
        submesh.vertex_colors = mesh.vertex_colors[roi_vertices]
    if mesh.vertex_normals is not None:
        submesh.vertex_normals = mesh.vertex_normals[roi_vertices]

    if mesh.faces is not None:
        removed_faces = np.any(np.isin(mesh.faces, indices), axis=1)
        roi_faces = ~removed_faces
        faces_subset = mesh.faces[roi_faces]

        idx_map = -np.ones(len(mesh.vertices), dtype=int)
        idx_map[roi_vertices] = np.arange(sum(roi_vertices))
        faces_subset = idx_map[faces_subset]
        submesh.faces = faces_subset

        if mesh.texture_indices is not None:
            texture_faces_subset = mesh.texture_indices[roi_faces]

            roi_texcoords = np.zeros(len(mesh.texcoords), dtype=bool)
            kept_texcoords_indices = np.unique(texture_faces_subset)
            roi_texcoords[kept_texcoords_indices] = True

            idx_map = -np.ones(len(mesh.texcoords), dtype=int)
            idx_map[roi_texcoords] = np.arange(sum(roi_texcoords))
            texture_faces_subset = idx_map[texture_faces_subset]

            submesh.texture_indices = texture_faces_subset
            submesh.texcoords = mesh.texcoords[roi_texcoords]

            if blackoutTexture:
                tri_indices = submesh.texture_indices
                tex_coords = submesh.texcoords
                img = render_texture(mesh.texture, tex_coords, tri_indices)
                # dilate the result to remove sewing
                kernel = np.ones((3, 3), np.uint8)
                texture_f32 = cv2.dilate(img, kernel, iterations=1)
                submesh.texture = texture_f32.astype(np.float64)

        if (mesh.faces_normal_indices is not None
                and mesh.face_normals is not None):
            normals_faces_subset = mesh.faces_normal_indices[roi_faces]

            roi_normals = np.zeros(len(mesh.face_normals), dtype=bool)
            kept_normals_indices = np.unique(normals_faces_subset)
            roi_normals[kept_normals_indices] = True

            idx_map = -np.ones(len(mesh.face_normals), dtype=int)
            idx_map[roi_normals] = np.arange(sum(roi_normals))
            normals_faces_subset = idx_map[normals_faces_subset]

            submesh.faces_normal_indices = normals_faces_subset
            submesh.face_normals = mesh.face_normals[roi_normals]

    return submesh


def render_texture(texture, tex_coords, tri_indices):
    if len(texture.shape) == 3 and texture.shape[2] == 4:
        texture = texture[:, :, 0:3]
    elif len(texture.shape) == 2:
        texture = np.concatenate([texture, texture, texture], axis=2)

    renderer = UVTrianglesRenderer.with_standalone_ctx(
        (texture.shape[1], texture.shape[0])
    )

    return renderer.render(tex_coords, tri_indices, texture, True)


def estimate_plane(a, b, c):
    """Estimate the parameters of the plane passing by three points.

    Returns:
        center(float): The center point of the three input points.
        normal(float): The normal to the plane.
    """
    center = (a + b + c) / 3
    normal = np.cross(b - a, c - a)
    assert(np.isclose(np.dot(b - a, normal), np.dot(c - a, normal)))
    return center, normal


def shoot_holes(vertices, n_holes, dropout, mask_faces=None, faces=None,
                rng=None):
    """Generate a partial shape by cutting holes of random location and size.

    Each hole is created by selecting a random point as the center and removing
    the k nearest-neighboring points around it.

    Args:
        vertices: The array of vertices of the mesh.
        n_holes (int or (int, int)): Number of holes to create, or bounds from
            which to randomly draw the number of holes.
        dropout (float or (float, float)): Proportion of points (with respect
            to the total number of points) in each hole, or bounds from which
            to randomly draw the proportions (a different proportion is drawn
            for each hole).
        mask_faces: A boolean mask on the faces. 1 to keep, 0 to ignore. If
                    set, the centers of the holes are sampled only on the
                    non-masked regions.
        faces: The array of faces of the mesh. Required only when `mask_faces`
               is set.
        rng: (optional) An initialised np.random.Generator object. If None, a
             default Generator is created.

    Returns:
        array: Indices of the points defining the holes.
    """
    if rng is None:
        rng = np.random.default_rng()

    if not isinstance(n_holes, numbers.Integral):
        n_holes_min, n_holes_max = n_holes
        n_holes = rng.integers(n_holes_min, n_holes_max)

    if mask_faces is not None:
        valid_vertex_indices = np.unique(faces[mask_faces > 0])
        valid_vertices = vertices[valid_vertex_indices]
    else:
        valid_vertices = vertices

    # Select random hole centers.
    center_indices = rng.choice(len(valid_vertices), size=n_holes)
    centers = valid_vertices[center_indices]

    n_vertices = len(valid_vertices)
    if isinstance(dropout, numbers.Number):
        hole_size = n_vertices * dropout
        hole_sizes = [hole_size] * n_holes
    else:
        hole_size_bounds = n_vertices * np.asarray(dropout)
        hole_sizes = rng.integers(*hole_size_bounds, size=n_holes)

    # Identify the points indices making up the holes.
    kdtree = KDTree(vertices, leafsize=200)
    to_crop = []
    for center, size in zip(centers, hole_sizes):
        _, indices = kdtree.query(center, k=size)
        to_crop.append(indices)
    to_crop = np.unique(np.concatenate(to_crop))

    return to_crop

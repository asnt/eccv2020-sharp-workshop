import copy

import cv2
import numpy as np
from scipy.spatial import cKDTree

from .trirender import UVTrianglesRenderer


LDMS = ['nose', 'neck', 'shoulder_right', 'elbow_right', 'wrist_right', 'shoulder_left', 'elbow_left', 'wrist_left', 'hip_middle', 'hip_right', 'knee_right', 'ankle_right', 'hip_left', 'knee_left', 'ankle_left', 'eye_right', 'eye_left', 'ear_right', 'ear_left', 'toe_1_left', 'toe_5_left', 'heel_left', 'toe_1_right', 'toe_5_right', 'heel_right', 'hand_base_left', 'finger_thumb_base_left', 'finger_thumb_middle_left', 'finger_thumb_top_left', 'finger_thumb_tip_left', 'finger_index_base_left', 'finger_index_middle_left', 'finger_index_top_left', 'finger_index_tip_left', 'finger_middle_base_left', 'finger_middle_middle_left', 'finger_middle_top_left', 'finger_middle_tip_left', 'finger_ring_base_left', 'finger_ring_middle_left', 'finger_ring_top_left', 'finger_ring_tip_left', 'finger_baby_base_left', 'finger_baby_middle_left', 'finger_baby_top_left', 'finger_baby_tip_left', 'hand_base_right', 'finger_thumb_base_right', 'finger_thumb_middle_right', 'finger_thumb_top_right', 'finger_thumb_tip_right', 'finger_index_base_right', 'finger_index_middle_right', 'finger_index_top_right', 'finger_index_tip_right', 'finger_middle_base_right', 'finger_middle_middle_right', 'finger_middle_top_right', 'finger_middle_tip_right', 'finger_ring_base_right', 'finger_ring_middle_right', 'finger_ring_top_right', 'finger_ring_tip_right', 'finger_baby_base_right', 'finger_baby_middle_right', 'finger_baby_top_right', 'finger_baby_tip_right', 'finger_mean_base_knuckle_left', 'finger_mean_base_knuckle_right']




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


def shoot_holes(vertices, num_holes_range=(3, 10), dropout_range=(0.01, 0.05), random_state=None):
    n = vertices.shape[0]
    kdtree = cKDTree(vertices, leafsize=200)
    sampler = random_state and random_state.choice or np.random.choice

    #select point centers for holes
    point_indices = sampler(len(vertices), size=np.random.randint(num_holes_range[0], num_holes_range[1]))
    points = vertices[point_indices]
    points_to_remove = set()

    for p in points:
        #randomize number of points in each center neighborhood to remove
        n_rm_pts = int(np.random.randint(np.dot(dropout_range, n), size=1))
        points_to_remove.update(np.unique(kdtree.query(p, k=n_rm_pts)[1].flatten()))

    return np.asarray(list(points_to_remove))

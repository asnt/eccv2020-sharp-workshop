import csv
import numpy as np
import re
import os
import copy
import cv2
import shutil 
from scipy.spatial import cKDTree

from trirender import UVTrianglesRenderer


PAT = re.compile('(\d+)/?(\d*)?/?(\d*)?')

LDMS = ['nose', 'neck', 'shoulder_right', 'elbow_right', 'wrist_right', 'shoulder_left', 'elbow_left', 'wrist_left', 'hip_middle', 'hip_right', 'knee_right', 'ankle_right', 'hip_left', 'knee_left', 'ankle_left', 'eye_right', 'eye_left', 'ear_right', 'ear_left', 'toe_1_left', 'toe_5_left', 'heel_left', 'toe_1_right', 'toe_5_right', 'heel_right', 'hand_base_left', 'finger_thumb_base_left', 'finger_thumb_middle_left', 'finger_thumb_top_left', 'finger_thumb_tip_left', 'finger_index_base_left', 'finger_index_middle_left', 'finger_index_top_left', 'finger_index_tip_left', 'finger_middle_base_left', 'finger_middle_middle_left', 'finger_middle_top_left', 'finger_middle_tip_left', 'finger_ring_base_left', 'finger_ring_middle_left', 'finger_ring_top_left', 'finger_ring_tip_left', 'finger_baby_base_left', 'finger_baby_middle_left', 'finger_baby_top_left', 'finger_baby_tip_left', 'hand_base_right', 'finger_thumb_base_right', 'finger_thumb_middle_right', 'finger_thumb_top_right', 'finger_thumb_tip_right', 'finger_index_base_right', 'finger_index_middle_right', 'finger_index_top_right', 'finger_index_tip_right', 'finger_middle_base_right', 'finger_middle_middle_right', 'finger_middle_top_right', 'finger_middle_tip_right', 'finger_ring_base_right', 'finger_ring_middle_right', 'finger_ring_top_right', 'finger_ring_tip_right', 'finger_baby_base_right', 'finger_baby_middle_right', 'finger_baby_top_right', 'finger_baby_tip_right', 'finger_mean_base_knuckle_left', 'finger_mean_base_knuckle_right']

def read_3d_landmarks(inpath):
    """Read the 3d landmarks locations and names.

    Landmarks are stored in a CSV file with rows of the form:
        landmark_name x y z

    Parameters
    ----------
    inpath : string
        path to the file

    Returns
    -------
    landmarks: dict
        A dictionary of (landmark_name, 3d_location) pairs.
    """
    landmarks = {}
    with open(inpath) as f:
        reader = csv.reader(f, delimiter=' ')
        for row in reader:
            name = row[0]
            location = np.array([float(v) for v in row[1:4]])
            landmarks[name] = location
    return landmarks


def imread(path):
    img = cv2.imread(str(path), -1)
    return img.astype(float) / np.iinfo(img.dtype).max

def imwrite(path, img, dtype=np.uint16):
    img = (img * np.iinfo(dtype).max).astype(dtype)
    cv2.imwrite(str(path), img)


class Obj:
    """A custom implementation of .obj 3d file format with full support 
        of texture on save/load and rerendering texture on remove points
    """
    def __init__(self, filepath=None):
        self.vertices = None  # array with vertices (N, 3)
        # array with vertex colors if they exist (N, 3)
        self.vertex_colors = None
        self.vertex_normals = None  # array with vertex normals (N, 3)
        self.faces = None  # array with faces indices (M, 3 or 4)
        self.face_normals = None  # array with faces normals (M, 3)
        # array with indices of normals for each vertex in face
        self.faces_normal_indices = None
        self.texture_indices = None  # array with texture indices
        self.texcoords = None  # array of texture coordinates
        self.mtl = None  # name of the corresponding mtl file
        self.material = None
        self.texture = None  # texture image name
        self.filepath = filepath
        self.texture_image = None #texture image data

        if filepath:
            self.read(filepath)
    
    def read_mtl(self):
        mtlpath = os.path.join(os.path.dirname(self.filepath), self.mtl)
        if os.path.exists(mtlpath):
            with open(mtlpath) as f:
                for line in f:
                    ws = line.strip().split()
                    if ws:
                        if ws[0] == 'map_Kd':
                            self.texture = ' '.join(ws[1:])
                            return self.texture
        return None

    def read(self, filepath):
        self.__init__()  # (filepath=None)
        self.filepath = filepath
        vertices = []
        normals = []
        faces = []
        with open(filepath) as f:
            for line in f:
                if line.startswith('#'):
                    continue
                prefix = line[:2]

                ws = line.strip().split()
                if 'v ' == prefix:
                    vertices.append([float(x) for x in ws[1:]])
                elif 'vn' == prefix:
                    normals.append([float(x) for x in ws[1:]])
                elif 'f ' == prefix:
                    faces.append(ws[1:])
                elif 'vt' == prefix:
                    if self.texcoords is None:
                        self.texcoords = []
                    self.texcoords.append([float(ws[1]), float(ws[2])])
                if ws:
                    if ws[0] in ('usemtl', 'usemat'):
                        self.material = ws[1]
                    elif ws[0] == 'mtllib':
                        if len(ws) > 1:
                            self.mtl = ws[1]
                            self.read_mtl()

        vs = np.array(vertices)
        self.vertices = vs[:, :3]
        if vs.shape[1] == 6:
            self.vertex_colors = vs[:, 3:]

        self.faces, self.texture_indices, self.faces_normal_indices = self._parse_faces(
            faces)

        if len(normals):
            normals = np.array(normals)

            # Heuristics that decides what normals we have read
            if normals.shape[0] == self.vertices.shape[0]:
                self.vertex_normals = normals
            elif normals.shape[0] == self.faces.shape[0]:
                self.face_normals = normals

    def set_data(self, vertices, faces):
        self.__init__(filepath=None)
        if type(vertices) is list:
            vertices = np.array(vertices).reshape((-1, 3))
        if type(faces) is list:
            faces = np.array(faces).reshape((-1, 3))

        assert isinstance(vertices, np.ndarray)
        self.vertices = vertices
        assert isinstance(faces, np.ndarray)
        self.faces = faces

    def write(self, outpath, save_texture = True, verts_to_high_light=None):
        out_dir = os.path.dirname(outpath)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(os.path.dirname(outpath))
        with open(outpath, 'w') as f:
            if save_texture:
                basepath = os.path.splitext(outpath)[0]
                mtlpath = basepath + '.mtl'
                mtlname = os.path.basename(mtlpath)
                texpath = basepath + '.png'
                texname = os.path.basename(texpath)
                strr = 'mtllib ' + mtlname + '\n'
                f.write(strr)

                # strr = 'usemtl material_1 \n'
                # f.write(strr)

                # create mtl file
                mtlstr = '# File exported by Artec 3D Scanning Solutions\n\
                # www.artec3d.com\n\
                newmtl material_0\n\
                Ka 1 1 1\n\
                Kd 1 1 1\n\
                Ks 1 1 1\n\
                Ns 1000\n\
                map_Kd %s\n\
                newmtl material_1\n\n\
                Ka 1 1 1\n\
                Kd 1 1 1\n\
                Ks 1 1 1\n\
                Ns 1000\n\
                        ' % texname
                with open(mtlpath, 'w') as m:
                    m.write(mtlstr)
                    m.close()
                
                self.write_texture(texpath)

            for i, vertex in enumerate(self.vertices):
                p1, p2, p3 = vertex
                if verts_to_high_light is not None:
                    if i in verts_to_high_light:
                        f.write(
                            u'v {0:f} {1:f} {2:f} 1 0 0\n'.format(p1, p2, p3))
                    else:
                        f.write(
                            u'v {0:f} {1:f} {2:f} 1 1 1\n'.format(p1, p2, p3))
                else:
                    if self.vertex_colors is not None:
                        c1, c2, c3 = self.vertex_colors[i, :]
                        f.write(u'v {0:f} {1:f} {2:f} {3:f} {4:f} {5:f}\n'.format(p1, p2, p3, c1, c2, c3))
                    else:
                        f.write(u'v {0:f} {1:f} {2:f}\n'.format(p1, p2, p3))

                if self.vertex_normals is not None:
                    n1, n2, n3 = self.vertex_normals[i, :]
                    f.write(u'vn {0:f} {1:f} {2:f}\n'.format(n1, n2, n3))
            if self.texcoords is not None:
                for tc in self.texcoords:
                    t1, t2 = tc
                    f.write(u'vt {0:f} {1:f}\n'.format(t1, t2))

            for idx, face in enumerate(self.faces):
                el = ['' for x in range(len(face))]
                fs = face + 1

                ts = self.texture_indices[idx] + 1 if self.texture_indices is not None else el
                ns = self.faces_normal_indices[idx] + 1 if self.faces_normal_indices is not None else el
                f.write(u'f ')
                if self.texture_indices is None and self.faces_normal_indices is None:
                    [f.write(' {} '.format(f1)) for f1 in fs]
                elif self.faces_normal_indices is None:
                    [f.write(' {}/{} '.format(f1, t1))
                     for f1, t1 in zip(fs, ts)]
                else:
                    [f.write(' {}/{}/{} '.format(f1, t1, n1))
                     for f1, t1, n1 in zip(fs, ts, ns)]
                f.write(u'\n')

            f.close()

    @staticmethod
    def _parse_faces(faces):
        p_faces = []
        p_faces_normals = []
        p_face_textures = []
        for face in faces:
            fv, ft, fn = [], [], []
            arrs = (fv, ft, fn)
            for element in face:
                o = PAT.match(element)
                if o:
                    for i, g in enumerate(o.groups()):
                        if len(g):
                            arrs[i].append(int(g))
            if len(fv):
                p_faces.append(fv)
                if len(ft):
                    p_face_textures.append(ft)
                    hasReatTex = True
                else:
                    el = ['' for x in range(len(fv))]
                    p_face_textures.append(el)
                if len(fn):
                    p_faces_normals.append(fn)
                    hasRealNorms = True
                # else:
                #     el = ['' for x in range(len(fv))]
                #     p_faces_normals.append(el)

        if len(p_faces):
            # they start from 1 in OBJ file
            p_faces = np.array([np.array(p) - 1 for p in p_faces])
        if len(p_faces_normals):
            p_faces_normals = np.array([np.array(p) - 1 for p in p_faces_normals])
        else:
            p_faces_normals = None
        if len(p_face_textures):
            p_face_textures = np.array([np.array(p) - 1 for p in p_face_textures])
        else:
            p_face_textures = None

        return p_faces, p_face_textures, p_faces_normals

    def calc_tri_normals(self):
        tri_normals = []
        for tri in self.faces:
            p1, p2, p3 = tri
            v1 = self.vertices[p1] - self.vertices[p2]
            v2 = self.vertices[p1] - self.vertices[p3]
            n = np.cross(v1, v2)
            n /= np.linalg.norm(n)
            tri_normals.append(n)

        self.face_normals = np.asarray(tri_normals)

    def calc_vert_normals(self):
        if 'face_normals' not in dir(self) or self.face_normals is None:
            self.calc_tri_normals()

        nei_faces = {}  # neighbour to point faces
        for i in range(len(self.vertices)):
            nei_faces[i] = []

        for i_tri, tri in enumerate(self.faces):
            for p in tri:
                nei_faces[p].append(i_tri)

        pts_normals = []
        for i in range(len(self.vertices)):
            if len(nei_faces[i]) == 0:
                print(i)
            n = np.zeros(3)
            for f in nei_faces[i]:
                n += self.face_normals[f]

            pts_normals.append(n / np.linalg.norm(n))

        self.vertex_normals = np.array(pts_normals)

    def get_texture_path(self):
        inpath = self.filepath
        if os.path.splitext(inpath)[1] == '.obj':
            tpath = self.read_mtl()
            if tpath:
                tpath = os.path.join(os.path.dirname(inpath), tpath)
                if os.path.exists(tpath):
                    return tpath
        return None

    def read_texture(self):
        if self.texture_image is None:
            tpath = self.get_texture_path() 
            if tpath is not None:
                self.texture_image = imread(tpath)
            self.texture = tpath

    def write_texture(self, outpath):
        if self.texture_image is not None:
            imwrite(outpath, self.texture_image)
        else:
            intexpath = self.get_texture_path()
            if intexpath:
                shutil.copy2(intexpath, outpath)


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

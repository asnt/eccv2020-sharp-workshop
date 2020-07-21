import csv
import pathlib
import re

import cv2
import numpy as np


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
    """Read a color image.

    Return an image in RGB format with float values into [0, 1].
    """
    img = cv2.imread(str(path))
    # Convert to RGB. OpenCV returns BGR.
    img = img[..., ::-1]
    return img.astype(float) / np.iinfo(img.dtype).max


def imwrite(path, img, dtype=np.uint8):
    """Save an RGB image to a file.

    Expect float values into [0, 1].
    """
    img = (img * np.iinfo(dtype).max).astype(dtype)
    # OpenCV expects BGR.
    img = img[..., ::-1]
    cv2.imwrite(str(path), img)


def load_mesh(path):
    if str(path).endswith(".obj"):
        return load_obj(path)
    elif str(path).endswith(".npz"):
        return load_npz(path)
    raise ValueError(f"unknown mesh format {path}")


def save_mesh(path, mesh):
    if str(path).endswith(".obj"):
        return save_obj(path, mesh)
    elif str(path).endswith(".npz"):
        return save_npz(path, mesh)
    raise ValueError(f"unknown mesh format for {path}")


class Mesh:
    def __init__(self, path=None,
                 vertices=None, vertex_normals=None, vertex_colors=None,
                 faces=None, face_normals=None, faces_normal_indices=None,
                 normals=None,
                 texcoords=None, texture_indices=None, texture=None,
                 material=None):
        self.path = path
        self.vertices = vertices
        self.vertex_normals = vertex_normals
        self.vertex_colors = vertex_colors
        self.faces = faces
        self.face_normals = face_normals
        self.faces_normal_indices = faces_normal_indices
        self.normals = normals
        self.texcoords = texcoords
        self.texture_indices = texture_indices
        self.texture = texture
        self.material = material

    @staticmethod
    def load(path):
        return load_mesh(path)

    def save(self, path):
        save_mesh(path, self)


def _read_mtl(mtl_path):
    if not mtl_path.exists():
        return None
    with open(mtl_path) as f:
        for line in f:
            tokens = line.strip().split(maxsplit=1)
            if not tokens:
                continue
            if tokens[0] == 'map_Kd':
                texture_name = tokens[1]
                return texture_name
    return None


def _parse_faces(obj_faces):
    """Parse the OBJ encoding of the face attribute index buffers.

    A value of -1 in the index array of the texture means the index is
    undefined (i.e. no texture is mapped to this face corner).

    Returns:
        faces
        faces_texture
        faces_normals
    """
    face_pattern = re.compile(r'(\d+)/?(\d*)?/?(\d*)?')
    faces = []
    faces_normals = []
    faces_texture = []
    for obj_face in obj_faces:
        fv, ft, fn = [], [], []
        arrs = (fv, ft, fn)
        for element in obj_face:
            match = face_pattern.match(element)
            if match is not None:
                for i, group in enumerate(match.groups()):
                    if len(group) > 0:
                        arrs[i].append(int(group))
        if len(fv) > 0:
            faces.append(fv)
            if len(ft) > 0:
                faces_texture.append(ft)
            else:
                el = [-1 for x in range(len(fv))]
                faces_texture.append(el)
            if len(fn) > 0:
                faces_normals.append(fn)
            # else:
            #     el = ['' for x in range(len(fv))]
            #     faces_normals.append(el)

    faces = np.array(faces, dtype=int)
    faces_texture = np.array(faces_texture, dtype=int)
    faces_normals = np.array(faces_normals, dtype=int)

    # Change to zero-based indexing.
    faces -= 1
    faces_texture -= 1
    faces_normals -= 1

    return faces, faces_texture, faces_normals


def _complete_texcoords(texcoords, texture_indices):
    """Ensure all faces reference some texture coordinates.

    Make untextured faces reference a new dummy texture coordinate.
    The new texture coordinate is placed at `(u, v) = (0, 0)`, assuming no
    texture exists there (i.e. black color).
    """
    no_texcoords = texture_indices < 0
    if np.any(no_texcoords):
        texcoords = np.append(texcoords, [[.0, .0]], axis=0)
        new_index = len(texcoords) - 1
        texture_indices[no_texcoords] = new_index
    return texcoords, texture_indices


def _load_texture(path):
    return imread(path)


def _save_texture(path, texture):
    imwrite(path, texture)


def load_obj(path):
    path = pathlib.Path(path)

    vertices = []
    vertex_colors = []
    normals = []
    faces = []
    texcoords = []
    material_name = None
    mtl_filename = None
    texture_filename = None
    texture = None
    with open(path) as f:
        for line in f:
            line = line.strip()

            if not line:
                # blank line
                continue
            if line.startswith('#'):
                # comment
                continue

            tokens = line.split()
            if tokens[0] == 'v':
                vertices.append([float(x) for x in tokens[1:]])
            elif tokens[0] == 'vn':
                normals.append([float(x) for x in tokens[1:]])
            elif tokens[0] == 'f':
                faces.append(tokens[1:])
            elif tokens[0] == 'vt':
                texcoords.append([float(tokens[1]), float(tokens[2])])
            elif tokens[0] in ('usemtl', 'usemat'):
                material_name = tokens[1]
            elif tokens[0] == 'mtllib':
                if len(tokens) > 1:
                    mtl_filename = tokens[1]
                    mtl_path = path.parent / mtl_filename
                    texture_filename = _read_mtl(mtl_path)

        vertices = np.array(vertices)
        if vertices.shape[1] == 6:
            vertex_colors = vertices[:, 3:]
        vertices = vertices[:, :3]

        faces, texture_indices, faces_normal_indices = _parse_faces(faces)

        if texcoords:
            texcoords = np.asarray(texcoords, dtype=float)
            texture_indices = np.asarray(texture_indices, dtype=int)
            texcoords, texture_indices = _complete_texcoords(texcoords,
                                                             texture_indices)
        else:
            texture_indices = []

        if normals:
            normals = np.array(normals)

        if texture_filename is not None:
            texture_path = path.parent / texture_filename
            if texture_path.exists():
                texture = _load_texture(texture_path)

        return Mesh(
            path=path,
            vertices=vertices,
            vertex_colors=vertex_colors if len(vertex_colors) > 0 else None,
            faces=faces,
            faces_normal_indices=(faces_normal_indices
                                  if len(faces_normal_indices) > 0
                                  else None),
            normals=normals if len(normals) > 0 else None,
            texcoords=texcoords if len(texcoords) > 0 else None,
            texture=texture,
            texture_indices=(texture_indices
                             if len(texture_indices) > 0
                             else None),
            material=material_name,
        )


def save_obj(path, mesh, save_texture=True, verts_to_high_light=None):
    path = pathlib.Path(path)
    out_dir = pathlib.Path(path).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        if save_texture:
            mtlpath = path.with_suffix(".mtl")
            mtlname = mtlpath.name
            texpath = path.with_suffix(".png")
            texname = texpath.name
            strr = 'mtllib ' + mtlname + '\n'
            f.write(strr)

            f.write('usemtl material_0\n')

            # create mtl file
            mtlstr = '''\
# File exported by Artec 3D Scanning Solutions
# www.artec3d.com
newmtl material_0
Ka 1 1 1
Kd 1 1 1
Ks 1 1 1
Ns 1000
map_Kd %s
newmtl material_1
Ka 1 1 1
Kd 1 1 1
Ks 1 1 1
Ns 1000
''' % texname
            with open(mtlpath, 'w') as m:
                m.write(mtlstr)

            _save_texture(texpath, mesh.texture)

        for i, vertex in enumerate(mesh.vertices):
            p1, p2, p3 = vertex
            if verts_to_high_light is not None:
                if i in verts_to_high_light:
                    f.write(
                        u'v {0:f} {1:f} {2:f} 1 0 0\n'.format(p1, p2, p3))
                else:
                    f.write(
                        u'v {0:f} {1:f} {2:f} 1 1 1\n'.format(p1, p2, p3))
            else:
                if mesh.vertex_colors is not None:
                    c1, c2, c3 = mesh.vertex_colors[i, :]
                    f.write(u'v {0:f} {1:f} {2:f} {3:f} {4:f} {5:f}\n'.format(p1, p2, p3, c1, c2, c3))
                else:
                    f.write(u'v {0:f} {1:f} {2:f}\n'.format(p1, p2, p3))

            if mesh.vertex_normals is not None:
                n1, n2, n3 = mesh.vertex_normals[i, :]
                f.write(u'vn {0:f} {1:f} {2:f}\n'.format(n1, n2, n3))
        if mesh.texcoords is not None:
            for tc in mesh.texcoords:
                t1, t2 = tc
                f.write(u'vt {0:f} {1:f}\n'.format(t1, t2))

        for idx, face in enumerate(mesh.faces):
            el = ['' for x in range(len(face))]
            fs = face + 1

            ts = mesh.texture_indices[idx] + 1 if mesh.texture_indices is not None else el
            ns = mesh.faces_normal_indices[idx] + 1 if mesh.faces_normal_indices is not None else el
            f.write(u'f ')
            if mesh.texture_indices is None and mesh.faces_normal_indices is None:
                [f.write(' {}'.format(f1)) for f1 in fs]
            elif mesh.faces_normal_indices is None:
                [f.write(' {}/{}'.format(f1, t1))
                 for f1, t1 in zip(fs, ts)]
            else:
                [f.write(' {}/{}/{}'.format(f1, t1, n1))
                 for f1, t1, n1 in zip(fs, ts, ns)]
            f.write(u'\n')


def astype_or_none(array, type_):
    if array is None:
        return None
    return array.astype(type_)


def load_npz(path):
    data = np.load(path)

    assert data.f.texture.dtype == np.uint8
    texture = data.f.texture.astype(float) / 255

    return Mesh(
        path=path,
        vertices=data.f.vertices.astype(float),
        faces=data.f.faces.astype(int),
        texcoords=data.f.texcoords.astype(float),
        texture_indices=data.f.texcoords_indices.astype(int),
        texture=texture,
    )


def save_npz(path, mesh):
    np.savez_compressed(
        path,
        vertices=mesh.vertices.astype("float32"),
        faces=mesh.faces.astype("uint32"),
        texcoords=astype_or_none(mesh.texcoords, "float32"),
        texcoords_indices=astype_or_none(mesh.texture_indices, "uint32"),
        texture=((255 * mesh.texture).astype("uint8")
                 if mesh.texture is not None
                 else None),
    )

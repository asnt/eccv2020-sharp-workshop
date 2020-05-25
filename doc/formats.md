# Data format

## Meshes

The body scans are textured 3D meshes stored in a numpy npz archive.

Load and access arrays from an npz file in Python with

```python
  import numpy as np
  mesh = np.load("name.npz", allow_pickle=True)
  mesh["vertices"]
  mesh["faces"]
  # ...
```

The following fields define a mesh:

* `vertices`, float (N, 3):
    The 3D positions of the vertices. Variable number of vertices across the
    meshes.
* `faces`, int (20000, 3):
    The vertex indices defining the faces in 3D space (i.e. triplets of indices
    into the `vertices` array). Fixed number of faces (20000) for all meshes.
* `texcoords`, float (Nt, 2):
    The 2D positions of the vertices in the texture atlas (Nt > N).
* `texcoords_indices`, int (20000, 3):
    The vertex indices defining the faces in the UV space (2D texture image)
    (i.e. triplets of indices into the `texcoords` array). Fixed number of
    faces (20000) for all meshes
* `texture`, uint8 (2048, 2048, 3):
    The RGB texture image.

(Other existing fields are either empty and/or should not be relied upon.)

## Landmarks

The landmarks as stored in space-separated text file with columns

```
  name x y z
```

where `name` is the name of the landmark, and `(x, y, z)` is its 3D position in
the frame of reference the scan or meshes.

For example,

```
  elbow_left 1.234 0.123 0.389
```

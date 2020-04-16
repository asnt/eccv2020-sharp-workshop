# SHARP Challenge 1: Recovery of Human Body Scans

In both tracks, the data is split into train/test/eval sets. The train/test
sets are provided. The eval set is kept secret for the final evaluation.

## Track 1: Recovery of Large Regions

The data is a set of raw scans and 3D body landmarks with the following
directory structure:

```
  train/
    170410-001-m-r9iu-df44-low-res-result/
      170410-001-m-r9iu-df44-low-res-result_normalized.npz
      landmarks3d.txt
```

Each scan has a unique name, e.g. `170410-007-f-1moq-b682-low-res-result`, and
its data files are stored in the corresponding subdirectory.
The data files are:

* `*.npz`: The raw scan as a textured mesh. Stored as a numpy npz archive.
* `landmarks3d.txt`: 3D body landmark positions in text format.

See below for details on the file formats.

## Track 2: Recovery of Fine Details

The dataset has the following directory structure:

```
  train/
    170926-001-fitness-run-sbt1-d8f6-low-res-result/
      fitted_textured.npz
      fusion_textured.npz
      landmarks3d.txt
```

For each sample, the data is under a subdirectory with a unique name,
e.g. `170926-001-fitness-run-sbt1-d8f6-low-res-result/`.
The data files are:

* `fitted_textured.npz`:
  The reference mesh with details. It is obtained by fitting the SMPL-X body
  model to a body scan and transferring the texture.
* `fusion_textured.npz`:
  The simulated body scan. This is a texture mesh obtained from the fitted body
  model mesh by simulating the scanning process in software. It is less
  detailed and contains artefacts similar to a real 3D scan.
* `landmarks3d.txt`:
  The 3D positions of the 3D landmarks. Common to both meshes.

Both meshes are aligned and in the same frame of reference.

See below for details on the file formats.

## 3D body landmarks

The body landmarks are detected automatically on each scan. They are provided
to generate the partial data but can also be used as part of the proposed
method.
They comprise standard body joints and other keypoints on the body (eyes, nose,
ears...). The detection of most landmarks is stable except for the finger
joints which vary in accuracy.

## Data format

### Meshes

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

### Landmarks

The landmarks as stored in space-separated text file with columns

```
  name x y z
```

where `name` is the name of the landmark, and (x, y, z) is its 3D position in
the frame of reference the scan or meshes.

For example,

```
  elbow_left 1.234 0.123 0.389
```

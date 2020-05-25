# Challenge 1 - Track 2: Recovery of Fine Details in Human Scans

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

During the final evaluation:

* the reference mesh `Y` is `fitted_textured.npz`,
* the partial views `X` are generated from `fusion_textured.npz`.

See below for details on the file formats.

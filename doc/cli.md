# Command line interface and tools

Display help on available commands:

```bash
$ python -m sharp
```

Display help on the `convert` command:

```bash
$ python -m sharp convert -h
```

## Convert between mesh formats

Supported formats: `.obj`, `.npz`.

```bash
$ python -m sharp convert input.obj output.npz
$ python -m sharp convert input.npz output.obj
```

## Generate partial data

### Holes shooting

```bash
# Shoot 7 holes with each hole removing 5% of the points of the mesh.
$ python -m sharp shoot input.obj output.obj --holes 7 --dropout 0.05
# Shoot 5 to 20 holes (determined randomly) with each hole removing from 2% to 8% of the points of the mesh.
$ python -m sharp shoot input.npz output.npz --min-holes 5 --max-holes 20 --min-dropout 0.02 --max-dropout 0.08
```

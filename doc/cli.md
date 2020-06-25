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

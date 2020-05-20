# SHARP: SHApe Recovery from Partial textured 3D scans

The goal is to recover a reference scan `Y` from a partial version of it `X`.
The data consists in pairs `(X, Y)` of partial and reference scans.

There are two datasets of textured 3D scans:

1. 3DBodyTex-2: a dataset of 3D human scans (extending
   [3DBodyTex](https://cvi2.uni.lu/datasets/)).
2. 3DObjectTex: a dataset of 3D scans of generic objects.

The scans from the datasets serve as reference data `Y`.

The partial views `X` are not provided directly but must be generated
synthetically.
We provide [some routines](sharp/preprocess.py) that will be used to generate
the data for the final evaluation.
Custom ways to generate partial views may be used for augmenting the training
provided they are reported.

The datasets are split into `train/test/eval` sets.
For the `train/test` sets, the reference scans `Y` are provided.
The participants generate the partial data `X`.
For the `eval` set, the partial data `X` will be shared with the participants
at a later stage of the competition.
The ground-truth data `Y` is kept secret.
It will be released after the competition.

The submissions are evaluated quantitatively by computing the distance from
point-to-surface or surface-to-surface distance from `Y` to `X`.

## Datasets

## Challenges

- [Challenge 1: Recovery of Human Body Scans](doc/challenge1.md)
- [Challenge 2: Recovery of Generic Object Scans](doc/challenge2.md)
- [Generation of partial data](doc/partial_data.md)
- [Evaluation and metrics]()

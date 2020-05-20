# SHARP: SHApe Recovery from Partial textured 3D scans

The goal is to recover a reference scan `Y` from a partial version of it `X`.
The data consists in pairs `(X, Y)` of partial and reference scans.

Only the reference data `Y` is provided.
The partial views `X` are to be generated synthetically with the
[suggested routines](sharp/preprocess.py).
These routines will be used to generate the data for the final evaluation.
Custom ways to generate partial views may be used for augmenting the training
provided they are reported.

- [Challenge 1: Recovery of Human Body Scans](doc/challenge1.md)
- [Challenge 2: Recovery of Generic Object Scans](doc/challenge2.md)
- [Generation of partial data](doc/partial_data.md)
- [Evaluation]()

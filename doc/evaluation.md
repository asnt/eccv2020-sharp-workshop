# Evaluation

## Quantitative

Notation:

- `X`: the partial shape,
- `Y`: the ground truth complete shape,
- `Y'`: the estimated complete shape.

The quality of the estimation, $`Y'`$, is evaluated quantitatively with respect
to the ground truth, `Y`, with a surface-to-surface distance:

```math
d(Y', Y) = \frac{1}{2} (\text{accuracy}_Y(Y') + \text{completeness}_Y(Y'))
```

where accuracy is the directed distance from estimation to reference,

```math
\text{accuracy}_Y(Y') = \sum_{y' \in Y'} d(y', Y),
```

and completeness is the directed distance from reference to estimation,

```math
\text{completeness}_Y(Y') = \sum_{y \in Y} d(y, Y').
```

The directed distance $`d(A, B)`$ between meshes $`A`$ and $`B`$ is
approximated in practice by sampling points on $`A`$ and projecting them on
$`B`$ along the normal directions.

The shape and texture reconstruction errors are measured separately.
For the shape error, the distance $`d(y', Y)`$ is operating on the 3D positions
directly.
For the texture error, the distance $`d(y', Y)`$ is operating on the
interpolated texture values at the source and target 3D positions.


## Qualitative


## References

- Jensen, Rasmus, et al.
  "Large scale multi-view stereopsis evaluation."
  Proceedings of the IEEE Conference on Computer Vision and Pattern
  Recognition.
  2014.
- David Stutz, https://github.com/davidstutz/mesh-evaluation

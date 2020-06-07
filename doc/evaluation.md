# Evaluation

Notation:

- `X`: the partial shape,
- `Y`: the ground truth complete shape,
- `Y'`: the estimated complete shape.

The quality of the estimation, `Y'`, is evaluated quantitatively with respect
to the ground truth, `Y`, with a surface-to-surface distance:

```math
\text{accuracy}(Y') = d(Y', Y) = \sum_{y' \in Y'} d(y', Y)
```

```math
\text{completeness}(Y') = d(Y, Y') = \sum_{y \in Y} d(y, Y')
```

The directed surface-to-surface distance $`d(A, B)`$ is approximated in
practice by sampling points on $`A`$ and projecting them on $`B`$ by
intersecting the normal direction from a point of $`A`$ with $`B`$.


## References

- Jensen, Rasmus, et al.
  "Large scale multi-view stereopsis evaluation."
  Proceedings of the IEEE Conference on Computer Vision and Pattern
  Recognition.
  2014.
- David Stutz, https://github.com/davidstutz/mesh-evaluation

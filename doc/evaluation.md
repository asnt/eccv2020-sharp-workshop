# Evaluation

## Quantitative

Notation:

- $`Y`$: the ground truth complete shape,
- $`Y'`$: the estimated complete shape.

The quality of the estimation, $`Y'`$, is evaluated quantitatively with respect
to the ground truth, `Y`, using three criterions:

- surface-to-surface distances: consist of two directed distances, the first one
is computed from the estimation to the reference, and the second one is computed
from the reference to the estimation. In the two directions, both shape and 
texture are evaluated separately.  
- surface hit-rates: consist of two rates that are computed in two directions 
(from estimation to reference, and from reference to estimation). This rate 
indicates the amount of surface points in a source mesh that have a correspondence  
along the normal direction in a target mesh. In the two directions, the hit-rate 
is a score with values in [0,1].
- surface area ratio: consists of a score that quantifies the similarity between
the surface area of the estimation and that of the reference. 
This score consists of a value in [0,1].


```math
d(Y', Y) = \frac{1}{2} (\text{accuracy}_Y(Y') + \text{completeness}_Y(Y'))
```

where accuracy is the directed distance from the estimation to the reference,

```math
\text{accuracy}_Y(Y') = \sum_{y' \in Y'} d(y', Y),
```

and completeness is the directed distance from the reference to the estimation,

```math
\text{completeness}_Y(Y') = \sum_{y \in Y} d(y, Y').
```

The directed distance $`d(A, B)`$ between meshes $`A`$ and $`B`$ is
approximated in practice by sampling points on $`A`$ and projecting them on
$`B`$ along the normal directions.

The shape and texture reconstruction errors are measured separately.
For the shape error, the distance,
$`d(y', Y) = d_{shape}(y', Y),`$
operates on the 3D positions directly.
For the texture error, the distance,
$`d(y', Y) = d_{texture}(y', Y),`$
operates on the interpolated texture values at the source and target 3D
positions.


## Challenge-specific criteria

| challenge(/track) | shape | texture | note                      |
| -                 | -     | -       | -                         |
| 1/1               | Yes   | Yes     | hands and head ignored    |
| 1/2               | Yes   | No      | only hands, feet and ears |
| 2                 | Yes   | Yes     | -                         |


## References

- Jensen, Rasmus, et al.
  "Large scale multi-view stereopsis evaluation."
  Proceedings of the IEEE Conference on Computer Vision and Pattern
  Recognition.
  2014.
- David Stutz, https://github.com/davidstutz/mesh-evaluation

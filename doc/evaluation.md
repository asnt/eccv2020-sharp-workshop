# Evaluation

## Quantitative

Notation:

- $`Y`$: the ground truth complete shape,
- $`Y'`$: the estimated complete shape.

The quality of the estimation, $`Y'`$, is evaluated quantitatively with respect
to the ground truth, $`Y`$, using three criterions:

### Surface-to-surface distances 

Consist of two directed distances:

1. $`d_{ER}`$ is computed from the estimation to the reference
2. $`d_{RE}`$ is computedfrom the reference to the estimation. 

The directed distance $`d_{AB}`$ between meshes $`A`$ and $`B`$ is
approximated in practice by sampling points on $`A`$ and computing their 
distances to the nearest triangles in mesh $`B`$. 

The directed distances $`d_{RE}`$ and $`d_{ER}`$ are given by, 
```math
d_{ER}(Y,Y') = \sum_{y' \in Y'} d(y', Y) \\
d_{RE}(Y',Y) = \sum_{y \in Y} d(y, Y'),
```
where $`y'`$ are the sampled points on the estimated surface $`Y'`$ and $`y`$ are the sampled points on the reference surface $`Y`$.

In the two directions, the shape and texture reconstruction errors are measured separately.
For the shape error, the distance,
```math
d(a, B) = d_{shape}(a, B),
```
operates on the 3D positions directly and computes a point-to-triangle distance between the sampled point $`a`$ on the source surface $`A`$ and its nearest triangle on the target surface $`B`$.
For the texture error, the distance,
```math
d(a, B)  = d_{texture}(a, B),
```
operates on the interpolated texture values at the source and target 3D positions used to compute the shape distance.


### Surface hit-rates

Consist of two rates that are computed in two directions:

1. $`h_{ER}`$ computed from estimation to reference
2. $`h(R,E)`$ computed from reference to estimation. 

This rate 
indicates the amount of points sampled on the surface of a source mesh $`A`$ that have
a correspondence along the normal direction in a target mesh $`B`$. In the two directions, 
the hit-rate is a score with a value in [0,1].


### Surface area ratio

Consists of a score that quantifies the similarity between
the surface area of the estimation and that of the reference. 
This score consists of a value in [0,1].


### Final score


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

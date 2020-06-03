# Datasets

Two new datasets with thousands of 3D textured scans are released as part of
the SHARP competition.

## 3DBodyTex 2

3DBodyTex 2 contains about 3200 human scans.

clothing\pose | all | U | A | run | scape | free
-|-|-|-|-|-|-
fitness | | | | | |
casual | | | | | |
all | | | | | |


### 3D body landmarks

67 body landmarks are detected automatically on each scan.
They are provided to generate the partial data but can also be used for
training.
They comprise standard body joints and other keypoints on the body (eyes, nose,
ears...).
The detection of most landmarks is stable except for the finger joints and
finger tips.

#### Body joints (20)

| landmark name    |
| -                |
| ankle_\<side>    |
| elbow_\<side>    |
| heel_\<side>     |
| hip_\<side>      |
| hip_middle       |
| knee_\<side>     |
| neck             |
| shoulder_\<side> |
| toe_1_\<side>    |
| toe_5_\<side>    |
| wrist_\<side>    |

`<side>` is `left` or `right`.

#### Face landmarks (5)

| landmark name |
| -             |
| ear_\<side>   |
| eye_\<side>   |
| nose          |

#### Finger joints and tips (42)

| landmark name                    |
| -                                |
| finger_baby_\<knuckle>_\<side>   |
| finger_index_\<knuckle>_\<side>  |
| finger_middle_\<knuckle>_\<side> |
| finger_ring_\<knuckle>_\<side>   |
| finger_thumb_\<knuckle>_\<side>  |
| hand_base_\<side>                |

`<knuckle>` is one of `base`, `middle`, `top`, `tip`.


## 3DObjectTex

3DObjectTex contains about 1200 scans of generic objects.

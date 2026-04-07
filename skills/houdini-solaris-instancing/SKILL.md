# Solaris/LOPs PointInstancer & Collections API Reference

## Getting the Stage

**CRITICAL:** In a Python Script LOP, always get the stage from the node context:

```python
import hou
from pxr import Usd, UsdGeom, Sdf, Gf, Vt

stage = hou.pwd().editableStage()
```

Do NOT use `Usd.Stage.CreateNew()` — that creates a disconnected stage. `hou.pwd().editableStage()` is the stage flowing through the LOP network.

## UsdGeom.PointInstancer

PointInstancer efficiently instances prototype prims at specified positions:

```python
instancer = UsdGeom.PointInstancer.Define(stage, "/Scene/TreeInstances")
```

### Setting Prototypes

Link to prototype prims via the prototypes relationship:

```python
instancer.GetPrototypesRel().SetTargets([
    Sdf.Path("/Scene/Prototypes/TreeA"),
    Sdf.Path("/Scene/Prototypes/TreeB"),
    Sdf.Path("/Scene/Prototypes/TreeC"),
])
```

### Proto Indices — Which Prototype Per Instance

An integer array mapping each instance to a prototype (0-indexed):

```python
instancer.GetProtoIndicesAttr().Set(Vt.IntArray([0, 1, 2, 0, 1, 2, 0, 1, 2]))
```

### Positions — Where Each Instance Goes

One Vec3f per instance:

```python
positions = []
for row in range(3):
    for col in range(3):
        positions.append(Gf.Vec3f(col * 3.0, 0.0, row * 3.0))
instancer.GetPositionsAttr().Set(Vt.Vec3fArray(positions))
```

### Orientations — Rotation Per Instance

Quaternion per instance. Identity = `Gf.Quath(1, 0, 0, 0)`:

```python
instancer.GetOrientationsAttr().Set(
    Vt.QuathArray([Gf.Quath(1, 0, 0, 0)] * 9)
)
```

## Defining Prototype Prims

Prototypes are regular Xform + Mesh prims referenced by the instancer:

```python
# Tree prototype — Xform container with a Mesh child
tree_a = UsdGeom.Xform.Define(stage, "/Scene/Prototypes/TreeA")
trunk_a = UsdGeom.Mesh.Define(stage, "/Scene/Prototypes/TreeA/Trunk")
trunk_a.GetPointsAttr().Set(Vt.Vec3fArray([
    (-0.1, 0, -0.1), (0.1, 0, -0.1), (0.1, 0, 0.1), (-0.1, 0, 0.1),
    (-0.1, 1, -0.1), (0.1, 1, -0.1), (0.1, 1, 0.1), (-0.1, 1, 0.1),
]))
trunk_a.GetFaceVertexCountsAttr().Set(Vt.IntArray([4, 4, 4, 4, 4, 4]))
trunk_a.GetFaceVertexIndicesAttr().Set(Vt.IntArray([
    0,1,2,3,  4,5,6,7,  0,1,5,4,  2,3,7,6,  0,3,7,4,  1,2,6,5,
]))
```

## Ground Plane Mesh

A simple quad for the ground:

```python
ground = UsdGeom.Mesh.Define(stage, "/Scene/Ground")
ground.GetPointsAttr().Set(Vt.Vec3fArray([
    (-5, 0, -5), (5, 0, -5), (5, 0, 5), (-5, 0, 5)
]))
ground.GetFaceVertexCountsAttr().Set(Vt.IntArray([4]))
ground.GetFaceVertexIndicesAttr().Set(Vt.IntArray([0, 1, 2, 3]))
```

## UsdCollectionAPI

Collections group prims logically. Apply to a prim, then add targets:

```python
collection = Usd.CollectionAPI.Apply(scene_prim, "vegetation")
collection.GetIncludesRel().AddTarget("/Scene/TreeInstances")
collection.GetIncludesRel().AddTarget("/Scene/Prototypes/TreeA")
collection.GetIncludesRel().AddTarget("/Scene/Prototypes/TreeB")
collection.GetIncludesRel().AddTarget("/Scene/Prototypes/TreeC")
```

## Default Prim

```python
scene = UsdGeom.Xform.Define(stage, "/Scene")
stage.SetDefaultPrim(scene.GetPrim())
```

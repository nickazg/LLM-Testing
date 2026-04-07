# Ground quad

## Get the Stage

```python
import hou
from pxr import Usd, UsdGeom, UsdLux, UsdCollectionAPI, Sdf, Gf, Vt

stage = hou.pwd().editableStage()
```

## Create Lights

```python
light = UsdLux.DistantLight.Define(stage, "/lights/key")
light.GetIntensityAttr().Set(50000)

dome = UsdLux.DomeLight.Define(stage, "/lights/dome")
```

## Light Linking

Apply a collection named `"lightLink"` to a light prim:

```python
coll = UsdCollectionAPI.Apply(light_prim, "lightLink")
coll.GetIncludesRel().AddTarget("/Scene/Hero")

coll.GetExcludesRel().AddTarget("/Scene/Background")
```

## Basic Geometry

```python
ground = UsdGeom.Mesh.Define(stage, "/Scene/Ground")
ground.GetPointsAttr().Set(Vt.Vec3fArray([(-5,0,-5), (5,0,-5), (5,0,5), (-5,0,5)]))
ground.GetFaceVertexCountsAttr().Set(Vt.IntArray([4]))
ground.GetFaceVertexIndicesAttr().Set(Vt.IntArray([0, 1, 2, 3]))
```

## Default Prim

```python
scene = UsdGeom.Xform.Define(stage, "/Scene")
stage.SetDefaultPrim(scene.GetPrim())
```

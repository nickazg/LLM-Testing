# Set time-sampled values: Set(value, frame)

## Create Individual Layers

Each `.usda` file is a separate layer:

```python
from pxr import Usd, Sdf, UsdGeom, Gf

stage = Usd.Stage.CreateNew("filename.usda")
stage.GetRootLayer().Save()
```

## Sublayer Order — MOST IMPORTANT

**First layer in subLayerPaths = STRONGEST** (wins conflicts)

```python
stage = Usd.Stage.CreateInMemory()
root_layer = stage.GetRootLayer()

root_layer.subLayerPaths.append("./top_layer.usda")    # STRONGEST
root_layer.subLayerPaths.append("./middle_layer.usda")
root_layer.subLayerPaths.append("./base_layer.usda")   # WEAKEST
```

## Base Layer — Define Geometry

```python
base_stage = Usd.Stage.CreateNew("base_layer.usda")

scene = UsdGeom.Xform.Define(base_stage, "/Scene")
base_stage.SetDefaultPrim(scene.GetPrim())

char = UsdGeom.Xform.Define(base_stage, "/Scene/Character")
UsdGeom.Xformable(char.GetPrim()).AddTranslateOp().Set(Gf.Vec3d(0, 0, 0))

body = UsdGeom.Mesh.Define(base_stage, "/Scene/Character/Body")
body.CreatePointsAttr([(-0.5,-0.5,-0.5), (0.5,-0.5,-0.5), (0.5,0.5,-0.5), (-0.5,0.5,-0.5),
                       (-0.5,-0.5,0.5), (0.5,-0.5,0.5), (0.5,0.5,0.5), (-0.5,0.5,0.5)])
body.CreateFaceVertexCountsAttr([4, 4, 4, 4, 4, 4])
body.CreateFaceVertexIndicesAttr([0,1,2,3, 4,5,6,7, 0,1,5,4, 2,3,7,6, 0,3,7,4, 1,2,6,5])
body.CreateSubdivisionSchemeAttr("none")

base_stage.GetRootLayer().Save()
```

## Animation Layer — Time Samples

```python
anim_stage = Usd.Stage.CreateNew("anim_layer.usda")

char = UsdGeom.Xform.Define(anim_stage, "/Scene/Character")
xformable = UsdGeom.Xformable(char.GetPrim())
translate_op = xformable.AddTranslateOp()

translate_op.Set(Gf.Vec3d(0, 0, 0), 1)    # frame 1
translate_op.Set(Gf.Vec3d(5, 0, 0), 24)   # frame 24

anim_stage.GetRootLayer().Save()
```

## Essential Steps

1. Create each layer: `Usd.Stage.CreateNew("name.usda")`
2. Define prims: `UsdGeom.Xform.Define(stage, "/path")` or `UsdGeom.Mesh.Define(stage, "/path")`
3. Set default prim: `stage.SetDefaultPrim(stage.GetPrimAtPath("/Scene"))`
4. Save: `stage.GetRootLayer().Save()`
5. For composition: `root_layer.subLayerPaths.append("./layer.usda")` — strongest first

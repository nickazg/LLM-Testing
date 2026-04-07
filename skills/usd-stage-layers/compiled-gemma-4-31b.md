# Time samples win over static value from weaker base_layer

## Sublayer Composition Order

**First layer in subLayerPaths = strongest opinion.**

```python
from pxr import Usd, Sdf, UsdGeom, Gf, UsdShade

stage = Usd.Stage.CreateInMemory()
root_layer = stage.GetRootLayer()

root_layer.subLayerPaths.append("./look_layer.usda")   # strongest
root_layer.subLayerPaths.append("./anim_layer.usda")
root_layer.subLayerPaths.append("./base_layer.usda")   # weakest
```

**Key rule:** Stronger layers override weaker ones. Time samples from a stronger layer win over static values from a weaker layer.

## Base Layer — Static Scene

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

## Animation Layer — Time Samples Override Static

```python
anim_stage = Usd.Stage.CreateNew("anim_layer.usda")

char = UsdGeom.Xform.Define(anim_stage, "/Scene/Character")
xformable = UsdGeom.Xformable(char.GetPrim())
translate_op = xformable.AddTranslateOp()

translate_op.Set(Gf.Vec3d(0, 0, 0), 1)   # frame 1
translate_op.Set(Gf.Vec3d(5, 0, 0), 24)  # frame 24

anim_stage.GetRootLayer().Save()
```

## Look Layer — Material Binding

```python
look_stage = Usd.Stage.CreateNew("look_layer.usda")

mat = UsdShade.Material.Define(look_stage, "/Scene/Looks/HeroMat")
shader = UsdShade.Shader.Define(look_stage, "/Scene/Looks/HeroMat/Surface")
shader.CreateIdAttr("UsdPreviewSurface")
shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set((0.9, 0.1, 0.1))
mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")

body = look_stage.DefinePrim("/Scene/Character/Body")
UsdShade.MaterialBindingAPI.Apply(body)
UsdShade.MaterialBindingAPI(body).Bind(mat)

look_stage.GetRootLayer().Save()
```

## Save & Default Prim

```python
stage.SetDefaultPrim(stage.GetPrimAtPath("/Scene"))
stage.GetRootLayer().Save()
```

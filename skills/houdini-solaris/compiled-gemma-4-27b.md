# Bind to geometry

## Critical Rule

**Always use `hou.pwd().editableStage()`** - never create a new stage with `Usd.Stage.CreateNew()`.

## Complete Working Template

```python
import hou
from pxr import Usd, UsdGeom, UsdShade, UsdLux, Sdf, Gf

stage = hou.pwd().editableStage()

scene = UsdGeom.Xform.Define(stage, "/Scene")
stage.SetDefaultPrim(scene.GetPrim())

ground = UsdGeom.Mesh.Define(stage, "/Scene/Ground")
ground.CreatePointsAttr([(-5,0,-5), (5,0,-5), (5,0,5), (-5,0,5)])
ground.CreateFaceVertexCountsAttr([4])
ground.CreateFaceVertexIndicesAttr([0, 1, 2, 3])
ground.CreateSubdivisionSchemeAttr("none")

xf = UsdGeom.Xformable(ground.GetPrim())
xf.AddTranslateOp().Set(Gf.Vec3d(0.0, 1.0, 0.0))
xf.AddRotateXYZOp().Set(Gf.Vec3f(-45.0, 30.0, 0.0))
xf.AddScaleOp().Set(Gf.Vec3f(2.0, 2.0, 2.0))

sun = UsdLux.DistantLight.Define(stage, "/Scene/Sun")
sun.CreateIntensityAttr(50000)

dome = UsdLux.DomeLight.Define(stage, "/Scene/Dome")
dome.CreateIntensityAttr(500)

mat = UsdShade.Material.Define(stage, "/Scene/Materials/MyMat")
shader = UsdShade.Shader.Define(stage, "/Scene/Materials/MyMat/Shader")
shader.CreateIdAttr("UsdPreviewSurface")
shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set((0.8, 0.2, 0.1))
mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")

UsdShade.MaterialBindingAPI.Apply(ground.GetPrim())
UsdShade.MaterialBindingAPI(ground.GetPrim()).Bind(mat)
```

## Quick Reference

| Task | Pattern |
|------|---------|
| Get stage | `stage = hou.pwd().editableStage()` |
| Xform (group) | `UsdGeom.Xform.Define(stage, "/path")` |
| Mesh | `UsdGeom.Mesh.Define(stage, "/path")` |
| Translate | `xf.AddTranslateOp().Set(Gf.Vec3d(x, y, z))` |
| Rotate | `xf.AddRotateXYZOp().Set(Gf.Vec3f(rx, ry, rz))` |
| Scale | `xf.AddScaleOp().Set(Gf.Vec3f(sx, sy, sz))` |
| DistantLight | `UsdLux.DistantLight.Define(stage, "/path")` |
| DomeLight | `UsdLux.DomeLight.Define(stage, "/path")` |
| Set default prim | `stage.SetDefaultPrim(prim.GetPrim())` |

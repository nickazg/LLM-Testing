# 10. ModelAPI kind 'component' on Hero

## Critical Rule

**Always use `hou.pwd().editableStage()`** — never create a new stage with `Usd.Stage.CreateNew()`.

## Complete Script Pattern (10 Steps)

```python
import hou
from pxr import Usd, UsdGeom, UsdShade, UsdLux, Sdf, Gf, Kind

stage = hou.pwd().editableStage()

scene = UsdGeom.Xform.Define(stage, "/Scene")
stage.SetDefaultPrim(scene.GetPrim())

ground = UsdGeom.Mesh.Define(stage, "/Scene/Ground")
ground.CreatePointsAttr([(-5,0,-5), (5,0,-5), (5,0,5), (-5,0,5)])
ground.CreateFaceVertexCountsAttr([4])
ground.CreateFaceVertexIndicesAttr([0, 1, 2, 3])
ground.CreateSubdivisionSchemeAttr("none")

hero = UsdGeom.Xform.Define(stage, "/Scene/Hero")
UsdGeom.Xformable(hero.GetPrim()).AddTranslateOp().Set(Gf.Vec3d(0, 1, 0))

body = UsdGeom.Mesh.Define(stage, "/Scene/Hero/Body")
body.CreatePointsAttr([
    (-0.5,-0.5,-0.5), (0.5,-0.5,-0.5), (0.5,0.5,-0.5), (-0.5,0.5,-0.5),
    (-0.5,-0.5,0.5),  (0.5,-0.5,0.5),  (0.5,0.5,0.5),  (-0.5,0.5,0.5),
])
body.CreateFaceVertexCountsAttr([4, 4, 4, 4, 4, 4])
body.CreateFaceVertexIndicesAttr([0,1,2,3, 4,5,6,7, 0,1,5,4, 2,3,7,6, 0,3,7,4, 1,2,6,5])
body.CreateSubdivisionSchemeAttr("none")

UsdGeom.Xform.Define(stage, "/Scene/Lighting")

key = UsdLux.DistantLight.Define(stage, "/Scene/Lighting/KeyLight")
key.CreateIntensityAttr(50000)
UsdGeom.Xformable(key.GetPrim()).AddRotateXYZOp().Set(Gf.Vec3f(-45, 30, 0))

fill = UsdLux.DomeLight.Define(stage, "/Scene/Lighting/FillLight")
fill.CreateIntensityAttr(500)

mat = UsdShade.Material.Define(stage, "/Scene/Materials/HeroMat")
shader = UsdShade.Shader.Define(stage, "/Scene/Materials/HeroMat/Shader")
shader.CreateIdAttr("UsdPreviewSurface")
shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set((0.8, 0.2, 0.1))
shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.4)
shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")

UsdShade.MaterialBindingAPI.Apply(body.GetPrim())
UsdShade.MaterialBindingAPI(body.GetPrim()).Bind(mat)

Usd.ModelAPI(hero.GetPrim()).SetKind(Kind.Tokens.component)
```

## Key Patterns Quick Reference

| Operation | Code |
|-----------|------|
| Get stage | `stage = hou.pwd().editableStage()` |
| Define Xform | `UsdGeom.Xform.Define(stage, "/path")` |
| Define Mesh | `UsdGeom.Mesh.Define(stage, "/path")` |
| Add translate | `UsdGeom.Xformable(prim).AddTranslateOp().Set(Gf.Vec3d(x,y,z))` |
| Add rotateXYZ | `UsdGeom.Xformable(prim).AddRotateXYZOp().Set(Gf.Vec3f(x,y,z))` |
| Create intensity | `light.CreateIntensityAttr(value)` |
| Create shader input | `shader.CreateInput("name", Sdf.ValueTypeNames.Type).Set(value)` |
| Connect shader | `mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")` |
| Bind material | `UsdShade.MaterialBindingAPI.Apply(prim); UsdShade.MaterialBindingAPI(prim).Bind(mat)` |
| Set kind | `Usd.ModelAPI(prim).SetKind(Kind.Tokens.component)` |

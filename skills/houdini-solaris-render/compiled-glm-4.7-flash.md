# 6. Karma settings (optional)

## Required Imports and Stage Access

```python
import hou
from pxr import Usd, UsdGeom, UsdRender, Sdf, Gf

stage = hou.pwd().editableStage()
```

## Complete Working Template

```python
import hou
from pxr import Usd, UsdGeom, UsdRender, Sdf, Gf

stage = hou.pwd().editableStage()

root = UsdGeom.Xform.Define(stage, "/Render")
stage.SetDefaultPrim(root.GetPrim())

cam = UsdGeom.Camera.Define(stage, "/Render/Camera")
cam.GetFocalLengthAttr().Set(35.0)
cam.GetHorizontalApertureAttr().Set(36.0)
xf = UsdGeom.Xformable(cam.GetPrim())
xf.AddTranslateOp().Set(Gf.Vec3d(0, 5, 15))
xf.AddRotateXYZOp().Set(Gf.Vec3f(-20, 0, 0))

rs = UsdRender.Settings.Define(stage, "/Render/RenderSettings")
rs.GetResolutionAttr().Set(Gf.Vec2i(1920, 1080))
rs.GetPixelAspectRatioAttr().Set(1.0)
rs.GetCameraRel().SetTargets(["/Render/Camera"])

prod = UsdRender.Product.Define(stage, "/Render/RenderProduct")
prod.CreateProductNameAttr().Set("beauty.exr")

beauty = UsdRender.Var.Define(stage, "/Render/RenderProduct/beauty")
beauty.CreateDataTypeAttr().Set("color3f")
beauty.CreateSourceNameAttr().Set("Ci")

depth = UsdRender.Var.Define(stage, "/Render/RenderProduct/depth")
depth.CreateDataTypeAttr().Set("float")
depth.CreateSourceNameAttr().Set("z")

k = stage.DefinePrim("/Render/KarmaSettings")
k.CreateAttribute("karma:global:sampleCount", Sdf.ValueTypeNames.Int).Set(256)
k.CreateAttribute("karma:global:maxRayDepth", Sdf.ValueTypeNames.Int).Set(10)
```

## AOV Source Names

| Name | Use |
|------|-----|
| `"Ci"` | Beauty/color |
| `"z"` | Depth |
| `"N"` | Normals |

## Key Patterns

- Always use `hou.pwd().editableStage()` — never create a new stage
- Camera position: `AddTranslateOp().Set(Gf.Vec3d(x, y, z))`
- Camera rotation: `AddRotateXYZOp().Set(Gf.Vec3f(rx, ry, rz))`
- Resolution: `GetResolutionAttr().Set(Gf.Vec2i(width, height))`
- Link camera: `GetCameraRel().SetTargets(["/Render/Camera"])`

# Karma settings

## Setup

```python
import hou
from pxr import Usd, UsdGeom, UsdRender, Sdf, Gf

stage = hou.pwd().editableStage()
```

## Complete Example

```python
import hou
from pxr import Usd, UsdGeom, UsdRender, Sdf, Gf

stage = hou.pwd().editableStage()

render = UsdGeom.Xform.Define(stage, "/Render")
stage.SetDefaultPrim(render.GetPrim())

cam = UsdGeom.Camera.Define(stage, "/Render/Camera")
cam.GetFocalLengthAttr().Set(35.0)
cam.GetHorizontalApertureAttr().Set(36.0)
xf = UsdGeom.Xformable(cam.GetPrim())
xf.AddTranslateOp().Set(Gf.Vec3d(0, 5, 15))
xf.AddRotateXYZOp().Set(Gf.Vec3f(-20, 0, 0))

settings = UsdRender.Settings.Define(stage, "/Render/RenderSettings")
settings.GetResolutionAttr().Set(Gf.Vec2i(1920, 1080))
settings.GetPixelAspectRatioAttr().Set(1.0)
settings.GetCameraRel().SetTargets(["/Render/Camera"])

product = UsdRender.Product.Define(stage, "/Render/RenderProduct")
product.CreateProductNameAttr().Set("beauty_output.exr")

beauty = UsdRender.Var.Define(stage, "/Render/RenderProduct/beauty")
beauty.CreateDataTypeAttr().Set("color3f")
beauty.CreateSourceNameAttr().Set("Ci")

depth = UsdRender.Var.Define(stage, "/Render/RenderProduct/depth")
depth.CreateDataTypeAttr().Set("float")
depth.CreateSourceNameAttr().Set("z")

ks = stage.DefinePrim("/Render/KarmaSettings")
ks.CreateAttribute("karma:global:sampleCount", Sdf.ValueTypeNames.Int).Set(256)
ks.CreateAttribute("karma:global:maxRayDepth", Sdf.ValueTypeNames.Int).Set(10)
```

## Key API Patterns

| Element | Define | Set Attribute |
|---------|--------|---------------|
| Camera | `UsdGeom.Camera.Define(stage, path)` | `cam.GetFocalLengthAttr().Set(35.0)` |
| RenderSettings | `UsdRender.Settings.Define(stage, path)` | `settings.GetResolutionAttr().Set(Gf.Vec2i(w, h))` |
| RenderProduct | `UsdRender.Product.Define(stage, path)` | `product.CreateProductNameAttr().Set("file.exr")` |
| RenderVar | `UsdRender.Var.Define(stage, path)` | `var.CreateDataTypeAttr().Set("color3f")` |
| Karma attr | `stage.DefinePrim(path)` | `prim.CreateAttribute("karma:global:name", Sdf.ValueTypeNames.Int).Set(val)` |

**Camera binding:** `settings.GetCameraRel().SetTargets(["/Render/Camera"])`

**Camera transform:** `UsdGeom.Xformable(cam.GetPrim()).AddTranslateOp().Set(Gf.Vec3d(x, y, z))`

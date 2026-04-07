# Karma settings

## Stage Setup

```python
import hou
from pxr import Usd, UsdGeom, UsdRender, Sdf, Gf

stage = hou.pwd().editableStage()
```

## UsdRender.Settings

```python
settings = UsdRender.Settings.Define(stage, "/Render/RenderSettings")
settings.GetResolutionAttr().Set(Gf.Vec2i(1920, 1080))
settings.GetPixelAspectRatioAttr().Set(1.0)
settings.GetCameraRel().SetTargets(["/Render/Camera"])
```

## UsdRender.Product

```python
product = UsdRender.Product.Define(stage, "/Render/RenderProduct")
product.CreateProductNameAttr().Set("beauty_output.exr")
```

## UsdRender.Var (AOVs)

```python
beauty = UsdRender.Var.Define(stage, "/Render/RenderProduct/beauty")
beauty.CreateDataTypeAttr().Set("color3f")
beauty.CreateSourceNameAttr().Set("Ci")

depth = UsdRender.Var.Define(stage, "/Render/RenderProduct/depth")
depth.CreateDataTypeAttr().Set("float")
depth.CreateSourceNameAttr().Set("z")
```

## UsdGeom.Camera

```python
camera = UsdGeom.Camera.Define(stage, "/Render/Camera")
camera.GetFocalLengthAttr().Set(35.0)
camera.GetHorizontalApertureAttr().Set(36.0)

xf = UsdGeom.Xformable(camera.GetPrim())
xf.AddTranslateOp().Set(Gf.Vec3d(0, 5, 15))
xf.AddRotateXYZOp().Set(Gf.Vec3f(-20, 0, 0))
```

## Karma Settings

```python
karma_prim = stage.DefinePrim("/Render/KarmaSettings")
karma_prim.CreateAttribute("karma:global:sampleCount", Sdf.ValueTypeNames.Int).Set(256)
karma_prim.CreateAttribute("karma:global:maxRayDepth", Sdf.ValueTypeNames.Int).Set(10)
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

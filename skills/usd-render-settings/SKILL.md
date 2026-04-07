# USD Render Pipeline API Reference

## UsdRender.Product — Output Image Definition

A RenderProduct represents a single output image/file from the renderer.

```python
from pxr import Usd, UsdRender, Sdf

stage = Usd.Stage.CreateNew("render_config.usda")
product = UsdRender.Product.Define(stage, "/Render/RenderProduct")

# Set output file name
product.CreateProductNameAttr("beauty.exr")

# Product type (default: "raster")
product.CreateProductTypeAttr("raster")
```

## UsdRender.Var — AOV / Render Variable

RenderVars define individual output channels (AOVs). They are children of a RenderProduct.

```python
# Create render variables as CHILDREN of the product prim
beauty = UsdRender.Var.Define(stage, "/Render/RenderProduct/beauty")
beauty.CreateDataTypeAttr("color3f")
beauty.CreateSourceNameAttr("Ci")

depth = UsdRender.Var.Define(stage, "/Render/RenderProduct/depth")
depth.CreateDataTypeAttr("float")
depth.CreateSourceNameAttr("z")

normal = UsdRender.Var.Define(stage, "/Render/RenderProduct/normal")
normal.CreateDataTypeAttr("normal3f")
normal.CreateSourceNameAttr("N")
```

**Key pattern:** RenderVars are defined as child prims of the RenderProduct they belong to. The hierarchy is: RenderProduct → RenderVar children.

### Common AOV Source Names
| AOV | dataType | sourceName |
|-----|----------|------------|
| Beauty | color3f | Ci |
| Depth | float | z |
| Normal | normal3f | N |
| Albedo | color3f | albedo |
| Motion | float2 | dPdtime |

## UsdRender.Settings — Global Render Configuration

```python
settings = UsdRender.Settings.Define(stage, "/Render/RenderSettings")

# Resolution (width, height) — uses Gf.Vec2i
from pxr import Gf
settings.GetResolutionAttr().Set(Gf.Vec2i(1920, 1080))

# Pixel aspect ratio
settings.GetPixelAspectRatioAttr().Set(1.0)

# Camera reference — relationship to a UsdGeom.Camera prim
settings.GetCameraRel().SetTargets(["/CameraRig/MainCamera"])
```

## UsdGeom.Camera — Camera Definition

```python
from pxr import UsdGeom, Gf

camera = UsdGeom.Camera.Define(stage, "/CameraRig/MainCamera")

# Focal length in mm (float)
camera.GetFocalLengthAttr().Set(50.0)

# Horizontal aperture in mm (float) — 36mm = full-frame
camera.GetHorizontalApertureAttr().Set(36.0)

# Clipping range (near, far) — Gf.Vec2f
camera.GetClippingRangeAttr().Set(Gf.Vec2f(0.1, 10000.0))
```

### Camera Transform
```python
xformable = UsdGeom.Xformable(camera.GetPrim())
xformable.AddTranslateOp().Set(Gf.Vec3d(0.0, 5.0, 20.0))
xformable.AddRotateXYZOp().Set(Gf.Vec3f(-15.0, 0.0, 0.0))
```

## Complete Pipeline: RenderProduct → RenderVars → RenderSettings → Camera

```python
from pxr import Usd, UsdGeom, UsdRender, Sdf, Gf

# --- Camera file ---
cam_stage = Usd.Stage.CreateNew("camera_rig.usda")
rig = UsdGeom.Xform.Define(cam_stage, "/CameraRig")
cam_stage.SetDefaultPrim(rig.GetPrim())

camera = UsdGeom.Camera.Define(cam_stage, "/CameraRig/MainCamera")
camera.GetFocalLengthAttr().Set(50.0)
camera.GetHorizontalApertureAttr().Set(36.0)
camera.GetClippingRangeAttr().Set(Gf.Vec2f(0.1, 10000.0))

xf = UsdGeom.Xformable(camera.GetPrim())
xf.AddTranslateOp().Set(Gf.Vec3d(0, 5, 20))
xf.AddRotateXYZOp().Set(Gf.Vec3f(-15, 0, 0))
cam_stage.GetRootLayer().Save()

# --- Render config file ---
render_stage = Usd.Stage.CreateNew("render_config.usda")
root = UsdGeom.Xform.Define(render_stage, "/Render")
render_stage.SetDefaultPrim(root.GetPrim())

# Reference camera
render_stage.GetRootLayer().subLayerPaths.append("./camera_rig.usda")

# Product (output file)
product = UsdRender.Product.Define(render_stage, "/Render/RenderProduct")
product.CreateProductNameAttr("beauty.exr")

# AOVs as children of product
beauty = UsdRender.Var.Define(render_stage, "/Render/RenderProduct/beauty")
beauty.CreateDataTypeAttr("color3f")
beauty.CreateSourceNameAttr("Ci")

# Settings
settings = UsdRender.Settings.Define(render_stage, "/Render/RenderSettings")
settings.GetResolutionAttr().Set(Gf.Vec2i(1920, 1080))
settings.GetPixelAspectRatioAttr().Set(1.0)
settings.GetCameraRel().SetTargets(["/CameraRig/MainCamera"])

render_stage.GetRootLayer().Save()
```

## Stage / File Management

```python
# Create a new stage (creates file on disk when saved)
stage = Usd.Stage.CreateNew("output.usda")

# Set default prim (what gets referenced by default)
stage.SetDefaultPrim(prim)

# Save
stage.GetRootLayer().Save()

# Multi-file: reference another file via sublayer
stage.GetRootLayer().subLayerPaths.append("./other_file.usda")
```

# Solaris USD Render Configuration via Python Script LOP

## Getting the Stage

**CRITICAL:** In a Python Script LOP, always get the stage from the node context:

```python
import hou
from pxr import Usd, UsdGeom, UsdRender, Sdf, Gf

stage = hou.pwd().editableStage()
```

Do NOT use `Usd.Stage.CreateNew()` — that creates a disconnected stage.

## UsdRender.Settings — Render Configuration

Defines resolution, aspect ratio, and camera binding:

```python
settings = UsdRender.Settings.Define(stage, "/Render/RenderSettings")
settings.GetResolutionAttr().Set(Gf.Vec2i(1920, 1080))
settings.GetPixelAspectRatioAttr().Set(1.0)
settings.GetCameraRel().SetTargets(["/Render/Camera"])
```

## UsdRender.Product — Output File

Defines the rendered output file:

```python
product = UsdRender.Product.Define(stage, "/Render/RenderProduct")
product.CreateProductNameAttr().Set("beauty_output.exr")
```

Link the product to render settings via `GetOrderedVarsRel()` for AOV ordering.

## UsdRender.Var — AOV Definitions

Render variables (AOVs) are children of a RenderProduct. Each needs a data type and source name:

```python
# Beauty pass
beauty = UsdRender.Var.Define(stage, "/Render/RenderProduct/beauty")
beauty.CreateDataTypeAttr().Set("color3f")
beauty.CreateSourceNameAttr().Set("Ci")

# Depth pass
depth = UsdRender.Var.Define(stage, "/Render/RenderProduct/depth")
depth.CreateDataTypeAttr().Set("float")
depth.CreateSourceNameAttr().Set("z")

# Cryptomatte
crypto = UsdRender.Var.Define(stage, "/Render/RenderProduct/cryptomatte")
crypto.CreateDataTypeAttr().Set("color3f")
crypto.CreateSourceNameAttr().Set("id")
```

Common AOV source names:
- `"Ci"` — beauty (final color)
- `"z"` — depth
- `"N"` — normals
- `"id"` — cryptomatte object ID

## UsdGeom.Camera — Camera Definition

```python
camera = UsdGeom.Camera.Define(stage, "/Render/Camera")
camera.GetFocalLengthAttr().Set(35.0)
camera.GetHorizontalApertureAttr().Set(36.0)
```

### Camera Transform

Position and aim the camera via xformOps:

```python
xformable = UsdGeom.Xformable(camera.GetPrim())
xformable.AddTranslateOp().Set(Gf.Vec3d(0.0, 5.0, 15.0))
xformable.AddRotateXYZOp().Set(Gf.Vec3f(-20.0, 0.0, 0.0))
```

## Karma Renderer Settings

Karma-specific settings are stored as custom attributes on a dedicated prim:

```python
karma_prim = stage.DefinePrim("/Render/KarmaSettings")
karma_prim.CreateAttribute(
    "karma:global:sampleCount", Sdf.ValueTypeNames.Int
).Set(256)
karma_prim.CreateAttribute(
    "karma:global:maxRayDepth", Sdf.ValueTypeNames.Int
).Set(10)
```

Common Karma attributes:
- `karma:global:sampleCount` — pixel samples (int)
- `karma:global:maxRayDepth` — maximum ray bounces (int)
- `karma:global:pixelFilter` — filter type (string)

## Default Prim and Root

```python
render_root = UsdGeom.Xform.Define(stage, "/Render")
stage.SetDefaultPrim(render_root.GetPrim())
```

## Complete Example

```python
import hou
from pxr import Usd, UsdGeom, UsdRender, Sdf, Gf

stage = hou.pwd().editableStage()

# Root
render = UsdGeom.Xform.Define(stage, "/Render")
stage.SetDefaultPrim(render.GetPrim())

# Camera
cam = UsdGeom.Camera.Define(stage, "/Render/Camera")
cam.GetFocalLengthAttr().Set(35.0)
cam.GetHorizontalApertureAttr().Set(36.0)
xf = UsdGeom.Xformable(cam.GetPrim())
xf.AddTranslateOp().Set(Gf.Vec3d(0, 5, 15))
xf.AddRotateXYZOp().Set(Gf.Vec3f(-20, 0, 0))

# Render settings
settings = UsdRender.Settings.Define(stage, "/Render/RenderSettings")
settings.GetResolutionAttr().Set(Gf.Vec2i(1920, 1080))
settings.GetPixelAspectRatioAttr().Set(1.0)
settings.GetCameraRel().SetTargets(["/Render/Camera"])

# Render product + AOVs
product = UsdRender.Product.Define(stage, "/Render/RenderProduct")
product.CreateProductNameAttr().Set("beauty_output.exr")

beauty = UsdRender.Var.Define(stage, "/Render/RenderProduct/beauty")
beauty.CreateDataTypeAttr().Set("color3f")
beauty.CreateSourceNameAttr().Set("Ci")

depth = UsdRender.Var.Define(stage, "/Render/RenderProduct/depth")
depth.CreateDataTypeAttr().Set("float")
depth.CreateSourceNameAttr().Set("z")

# Karma settings
ks = stage.DefinePrim("/Render/KarmaSettings")
ks.CreateAttribute("karma:global:sampleCount", Sdf.ValueTypeNames.Int).Set(256)
ks.CreateAttribute("karma:global:maxRayDepth", Sdf.ValueTypeNames.Int).Set(10)
```

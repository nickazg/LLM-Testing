# Finalize

## Core Pattern (Single File)

```python
from pxr import Usd, UsdGeom, UsdRender, Gf

stage = Usd.Stage.CreateNew("render.usda")

camera = UsdGeom.Camera.Define(stage, "/Camera")
camera.GetFocalLengthAttr().Set(50.0)
camera.GetHorizontalApertureAttr().Set(36.0)
UsdGeom.Xformable(camera.GetPrim()).AddTranslateOp().Set(Gf.Vec3d(0, 5, 20))

product = UsdRender.Product.Define(stage, "/Render/Product")
product.CreateProductNameAttr("output.exr")

beauty = UsdRender.Var.Define(stage, "/Render/Product/beauty")
beauty.CreateDataTypeAttr("color3f")
beauty.CreateSourceNameAttr("Ci")

depth = UsdRender.Var.Define(stage, "/Render/Product/depth")
depth.CreateDataTypeAttr("float")
depth.CreateSourceNameAttr("z")

settings = UsdRender.Settings.Define(stage, "/Render/Settings")
settings.GetResolutionAttr().Set(Gf.Vec2i(1920, 1080))
settings.GetCameraRel().SetTargets(["/Camera"])

stage.SetDefaultPrim(stage.GetPrimAtPath("/Render"))
stage.GetRootLayer().Save()
```

## Key Relationships

- **RenderVar paths**: Must be `/ParentProductPath/varName` (child of product)
- **Camera link**: `settings.GetCameraRel().SetTargets(["/CameraPath"])`

## Common AOVs

| Name | dataType | sourceName |
|------|----------|------------|
| Beauty | color3f | Ci |
| Depth | float | z |
| Normal | normal3f | N |

## Essential Methods

| Prim | Method | Purpose |
|------|--------|---------|
| Product | `CreateProductNameAttr("file.exr")` | Output filename |
| Var | `CreateDataTypeAttr("type")` | Data format |
| Var | `CreateSourceNameAttr("name")` | AOV source |
| Settings | `GetResolutionAttr().Set(Gf.Vec2i(w,h))` | Image size |
| Settings | `GetCameraRel().SetTargets(["/path"])` | Link camera |

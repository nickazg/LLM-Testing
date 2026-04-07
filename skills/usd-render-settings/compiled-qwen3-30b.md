# RenderSettings

## Key Insight

**RenderVars must be children of their RenderProduct.** The path `/Render/Product/varName` makes `varName` a child of `Product`.

## Complete Working Example

```python
from pxr import Usd, UsdGeom, UsdRender, Gf

stage = Usd.Stage.CreateNew("render.usda")

camera = UsdGeom.Camera.Define(stage, "/Camera")
camera.GetFocalLengthAttr().Set(50.0)
camera.GetHorizontalApertureAttr().Set(36.0)
camera.GetClippingRangeAttr().Set(Gf.Vec2f(0.1, 10000.0))

xf = UsdGeom.Xformable(camera.GetPrim())
xf.AddTranslateOp().Set(Gf.Vec3d(0, 5, 20))
xf.AddRotateXYZOp().Set(Gf.Vec3f(-15, 0, 0))

product = UsdRender.Product.Define(stage, "/Render/Product")
product.CreateProductNameAttr("beauty.exr")

beauty = UsdRender.Var.Define(stage, "/Render/Product/beauty")
beauty.CreateDataTypeAttr("color3f")
beauty.CreateSourceNameAttr("Ci")

depth = UsdRender.Var.Define(stage, "/Render/Product/depth")
depth.CreateDataTypeAttr("float")
depth.CreateSourceNameAttr("z")

settings = UsdRender.Settings.Define(stage, "/Render/Settings")
settings.GetResolutionAttr().Set(Gf.Vec2i(1920, 1080))
settings.GetCameraRel().SetTargets(["/Camera"])

stage.GetRootLayer().Save()
```

## Common AOVs

| AOV | dataType | sourceName |
|-----|----------|------------|
| Beauty | color3f | Ci |
| Depth | float | z |
| Normal | normal3f | N |
| Albedo | color3f | albedo |

## Set Default Prim

```python
stage.SetDefaultPrim(prim)
```

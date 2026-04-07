# Set default and save

## Key Concept

**RenderVars must be children of their RenderProduct.** The path pattern is: `/Render/ProductName/varName`

## Complete Working Example

```python
from pxr import Usd, UsdGeom, UsdRender, Gf

stage = Usd.Stage.CreateNew("render.usda")

camera = UsdGeom.Camera.Define(stage, "/Camera")
camera.GetFocalLengthAttr().Set(50.0)
camera.GetHorizontalApertureAttr().Set(36.0)

xf = UsdGeom.Xformable(camera.GetPrim())
xf.AddTranslateOp().Set(Gf.Vec3d(0, 5, 20))

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

## Essential Attributes

| Prim | Method | Value Type |
|------|--------|------------|
| Product | `CreateProductNameAttr("name.exr")` | string |
| Var | `CreateDataTypeAttr("color3f")` | string |
| Var | `CreateSourceNameAttr("Ci")` | string |
| Settings | `GetResolutionAttr().Set(Gf.Vec2i(w, h))` | Vec2i |
| Settings | `GetCameraRel().SetTargets(["/path"])` | list |
| Camera | `GetFocalLengthAttr().Set(50.0)` | float |

## Common AOVs

- Beauty: `"Ci"` with `"color3f"`
- Depth: `"z"` with `"float"`
- Normal: `"N"` with `"normal3f"`

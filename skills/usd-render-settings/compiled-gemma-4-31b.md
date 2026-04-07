# ... create prims ...

## RenderProduct (output image file)

```python
from pxr import Usd, UsdRender, Sdf, Gf

product = UsdRender.Product.Define(stage, "/Render/RenderProduct")
product.CreateProductNameAttr("beauty.exr")  # output filename
```

## RenderVar (AOV channels - must be CHILDREN of RenderProduct)

```python
beauty = UsdRender.Var.Define(stage, "/Render/RenderProduct/beauty")
beauty.CreateDataTypeAttr("color3f")   # Ci (beauty)
beauty.CreateSourceNameAttr("Ci")

depth = UsdRender.Var.Define(stage, "/Render/RenderProduct/depth")
depth.CreateDataTypeAttr("float")      # z (depth)
depth.CreateSourceNameAttr("z")
```

## RenderSettings (resolution, camera reference)

```python
settings = UsdRender.Settings.Define(stage, "/Render/RenderSettings")
settings.GetResolutionAttr().Set(Gf.Vec2i(1920, 1080))
settings.GetPixelAspectRatioAttr().Set(1.0)
settings.GetCameraRel().SetTargets(["/CameraRig/MainCamera"])
```

## Camera

```python
from pxr import UsdGeom, Gf

camera = UsdGeom.Camera.Define(stage, "/CameraRig/MainCamera")
camera.GetFocalLengthAttr().Set(50.0)
camera.GetHorizontalApertureAttr().Set(36.0)
camera.GetClippingRangeAttr().Set(Gf.Vec2f(0.1, 10000.0))
```

## Stage Save Pattern

```python
stage = Usd.Stage.CreateNew("output.usda")
stage.GetRootLayer().Save()
```

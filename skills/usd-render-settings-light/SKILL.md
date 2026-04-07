# USD Render Pipeline — Key Patterns

- **RenderProduct** is the output file: `UsdRender.Product.Define(stage, path)`, set `CreateProductNameAttr("beauty.exr")`
- **RenderVars** are AOVs — define as **children of RenderProduct**: `UsdRender.Var.Define(stage, "/Render/RenderProduct/beauty")`
  - Each var needs `CreateDataTypeAttr("color3f")` and `CreateSourceNameAttr("Ci")`
  - Common: beauty=Ci/color3f, depth=z/float, normal=N/normal3f
- **RenderSettings** holds resolution and camera reference:
  - `settings.GetResolutionAttr().Set(Gf.Vec2i(1920, 1080))`
  - `settings.GetPixelAspectRatioAttr().Set(1.0)`
  - Camera link: `settings.GetCameraRel().SetTargets(["/path/to/camera"])`
- **UsdGeom.Camera**: focalLength in mm (float), horizontalAperture in mm, clippingRange as `Gf.Vec2f(near, far)`
- Camera transforms via `UsdGeom.Xformable(camera.GetPrim())` — `AddTranslateOp().Set(Gf.Vec3d(...))`, `AddRotateXYZOp().Set(Gf.Vec3f(...))`
- Set default prim: `stage.SetDefaultPrim(prim)`
- Save: `stage.GetRootLayer().Save()`
- Multi-file reference: `stage.GetRootLayer().subLayerPaths.append("./other.usda")`

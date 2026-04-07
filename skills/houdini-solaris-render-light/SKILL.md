# Solaris USD Render Setup — Key Patterns

- **CRITICAL:** `stage = hou.pwd().editableStage()` — never `Usd.Stage.CreateNew()`
- **UsdRender.Settings:** `GetResolutionAttr().Set(Gf.Vec2i(1920, 1080))`, `GetPixelAspectRatioAttr().Set(1.0)`, camera link via `GetCameraRel().SetTargets(["/path/to/camera"])`
- **UsdRender.Product:** output file — `CreateProductNameAttr().Set("beauty_output.exr")`
- **UsdRender.Var:** AOVs as children of Product — each needs `CreateDataTypeAttr()` and `CreateSourceNameAttr()`
  - Beauty: dataType="color3f", sourceName="Ci"
  - Depth: dataType="float", sourceName="z"
  - Cryptomatte: dataType="color3f", sourceName="id"
- **UsdGeom.Camera:** `GetFocalLengthAttr().Set(35.0)`, `GetHorizontalApertureAttr().Set(36.0)`
- Camera transform: `UsdGeom.Xformable(cam.GetPrim())` then `AddTranslateOp()`, `AddRotateXYZOp()`
- **Karma settings:** custom attributes on a prim — `prim.CreateAttribute("karma:global:sampleCount", Sdf.ValueTypeNames.Int).Set(256)`
- Default prim: `stage.SetDefaultPrim(xform.GetPrim())`

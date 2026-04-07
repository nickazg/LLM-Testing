# USD Composition — Key Patterns & Gotchas

- **Sublayers** merge opinions from multiple files — stronger layers listed FIRST:
  - `stage.GetRootLayer().subLayerPaths.append("./assets.usda")`
- **References** bring a prim from another file:
  - `prim.GetReferences().AddReference("./assets.usda", "/Assets/Chair")`
- **Variant sets** for switchable options:
  - `vset = prim.GetVariantSets().AddVariantSet("modelVariant")`
  - `vset.AddVariant("simple")` then `vset.SetVariantSelection("simple")`
  - Author inside variant: `with vset.GetVariantEditContext():` — all defines/sets inside this context go into the variant
- **Transform ops:**
  - `UsdGeom.Xformable(prim).AddTranslateOp().Set(Gf.Vec3d(x, y, z))`
  - `AddRotateXYZOp().Set(Gf.Vec3f(rx, ry, rz))`
- **Set default prim:** `stage.SetDefaultPrim(prim)` — required for referencing
- **Save:** `stage.GetRootLayer().Save()`
- **Mesh cube:** 8 points, 6 quad faces (faceVertexCounts=[4,4,4,4,4,4])
- **Lighting:** `UsdLux.DistantLight.Define(stage, path)` with `.CreateIntensityAttr(val)`, `UsdLux.DomeLight.Define(stage, path)`

# Solaris USD Light Linking — Key Patterns

- **CRITICAL:** `stage = hou.pwd().editableStage()` — never `Usd.Stage.CreateNew()`
- **DistantLight:** `UsdLux.DistantLight.Define(stage, path)` — `GetIntensityAttr().Set(50000)`, `GetAngleAttr().Set(1.0)`
- **DomeLight:** `UsdLux.DomeLight.Define(stage, path)` — for environment lighting
- Light transforms: `UsdGeom.Xformable(light.GetPrim())` then `AddRotateXYZOp().Set(Gf.Vec3f(...))`
- **Light linking:** `Usd.CollectionAPI.Apply(light_prim, "lightLink")` then:
  - `GetIncludesRel().AddTarget("/Scene/Hero")` — light illuminates this geo
  - `GetExcludesRel().AddTarget("/Scene/Environment")` — light skips this geo
  - Each light gets its own `"lightLink"` collection for selective illumination
- **Light filters:** child prims of light — `stage.DefinePrim(light_path + "/BarnDoor")`, add custom float attributes
- **Purpose:** `UsdGeom.Imageable(prim).GetPurposeAttr().Set(UsdGeom.Tokens.render)` — also `proxy`, `guide`
- Default prim: `stage.SetDefaultPrim(xform.GetPrim())`

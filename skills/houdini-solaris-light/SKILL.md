# Houdini Solaris Python Script LOP — Key Patterns & Gotchas

- **CRITICAL:** `stage = hou.pwd().editableStage()`, NOT `Usd.Stage.CreateNew()` — this is the LOP network stage
- **Geometry:** Use `UsdGeom.Xform.Define(stage, path)` for transforms, `UsdGeom.Mesh.Define(stage, path)` for geo
- **Lighting:** `UsdLux.DistantLight.Define(stage, path)` for directional, `UsdLux.DomeLight.Define(stage, path)` for environment
  - `.CreateIntensityAttr(value)` for light intensity
- **Transforms:** `UsdGeom.Xformable(prim).AddTranslateOp().Set(Gf.Vec3d(x,y,z))`
  - Rotation: `.AddRotateXYZOp().Set(Gf.Vec3f(rx, ry, rz))`
- **Material binding:**
  - Define: `mat = UsdShade.Material.Define(stage, path)`
  - Shader: `shader.CreateIdAttr("UsdPreviewSurface")`
  - Inputs: `shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set((r,g,b))`
  - Connect: `mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")`
  - Bind: `UsdShade.MaterialBindingAPI.Apply(prim)` then `UsdShade.MaterialBindingAPI(prim).Bind(mat)`
- **Kind:** `Usd.ModelAPI(prim).SetKind(Kind.Tokens.component)` — marks asset type in hierarchy
- **Default prim:** `stage.SetDefaultPrim(prim)` — important for references
- **DO NOT save/export** — the LOP network handles stage output

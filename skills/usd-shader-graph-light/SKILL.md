# USD Shader Network — Key Patterns

- **Shader IDs:** `UsdPreviewSurface`, `UsdUVTexture`, `UsdPrimvarReader_float2`
  - Set via `shader.CreateIdAttr("UsdPreviewSurface")`
- **Wire outputs to inputs:** `input.ConnectToSource(shader.ConnectableAPI(), "outputName")`
  - Texture rgb → Surface diffuseColor: `surface.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(tex.ConnectableAPI(), "rgb")`
  - UV result → Texture st: `tex.CreateInput("st", Sdf.ValueTypeNames.Float2).ConnectToSource(uv_reader.ConnectableAPI(), "result")`
- **Create inputs with specific types:** `shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.7)`
  - Key types: `Color3f`, `Float`, `Float2`, `Float3`, `Asset`, `Token`
- **Texture shader:** needs `file` (Asset), `st` (Float2 input), outputs `rgb` (Float3) and `a` (Float)
- **UV reader:** `CreateIdAttr("UsdPrimvarReader_float2")`, input `varname`="st", output `result` (Float2)
- **Connect shader to material:** `mat.CreateSurfaceOutput().ConnectToSource(surface.ConnectableAPI(), "surface")`
- **UsdGeom.Subset** for per-face material assignment:
  - `UsdGeom.Subset.Define(stage, "/Mesh/subset_name")`
  - Set `elementType`="face", `indices`=[face_indices], `familyName`="materialBind"
  - Bind material to subset prim with `MaterialBindingAPI`
- **Material binding:** `UsdShade.MaterialBindingAPI.Apply(prim)` then `.Bind(mat)`

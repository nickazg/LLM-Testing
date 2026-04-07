# USD Custom Metadata & Extensibility — Key Patterns

- **Custom metadata:** `prim.SetCustomDataByKey("pipeline:version", "2.1")` — stores arbitrary key-value pairs on any prim
- **Asset info:** `Usd.ModelAPI(prim).SetAssetInfo({"name": "hero_asset", "identifier": Sdf.AssetPath("path/to/file.usd")})` — standard asset identification
- **Purpose tokens** for visibility classification:
  - `UsdGeom.Imageable(prim).GetPurposeAttr().Set(UsdGeom.Tokens.render)` — full render geo
  - `UsdGeom.Tokens.proxy` — lightweight viewport proxy
  - `UsdGeom.Tokens.guide` — guide geometry (not rendered)
- **Kind classification:** `Usd.ModelAPI(prim).SetKind(Kind.Tokens.component)` — marks prim role in hierarchy
  - Available: `Kind.Tokens.component`, `Kind.Tokens.assembly`, `Kind.Tokens.group`
- **Custom attributes:** `prim.CreateAttribute("custom:shotName", Sdf.ValueTypeNames.String).Set("SH010")`
  - Use namespace prefix (`custom:`) for organization
  - `Sdf.ValueTypeNames.Int2` for int pairs: `.Set(Gf.Vec2i(1001, 1100))`
  - Other types: `String`, `Float`, `Bool`, `Color3f`, `Asset`, `Token`
- **ModelAPI** is implicit — no `.Apply()` needed, just `Usd.ModelAPI(prim)`
- Set default prim: `stage.SetDefaultPrim(prim)`
- Save: `stage.GetRootLayer().Save()`

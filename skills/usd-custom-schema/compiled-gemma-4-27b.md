# Read

## Custom Data — Arbitrary Key-Value Metadata

```python
prim.SetCustomDataByKey("pipeline:version", "2.1")
prim.SetCustomDataByKey("pipeline:department", "lighting")

all_data = prim.GetCustomData()                     # dict
value = prim.GetCustomDataByKey("pipeline:version") # single value
```

## Asset Info — Standard Asset Metadata

```python
model = Usd.ModelAPI(prim)

model.SetAssetInfo({
    "name": "hero_asset",
    "identifier": Sdf.AssetPath("assets/hero/v003/hero.usd"),
    "version": "003",
})

info = model.GetAssetInfo()             # dict
name = model.GetAssetInfoByKey("name")  # single value
```

## Purpose — Visibility Classification

```python
img = UsdGeom.Imageable(prim)
img.GetPurposeAttr().Set(UsdGeom.Tokens.render)  # or: proxy, guide, default_
```

## Kind — Model Hierarchy Classification

```python
model = Usd.ModelAPI(prim)
model.SetKind(Kind.Tokens.component)  # or: assembly, group, subcomponent
```

## Custom Attributes

```python
prim.CreateAttribute("custom:shotName", Sdf.ValueTypeNames.String).Set("SH010")
prim.CreateAttribute("custom:frameRange", Sdf.ValueTypeNames.Int2).Set(Gf.Vec2i(1001, 1100))
prim.CreateAttribute("custom:renderScale", Sdf.ValueTypeNames.Float).Set(1.0)
prim.CreateAttribute("custom:approved", Sdf.ValueTypeNames.Bool).Set(False)
```

**Common Types:** `String`, `Int`, `Int2` (Gf.Vec2i), `Float`, `Bool`, `Color3f` (Gf.Vec3f), `Asset` (Sdf.AssetPath)

## Notes

- `Usd.ModelAPI(prim)` — no Apply() needed
- Save stage: `stage.GetRootLayer().Save()`
- Set default prim: `stage.SetDefaultPrim(prim)`

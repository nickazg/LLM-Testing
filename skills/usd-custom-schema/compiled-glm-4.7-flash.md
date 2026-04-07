# USD Metadata Quick Reference

## Custom Data

```python
prim.SetCustomDataByKey("pipeline:version", "2.1")
prim.SetCustomDataByKey("pipeline:department", "lighting")

value = prim.GetCustomDataByKey("pipeline:version")
all_data = prim.GetCustomData()  # returns dict
```

## Asset Info

```python
model = Usd.ModelAPI(prim)
model.SetAssetInfoByKey("name", "hero_asset")
model.SetAssetInfoByKey("identifier", Sdf.AssetPath("assets/hero.usd"))
model.SetAssetInfoByKey("version", "003")

name = model.GetAssetInfoByKey("name")
info = model.GetAssetInfo()  # returns dict
```

## Purpose

```python
img = UsdGeom.Imageable(prim)
img.GetPurposeAttr().Set(UsdGeom.Tokens.render)  # proxy, guide, default_
```

## Kind

```python
Usd.ModelAPI(prim).SetKind(Kind.Tokens.component)  # assembly, group, subcomponent
```

## Custom Attributes

```python
prim.CreateAttribute("custom:shotName", Sdf.ValueTypeNames.String).Set("SH010")
prim.CreateAttribute("custom:frameRange", Sdf.ValueTypeNames.Int2).Set(Gf.Vec2i(1001, 1100))
prim.CreateAttribute("custom:approved", Sdf.ValueTypeNames.Bool).Set(False)
prim.CreateAttribute("custom:file", Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath("path/to/file"))
```

## Stage Operations

```python
stage.SetDefaultPrim(prim)
stage.GetRootLayer().Save()
```

# Tokens: UsdGeom.Tokens.render, proxy, guide, default_

## Imports

```python
from pxr import Usd, UsdGeom, Sdf, Gf, Kind
```

## Custom Data - Arbitrary Key-Value Metadata

```python
stage = Usd.Stage.CreateNew("pipeline.usda")
prim = UsdGeom.Xform.Define(stage, "/Project").GetPrim()

prim.SetCustomDataByKey("pipeline:version", "2.1")
prim.SetCustomDataByKey("pipeline:department", "lighting")

all_data = prim.GetCustomData()              # returns dict
value = prim.GetCustomDataByKey("pipeline:version")
```

## Asset Info - Standard Asset Metadata

```python
from pxr import Usd, Sdf

model = Usd.ModelAPI(prim)

model.SetAssetInfoByKey("name", "hero_asset")
model.SetAssetInfoByKey("identifier", Sdf.AssetPath("assets/hero.usd"))
model.SetAssetInfoByKey("version", "003")

info = model.GetAssetInfo()              # returns dict
name = model.GetAssetInfoByKey("name")
```

## Custom Attributes - Typed Properties

```python
prim.CreateAttribute("custom:shotName", Sdf.ValueTypeNames.String).Set("SH010")
prim.CreateAttribute("custom:frameRange", Sdf.ValueTypeNames.Int2).Set(Gf.Vec2i(1001, 1100))
prim.CreateAttribute("custom:renderScale", Sdf.ValueTypeNames.Float).Set(1.0)
prim.CreateAttribute("custom:approved", Sdf.ValueTypeNames.Bool).Set(False)

value = prim.GetAttribute("custom:shotName").Get()
```

## Kind - Model Hierarchy

```python
Usd.ModelAPI(prim).SetKind(Kind.Tokens.component)
```

## Purpose - Visibility Classification

```python
UsdGeom.Imageable(prim).GetPurposeAttr().Set(UsdGeom.Tokens.render)
```

## Save Stage

```python
stage.GetRootLayer().Save()
```

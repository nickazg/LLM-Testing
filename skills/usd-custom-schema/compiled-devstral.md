# Set default prim

## Custom Data (Arbitrary Key-Value)

```python
from pxr import Usd, UsdGeom, Sdf, Gf, Kind

prim.SetCustomDataByKey("pipeline:version", "2.1")
prim.SetCustomDataByKey("pipeline:department", "lighting")

all_data = prim.GetCustomData()
value = prim.GetCustomDataByKey("pipeline:version")
```

## Asset Info (Standard Asset Metadata)

```python
from pxr import Usd, Sdf

model = Usd.ModelAPI(prim)
model.SetAssetInfoByKey("name", "hero_asset")
model.SetAssetInfoByKey("identifier", Sdf.AssetPath("assets/hero.usd"))
model.SetAssetInfoByKey("version", "003")

info = model.GetAssetInfo()
name = model.GetAssetInfoByKey("name")
```

## Purpose (Visibility Classification)

```python
from pxr import UsdGeom

img = UsdGeom.Imageable(prim)
img.GetPurposeAttr().Set(UsdGeom.Tokens.render)  # or: proxy, guide, default_
```

## Kind (Model Hierarchy)

```python
from pxr import Usd, Kind

Usd.ModelAPI(prim).SetKind(Kind.Tokens.component)  # or: assembly, group, subcomponent
```

## Custom Attributes

```python
from pxr import Sdf, Gf

prim.CreateAttribute("custom:shotName", Sdf.ValueTypeNames.String).Set("SH010")
prim.CreateAttribute("custom:frameRange", Sdf.ValueTypeNames.Int2).Set(Gf.Vec2i(1001, 1100))
prim.CreateAttribute("custom:approved", Sdf.ValueTypeNames.Bool).Set(False)
prim.CreateAttribute("custom:file", Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath("path/to/file"))
```

## Common Patterns

```python
model = Usd.ModelAPI(prim)

stage.GetRootLayer().Save()

stage.SetDefaultPrim(prim)
```

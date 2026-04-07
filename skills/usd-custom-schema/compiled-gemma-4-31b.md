# Read asset info

## Custom Data — Arbitrary Key-Value Metadata

```python
from pxr import Usd, UsdGeom, Sdf, Gf, Kind

prim.SetCustomDataByKey("pipeline:version", "2.1")
prim.SetCustomDataByKey("pipeline:department", "lighting")

all_data = prim.GetCustomData()                     # dict of all custom data
value = prim.GetCustomDataByKey("pipeline:version") # single value
```

## Asset Info — Standard Asset Metadata

```python
from pxr import Usd, Sdf

model = Usd.ModelAPI(prim)
model.SetAssetInfoByKey("name", "hero_asset")
model.SetAssetInfoByKey("identifier", Sdf.AssetPath("assets/hero.usd"))
model.SetAssetInfoByKey("version", "003")

name = prim.GetAssetInfoByKey("name")
info_dict = prim.GetAssetInfo()
```

## Purpose — Render Visibility Classification

```python
from pxr import UsdGeom

img = UsdGeom.Imageable(prim)
img.GetPurposeAttr().Set(UsdGeom.Tokens.render)   # options: render, proxy, guide, default_
```

## Kind — Model Hierarchy Classification

```python
from pxr import Kind

model = Usd.ModelAPI(prim)
model.SetKind(Kind.Tokens.component)  # options: component, assembly, group, subcomponent
```

## Custom Attributes — Typed Properties

```python
prim.CreateAttribute("custom:shotName", Sdf.ValueTypeNames.String).Set("SH010")
prim.CreateAttribute("custom:frameRange", Sdf.ValueTypeNames.Int2).Set(Gf.Vec2i(1001, 1100))
prim.CreateAttribute("custom:approved", Sdf.ValueTypeNames.Bool).Set(False)
prim.CreateAttribute("custom:color", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(1, 0, 0))
prim.CreateAttribute("custom:asset", Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath("path/to/file"))
```

## Notes

- `Usd.ModelAPI(prim)` wraps any prim for asset info / kind operations
- Save: `stage.GetRootLayer().Save()`
- Set default prim: `stage.SetDefaultPrim(prim)`

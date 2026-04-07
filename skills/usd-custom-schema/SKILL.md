# USD Custom Metadata & Extensibility API Reference

## Custom Data — Arbitrary Key-Value Metadata

`SetCustomDataByKey` stores arbitrary metadata on any prim. Keys can use namespace prefixes.

```python
from pxr import Usd, UsdGeom, Sdf, Gf, Kind

stage = Usd.Stage.CreateNew("pipeline.usda")
project = UsdGeom.Xform.Define(stage, "/Project")
stage.SetDefaultPrim(project.GetPrim())

# Set arbitrary metadata
project.GetPrim().SetCustomDataByKey("pipeline:version", "2.1")
project.GetPrim().SetCustomDataByKey("pipeline:department", "lighting")
```

### Reading Custom Data
```python
custom_data = prim.GetCustomData()     # returns dict of all custom data
value = prim.GetCustomDataByKey("pipeline:version")
```

## Asset Info — Standard Asset Metadata

USD has built-in support for asset identification via `assetInfo`.

```python
from pxr import Usd, Sdf

model = Usd.ModelAPI(project.GetPrim())

# Set asset info (standard keys: name, identifier, version, payloadAssetDependencies)
model.SetAssetInfo({
    "name": "hero_asset",
    "identifier": Sdf.AssetPath("assets/hero/v003/hero.usd"),
    "version": "003",
})
```

### Alternative: SetAssetInfoByKey
```python
model.SetAssetInfoByKey("name", "hero_asset")
model.SetAssetInfoByKey("identifier", Sdf.AssetPath("assets/hero/v003/hero.usd"))
```

### Reading Asset Info
```python
info = prim.GetAssetInfo()         # returns dict
name = prim.GetAssetInfoByKey("name")
```

## UsdGeom Purpose — Visibility Classification

Purpose controls which geometry is visible in different rendering contexts.

```python
from pxr import UsdGeom

# Define prims
hero = UsdGeom.Xform.Define(stage, "/Project/Hero")
proxy = UsdGeom.Xform.Define(stage, "/Project/Hero/Proxy")
guide = UsdGeom.Xform.Define(stage, "/Project/Hero/Guide")

# Set purpose using tokens
UsdGeom.Imageable(hero.GetPrim()).GetPurposeAttr().Set(UsdGeom.Tokens.render)
UsdGeom.Imageable(proxy.GetPrim()).GetPurposeAttr().Set(UsdGeom.Tokens.proxy)
UsdGeom.Imageable(guide.GetPrim()).GetPurposeAttr().Set(UsdGeom.Tokens.guide)
```

### Purpose Tokens
| Token | Meaning |
|-------|---------|
| `UsdGeom.Tokens.render` | Full-quality render geometry |
| `UsdGeom.Tokens.proxy` | Lightweight viewport proxy |
| `UsdGeom.Tokens.guide` | Guide geometry (not rendered) |
| `UsdGeom.Tokens.default_` | Inherit purpose from parent |

## Kind — Model Hierarchy Classification

Kind classifies prims in the scene hierarchy for efficient traversal.

```python
from pxr import Usd, Kind

# Set kind on a prim
model = Usd.ModelAPI(hero.GetPrim())
model.SetKind(Kind.Tokens.component)
```

### Kind Tokens
| Token | Meaning |
|-------|---------|
| `Kind.Tokens.component` | Leaf-level publishable asset |
| `Kind.Tokens.assembly` | Group of components |
| `Kind.Tokens.group` | Organizational grouping |
| `Kind.Tokens.subcomponent` | Sub-part, not independently publishable |
| `Kind.Tokens.model` | Base class (rarely used directly) |

## Custom Attributes — Adding Properties to Prims

Create typed attributes with namespace prefixes for organization.

```python
from pxr import Sdf

prim = hero.GetPrim()

# String attribute
prim.CreateAttribute("custom:shotName", Sdf.ValueTypeNames.String).Set("SH010")

# Int2 attribute (pair of ints)
prim.CreateAttribute("custom:frameRange", Sdf.ValueTypeNames.Int2).Set(Gf.Vec2i(1001, 1100))

# Float attribute
prim.CreateAttribute("custom:renderScale", Sdf.ValueTypeNames.Float).Set(1.0)

# Bool attribute
prim.CreateAttribute("custom:approved", Sdf.ValueTypeNames.Bool).Set(False)
```

### Common Sdf.ValueTypeNames for Custom Attributes
| Type | Python Value |
|------|-------------|
| `String` | `"text"` |
| `Int` | `42` |
| `Int2` | `Gf.Vec2i(1001, 1100)` |
| `Float` | `1.0` |
| `Double` | `1.0` |
| `Bool` | `True` / `False` |
| `Color3f` | `Gf.Vec3f(1, 0, 0)` |
| `Asset` | `Sdf.AssetPath("path/to/file")` |
| `Token` | `"tokenValue"` |

## Notes

- **ModelAPI** is implicit -- no `.Apply()` needed, just `Usd.ModelAPI(prim)`
- **MaterialBindingAPI** requires `.Apply(prim)` before binding
- Save stage: `stage.GetRootLayer().Save()`
- Set default prim: `stage.SetDefaultPrim(prim)`

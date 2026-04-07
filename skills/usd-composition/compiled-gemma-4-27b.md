# USD Composition Reference

## Sublayers

Merge multiple USD files. Stronger opinions come from layers listed first.

```python
from pxr import Usd

stage = Usd.Stage.CreateNew("shot.usda")
stage.GetRootLayer().subLayerPaths.append("./assets.usda")
```

## References

Bring a prim subtree from another file into your scene.

```python
stage = Usd.Stage.CreateNew("shot.usda")
chair = stage.DefinePrim("/Shot/Chair", "Xform")
chair.GetReferences().AddReference("./assets.usda", "/Assets/Chair")
```

## Default Prim

Set a default prim so others can reference your file without specifying a path.

```python
stage.SetDefaultPrim(stage.GetPrimAtPath("/Assets"))
```

## Variant Sets

Create switchable variations on a prim.

```python
prim = stage.DefinePrim("/Asset", "Xform")
vset = prim.GetVariantSets().AddVariantSet("version")
vset.AddVariant("low")
vset.AddVariant("high")

vset.SetVariantSelection("low")
with vset.GetVariantEditContext():
    stage.DefinePrim("/Asset/Geo", "Xform")
```

## Save Stage

```python
stage.GetRootLayer().Save()
```

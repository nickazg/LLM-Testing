# USD Layer Opinion System API Reference

## Sdf.Layer — Individual Layer Files

Each `.usda` file is a layer. Layers hold raw opinions before composition.

```python
from pxr import Usd, Sdf, UsdGeom, Gf

# Create individual layers as separate stages
base_stage = Usd.Stage.CreateNew("base_layer.usda")
```

## Layer Stack — Sublayer Composition

Sublayers merge opinions from multiple files. **Stronger layers are listed FIRST** in `subLayerPaths`.

```python
# Create the composed stage
stage = Usd.Stage.CreateInMemory()
root_layer = stage.GetRootLayer()

# Order matters: first = strongest, last = weakest
root_layer.subLayerPaths.append("./look_layer.usda")   # strongest
root_layer.subLayerPaths.append("./anim_layer.usda")   # middle
root_layer.subLayerPaths.append("./base_layer.usda")   # weakest
```

**Key rule:** When multiple layers define the same attribute, the strongest layer's opinion wins. For time samples, if a stronger layer has time samples for an attribute that has a static value in a weaker layer, the time samples win.

## Authoring in Individual Layers

### Base Layer — Static Scene Definition

```python
base_stage = Usd.Stage.CreateNew("base_layer.usda")
scene = UsdGeom.Xform.Define(base_stage, "/Scene")
base_stage.SetDefaultPrim(scene.GetPrim())

# Character with static transform
char = UsdGeom.Xform.Define(base_stage, "/Scene/Character")
UsdGeom.Xformable(char.GetPrim()).AddTranslateOp().Set(Gf.Vec3d(0, 0, 0))

# Geometry
body = UsdGeom.Mesh.Define(base_stage, "/Scene/Character/Body")
body.CreatePointsAttr([
    (-0.5,-0.5,-0.5), (0.5,-0.5,-0.5), (0.5,0.5,-0.5), (-0.5,0.5,-0.5),
    (-0.5,-0.5,0.5),  (0.5,-0.5,0.5),  (0.5,0.5,0.5),  (-0.5,0.5,0.5),
])
body.CreateFaceVertexCountsAttr([4, 4, 4, 4, 4, 4])
body.CreateFaceVertexIndicesAttr([0,1,2,3, 4,5,6,7, 0,1,5,4, 2,3,7,6, 0,3,7,4, 1,2,6,5])
body.CreateSubdivisionSchemeAttr("none")

base_stage.GetRootLayer().Save()
```

### Animation Layer — Time-Sampled Overrides

```python
anim_stage = Usd.Stage.CreateNew("anim_layer.usda")

# Override the Character's transform with time samples
char = UsdGeom.Xform.Define(anim_stage, "/Scene/Character")
xformable = UsdGeom.Xformable(char.GetPrim())
translate_op = xformable.AddTranslateOp()

# Time-sampled values override the static value from base_layer
translate_op.Set(Gf.Vec3d(0, 0, 0), 1)      # frame 1
translate_op.Set(Gf.Vec3d(5, 0, 0), 24)     # frame 24

anim_stage.GetRootLayer().Save()
```

### Look/Material Layer — Additional Opinions

```python
from pxr import UsdShade

look_stage = Usd.Stage.CreateNew("look_layer.usda")

# Add material
mat = UsdShade.Material.Define(look_stage, "/Scene/Looks/HeroMat")
shader = UsdShade.Shader.Define(look_stage, "/Scene/Looks/HeroMat/Surface")
shader.CreateIdAttr("UsdPreviewSurface")
shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set((0.9, 0.1, 0.1))
mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")

# Bind material to existing mesh
body = look_stage.DefinePrim("/Scene/Character/Body")
UsdShade.MaterialBindingAPI.Apply(body)
UsdShade.MaterialBindingAPI(body).Bind(mat)

look_stage.GetRootLayer().Save()
```

## Querying Composed Results

```python
# Open with all sublayers composed
composed = Usd.Stage.Open("shot.usda")

# GetAttribute on a composed prim resolves all layer opinions
char = composed.GetPrimAtPath("/Scene/Character")
xf = UsdGeom.Xformable(char)
ops = xf.GetOrderedXformOps()

# Read time-sampled value at specific frame
for op in ops:
    val = op.Get(12)  # value at frame 12
    print(f"Translate at frame 12: {val}")
```

### SdfChangeBlock — Batched Edits

For performance when making many edits to a layer:

```python
from pxr import Sdf

with Sdf.ChangeBlock():
    # All edits within this block are batched
    prim.GetAttribute("xformOp:translate").Set(Gf.Vec3d(1, 2, 3))
    # ... more edits ...
# Notification sent once when block exits
```

## GetAttributeAtPath (Sdf) vs GetAttribute (Usd)

- `Sdf.Layer.Find(path).GetAttributeAtPath(sdf_path)` — reads raw opinion from one layer only
- `prim.GetAttribute("name")` — reads composed result across all layers

```python
# Raw layer opinion (uncomposed)
layer = Sdf.Layer.FindOrOpen("anim_layer.usda")
attr_spec = layer.GetAttributeAtPath("/Scene/Character.xformOp:translate")
if attr_spec:
    print("Raw opinion exists in this layer")

# Composed opinion (all layers resolved)
stage = Usd.Stage.Open("shot.usda")
prim = stage.GetPrimAtPath("/Scene/Character")
attr = prim.GetAttribute("xformOp:translate")
print(f"Composed value: {attr.Get()}")
```

## Default Prim

```python
stage.SetDefaultPrim(stage.GetPrimAtPath("/Scene"))
```

## Save Pattern

```python
stage.GetRootLayer().Save()
```

# USD Shader Network API Reference

## UsdShade.Material — Material Container

A Material groups shaders and exposes surface/displacement outputs.

```python
from pxr import Usd, UsdShade, UsdGeom, Sdf, Gf

stage = Usd.Stage.CreateNew("materials.usda")
mat = UsdShade.Material.Define(stage, "/Materials/WoodMat")
```

## UsdShade.Shader — Shader Node

Each shader has an `id` attribute that identifies the shader type.

```python
# UsdPreviewSurface — the standard PBR shader
surface = UsdShade.Shader.Define(stage, "/Materials/WoodMat/Surface")
surface.CreateIdAttr("UsdPreviewSurface")

# Set scalar inputs
surface.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.7)
surface.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)

# Connect shader output to material surface
mat.CreateSurfaceOutput().ConnectToSource(surface.ConnectableAPI(), "surface")
```

### Standard Shader IDs
| Shader ID | Purpose |
|-----------|---------|
| `UsdPreviewSurface` | PBR surface shader |
| `UsdUVTexture` | Texture map reader |
| `UsdPrimvarReader_float2` | UV coordinate reader |
| `UsdPrimvarReader_float` | Float primvar reader |
| `UsdPrimvarReader_float3` | Vector primvar reader |

## Connecting Shaders — The ConnectToSource Pattern

Wire outputs to inputs using `ConnectToSource(shader.ConnectableAPI(), "outputName")`.

```python
# Create a texture shader
texture = UsdShade.Shader.Define(stage, "/Materials/WoodMat/WoodTex")
texture.CreateIdAttr("UsdUVTexture")
texture.CreateInput("file", Sdf.ValueTypeNames.Asset).Set("wood_diffuse.png")
texture.CreateInput("wrapS", Sdf.ValueTypeNames.Token).Set("repeat")
texture.CreateInput("wrapT", Sdf.ValueTypeNames.Token).Set("repeat")
texture.CreateOutput("rgb", Sdf.ValueTypeNames.Float3)
texture.CreateOutput("a", Sdf.ValueTypeNames.Float)

# Connect texture rgb output → surface diffuseColor input
surface.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(
    texture.ConnectableAPI(), "rgb"
)
```

## UsdPrimvarReader_float2 — UV Reader

Reads UV coordinates from mesh primvars and passes them to texture nodes.

```python
uv_reader = UsdShade.Shader.Define(stage, "/Materials/WoodMat/UVReader")
uv_reader.CreateIdAttr("UsdPrimvarReader_float2")
uv_reader.CreateInput("varname", Sdf.ValueTypeNames.Token).Set("st")
uv_reader.CreateOutput("result", Sdf.ValueTypeNames.Float2)

# Connect UV reader result → texture st input
texture.CreateInput("st", Sdf.ValueTypeNames.Float2).ConnectToSource(
    uv_reader.ConnectableAPI(), "result"
)
```

## Complete Texture-Connected Material

```python
# Material
mat = UsdShade.Material.Define(stage, "/Materials/WoodMat")

# Surface shader
surface = UsdShade.Shader.Define(stage, "/Materials/WoodMat/Surface")
surface.CreateIdAttr("UsdPreviewSurface")
surface.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.7)
surface.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
mat.CreateSurfaceOutput().ConnectToSource(surface.ConnectableAPI(), "surface")

# Texture
tex = UsdShade.Shader.Define(stage, "/Materials/WoodMat/WoodTex")
tex.CreateIdAttr("UsdUVTexture")
tex.CreateInput("file", Sdf.ValueTypeNames.Asset).Set("wood_diffuse.png")
tex.CreateOutput("rgb", Sdf.ValueTypeNames.Float3)

# UV reader
uv = UsdShade.Shader.Define(stage, "/Materials/WoodMat/UVReader")
uv.CreateIdAttr("UsdPrimvarReader_float2")
uv.CreateInput("varname", Sdf.ValueTypeNames.Token).Set("st")
uv.CreateOutput("result", Sdf.ValueTypeNames.Float2)

# Wire: UV → Texture → Surface
tex.CreateInput("st", Sdf.ValueTypeNames.Float2).ConnectToSource(uv.ConnectableAPI(), "result")
surface.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(tex.ConnectableAPI(), "rgb")
```

## Simple Material (No Texture)

```python
metal_mat = UsdShade.Material.Define(stage, "/Materials/MetalMat")
metal_surface = UsdShade.Shader.Define(stage, "/Materials/MetalMat/Surface")
metal_surface.CreateIdAttr("UsdPreviewSurface")
metal_surface.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set((0.8, 0.8, 0.85))
metal_surface.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.2)
metal_surface.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(1.0)
metal_mat.CreateSurfaceOutput().ConnectToSource(metal_surface.ConnectableAPI(), "surface")
```

## UsdGeom.Subset — Per-Face Material Assignment

GeomSubsets allow binding different materials to different faces of a mesh.

```python
# Create mesh
table = UsdGeom.Mesh.Define(stage, "/Geometry/Table")
table.CreatePointsAttr([(-1,0,-1),(1,0,-1),(1,0,1),(-1,0,1)])
table.CreateFaceVertexCountsAttr([4])
table.CreateFaceVertexIndicesAttr([0,1,2,3])

# Bind overall material to the mesh
UsdShade.MaterialBindingAPI.Apply(table.GetPrim())
UsdShade.MaterialBindingAPI(table.GetPrim()).Bind(metal_mat)

# Create a subset for specific faces
subset = UsdGeom.Subset.Define(stage, "/Geometry/Table/top_face")
subset.CreateElementTypeAttr("face")
subset.CreateIndicesAttr([0])  # face indices that use this material
subset.CreateFamilyNameAttr("materialBind")

# Bind material to the subset (overrides the mesh-level binding for these faces)
UsdShade.MaterialBindingAPI.Apply(subset.GetPrim())
UsdShade.MaterialBindingAPI(subset.GetPrim()).Bind(wood_mat)
```

## Sdf.ValueTypeNames Reference

| Type | Use |
|------|-----|
| `Color3f` | RGB color (diffuseColor, etc.) |
| `Float` | Scalar (roughness, metallic) |
| `Float2` | UV coordinates |
| `Float3` | Generic 3-vector |
| `Asset` | File path (texture file) |
| `Token` | Enum/string token (varname, wrap mode) |

## Stage Save
```python
stage.GetRootLayer().Save()
```

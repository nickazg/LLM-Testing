# Wire: UV → Texture → Surface

## Imports & Setup

```python
from pxr import Usd, UsdShade, UsdGeom, Sdf
stage = Usd.Stage.CreateNew("materials.usda")
```

## Pattern 1: Textured Material (Complete)

```python
mat = UsdShade.Material.Define(stage, "/Materials/WoodMat")

surface = UsdShade.Shader.Define(stage, "/Materials/WoodMat/Surface")
surface.CreateIdAttr("UsdPreviewSurface")
surface.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.7)
surface.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
mat.CreateSurfaceOutput().ConnectToSource(surface.ConnectableAPI(), "surface")

tex = UsdShade.Shader.Define(stage, "/Materials/WoodMat/WoodTex")
tex.CreateIdAttr("UsdUVTexture")
tex.CreateInput("file", Sdf.ValueTypeNames.Asset).Set("wood_diffuse.png")
tex.CreateOutput("rgb", Sdf.ValueTypeNames.Float3)

uv = UsdShade.Shader.Define(stage, "/Materials/WoodMat/UVReader")
uv.CreateIdAttr("UsdPrimvarReader_float2")
uv.CreateInput("varname", Sdf.ValueTypeNames.Token).Set("st")
uv.CreateOutput("result", Sdf.ValueTypeNames.Float2)

tex.CreateInput("st", Sdf.ValueTypeNames.Float2).ConnectToSource(uv.ConnectableAPI(), "result")
surface.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(tex.ConnectableAPI(), "rgb")
```

## Pattern 2: Simple Material (No Texture)

```python
mat = UsdShade.Material.Define(stage, "/Materials/MetalMat")
surface = UsdShade.Shader.Define(stage, "/Materials/MetalMat/Surface")
surface.CreateIdAttr("UsdPreviewSurface")
surface.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set((0.8, 0.8, 0.85))
surface.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.2)
surface.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(1.0)
mat.CreateSurfaceOutput().ConnectToSource(surface.ConnectableAPI(), "surface")
```

## Bind Material to Geometry

```python
mesh = UsdGeom.Mesh.Define(stage, "/Geometry/MyMesh")
UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim())
UsdShade.MaterialBindingAPI(mesh.GetPrim()).Bind(mat)
```

## Key APIs

| Shader ID | Purpose |
|-----------|---------|
| `UsdPreviewSurface` | PBR surface shader |
| `UsdUVTexture` | Texture reader |
| `UsdPrimvarReader_float2` | UV coordinates |

| Sdf.ValueTypeNames | Use For |
|--------------------|---------|
| `Color3f` | RGB colors |
| `Float` | Scalars (roughness, metallic) |
| `Float2` | UV coordinates |
| `Asset` | File paths |
| `Token` | String enums |

## Save

```python
stage.GetRootLayer().Save()
```

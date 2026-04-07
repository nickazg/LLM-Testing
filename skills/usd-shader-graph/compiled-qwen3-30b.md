# Chain: UV → Texture → Surface

## Complete Working Example

```python
from pxr import Usd, UsdShade, UsdGeom, Sdf

stage = Usd.Stage.CreateNew("materials.usda")

mat = UsdShade.Material.Define(stage, "/Materials/MyMat")

surface = UsdShade.Shader.Define(stage, "/Materials/MyMat/Surface")
surface.CreateIdAttr("UsdPreviewSurface")
surface.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set((0.8, 0.2, 0.2))
surface.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.5)
surface.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)

mat.CreateSurfaceOutput().ConnectToSource(surface.ConnectableAPI(), "surface")
```

## Adding a Texture

```python
uv = UsdShade.Shader.Define(stage, "/Materials/MyMat/UV")
uv.CreateIdAttr("UsdPrimvarReader_float2")
uv.CreateInput("varname", Sdf.ValueTypeNames.Token).Set("st")
uv.CreateOutput("result", Sdf.ValueTypeNames.Float2)

tex = UsdShade.Shader.Define(stage, "/Materials/MyMat/Tex")
tex.CreateIdAttr("UsdUVTexture")
tex.CreateInput("file", Sdf.ValueTypeNames.Asset).Set("texture.png")
tex.CreateOutput("rgb", Sdf.ValueTypeNames.Float3)

tex.CreateInput("st", Sdf.ValueTypeNames.Float2).ConnectToSource(uv.ConnectableAPI(), "result")
surface.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(tex.ConnectableAPI(), "rgb")
```

## Bind Material to Geometry

```python
mesh = UsdGeom.Mesh.Define(stage, "/Geometry/MyMesh")
UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(mat)
```

## Essential Shader IDs

| ID | Use |
|----|-----|
| `UsdPreviewSurface` | Surface shader (required) |
| `UsdUVTexture` | Texture reader |
| `UsdPrimvarReader_float2` | UV coordinates |

## Save

```python
stage.GetRootLayer().Save()
```

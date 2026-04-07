# Syntax: input.ConnectToSource(shader.ConnectableAPI(), "outputName")

## Complete Material with Texture

```python
stage = Usd.Stage.CreateNew("materials.usda")

mat = UsdShade.Material.Define(stage, "/Materials/MyMat")

surface = UsdShade.Shader.Define(stage, "/Materials/MyMat/Surface")
surface.CreateIdAttr("UsdPreviewSurface")
surface.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set((0.8, 0.2, 0.1))
surface.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.5)
surface.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)

mat.CreateSurfaceOutput().ConnectToSource(surface.ConnectableAPI(), "surface")

uv = UsdShade.Shader.Define(stage, "/Materials/MyMat/UVReader")
uv.CreateIdAttr("UsdPrimvarReader_float2")
uv.CreateInput("varname", Sdf.ValueTypeNames.Token).Set("st")
uv.CreateOutput("result", Sdf.ValueTypeNames.Float2)

tex = UsdShade.Shader.Define(stage, "/Materials/MyMat/Tex")
tex.CreateIdAttr("UsdUVTexture")
tex.CreateInput("file", Sdf.ValueTypeNames.Asset).Set("texture.png")
tex.CreateOutput("rgb", Sdf.ValueTypeNames.Float3)

tex.CreateInput("st", Sdf.ValueTypeNames.Float2).ConnectToSource(uv.ConnectableAPI(), "result")
surface.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(tex.ConnectableAPI(), "rgb")

stage.GetRootLayer().Save()
```

## Connection Pattern

```python
input_attr.ConnectToSource(shader.ConnectableAPI(), "output_name")
```

## Quick Reference

**Shader IDs:** `UsdPreviewSurface` | `UsdUVTexture` | `UsdPrimvarReader_float2`

**Input Types:**
- `Sdf.ValueTypeNames.Color3f` — RGB colors
- `Sdf.ValueTypeNames.Float` — Scalars (roughness, metallic)
- `Sdf.ValueTypeNames.Float2` — UV coordinates
- `Sdf.ValueTypeNames.Asset` — File paths
- `Sdf.ValueTypeNames.Token` — String tokens

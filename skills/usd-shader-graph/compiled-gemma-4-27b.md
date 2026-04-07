# Wire: UV → Texture → Surface

## Basic Material (Color Only)

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

## Texture Material

```python
mat = UsdShade.Material.Define(stage, "/Materials/WoodMat")
surface = UsdShade.Shader.Define(stage, "/Materials/WoodMat/Surface")
surface.CreateIdAttr("UsdPreviewSurface")
mat.CreateSurfaceOutput().ConnectToSource(surface.ConnectableAPI(), "surface")

uv = UsdShade.Shader.Define(stage, "/Materials/WoodMat/UV")
uv.CreateIdAttr("UsdPrimvarReader_float2")
uv.CreateInput("varname", Sdf.ValueTypeNames.Token).Set("st")
uv.CreateOutput("result", Sdf.ValueTypeNames.Float2)

tex = UsdShade.Shader.Define(stage, "/Materials/WoodMat/Tex")
tex.CreateIdAttr("UsdUVTexture")
tex.CreateInput("file", Sdf.ValueTypeNames.Asset).Set("wood.png")
tex.CreateOutput("rgb", Sdf.ValueTypeNames.Float3)

tex.CreateInput("st", Sdf.ValueTypeNames.Float2).ConnectToSource(uv.ConnectableAPI(), "result")
surface.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).ConnectToSource(tex.ConnectableAPI(), "rgb")
```

## Bind Material to Geometry

```python
mesh = UsdGeom.Mesh.Define(stage, "/Geometry/Table")
UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim())
UsdShade.MaterialBindingAPI(mesh.GetPrim()).Bind(mat)

stage.GetRootLayer().Save()
```

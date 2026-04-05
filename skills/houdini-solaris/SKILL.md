# Houdini Solaris Python Script LOP Reference

## The editableStage() Pattern

In Houdini Solaris, Python Script LOPs operate on a USD stage provided by the node context:

```python
import hou
from pxr import Usd, UsdGeom, UsdShade, UsdLux, Sdf, Gf, Kind

# Get the stage from the current LOP node
stage = hou.pwd().editableStage()
```

**Critical:** Do NOT create a new stage with `Usd.Stage.CreateNew()`. Always use `hou.pwd().editableStage()` — this is the stage that flows through the LOP network.

## Prim Definition

### Xform (Transform Container)
```python
scene = UsdGeom.Xform.Define(stage, "/Scene")
# Set as default prim (important for references)
stage.SetDefaultPrim(scene.GetPrim())
```

### Mesh Geometry
```python
# Ground plane (quad)
ground = UsdGeom.Mesh.Define(stage, "/Scene/Ground")
ground.CreatePointsAttr([(-5,0,-5), (5,0,-5), (5,0,5), (-5,0,5)])
ground.CreateFaceVertexCountsAttr([4])
ground.CreateFaceVertexIndicesAttr([0, 1, 2, 3])
ground.CreateSubdivisionSchemeAttr("none")

# Cube (8 vertices, 6 quad faces)
cube = UsdGeom.Mesh.Define(stage, "/Scene/Hero/Body")
cube.CreatePointsAttr([
    (-0.5,-0.5,-0.5), (0.5,-0.5,-0.5), (0.5,0.5,-0.5), (-0.5,0.5,-0.5),
    (-0.5,-0.5,0.5),  (0.5,-0.5,0.5),  (0.5,0.5,0.5),  (-0.5,0.5,0.5),
])
cube.CreateFaceVertexCountsAttr([4, 4, 4, 4, 4, 4])
cube.CreateFaceVertexIndicesAttr([
    0,1,2,3,  4,5,6,7,  0,1,5,4,
    2,3,7,6,  0,3,7,4,  1,2,6,5,
])
cube.CreateSubdivisionSchemeAttr("none")
```

## Transform Operations

```python
from pxr import UsdGeom, Gf

# Translate
xformable = UsdGeom.Xformable(prim)
xformable.AddTranslateOp().Set(Gf.Vec3d(0.0, 1.0, 0.0))

# Rotate (Euler XYZ)
xformable.AddRotateXYZOp().Set(Gf.Vec3f(-45.0, 30.0, 0.0))

# Scale
xformable.AddScaleOp().Set(Gf.Vec3f(1.0, 1.0, 1.0))
```

## Lighting in Solaris

```python
from pxr import UsdLux

# Distant light (directional, like the sun)
sun = UsdLux.DistantLight.Define(stage, "/Scene/Lighting/KeyLight")
sun.CreateIntensityAttr(50000)
sun.CreateAngleAttr(0.53)
# Add rotation to aim the light
xf = UsdGeom.Xformable(sun.GetPrim())
xf.AddRotateXYZOp().Set(Gf.Vec3f(-45, 30, 0))

# Dome light (environment/IBL)
dome = UsdLux.DomeLight.Define(stage, "/Scene/Lighting/FillLight")
dome.CreateIntensityAttr(500)
```

## Material Binding

### Create Material + UsdPreviewSurface Shader
```python
from pxr import UsdShade, Sdf

# Define material
mat = UsdShade.Material.Define(stage, "/Scene/Materials/HeroMat")

# Define shader
shader = UsdShade.Shader.Define(stage, "/Scene/Materials/HeroMat/PBRShader")
shader.CreateIdAttr("UsdPreviewSurface")
shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set((0.8, 0.2, 0.1))
shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.4)
shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)

# Connect shader output to material surface
mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
```

### Bind Material to Geometry
```python
# Apply the binding API schema and bind
UsdShade.MaterialBindingAPI.Apply(body_prim)
UsdShade.MaterialBindingAPI(body_prim).Bind(mat)
```

## Model API / Kind

Used to classify prims in the scene hierarchy:
```python
from pxr import Usd, Kind

# Mark a prim as a 'component' (leaf-level asset)
model = Usd.ModelAPI(hero_prim)
model.SetKind(Kind.Tokens.component)

# Other kinds: 'assembly' (group of components), 'group', 'subcomponent'
```

## Complete Solaris Script Pattern

```python
import hou
from pxr import Usd, UsdGeom, UsdShade, UsdLux, Sdf, Gf, Kind

stage = hou.pwd().editableStage()

# 1. Root hierarchy
scene = UsdGeom.Xform.Define(stage, "/Scene")
stage.SetDefaultPrim(scene.GetPrim())

# 2. Geometry
ground = UsdGeom.Mesh.Define(stage, "/Scene/Ground")
ground.CreatePointsAttr([(-5,0,-5), (5,0,-5), (5,0,5), (-5,0,5)])
ground.CreateFaceVertexCountsAttr([4])
ground.CreateFaceVertexIndicesAttr([0, 1, 2, 3])

# 3. Transforms
hero = UsdGeom.Xform.Define(stage, "/Scene/Hero")
UsdGeom.Xformable(hero.GetPrim()).AddTranslateOp().Set(Gf.Vec3d(0, 1, 0))

# 4. Lighting
sun = UsdLux.DistantLight.Define(stage, "/Scene/Lighting/KeyLight")
sun.CreateIntensityAttr(50000)

# 5. Materials + binding
mat = UsdShade.Material.Define(stage, "/Scene/Materials/HeroMat")
shader = UsdShade.Shader.Define(stage, "/Scene/Materials/HeroMat/Shader")
shader.CreateIdAttr("UsdPreviewSurface")
shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set((0.8, 0.2, 0.1))
mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
UsdShade.MaterialBindingAPI.Apply(body_prim)
UsdShade.MaterialBindingAPI(body_prim).Bind(mat)

# 6. Kind metadata
Usd.ModelAPI(hero.GetPrim()).SetKind(Kind.Tokens.component)
```

# Solaris Python Script LOP - Task Patterns

## 1. Root Xform with Default Prim

```python
scene = UsdGeom.Xform.Define(stage, "/Scene")
stage.SetDefaultPrim(scene.GetPrim())
```

## 2. Ground Plane (4 points, 1 face)

```python
ground = UsdGeom.Mesh.Define(stage, "/Scene/Ground")
ground.CreatePointsAttr([(-5, 0, -5), (5, 0, -5), (5, 0, 5), (-5, 0, 5)])
ground.CreateFaceVertexCountsAttr([4])
ground.CreateFaceVertexIndicesAttr([0, 1, 2, 3])
```

## 3. Xform with Translate

```python
hero = UsdGeom.Xform.Define(stage, "/Scene/Hero")
UsdGeom.Xformable(hero.GetPrim()).AddTranslateOp().Set(Gf.Vec3d(0, 1, 0))
```

## 4. Cube Mesh (8 points, 6 faces)

```python
body = UsdGeom.Mesh.Define(stage, "/Scene/Hero/Body")
body.CreatePointsAttr([
    (-0.5,-0.5,-0.5), (0.5,-0.5,-0.5), (0.5,0.5,-0.5), (-0.5,0.5,-0.5),
    (-0.5,-0.5,0.5), (0.5,-0.5,0.5), (0.5,0.5,0.5), (-0.5,0.5,0.5)
])
body.CreateFaceVertexCountsAttr([4, 4, 4, 4, 4, 4])
body.CreateFaceVertexIndicesAttr([0,1,2,3, 4,5,6,7, 0,1,5,4, 2,3,7,6, 0,3,7,4, 1,2,6,5])
```

## 5. DistantLight with Intensity and Rotate

```python
key_light = UsdLux.DistantLight.Define(stage, "/Scene/Lighting/KeyLight")
key_light.CreateIntensityAttr(50000)
UsdGeom.Xformable(key_light.GetPrim()).AddRotateXYZOp().Set(Gf.Vec3f(-45, 30, 0))
```

## 6. DomeLight with Intensity

```python
fill_light = UsdLux.DomeLight.Define(stage, "/Scene/Lighting/FillLight")
fill_light.CreateIntensityAttr(500)
```

## 7. Material with UsdPreviewSurface Shader

```python
mat = UsdShade.Material.Define(stage, "/Scene/Materials/HeroMat")
shader = UsdShade.Shader.Define(stage, "/Scene/Materials/HeroMat/Shader")
shader.CreateIdAttr("UsdPreviewSurface")
shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set((0.8, 0.2, 0.1))
shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.4)
shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.0)
mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
```

## 8. Bind Material to Geometry

```python
UsdShade.MaterialBindingAPI.Apply(body.GetPrim())
UsdShade.MaterialBindingAPI(body.GetPrim()).Bind(mat)
```

## 9. Set Model Kind

```python
Usd.ModelAPI(hero.GetPrim()).SetKind(Kind.Tokens.component)
```

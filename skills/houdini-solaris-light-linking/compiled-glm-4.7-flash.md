# RimLight illuminates only Body

## Stage Access

```python
import hou
from pxr import Usd, UsdGeom, UsdLux, Sdf, Gf, Vt

stage = hou.pwd().editableStage()
```

## Create Lights

**Distant Light:**
```python
key = UsdLux.DistantLight.Define(stage, "/Lights/KeyLight")
key.GetIntensityAttr().Set(50000)
key.GetAngleAttr().Set(1.0)
```

**Dome Light:**
```python
dome = UsdLux.DomeLight.Define(stage, "/Lights/DomeLight")
dome.GetIntensityAttr().Set(500)
```

## Transform Lights

```python
xf = UsdGeom.Xformable(key.GetPrim())
xf.AddRotateXYZOp().Set(Gf.Vec3f(-45.0, 30.0, 0.0))
```

## Light Filter (Barn Door)

Create as a child prim under the light:
```python
barndoor = stage.DefinePrim("/Lights/KeyLight/BarnDoor")
barndoor.CreateAttribute("barndoor:top", Sdf.ValueTypeNames.Float).Set(0.2)
barndoor.CreateAttribute("barndoor:bottom", Sdf.ValueTypeNames.Float).Set(-0.1)
barndoor.CreateAttribute("barndoor:left", Sdf.ValueTypeNames.Float).Set(-0.3)
barndoor.CreateAttribute("barndoor:right", Sdf.ValueTypeNames.Float).Set(0.3)
```

## Light Linking with UsdCollectionAPI

Apply a `"lightLink"` collection to a light to control which geometry it illuminates:

```python
from pxr import Usd

collection = Usd.CollectionAPI.Apply(light_prim, "lightLink")
collection.GetIncludesRel().AddTarget("/Scene/Hero")
collection.GetExcludesRel().AddTarget("/Scene/Environment")
```

**Multiple lights example:**
```python
key_coll = Usd.CollectionAPI.Apply(key_light_prim, "lightLink")
key_coll.GetIncludesRel().AddTarget("/Scene/Hero")

rim_coll = Usd.CollectionAPI.Apply(rim_light_prim, "lightLink")
rim_coll.GetIncludesRel().AddTarget("/Scene/Hero/Body")
```

## Set Default Prim

```python
root = UsdGeom.Xform.Define(stage, "/Scene")
stage.SetDefaultPrim(root.GetPrim())
```

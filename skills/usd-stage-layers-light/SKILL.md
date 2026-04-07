# USD Layer Opinion System — Key Patterns

- **Create layers as separate stages:** `Usd.Stage.CreateNew("base_layer.usda")` for each layer file
- **Sublayer order matters:** Stronger layers go FIRST in `subLayerPaths` list
  - `root_layer.subLayerPaths.append("look_layer.usda")` — added first = strongest
  - `root_layer.subLayerPaths.append("base_layer.usda")` — added last = weakest
- **Time samples override statics:** If a stronger layer sets time-sampled values on an attribute, they override any static value from a weaker layer
- **Authoring time samples on transforms:**
  ```python
  translate_op = UsdGeom.Xformable(prim).AddTranslateOp()
  translate_op.Set(Gf.Vec3d(0,0,0), 1)    # frame 1
  translate_op.Set(Gf.Vec3d(5,0,0), 24)   # frame 24
  ```
- **Reading composed values:** `xformOp.Get(frame)` returns the resolved value at a specific time
- **Material in a layer:** Define material + shader, then `UsdShade.MaterialBindingAPI.Apply(prim)` and `.Bind(mat)` — works even if mesh is defined in another layer
- **DefinePrim vs OverridePrim:** Use `stage.DefinePrim(path)` to create/reference a prim for adding opinions; it creates the prim if it doesn't exist or targets an existing one
- Save each layer: `stage.GetRootLayer().Save()`
- Set default prim: `stage.SetDefaultPrim(prim)`

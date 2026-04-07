# Solaris PointInstancer & Collections — Key Patterns

- **CRITICAL:** `stage = hou.pwd().editableStage()` — never `Usd.Stage.CreateNew()`
- **PointInstancer:** `UsdGeom.PointInstancer.Define(stage, path)`
  - Prototypes: `GetPrototypesRel().SetTargets([Sdf.Path("/Proto/A"), ...])` — paths to Xform+Mesh prims
  - ProtoIndices: `GetProtoIndicesAttr().Set(Vt.IntArray([0,1,2,0,1,2,...]))` — which prototype per instance
  - Positions: `GetPositionsAttr().Set(Vt.Vec3fArray([Gf.Vec3f(x,y,z), ...]))` — one per instance
  - Orientations: `GetOrientationsAttr().Set(Vt.QuathArray([Gf.Quath(1,0,0,0)] * N))` — identity quaternion
- **Mesh points:** `GetPointsAttr().Set(Vt.Vec3fArray([...]))`, `GetFaceVertexCountsAttr()`, `GetFaceVertexIndicesAttr()`
- **CollectionAPI:** `Usd.CollectionAPI.Apply(prim, "collectionName")` then `GetIncludesRel().AddTarget(path)`
- Ground plane: 4-point quad `[(-5,0,-5), (5,0,-5), (5,0,5), (-5,0,5)]`
- Default prim: `stage.SetDefaultPrim(xform.GetPrim())`

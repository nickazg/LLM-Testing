# USD Skeletal Animation — Key Patterns

- **SkelRoot** wraps everything: `UsdSkel.Root.Define(stage, "/Root")` — all skel data must be under this
- **Skeleton** defines joint topology via path tokens: `["Hips", "Hips/Spine", "Hips/Spine/Head"]`
  - Joint paths use `/` separator, NO leading `/`
  - `GetJointsAttr().Set(joints)` for the joint list
  - `GetRestTransformsAttr()` and `GetBindTransformsAttr()` take `Vt.Matrix4dArray` — one `Gf.Matrix4d` per joint
- **Animation** has time-sampled transforms: `UsdSkel.Animation.Define(stage, path)`
  - `GetJointsAttr().Set(joints)` — must match skeleton's joint list exactly
  - `GetTranslationsAttr().Set(Vt.Vec3fArray([...]), frame)` — one Vec3f per joint per frame
  - `GetRotationsAttr().Set(Vt.QuatfArray([...]), frame)` — quaternions, Gf.Quatf(1,0,0,0) for identity
  - `GetScalesAttr().Set(Vt.Vec3hArray([...]), frame)` — half-precision Vec3h
- **BindingAPI** on the mesh: `UsdSkel.BindingAPI.Apply(mesh_prim)`
  - `CreateSkeletonRel().SetTargets(["/Root/Skeleton"])`
  - `CreateJointIndicesPrimvar(False, 1).Set(Vt.IntArray([0]*num_verts))` — per-vertex, 1 influence
  - `CreateJointWeightsPrimvar(False, 1).Set(Vt.FloatArray([1.0]*num_verts))`
- Save: `stage.GetRootLayer().Save()`

bl_info = {
    "name": "CPR Ellipsoid Tools",
    "author": "CPR Team",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > CPR",
    "description": "Create parametric ellipsoids with advanced transformation options",
    "warning": "",
    "doc_url": "",
    "category": "Add Mesh",
}

# Blender 脚本：基于参数化生成椭球并支持仿射变换
# 使用方法：在 Blender 的脚本编辑器中打开并运行（Blender 自带 Python 环境，不依赖 numpy）
# 功能：创建椭球（可部分），应用仿射矩阵 / 欧拉角旋转 / 平移，设置颜色材质

import bpy
import math

try:
    import numpy as np

    _HAS_NUMPY = True
except Exception:
    np = None
    _HAS_NUMPY = False
from mathutils import Matrix, Vector
import bmesh

# 缓存 u/v 网格以复用，键为 (u_res,v_res,u0,u1,v0,v1)
_UV_GRID_CACHE = {}


def _get_uv_grid(u_res, v_res, u_range, v_range, cache_uv=True):
    """返回 (u_grid, v_grid)。在有 numpy 时返回 numpy arrays，否则返回嵌套列表。"""

    def _coerce_int(x, name="value"):
        # Accept ints/floats directly
        if isinstance(x, (int,)):
            return int(x)
        if isinstance(x, float):
            return int(x)
        # Numpy integer types
        try:
            import numbers

            if isinstance(x, numbers.Integral):
                return int(x)
        except Exception:
            pass
        # Handle Blender _PropertyDeferred objects
        if str(type(x).__name__) == "_PropertyDeferred":
            try:
                # Extract default value from the property descriptor
                if hasattr(x, '__dict__') and 'default' in x.__dict__:
                    return int(x.__dict__['default'])
                # Try to access the default attribute
                if hasattr(x, 'default'):
                    return int(x.default)
            except Exception:
                pass
        # Blender deferred property descriptors often expose .default
        if hasattr(x, "default"):
            try:
                return int(x.default)
            except Exception:
                pass
        # Some objects may have .value
        if hasattr(x, "value"):
            try:
                return int(x.value)
            except Exception:
                pass
        # Try converting from string
        try:
            return int(float(str(x)))
        except Exception:
            raise TypeError(
                f"{name} must be an integer or int-like, got {type(x)}: {x}"
            )

    u_res = _coerce_int(u_res, "u_res")
    v_res = _coerce_int(v_res, "v_res")
    if u_res < 2 or v_res < 2:
        raise ValueError("u_res and v_res must be >= 2")

    u0, u1 = float(u_range[0]), float(u_range[1])
    v0, v1 = float(v_range[0]), float(v_range[1])
    key = (u_res, v_res, u0, u1, v0, v1)
    if cache_uv and _HAS_NUMPY and key in _UV_GRID_CACHE:
        return _UV_GRID_CACHE[key]
    if _HAS_NUMPY:
        u = np.linspace(u0, u1, u_res)
        v = np.linspace(v0, v1, v_res)
        u_grid, v_grid = np.meshgrid(u, v)
    else:
        u_vals = [u0 + (u1 - u0) * j / max(1, u_res - 1) for j in range(u_res)]
        v_vals = [v0 + (v1 - v0) * i / max(1, v_res - 1) for i in range(v_res)]
        u_grid = [[uv for uv in u_vals] for _ in range(v_res)]
        v_grid = [[vv for _ in range(u_res)] for vv in v_vals]
    if cache_uv and _HAS_NUMPY:
        _UV_GRID_CACHE[key] = (u_grid, v_grid)
    return u_grid, v_grid


def create_parametric_ellipsoid(
    a=1.0,
    b=1.0,
    c=1.0,
    u_res=32,
    v_res=16,
    u_range=(0.0, 2 * math.pi),
    v_range=(0.0, math.pi),
    name="Ellipsoid",
    color=(1.0, 0.3, 0.3, 1.0),
    affine_matrix=None,  # 4x4 nested list or mathutils.Matrix
    rotation_euler_deg=None,  # tuple (rx, ry, rz) degrees, used if affine_matrix is None
    location=(0.0, 0.0, 0.0),
    keep_y_positive=False,  # 如果 True，仅保留变换后 y >= 0 的顶点/面
    generate_uv: bool = False,  # 是否生成 UV 层
    triangulate: bool = True,  # 是否对面进行三角化
    use_bmesh: bool = True,  # 使用 bmesh 构建以提升性能
    return_mapping: bool = False,  # 若 True 返回 (obj, mapping)
    cache_uv: bool = True,  # 是否缓存 uv 网格以复用
    remove_unused_vertices: bool = True,  # 是否剔除未被面引用的顶点
):
    """
    在 Blender 中创建一个参数化椭球网格。

    参数说明：
      a,b,c: 椭球在 x,y,z 方向的半轴长度
      u_res,v_res: 网格分辨率（u 列数, v 行数）
      u_range,v_range: 参数范围
      color: RGBA 颜色（0..1）
      affine_matrix: 若提供，会作为 4x4 齐次矩阵直接应用到顶点上（优先）
      rotation_euler_deg: 如果未提供仿射矩阵，可通过欧拉角旋转（度），随后平移 location
      location: 平移向量（仅在未提供 affine_matrix 时生效）
      keep_y_positive: True 则剔除变换后 y < 0 的顶点/面（适合取 Y 正半部分）
    """

    # 生成 u/v 网格（可能从缓存中读取）
    u_grid, v_grid = _get_uv_grid(u_res, v_res, u_range, v_range, cache_uv)

    sv = np.sin(v_grid)
    cv = np.cos(v_grid)
    cu = np.cos(u_grid)
    su = np.sin(u_grid)

    x = (a * cu * sv).astype(float)
    y = (b * su * sv).astype(float)
    z = (c * cv).astype(float)

    # 将网格展平为 (N,3) 便于仿射矩阵或旋转统一处理
    pts = np.column_stack([x.ravel(), y.ravel(), z.ravel()])  # shape (N,3)

    # 处理仿射矩阵或欧拉旋转 + 平移
    if affine_matrix is not None:
        # 支持 mathutils.Matrix 或可被转换为 numpy 的嵌套列表
        if isinstance(affine_matrix, Matrix):
            A = np.array(affine_matrix)
        else:
            A = np.asarray(affine_matrix, dtype=float)
        if A.shape == (3, 3):
            A4 = np.eye(4, dtype=float)
            A4[:3, :3] = A
        elif A.shape == (3, 4):
            A4 = np.eye(4, dtype=float)
            A4[:3, :4] = A
        elif A.shape == (4, 4):
            A4 = A
        else:
            raise ValueError("affine_matrix must be shape (4,4), (3,3) or (3,4)")

        pts_h = np.hstack([pts, np.ones((pts.shape[0], 1), dtype=float)])  # (N,4)
        pts_t = (pts_h @ A4.T)[:, :3]
    else:
        pts_t = pts.copy()
        # 如果提供旋转角度（度），用 numpy 构建旋转矩阵并作用于所有点
        if rotation_euler_deg is not None:
            rx, ry, rz = np.radians(rotation_euler_deg)
            Rx = np.array(
                [[1, 0, 0], [0, np.cos(rx), -np.sin(rx)], [0, np.sin(rx), np.cos(rx)]],
                dtype=float,
            )
            Ry = np.array(
                [[np.cos(ry), 0, np.sin(ry)], [0, 1, 0], [-np.sin(ry), 0, np.cos(ry)]],
                dtype=float,
            )
            Rz = np.array(
                [[np.cos(rz), -np.sin(rz), 0], [np.sin(rz), np.cos(rz), 0], [0, 0, 1]],
                dtype=float,
            )
            R = Rz @ Ry @ Rx
            pts_t = pts_t @ R.T
        # 平移
        loc = np.asarray(location, dtype=float)
        pts_t = pts_t + loc.reshape(1, 3)

    # 生成 verts 列表与保留掩码
    verts = [(float(px), float(py), float(pz)) for px, py, pz in pts_t]
    if keep_y_positive:
        keep_mask = [pt[1] >= 0 for pt in verts]
    else:
        keep_mask = [True] * len(verts)

    # 构造面（四边形拼接），在遇到任何顶点被剔除时跳过该面
    faces = []
    for i in range(v_res - 1):
        for j in range(u_res):
            jn = (j + 1) % u_res
            v0_idx = i * u_res + j
            v1_idx = i * u_res + jn
            v2_idx = (i + 1) * u_res + jn
            v3_idx = (i + 1) * u_res + j
            # 如果任何顶点被剔除则跳过
            if not (
                keep_mask[v0_idx]
                and keep_mask[v1_idx]
                and keep_mask[v2_idx]
                and keep_mask[v3_idx]
            ):
                continue
            faces.append((v0_idx, v1_idx, v2_idx, v3_idx))

    # 剔除未被引用的顶点以节约内存（可选）
    if not faces:
        return None

    used_indices = sorted({idx for f in faces for idx in f})
    index_map = {old: new for new, old in enumerate(used_indices)}
    verts_used = [verts[i] for i in used_indices]
    faces_mapped = [[index_map[i] for i in f] for f in faces]

    # 创建 mesh 使用 bmesh（更快且支持复杂操作）
    mesh = bpy.data.meshes.new(name + "_mesh")
    if use_bmesh:
        bm = bmesh.new()
        bm_verts = [bm.verts.new(v) for v in verts_used]
        bm.verts.ensure_lookup_table()
        for f_idx in faces_mapped:
            try:
                bm.faces.new([bm_verts[i] for i in f_idx])
            except ValueError:
                pass
        bm.faces.ensure_lookup_table()
        if triangulate and len(bm.faces) > 0:
            bmesh.ops.triangulate(bm, faces=bm.faces[:])
        bm.to_mesh(mesh)
        bm.free()
    else:
        mesh.from_pydata(verts_used, [], [tuple(f) for f in faces_mapped])
        if triangulate:
            mesh.calc_loop_triangles()

    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    # 创建/分配简单材质
    mat = bpy.data.materials.new(name + "_mat")
    mat.diffuse_color = color  # RGBA
    obj.data.materials.append(mat)

    mapping = {"verts": verts_used, "faces": faces_mapped}

    # 生成 UV 层（按参数化 u/v）
    if generate_uv:
        if not mesh.uv_layers:
            uv_layer = mesh.uv_layers.new(name="UVMap")
        else:
            uv_layer = mesh.uv_layers.active
        # 计算原始每顶点的 uv（基于 u_grid,v_grid）
        if _HAS_NUMPY:
            u_flat = np.array(u_grid).ravel()
            v_flat = np.array(v_grid).ravel()
            uv_per_used = [(float(u_flat[i]), float(v_flat[i])) for i in used_indices]
        else:
            uv_flat = [u for row in u_grid for u in row]
            vv_flat = [v for row in v_grid for v in row]
            uv_per_used = [(float(uv_flat[i]), float(vv_flat[i])) for i in used_indices]
        for poly in mesh.polygons:
            for li, vi in enumerate(poly.vertices):
                uv = uv_per_used[vi]
                uv_layer.data[poly.loop_start + li].uv = uv

    if return_mapping:
        return obj, mapping
    return obj


# 辅助：删除场景中现有对象（谨慎使用）
def clear_scene(remove_mesh_data=True):
    objs = list(bpy.context.scene.objects)
    for o in objs:
        bpy.data.objects.remove(o, do_unlink=True)
    if remove_mesh_data:
        for m in list(bpy.data.meshes):
            bpy.data.meshes.remove(m, do_unlink=True)


def create_geometry_nodes_instancer(
    base_obj, rows=5, cols=5, spacing=(2.0, 2.0), name="Ellipsoid_Instancer"
):
    """在场景中创建一个 Geometry Nodes modifier，用 `base_obj` 作为实例，在网格点上布置实例。

    依赖 Blender 3.x 的 Geometry Nodes 节点名称（常见于官方 API）。
    Returns: the object which has the GeometryNodes modifier.
    """
    # 新建一个空对象作为 GN 容器
    gn_obj = bpy.data.objects.new(name + "_gn", None)
    bpy.context.collection.objects.link(gn_obj)

    mod = gn_obj.modifiers.new(name="GeometryNodes", type="NODES")
    node_group = bpy.data.node_groups.new(name + "_nodegroup", "GeometryNodeTree")
    mod.node_group = node_group

    nodes = node_group.nodes
    links = node_group.links

    nodes.clear()

    # Group Input / Output
    node_in = nodes.new("NodeGroupInput")
    node_in.location = (-800, 0)
    node_out = nodes.new("NodeGroupOutput")
    node_out.location = (800, 0)
    node_group.inputs.new("NodeSocketGeometry", "Geometry")
    node_group.outputs.new("NodeSocketGeometry", "Geometry")

    # Grid primitive
    node_grid = nodes.new("GeometryNodeMeshPrimitiveGrid")
    node_grid.location = (-400, 0)
    node_grid.inputs["Vertices X"].default_value = cols
    node_grid.inputs["Vertices Y"].default_value = rows
    node_grid.inputs["Size X"].default_value = spacing[0] * (cols - 1)
    node_grid.inputs["Size Y"].default_value = spacing[1] * (rows - 1)

    # Mesh to Points
    node_m2p = nodes.new("GeometryNodeMeshToPoints")
    node_m2p.location = (-100, 0)

    # Object Info (bring base object geometry to instance)
    node_obj = nodes.new("GeometryNodeObjectInfo")
    node_obj.location = (-100, -200)
    node_obj.inputs["Transform"].default_value = True
    node_obj.inputs["Object"].default_value = base_obj

    # Instance on Points
    node_inst = nodes.new("GeometryNodeInstanceOnPoints")
    node_inst.location = (200, 0)

    # Links: grid -> mesh to points -> instance -> output
    links.new(node_grid.outputs["Mesh"], node_m2p.inputs["Mesh"])
    links.new(node_m2p.outputs["Points"], node_inst.inputs["Points"])
    links.new(node_obj.outputs["Geometry"], node_inst.inputs["Instance"])
    links.new(node_inst.outputs["Instances"], node_out.inputs["Geometry"])

    return gn_obj


class CPR_OT_add_ellipsoid(bpy.types.Operator):
    bl_idname = "cpr.add_ellipsoid"
    bl_label = "Add Ellipsoid (CPR)"
    bl_description = "Create a parametric ellipsoid with customizable parameters"
    bl_options = {"REGISTER", "UNDO"}

    # Properties with proper defaults and ranges
    a: bpy.props.FloatProperty(
        name="X Radius",
        default=1.0,
        min=0.01,
        max=100.0,
        description="Ellipsoid radius in X direction"
    )
    b: bpy.props.FloatProperty(
        name="Y Radius", 
        default=1.0,
        min=0.01,
        max=100.0,
        description="Ellipsoid radius in Y direction"
    )
    c: bpy.props.FloatProperty(
        name="Z Radius",
        default=1.0,
        min=0.01,
        max=100.0,
        description="Ellipsoid radius in Z direction"
    )
    u_res: bpy.props.IntProperty(
        name="U Resolution",
        default=32,
        min=3,
        max=256,
        description="Resolution in U direction (longitude)"
    )
    v_res: bpy.props.IntProperty(
        name="V Resolution",
        default=16,
        min=2,
        max=256,
        description="Resolution in V direction (latitude)"
    )
    keep_y_positive: bpy.props.BoolProperty(
        name="Keep Y Positive Only",
        default=False,
        description="Only keep the part where Y >= 0"
    )
    use_geometry_nodes: bpy.props.BoolProperty(
        name="Use Geometry Nodes",
        default=False,
        description="Create a geometry nodes instancer"
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        try:
            obj = create_parametric_ellipsoid(
                a=self.a,
                b=self.b,
                c=self.c,
                u_res=self.u_res,
                v_res=self.v_res,
                keep_y_positive=self.keep_y_positive,
            )
            if self.use_geometry_nodes and obj is not None:
                create_geometry_nodes_instancer(obj)
            self.report({"INFO"}, f"Created ellipsoid with dimensions ({self.a:.2f}, {self.b:.2f}, {self.c:.2f})")
            return {"FINISHED"}
        except Exception as e:
            self.report({"ERROR"}, f"Failed to create ellipsoid: {str(e)}")
            return {"CANCELLED"}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "a")
        layout.prop(self, "b")
        layout.prop(self, "c")
        layout.separator()
        layout.prop(self, "u_res")
        layout.prop(self, "v_res")
        layout.separator()
        layout.prop(self, "keep_y_positive")
        layout.prop(self, "use_geometry_nodes")


class CPR_PT_ellipsoid_panel(bpy.types.Panel):
    bl_label = "CPR Ellipsoid"
    bl_idname = "CPR_PT_ellipsoid_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "CPR"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        
        # Main ellipsoid creation section
        box = layout.box()
        box.label(text="Parametric Ellipsoid", icon="MESH_SPHERE")
        col = box.column(align=True)
        
        # Quick add buttons with presets
        row = col.row(align=True)
        row.operator("cpr.add_ellipsoid", text="Sphere").a = 1.0
        row.operator("cpr.add_ellipsoid", text="Ellipsoid").a = 2.0
        
        # Advanced settings
        col.separator()
        col.operator("cpr.add_ellipsoid", text="Custom Ellipsoid")
        
        # Utilities section
        layout.separator()
        box = layout.box()
        box.label(text="Utilities", icon="TOOL_SETTINGS")
        col = box.column(align=True)
        col.operator(
            "cpr.create_gnodes_from_active", text="Create GN Instancer from Active"
        )
        
        # Info section
        layout.separator()
        box = layout.box()
        box.label(text="Information", icon="INFO")
        col = box.column(align=True)
        col.scale_y = 0.8
        col.label(text="• Use Custom Ellipsoid for full parameters")
        col.label(text="• Geometry Nodes creates instancer grid")
        col.label(text="• Keep Y Positive for half-sphere")


class CPR_OT_create_gnodes_from_active(bpy.types.Operator):
    bl_idname = "cpr.create_gnodes_from_active"
    bl_label = "Create Geometry Nodes Instancer from Active"
    bl_description = "Create a geometry nodes instancer from the active object"
    bl_options = {"REGISTER", "UNDO"}

    rows: bpy.props.IntProperty(
        name="Rows",
        default=5,
        min=1,
        max=50,
        description="Number of rows in the instancer grid"
    )
    cols: bpy.props.IntProperty(
        name="Columns",
        default=5,
        min=1,
        max=50,
        description="Number of columns in the instancer grid"
    )
    spacing_x: bpy.props.FloatProperty(
        name="X Spacing",
        default=2.0,
        min=0.1,
        max=50.0,
        description="Spacing between instances in X direction"
    )
    spacing_y: bpy.props.FloatProperty(
        name="Y Spacing",
        default=2.0,
        min=0.1,
        max=50.0,
        description="Spacing between instances in Y direction"
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        base = context.active_object
        if base is None:
            self.report({"ERROR"}, "No active object to instance. Please select an object first.")
            return {"CANCELLED"}
        
        try:
            instancer = create_geometry_nodes_instancer(
                base,
                rows=self.rows,
                cols=self.cols,
                spacing=(self.spacing_x, self.spacing_y),
            )
            self.report({"INFO"}, f"Created geometry nodes instancer with {self.rows}x{self.cols} grid")
            return {"FINISHED"}
        except Exception as e:
            self.report({"ERROR"}, f"Failed to create geometry nodes instancer: {str(e)}")
            return {"CANCELLED"}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "rows")
        layout.prop(self, "cols")
        layout.prop(self, "spacing_x")
        layout.prop(self, "spacing_y")


def register():
    try:
        bpy.utils.register_class(CPR_OT_add_ellipsoid)
        bpy.utils.register_class(CPR_PT_ellipsoid_panel)
        bpy.utils.register_class(CPR_OT_create_gnodes_from_active)
        print("CPR Ellipsoid addon registered successfully")
    except Exception as e:
        print(f"Failed to register CPR Ellipsoid addon: {e}")


def unregister():
    try:
        bpy.utils.unregister_class(CPR_OT_create_gnodes_from_active)
        bpy.utils.unregister_class(CPR_PT_ellipsoid_panel)
        bpy.utils.unregister_class(CPR_OT_add_ellipsoid)
        print("CPR Ellipsoid addon unregistered successfully")
    except Exception as e:
        print(f"Failed to unregister CPR Ellipsoid addon: {e}")


# 示例：如果直接在 Blender 中运行该脚本
if __name__ == "__main__":
    # 注册 UI 类
    try:
        register()
    except Exception:
        pass

    # 清理场景（开发时便于重复运行）
    clear_scene()

    # 示例1：默认椭球
    create_parametric_ellipsoid(
        a=2.5,
        b=1.2,
        c=1.0,
        u_res=64,
        v_res=32,
        name="Ellipsoid_default",
        color=(0.2, 0.6, 1.0, 1.0),
    )

    # 示例2：仿射镜像 + 平移
    A = Matrix(
        (
            (-1.0, 0.0, 0.0, 3.0),
            (0.0, 1.0, 0.0, 0.0),
            (0.0, 0.0, -1.0, 0.0),
            (0.0, 0.0, 0.0, 1.0),
        )
    )
    create_parametric_ellipsoid(
        a=1.0,
        b=0.8,
        c=1.2,
        u_res=48,
        v_res=24,
        name="Ellipsoid_affine",
        color=(1.0, 0.4, 0.6, 1.0),
        affine_matrix=A,
    )

    # 示例3：只保留 Y >= 0 的部分曲面
    create_parametric_ellipsoid(
        a=2.0,
        b=1.0,
        c=1.0,
        u_res=48,
        v_res=24,
        name="Ellipsoid_halfY",
        color=(1.0, 0.8, 0.2, 1.0),
        keep_y_positive=True,
    )

    print("Blender: 已创建示例椭球对象，检查 3D 视图。")

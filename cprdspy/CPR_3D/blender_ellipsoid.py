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
from mathutils import Matrix, Vector, Euler, Quaternion
import bmesh

# 缓存 u/v 网格以复用，键为 (u_res,v_res,u0,u1,v0,v1)
_UV_GRID_CACHE = {}


def _get_uv_grid(u_res, v_res, u_range, v_range, cache_uv=True):
    """返回 (u_grid, v_grid)。在有 numpy 时返回 numpy arrays，否则返回嵌套列表。"""
    try:
        u_res = int(u_res)
    except Exception:
        u_res = int(float(u_res))
    try:
        v_res = int(v_res)
    except Exception:
        v_res = int(float(v_res))
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


def _quaternion_to_rotation_matrix(q: list) -> Matrix:
    """
    将四元数转换为Blender的3x3旋转矩阵
    参数: q = [w, x, y, z] - 四元数 (w是标量部分, [x, y, z]是向量部分)
    返回: 3x3 rotation Matrix
    """
    w, x, y, z = q
    # 标准化四元数
    norm = math.sqrt(w * w + x * x + y * y + z * z)
    if norm == 0:
        return Matrix.Identity(3)
    w, x, y, z = w / norm, x / norm, y / norm, z / norm

    # 计算旋转矩阵
    m = Matrix()
    m[0][0] = 1 - 2 * (y * y + z * z)
    m[0][1] = 2 * (x * y - w * z)
    m[0][2] = 2 * (x * z + w * y)
    m[1][0] = 2 * (x * y + w * z)
    m[1][1] = 1 - 2 * (x * x + z * z)
    m[1][2] = 2 * (y * z - w * x)
    m[2][0] = 2 * (x * z - w * y)
    m[2][1] = 2 * (y * z + w * x)
    m[2][2] = 1 - 2 * (x * x + y * y)
    return m


def _axis_angle_to_quaternion(axis: list, angle: float) -> list:
    """
    将轴角表示转换为四元数
    参数: axis - 旋转轴向量
          angle - 旋转角度（弧度）
    返回: [w, x, y, z] 四元数
    """
    axis = Vector(axis).normalized()
    half_angle = angle / 2
    sin_half = math.sin(half_angle)
    cos_half = math.cos(half_angle)
    return [cos_half, axis[0] * sin_half, axis[1] * sin_half, axis[2] * sin_half]


def create_parametric_ellipsoid(
    a=1.0,
    b=1.0,
    c=1.0,
    u_res=32,
    v_res=32,
    u_range=(0.0, 2 * math.pi),
    v_range=(0.0, math.pi),
    name="Ellipsoid",
    color=(1.0, 0.3, 0.3, 1.0),
    affine_matrix=None,  # 4x4 nested list or mathutils.Matrix
    rotation_euler_deg=None,  # tuple (rx, ry, rz) degrees, used if affine_matrix is None
    quaternion=None,  # list [w, x, y, z], used if affine_matrix and rotation_euler_deg are None
    axis_angle=None,  # tuple (axis, angle_deg), used if higher priority params are None
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
      affine_matrix: 若提供，会作为 4x4 齐次矩阵直接应用到顶点上（优先级最高）
      rotation_euler_deg: 如果未提供仿射矩阵，可通过欧拉角旋转（度），随后平移 location
      quaternion: 如果未提供仿射矩阵和欧拉角，可通过四元数旋转（[w, x, y, z]），随后平移 location
      axis_angle: 如果未提供仿射矩阵、欧拉角和四元数，可通过轴角旋转（(axis, angle_deg)），随后平移 location
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

        # 如果提供了旋转参数，先应用旋转
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
            pts = pts @ R.T
        # 如果提供四元数，转换为旋转矩阵并应用
        elif quaternion is not None:
            R = _quaternion_to_rotation_matrix(quaternion)
            # 将Matrix转换为numpy数组
            R_np = np.array(R).T  # 转置是因为Blender使用列主序
            pts = pts @ R_np
        # 如果提供轴角，先转换为四元数，再转换为旋转矩阵并应用
        elif axis_angle is not None:
            axis, angle_deg = axis_angle
            q = _axis_angle_to_quaternion(axis, math.radians(angle_deg))
            R = _quaternion_to_rotation_matrix(q)
            # 将Matrix转换为numpy数组
            R_np = np.array(R).T  # 转置是因为Blender使用列主序
            pts = pts @ R_np

        # 然后应用仿射变换
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
        # 如果提供四元数，转换为旋转矩阵并应用
        elif quaternion is not None:
            R = _quaternion_to_rotation_matrix(quaternion)
            # 将Matrix转换为numpy数组
            R_np = np.array(R).T  # 转置是因为Blender使用列主序
            pts_t = pts_t @ R_np
        # 如果提供轴角，先转换为四元数，再转换为旋转矩阵并应用
        elif axis_angle is not None:
            axis, angle_deg = axis_angle
            q = _axis_angle_to_quaternion(axis, math.radians(angle_deg))
            R = _quaternion_to_rotation_matrix(q)
            # 将Matrix转换为numpy数组
            R_np = np.array(R).T  # 转置是因为Blender使用列主序
            pts_t = pts_t @ R_np

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
        description="Ellipsoid radius in X direction",
    )
    b: bpy.props.FloatProperty(
        name="Y Radius",
        default=1.0,
        min=0.01,
        max=100.0,
        description="Ellipsoid radius in Y direction",
    )
    c: bpy.props.FloatProperty(
        name="Z Radius",
        default=1.0,
        min=0.01,
        max=100.0,
        description="Ellipsoid radius in Z direction",
    )
    u_res: bpy.props.IntProperty(
        name="U Resolution",
        default=32,
        min=3,
        max=256,
        description="Resolution in U direction (longitude)",
    )
    v_res: bpy.props.IntProperty(
        name="V Resolution",
        default=16,
        min=2,
        max=256,
        description="Resolution in V direction (latitude)",
    )
    u_start: bpy.props.FloatProperty(
        name="U Start",
        default=0.0,
        min=0.0,
        max=2 * math.pi,
        description="Starting angle in radians for U direction",
    )
    u_end: bpy.props.FloatProperty(
        name="U End",
        default=2 * math.pi,
        min=0.0,
        max=2 * math.pi,
        description="Ending angle in radians for U direction",
    )
    v_start: bpy.props.FloatProperty(
        name="V Start",
        default=0.0,
        min=0.0,
        max=math.pi,
        description="Starting angle in radians for V direction",
    )
    v_end: bpy.props.FloatProperty(
        name="V End",
        default=math.pi,
        min=0.0,
        max=math.pi,
        description="Ending angle in radians for V direction",
    )
    keep_y_positive: bpy.props.BoolProperty(
        name="Keep Y Positive Only",
        default=False,
        description="Only keep the part where Y >= 0",
    )
    use_geometry_nodes: bpy.props.BoolProperty(
        name="Use Geometry Nodes",
        default=False,
        description="Create a geometry nodes instancer",
    )
    color_r: bpy.props.FloatProperty(
        name="Red",
        default=1.0,
        min=0.0,
        max=1.0,
        description="Red color component",
    )
    color_g: bpy.props.FloatProperty(
        name="Green",
        default=0.3,
        min=0.0,
        max=1.0,
        description="Green color component",
    )
    color_b: bpy.props.FloatProperty(
        name="Blue",
        default=0.3,
        min=0.0,
        max=1.0,
        description="Blue color component",
    )
    color_a: bpy.props.FloatProperty(
        name="Alpha",
        default=1.0,
        min=0.0,
        max=1.0,
        description="Alpha (transparency) component",
    )

    # Rotation parameters (in degrees)
    rotation_x: bpy.props.FloatProperty(
        name="Rotation X",
        default=0.0,
        min=-360.0,
        max=360.0,
        description="Rotation around X axis (degrees)",
    )
    rotation_y: bpy.props.FloatProperty(
        name="Rotation Y",
        default=0.0,
        min=-360.0,
        max=360.0,
        description="Rotation around Y axis (degrees)",
    )
    rotation_z: bpy.props.FloatProperty(
        name="Rotation Z",
        default=0.0,
        min=-360.0,
        max=360.0,
        description="Rotation around Z axis (degrees)",
    )

    # Location parameters
    location_x: bpy.props.FloatProperty(
        name="Location X",
        default=0.0,
        description="X coordinate of the ellipsoid center",
    )
    location_y: bpy.props.FloatProperty(
        name="Location Y",
        default=0.0,
        description="Y coordinate of the ellipsoid center",
    )
    location_z: bpy.props.FloatProperty(
        name="Location Z",
        default=0.0,
        description="Z coordinate of the ellipsoid center",
    )

    # Affine transformation matrix toggle
    use_affine_matrix: bpy.props.BoolProperty(
        name="Use Affine Matrix",
        default=False,
        description="Use custom affine transformation matrix",
    )

    # Affine matrix elements (4x4 matrix flattened)
    # Row 1
    affine_00: bpy.props.FloatProperty(default=1.0)
    affine_01: bpy.props.FloatProperty(default=0.0)
    affine_02: bpy.props.FloatProperty(default=0.0)
    affine_03: bpy.props.FloatProperty(default=0.0)
    # Row 2
    affine_10: bpy.props.FloatProperty(default=0.0)
    affine_11: bpy.props.FloatProperty(default=1.0)
    affine_12: bpy.props.FloatProperty(default=0.0)
    affine_13: bpy.props.FloatProperty(default=0.0)
    # Row 3
    affine_20: bpy.props.FloatProperty(default=0.0)
    affine_21: bpy.props.FloatProperty(default=0.0)
    affine_22: bpy.props.FloatProperty(default=1.0)
    affine_23: bpy.props.FloatProperty(default=0.0)
    # Row 4
    affine_30: bpy.props.FloatProperty(default=0.0)
    affine_31: bpy.props.FloatProperty(default=0.0)
    affine_32: bpy.props.FloatProperty(default=0.0)
    affine_33: bpy.props.FloatProperty(default=1.0)

    def execute(self, context):
        # Prepare u_range and v_range tuples
        u_range = (float(self.u_start), float(self.u_end))
        v_range = (float(self.v_start), float(self.v_end))

        # Prepare color tuple
        color = (
            float(self.color_r),
            float(self.color_g),
            float(self.color_b),
            float(self.color_a),
        )

        # Prepare location tuple
        location = (
            float(self.location_x),
            float(self.location_y),
            float(self.location_z),
        )

        # Prepare rotation tuple (will be converted to radians inside the function)
        rotation_euler_deg = (
            float(self.rotation_x),
            float(self.rotation_y),
            float(self.rotation_z),
        )

        # Prepare affine matrix if enabled
        affine_matrix = None
        if self.use_affine_matrix:
            affine_matrix = [
                [
                    float(self.affine_00),
                    float(self.affine_01),
                    float(self.affine_02),
                    float(self.affine_03),
                ],
                [
                    float(self.affine_10),
                    float(self.affine_11),
                    float(self.affine_12),
                    float(self.affine_13),
                ],
                [
                    float(self.affine_20),
                    float(self.affine_21),
                    float(self.affine_22),
                    float(self.affine_23),
                ],
                [
                    float(self.affine_30),
                    float(self.affine_31),
                    float(self.affine_32),
                    float(self.affine_33),
                ],
            ]

        obj = create_parametric_ellipsoid(
            a=float(self.a),
            b=float(self.b),
            c=float(self.c),
            u_res=int(self.u_res),
            v_res=int(self.v_res),
            u_range=u_range,
            v_range=v_range,
            color=color,
            affine_matrix=affine_matrix,
            rotation_euler_deg=rotation_euler_deg,
            location=location,
            keep_y_positive=bool(self.keep_y_positive),
        )
        if self.use_geometry_nodes and obj is not None:
            create_geometry_nodes_instancer(obj)
        return {"FINISHED"}

    def invoke(self, context, event):
        # Always show the property dialog
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout

        # Basic parameters
        box = layout.box()
        box.label(text="Basic Parameters:")
        row = box.row()
        row.prop(self, "a")
        row.prop(self, "b")
        row.prop(self, "c")

        # Resolution parameters
        box = layout.box()
        box.label(text="Resolution:")
        row = box.row()
        row.prop(self, "u_res")
        row.prop(self, "v_res")

        # Range parameters
        box = layout.box()
        box.label(text="Parameter Ranges (Radians):")
        row = box.row()
        col = row.column()
        col.prop(self, "u_start")
        col.prop(self, "u_end")
        col = row.column()
        col.prop(self, "v_start")
        col.prop(self, "v_end")

        # Color parameters
        box = layout.box()
        box.label(text="Color:")
        row = box.row()
        row.prop(self, "color_r", text="R")
        row.prop(self, "color_g", text="G")
        row.prop(self, "color_b", text="B")
        row.prop(self, "color_a", text="A")

        # Transform parameters
        box = layout.box()
        box.label(text="Transform:")
        # Location
        row = box.row()
        row.label(text="Location:")
        row.prop(self, "location_x", text="X")
        row.prop(self, "location_y", text="Y")
        row.prop(self, "location_z", text="Z")

        # Rotation
        row = box.row()
        row.label(text="Rotation:")
        row.prop(self, "rotation_x", text="X")
        row.prop(self, "rotation_y", text="Y")
        row.prop(self, "rotation_z", text="Z")

        # Affine matrix toggle
        box.prop(self, "use_affine_matrix")

        # Affine matrix elements (only shown when enabled)
        if self.use_affine_matrix:
            box.label(text="Affine Matrix:")
            # Row 1
            row = box.row()
            row.prop(self, "affine_00", text="")
            row.prop(self, "affine_01", text="")
            row.prop(self, "affine_02", text="")
            row.prop(self, "affine_03", text="")
            # Row 2
            row = box.row()
            row.prop(self, "affine_10", text="")
            row.prop(self, "affine_11", text="")
            row.prop(self, "affine_12", text="")
            row.prop(self, "affine_13", text="")
            # Row 3
            row = box.row()
            row.prop(self, "affine_20", text="")
            row.prop(self, "affine_21", text="")
            row.prop(self, "affine_22", text="")
            row.prop(self, "affine_23", text="")
            # Row 4
            row = box.row()
            row.prop(self, "affine_30", text="")
            row.prop(self, "affine_31", text="")
            row.prop(self, "affine_32", text="")
            row.prop(self, "affine_33", text="")

        # Other options
        box = layout.box()
        box.label(text="Options:")
        box.prop(self, "keep_y_positive")
        box.prop(self, "use_geometry_nodes")


class CPR_OT_create_gnodes_from_active(bpy.types.Operator):
    bl_idname = "cpr.create_gnodes_from_active"
    bl_label = "Create GN Instancer from Active"
    bl_description = "Create a geometry nodes instancer from the active object"
    bl_options = {"REGISTER", "UNDO"}

    rows: bpy.props.IntProperty(
        name="Rows",
        default=5,
        min=1,
        max=100,
        description="Number of rows in the grid",
    )
    cols: bpy.props.IntProperty(
        name="Columns",
        default=5,
        min=1,
        max=100,
        description="Number of columns in the grid",
    )
    spacing_x: bpy.props.FloatProperty(
        name="Spacing X",
        default=2.0,
        min=0.01,
        max=100.0,
        description="Spacing between rows",
    )
    spacing_y: bpy.props.FloatProperty(
        name="Spacing Y",
        default=2.0,
        min=0.01,
        max=100.0,
        description="Spacing between columns",
    )

    def execute(self, context):
        active_obj = context.active_object
        if active_obj is None:
            self.report({"ERROR"}, "No active object")
            return {"CANCELLED"}
        create_geometry_nodes_instancer(
            active_obj,
            rows=int(self.rows),
            cols=int(self.cols),
            spacing=(float(self.spacing_x), float(self.spacing_y)),
        )
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "rows")
        layout.prop(self, "cols")
        layout.separator()
        layout.prop(self, "spacing_x")
        layout.prop(self, "spacing_y")


class CPR_PT_ellipsoid_panel(bpy.types.Panel):
    bl_label = "CPR Ellipsoid"
    bl_idname = "CPR_PT_ellipsoid_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "CPR"

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Add Parametric Ellipsoid")

        # Quick buttons for common shapes
        row = col.row(align=True)
        op = row.operator("cpr.add_ellipsoid", text="Sphere")
        op.a = 1.0
        op.b = 1.0
        op.c = 1.0

        op = row.operator("cpr.add_ellipsoid", text="Ellipsoid")
        op.a = 2.0
        op.b = 1.0
        op.c = 1.0

        # Button for full parameter customization
        col.operator("cpr.add_ellipsoid", text="Custom Ellipsoid...")

        col.separator()
        col.label(text="Utilities")
        col.operator(
            "cpr.create_gnodes_from_active", text="Create GN Instancer from Active"
        )


def register():
    bpy.utils.register_class(CPR_OT_add_ellipsoid)
    bpy.utils.register_class(CPR_PT_ellipsoid_panel)
    bpy.utils.register_class(CPR_OT_create_gnodes_from_active)


def unregister():
    bpy.utils.unregister_class(CPR_OT_add_ellipsoid)
    bpy.utils.unregister_class(CPR_PT_ellipsoid_panel)
    bpy.utils.unregister_class(CPR_OT_create_gnodes_from_active)


M = Matrix(
    (
        (1.0, 0.0, 0.0, 0.0),
        (0.0, 1.0, 0.0, 0.0),
        (0.0, 0.0, 1.0, 0.0),
        (0.0, 0.0, 0.0, 1.0),
    )
)


def petal(
    a=2,
    b=1 / 3,
    c=2,
    n=4,
    u_res=100,
    v_res=100,
    color1=(1.0, 0.4, 1.0, 0.7),
    color2=(0, 1.0, 0, 0.7),
    affine_matrix=M,
    name="Petal",
    triangulate=True,
    use_bmesh=True,
    rotation_euler_deg=None,  # 绕原点的欧拉角旋转（度）
    quaternion=None,  # 绕原点的四元数旋转
    axis_angle=None,  # 绕原点的轴角旋转
    location=(0.0, 0.0, 0.0),  # 绕原点的平移
    scale=(1.0, 1.0, 1.0),  # 绕原点的缩放
):
    theta = np.pi / 2 - np.pi / n
    y_dist = c * np.cos(theta)
    x_dist = a * np.sin(theta)

    # 为右半部分创建矩阵
    A = affine_matrix.copy()
    A[0][3] += x_dist
    A[1][3] += -y_dist

    # 创建右半部分
    right_obj = create_parametric_ellipsoid(
        a,
        b,
        c,
        u_res,
        v_res,
        u_range=(0, np.pi),
        v_range=(0, theta),
        name=name + "_right",
        color=color1,
        affine_matrix=A,
        rotation_euler_deg=(-90, 0, 0),
        triangulate=triangulate,
        use_bmesh=use_bmesh,
    )

    # 为左半部分创建矩阵
    B = affine_matrix.copy()
    B[0][0] = -B[0][0]
    B[1][1] = -B[1][1]
    B[0][3] += x_dist
    B[1][3] += y_dist

    # 创建左半部分
    left_obj = create_parametric_ellipsoid(
        a,
        b,
        c,
        u_res,
        v_res,
        u_range=(0, np.pi),
        v_range=(0, theta),
        name=name + "_left",
        color=color2,
        affine_matrix=B,
        rotation_euler_deg=(-90, 0, 0),
        triangulate=triangulate,
        use_bmesh=use_bmesh,
    )

    # 创建一个空对象作为父级，用于整体变换
    if right_obj is not None and left_obj is not None:
        # 创建一个空对象作为父级
        parent_empty = bpy.data.objects.new(name + "_parent", None)
        bpy.context.collection.objects.link(parent_empty)

        # 设置整体变换
        if rotation_euler_deg is not None:
            parent_empty.rotation_euler = [
                math.radians(deg) for deg in rotation_euler_deg
            ]
        elif quaternion is not None:
            parent_empty.rotation_mode = "QUATERNION"
            parent_empty.rotation_quaternion = quaternion
        elif axis_angle is not None:
            axis, angle_deg = axis_angle
            # 将轴角转换为欧拉角（因为Blender的空对象不直接支持轴角旋转）
            quat = Quaternion(axis, math.radians(angle_deg))
            parent_empty.rotation_mode = "QUATERNION"
            parent_empty.rotation_quaternion = quat
        # 应用平移
        parent_empty.location = location
        # 应用缩放
        parent_empty.scale = scale

        # 设置父子关系
        right_obj.parent = parent_empty
        left_obj.parent = parent_empty


def flower(
    a=2,
    b=1 / 3,
    c=2,
    n=4,
    u_res=100,
    v_res=100,
    color1=(0.5, 1.0, 0.5, 0.7),
    color2=(0.5, 0.5, 1.0, 0.7),
    affine_matrix=M,
    name="Petal",
    triangulate=True,
    use_bmesh=True,
    rotation_euler_deg=(0, 0, 0),  # 绕原点的欧拉角旋转（度）
    quaternion=None,  # 绕原点的四元数旋转
    axis_angle=None,  # 绕原点的轴角旋转
    location=(0.0, 0.0, 0.0),  # 绕原点的平移
    scale=(1.0, 1.0, 1.0),  # 绕原点的缩放
):
    for i in range(12):
        petal(
            a,
            b,
            c,
            n,
            u_res,
            v_res,
            color1,
            color2,
            affine_matrix=affine_matrix,
            name=name + str(i + 1),
            triangulate=triangulate,
            use_bmesh=use_bmesh,
            rotation_euler_deg=(
                30 + rotation_euler_deg[0],
                -60 + rotation_euler_deg[1],
                i * 30 + 15 + rotation_euler_deg[2],
            ),  # 绕Z轴旋转30度
            quaternion=quaternion,
            axis_angle=axis_angle,
            location=location,
            scale=scale,  # 缩放
        )


def flowers(
    a=2,
    b=1 / 3,
    c=2,
    n=4,
    M=3,
    u_res=100,
    v_res=100,
    color1=(0.5, 1.0, 0.5, 0.7),
    color2=(0.5, 0.5, 1.0, 0.7),
    affine_matrix=M,
    name="Petal",
):
    for i in range(M):
        flower(
            a,
            b,
            c,
            n,
            u_res,
            v_res,
            color1,
            color2,
            affine_matrix=affine_matrix,
            name=name + "_" + str(i + 1),
            rotation_euler_deg=(30, -60, i * 30 + 15),
        )


clear_scene()
# 示例：创建一个
# petal(
#     a=2,
#     b=1 / 3,
#     c=2,
#     n=4,
#     u_res=100,
#     v_res=100,
#     color1=(1.0, 0.5, 0.5, 0.7),
#     color2=(1.0, 0.5, 0.5, 0.7),
#     affine_matrix=M,
#     name="Petal",
# )

# # 示例：使用新增的整体变换功能
# # 创建一个旋转30度、平移(2, 0, 0)、缩放(1.2, 1.2, 1.0)的
# petal(
#     a=2,
#     b=1 / 3,
#     c=2,
#     n=4,
#     u_res=100,
#     v_res=100,
#     color1=(0.5, 1.0, 0.5, 0.7),
#     color2=(0.5, 0.5, 1.0, 0.7),
#     affine_matrix=M,
#     name="Petal_Rotated",
#     rotation_euler_deg=(0, 0, 30),  # 绕Z轴旋转30度
#     location=(2, 0, 0),  # 平移
#     scale=(1.2, 1.2, 1.0),  # 缩放
# )

# a, b, c = 2, 1 / 3, 2
# n = 4
# u_res = 100
# v_res = 100
# color1 = (0.5, 1.0, 0.5, 0.7)
# color2 = (0.5, 0.5, 1.0, 0.7)

# for i in range(12):
#     petal(
#         a,
#         b,
#         c,
#         n,
#         u_res,
#         v_res,
#         color1,
#         color2,
#         affine_matrix=M,
#         name="Petal_L0_" + str(i + 1),
#         rotation_euler_deg=(15, 0, i * 30 + 15),  # 绕Z轴旋转30度
#         scale=(np.sqrt(8), np.sqrt(8), np.sqrt(8)),
#     )
#     petal(
#         a,
#         b,
#         c,
#         n,
#         u_res,
#         v_res,
#         color1,
#         color2,
#         affine_matrix=M,
#         name="Petal_L1_" + str(i + 1),
#         rotation_euler_deg=(15, -15, i * 30),  # 绕Z轴旋转30度
#         scale=(2, 2, 2),
#     )
#     petal(
#         a,
#         b,
#         c,
#         n,
#         u_res,
#         v_res,
#         color1,
#         color2,
#         affine_matrix=M,
#         name="Petal_L2_" + str(i + 1),
#         rotation_euler_deg=(30, -30, i * 30 + 15),  # 绕Z轴旋转30度
#         scale=(1.5, 1.5, 1.5),  # 缩放
#     )
#     petal(
#         a,
#         b,
#         c,
#         n,
#         u_res,
#         v_res,
#         color1,
#         color2,
#         affine_matrix=M,
#         name="Petal_L3_" + str(i + 1),
#         rotation_euler_deg=(30, -45, i * 30),  # 绕Z轴旋转30度
#         scale=(1.3, 1.3, 1.3),  # 缩放
#     )
#     petal(
#         a,
#         b,
#         c,
#         n,
#         u_res,
#         v_res,
#         color1,
#         color2,
#         affine_matrix=M,
#         name="Petal_L4_" + str(i + 1),
#         rotation_euler_deg=(30, -60, i * 30 + 15),  # 绕Z轴旋转30度
#         scale=(1, 1, 1),  # 缩放
#     )
flower()

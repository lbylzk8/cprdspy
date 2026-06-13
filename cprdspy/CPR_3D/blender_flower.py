"""blender_flower.py

Blender 脚本：在 Blender 环境中生成可扩展的花朵模型。

此文件提供几个可在 Blender (bpy) 环境中直接调用的函数：
- `ensure_collection`：确保场景中存在指定名称的 Collection（用于组织生成的对象）；
- `create_petal_curve`：生成一个椭圆/花瓣形状的 Curve 对象（带 bevel，使其具有厚度）；
- `add_material`：为对象创建或复用基础的节点材质并赋值；
- `create_flower`：以辐射方式复制花瓣生成整朵花；
- `clear_collection`：删除指定 Collection 及其对象（用于清理示例输出）。

使用方法：在 Blender 的 Scripting 面板打开本脚本并运行，或在命令行通过
`blender --background --python path/to/blender_flower.py` 执行（注意：命令行模式下
通常不会自动打开 UI，仅用于批量生成/渲染）。
"""

import math
from math import pi

try:
    # 在 Blender 的内置 Python 中可导入 bpy
    import bpy
except Exception:
    # 在非 Blender 环境（例如本地测试、静态分析）时，bpy 不可用
    bpy = None


def ensure_collection(name="CPR_Flowers"):
    """确保场景中存在名为 `name` 的 Collection 并返回它。

    参数:
        name (str): Collection 名称。

    返回:
        bpy.types.Collection | None: 如果 bpy 不可用返回 None，否则返回或创建后的 Collection 对象。
    """
    if bpy is None:
        # 如果不是在 Blender 环境中运行，直接返回 None（调用方需判断）
        return None
    # 尝试获取已有的 collection
    col = bpy.data.collections.get(name)
    if col is None:
        # 若不存在则新建并把它挂到主场景的 collection 下，便于在 Outliner 中查看
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def create_petal_curve(name="Petal", length=1.0, width=0.4, thickness=0.02, points=16):
    """创建一个封闭的花瓣曲线对象（Curve），并设置 bevel_depth 以获得可见厚度。

    实现要点：
    - 生成一组从花瓣根部到尖端的采样点（forward），用简单的数学函数控制轮廓形状；
    - 将 forward 与其沿中线镜像的点拼接，得到封闭轮廓；
    - 使用 POLY spline 并启用 cyclic（闭合），然后设置 bevel_depth 使曲线有厚度，
      最终返回一个未链接到场景的对象，调用方应把它 link 到目标 Collection 或 Scene。

    参数:
        name (str): 创建对象的名称（不含后缀）。
        length (float): 花瓣在 Y 方向的长度（从根到尖）。
        width (float): 花瓣中线最大半宽。
        thickness (float): 曲线的 bevel 深度，控制厚度。
        points (int): 用于近似轮廓的采样点数（单侧）。

    返回:
        bpy.types.Object: 创建的 Curve 对象（尚未 link 到 Collection）。
    """
    if bpy is None:
        raise RuntimeError(
            "This function must be run inside Blender (bpy not available)"
        )

    # 创建 Curve 数据容器并设置为 3D 曲线
    curve_data = bpy.data.curves.new(name + "_curve", type="CURVE")
    curve_data.dimensions = "3D"

    # 确保至少有 4 个采样点
    n = max(4, int(points))
    forward = []
    # 生成从花瓣根部到花瓣尖端的一侧轮廓（参数化 t 在 [0,1]）
    for i in range(n):
        t = i / (n - 1)
        # x: 横向形状，使用 sin 控制类似叶尖收窄的效果；
        # y: 纵向位置，使用幂函数让尖端更平滑（可调整）
        x = width * math.sin(math.pi * t)
        y = length * (t**0.9)
        # spline.points 使用四元组 (x,y,z,w)，w 通常设为 1
        forward.append((x, y, 0.0, 1.0))

    # 把 forward 与其镜像拼接得到闭合轮廓（沿中线对称）
    pts = forward + [(-x, y, z, w) for (x, y, z, w) in reversed(forward)]

    # 使用多边形样条（POLY）并设置点坐标
    spline = curve_data.splines.new("POLY")
    spline.points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        spline.points[i].co = p
    spline.use_cyclic_u = True

    # 设置 bevel，使曲线在渲染/视图中可见厚度
    curve_data.bevel_depth = thickness
    curve_data.bevel_resolution = 4

    # 返回 Curve 对应的 Object（尚未 link）
    curve_obj = bpy.data.objects.new(name, curve_data)
    return curve_obj


def add_material(obj, name="PetalMat", color=(1.0, 0.2, 0.2, 1.0)):
    """为对象添加或复用基础节点材质，并设置 Base Color。

    参数:
        obj (bpy.types.Object): 目标对象（通常为 Curve 或 Mesh）。
        name (str): 材质名称，若已存在则复用。
        color (tuple): RGBA 颜色（0-1 范围）。

    返回:
        bpy.types.Material | None: 创建或复用的材质对象；若 bpy 不可用则返回 None。
    """
    if bpy is None:
        return None
    mat = bpy.data.materials.get(name)
    if mat is None:
        # 不存在则新建并启用节点系统（Principled BSDF）
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf is not None:
            # 设置基础颜色与粗糙度，其他属性可由调用者通过节点进一步定制
            bsdf.inputs["Base Color"].default_value = color
            bsdf.inputs["Roughness"].default_value = 0.5
    # 将材质赋予对象（覆盖第一个插槽或新增）
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    return mat


def create_flower(
    num_petals=8,
    petal_length=1.0,
    petal_width=0.4,
    petal_thickness=0.02,
    radius=0.0,
    collection_name="CPR_Flowers",
    color=(0.9, 0.3, 0.6, 1.0),
):
    """以放射对称方式生成整朵花（重复花瓣曲线并旋转/平移）。

    实现说明：
    - 先创建一个基准花瓣 Curve（`petal_base`），并把它 link 到目标 Collection；
    - 对基准对象进行复制（`copy()`）并复制其数据块（`data.copy()`），这样每
      个花瓣都能单独编辑；
    - 通过设置 `rotation_euler`（绕 Z 轴）控制每片花瓣的朝向；
    - 如果传入 `radius`，花瓣将被沿径向挪动到指定半径位置，适用于制作环形多层
      或中心空心的造型；
    - 最后删除基准对象，仅保留复制出的花瓣（方便场景清洁）。

    参数:
        num_petals (int): 花瓣数量。
        petal_length (float): 单片花瓣的长度（传递给 create_petal_curve）。
        petal_width (float): 单片花瓣的宽度（传递给 create_petal_curve）。
        petal_thickness (float): 花瓣 bevel 厚度。
        radius (float): 如果 >0，则将每片花瓣沿径向偏移该距离。
        collection_name (str): 目标 Collection 名称。
        color (tuple): RGBA 颜色，传递给材质创建函数。

    返回:
        list[bpy.types.Object]: 创建的花瓣对象列表。
    """
    if bpy is None:
        raise RuntimeError("Run inside Blender (bpy not available)")

    # 获取或创建用于存放花瓣的 Collection
    col = ensure_collection(collection_name)

    # 创建基准花瓣并加入 Collection
    base = create_petal_curve(
        "petal_base", length=petal_length, width=petal_width, thickness=petal_thickness
    )
    col.objects.link(base)
    # 给基准对象赋材质（复制出的对象会共享材质引用）
    add_material(base, name="PetalMat", color=color)

    created = []
    for i in range(num_petals):
        # 计算每个花瓣绕 Z 轴的角度（均匀分布）
        angle = i * 2 * pi / num_petals
        # 复制对象与复制其数据块，以便后续可单独编辑每片花瓣的形状
        petal = base.copy()
        petal.data = base.data.copy()
        petal.name = f"petal_{i:02d}"
        # 设置旋转，使花瓣尖端朝外（XY 平面）
        petal.rotation_euler = (0.0, 0.0, angle)
        # 可选：沿径向平移到 radius（用于多层或环形排布）
        if radius:
            petal.location = (math.cos(angle) * radius, math.sin(angle) * radius, 0.0)
        col.objects.link(petal)
        created.append(petal)

    # 删除模板基准对象（仅保留复制出的花瓣），避免在场景中留下不必要的对象
    bpy.data.objects.remove(base, do_unlink=True)
    return created


def clear_collection(collection_name="CPR_Flowers"):
    """删除指定 Collection 及其包含的所有对象（用于示例重置/清理）。

    注意：此操作会永久删除场景中的对象，谨慎调用。
    """
    if bpy is None:
        return
    col = bpy.data.collections.get(collection_name)
    if not col:
        return
    # 先删除 collection 中的对象，再移除 collection
    for obj in list(col.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    bpy.data.collections.remove(col)


if __name__ == "__main__":
    if bpy is None:
        print("This script must be run inside Blender's Python environment.")
    else:
        # 示例：先清空目标 collection，然后生成一朵 12 片花瓣的花
        clear_collection("CPR_Flowers")
        create_flower(
            num_petals=12,
            petal_length=1.2,
            petal_width=0.45,
            petal_thickness=0.02,
            radius=0.0,
            collection_name="CPR_Flowers",
            color=(0.9, 0.3, 0.6, 1.0),
        )
        print("Flower created in collection CPR_Flowers.")

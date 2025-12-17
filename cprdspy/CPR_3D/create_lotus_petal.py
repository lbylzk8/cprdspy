"""
创建单个平滑睡莲花瓣
扁平、水平展开，完全弧形，无直线棱角，优化的顶点数避免崩溃
"""

import bpy
import bmesh
from mathutils import Vector
from math import radians, sin, cos, pi, sqrt

# 清除场景中现有的网格对象
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def create_smooth_water_lily_petal():
    """创建一朵平滑的睡莲花瓣，扁平、水平展开，完全弧形，无棱角
    
    睡莲花瓣特点：
    - 扁平，水平展开（不像莲花那样向后弯曲）
    - 椭圆形，前端圆润，后端较窄
    - 完全平滑的弧形边缘，无直线
    - 适合浮在水面上的扁平结构
    - 合理的顶点数，避免崩溃
    """
    mesh = bpy.data.meshes.new(name="WaterLilyPetal")
    obj = bpy.data.objects.new("WaterLilyPetal", mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    # 使用合理的细分段数（不会导致崩溃）
    num_segments_length = 16  # 长度方向段数（圆形边缘）
    num_segments_width = 12   # 宽度方向段数
    
    length = 1.8  # 花瓣长度
    max_width = 1.5  # 最大宽度（睡莲花瓣较宽）
    
    verts = []
    
    # 创建扁平椭圆形的花瓣顶点网格
    for i in range(num_segments_length):
        t_length = i / (num_segments_length - 1)  # 0 到 1
        
        # 宽度变化：前端（上方）较宽，后端（下方）较窄
        # 使用椭圆函数创建平滑的宽度变化
        if t_length < 0.5:
            # 前半部分：逐渐变宽
            width_factor = sin(t_length * pi)
        else:
            # 后半部分：逐渐变窄
            width_factor = sin((1 - t_length) * pi)
        
        for j in range(num_segments_width):
            t_width = (j / (num_segments_width - 1) - 0.5) * 2  # -1 到 1
            
            # 宽度：椭圆形状，中间宽两边窄
            width = max_width * width_factor * sqrt(1 - t_width * t_width)
            
            # X坐标（宽度方向）
            x = width * t_width
            
            # Y坐标（长度方向，椭圆形分布）
            # 前端向上，后端向下，形成椭圆形
            angle = t_length * pi - pi/2  # 从 -90度到 90度
            y = sin(angle) * length
            
            # Z坐标：扁平结构，只有轻微厚度
            # 花瓣边缘轻微向上弯曲
            thickness_factor = cos(t_width * pi / 2)
            edge_curve = 0.02 * sin(t_width * pi) * width_factor  # 边缘轻微起伏
            z = 0.01 * thickness_factor + edge_curve  # 非常薄的扁平结构
            
            verts.append(bm.verts.new((x, y, z)))
    
    # 创建圆润的尖端（前端中心点）
    tip_x = 0
    tip_y = length + 0.1
    tip_z = 0.02
    tip_vert = bm.verts.new((tip_x, tip_y, tip_z))
    
    # 创建面：连接所有顶点形成平滑网格
    for i in range(num_segments_length - 1):
        for j in range(num_segments_width - 1):
            idx1 = i * num_segments_width + j
            idx2 = i * num_segments_width + (j + 1)
            idx3 = (i + 1) * num_segments_width + (j + 1)
            idx4 = (i + 1) * num_segments_width + j
            
            try:
                bm.faces.new([verts[idx1], verts[idx2], verts[idx3], verts[idx4]])
            except:
                pass
    
    # 连接最后一行（前端）到尖端
    last_row_start = (num_segments_length - 1) * num_segments_width
    last_row_verts = verts[last_row_start:]
    
    for j in range(len(last_row_verts) - 1):
        try:
            bm.faces.new([last_row_verts[j], last_row_verts[j+1], tip_vert])
        except:
            pass
    
    # 创建底部边缘（闭合后端）
    first_row_verts = verts[:num_segments_width]
    base_center = bm.verts.new((0, -length - 0.1, 0))
    
    for j in range(len(first_row_verts) - 1):
        try:
            bm.faces.new([first_row_verts[j], first_row_verts[j+1], base_center])
        except:
            pass
    
    bm.to_mesh(mesh)
    bm.free()
    
    # 添加细分曲面修饰器 - 使用合理的级别
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    # 单个高细分修饰器（比多层更稳定）
    mod = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    mod.levels = 3  # 合理的细分级别，既能平滑又不会导致崩溃
    
    return obj

# 创建花瓣
print("开始创建睡莲花瓣...")
petal = create_smooth_water_lily_petal()
petal.location = (0, 0, 0)
# 旋转90度使其水平放置（X轴旋转-90度）
petal.rotation_euler = (radians(-90), 0, 0)
print("花瓣几何体创建完成")

# 创建材质
petal_material = bpy.data.materials.new(name="WaterLilyPetalMaterial")
petal_material.use_nodes = True
if petal_material.use_nodes:
    nodes = petal_material.node_tree.nodes
    links = petal_material.node_tree.links
    nodes.clear()
    output = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    links.new(bsdf.outputs[0], output.inputs[0])
    # 睡莲花瓣颜色：白色到淡粉色
    bsdf.inputs["Base Color"].default_value = (1.0, 0.95, 0.98, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.7

# 应用材质和平滑着色
petal = bpy.data.objects.get("WaterLilyPetal")
if petal:
    petal.data.materials.append(petal_material)
    bpy.context.view_layer.objects.active = petal
    if petal.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()

print("材质已应用，花瓣已平滑着色")

# 设置光照
if "Sun" in bpy.data.objects:
    sun = bpy.data.objects["Sun"]
    sun.data.energy = 5
    sun.location = (3, 3, 6)
else:
    bpy.ops.object.light_add(type='SUN', location=(3, 3, 6))
    sun = bpy.context.active_object
    sun.data.energy = 5

# 添加区域光源（从上方照亮，适合俯视睡莲）
bpy.ops.object.light_add(type='AREA', location=(0, 0, 5))
area_light = bpy.context.active_object
area_light.data.energy = 100
area_light.data.size = 8

# 调整相机以俯视角度展示（睡莲适合从上往下看）
if "Camera" in bpy.data.objects:
    camera = bpy.data.objects["Camera"]
    camera.location = (0, -8, 6)
    camera.rotation_euler = (radians(50), 0, 0)
    camera.data.lens = 50

# 设置视图模式
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'SOLID'
                space.shading.color_type = 'MATERIAL'
                space.shading.light = 'STUDIO'

# 获取花瓣对象
petal = bpy.data.objects.get("WaterLilyPetal")
if petal:
    print("=" * 60)
    print("睡莲花瓣创建完成！")
    print("=" * 60)
    print(f"  基础顶点数：{len(petal.data.vertices)}")
    print(f"  基础面数：{len(petal.data.polygons)}")
    print(f"  细分级别：3")
    print(f"  材质：白色到淡粉色")
    print(f"  特点：扁平、水平展开，完全平滑的弧形")
    print("=" * 60)
else:
    print("错误：花瓣对象未找到")


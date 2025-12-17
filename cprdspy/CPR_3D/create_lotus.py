import bpy
import bmesh
from mathutils import Vector
from math import radians, sin, cos, pi
import random

# 清除场景中现有的网格对象
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def create_lotus_petal(layer_num, petal_width=1.0, petal_length=1.0, curve_strength=0.3):
    """创建莲花花瓣
    
    参数:
        layer_num: 层数（用于调整大小）
        petal_width: 花瓣宽度
        petal_length: 花瓣长度
        curve_strength: 弯曲强度
    """
    mesh = bpy.data.meshes.new(name=f"LotusPetal_Layer{layer_num}")
    obj = bpy.data.objects.new(f"LotusPetal_Layer{layer_num}", mesh)
    bpy.context.collection.objects.link(obj)
    
    bm = bmesh.new()
    
    # 创建花瓣的顶点（椭圆形，尖端圆润）
    verts = []
    
    # 花瓣底部边缘（较宽）
    num_points = 10
    for i in range(num_points):
        t = i / (num_points - 1)
        angle = (t - 0.5) * pi * 0.6  # 底部弧度
        # 底部宽度逐渐变窄
        width_factor = 1.0 - abs(t - 0.5) * 1.2
        x = cos(angle) * petal_width * width_factor
        y = sin(angle) * petal_width * 0.3
        z = 0
        verts.append(bm.verts.new((x, y, z)))
    
    # 花瓣顶部（圆润的尖端）
    top_verts = []
    num_top = 6
    for i in range(num_top):
        t = i / (num_top - 1)
        angle = (t - 0.5) * pi * 0.3  # 顶部弧度更小
        width_factor = 1.0 - abs(t - 0.5) * 2.0
        x = cos(angle) * petal_width * 0.15 * width_factor
        y = petal_length * (0.7 + t * 0.3)
        z = 0
        top_verts.append(bm.verts.new((x, y, z)))
    
    # 花瓣最尖端
    top_point = bm.verts.new((0, petal_length, 0))
    
    # 创建侧面（底部到顶部）
    all_verts = verts + top_verts + [top_point]
    
    # 创建底部面
    bm.faces.new(verts)
    
    # 创建侧面三角形（底部边缘到顶部）
    for i in range(len(verts) - 1):
        # 找到对应的顶部顶点
        top_idx = int((i / (len(verts) - 1)) * len(top_verts))
        if top_idx >= len(top_verts):
            top_idx = len(top_verts) - 1
        top_vert = top_verts[top_idx]
        bm.faces.new([verts[i], verts[i+1], top_vert])
    
    # 创建顶部面
    bm.faces.new(top_verts + [top_point])
    
    bm.to_mesh(mesh)
    bm.free()
    
    # 添加细分曲面修饰器
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_add(type='SUBSURF')
    obj.modifiers["Subdivision Surface"].levels = 2
    
    return obj

def create_lotus_center():
    """创建莲花中心的花蕊部分"""
    # 创建花蕊底座（圆锥形）
    bpy.ops.mesh.primitive_cone_add(radius1=0.15, radius2=0.05, depth=0.2, location=(0, 0, 0))
    center_base = bpy.context.active_object
    center_base.name = "LotusCenterBase"
    center_base.location.z = 0.05
    
    # 创建多个小圆点作为花蕊
    stamens = []
    num_stamens = 20
    for i in range(num_stamens):
        angle = (i / num_stamens) * 2 * pi
        radius = random.uniform(0.03, 0.12)
        x = cos(angle) * radius
        y = sin(angle) * radius
        
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.015, location=(x, y, 0.12))
        stamen = bpy.context.active_object
        stamen.name = f"Stamen_{i}"
        stamens.append(stamen)
    
    return center_base, stamens

def create_lotus():
    """创建完整的莲花模型"""
    
    # 莲花层次结构：3-4层花瓣
    layers_config = [
        {"petals": 12, "width": 1.2, "length": 1.5, "height": -0.1, "angle": 20, "scale": 1.0},  # 最外层
        {"petals": 12, "width": 1.0, "length": 1.3, "height": 0.05, "angle": 15, "scale": 0.85},  # 第二层
        {"petals": 10, "width": 0.8, "length": 1.1, "height": 0.15, "angle": 10, "scale": 0.7},   # 第三层
        {"petals": 8, "width": 0.6, "length": 0.9, "height": 0.25, "angle": 5, "scale": 0.55},    # 第四层（内层）
    ]
    
    all_petals = []
    
    # 创建每一层
    for layer_idx, layer_config in enumerate(layers_config):
        layer_petals = []
        
        for i in range(layer_config["petals"]):
            # 创建花瓣
            petal = create_lotus_petal(
                layer_idx,
                petal_width=layer_config["width"],
                petal_length=layer_config["length"]
            )
            
            # 计算位置和旋转
            angle = (i / layer_config["petals"]) * 360
            
            # 位置（圆形排列）
            radius = 0.1 * (layer_idx + 1)  # 每层稍微向外偏移
            x = cos(radians(angle)) * radius
            y = sin(radians(angle)) * radius
            z = layer_config["height"]
            
            petal.location = Vector((x, y, z))
            
            # 旋转
            petal.rotation_euler.z = radians(angle)
            petal.rotation_euler.x = radians(layer_config["angle"])  # 外层向下倾斜
            
            # 缩放
            petal.scale = (layer_config["scale"], layer_config["scale"], layer_config["scale"])
            
            # 添加轻微随机旋转，使更自然
            petal.rotation_euler.z += radians(random.uniform(-5, 5))
            petal.rotation_euler.x += radians(random.uniform(-3, 3))
            
            layer_petals.append(petal)
        
        all_petals.extend(layer_petals)
    
    # 创建中心花蕊
    center_base, stamens = create_lotus_center()
    
    # 创建材质
    # 花瓣材质（粉白色到粉红色渐变）
    petal_material = bpy.data.materials.new(name="LotusPetalMaterial")
    petal_material.use_nodes = True
    bsdf = petal_material.node_tree.nodes["Principled BSDF"]
    # 莲花通常是粉白色或淡粉色
    bsdf.inputs["Base Color"].default_value = (1.0, 0.85, 0.9, 1.0)  # 淡粉色
    bsdf.inputs["Roughness"].default_value = 0.6
    bsdf.inputs["Specular"].default_value = 0.3
    
    # 中心花蕊材质（黄色到绿色）
    center_material = bpy.data.materials.new(name="LotusCenterMaterial")
    center_material.use_nodes = True
    bsdf = center_material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.9, 0.8, 0.3, 1.0)  # 淡黄色
    bsdf.inputs["Roughness"].default_value = 0.4
    
    # 花蕊材质（黄色）
    stamen_material = bpy.data.materials.new(name="StamenMaterial")
    stamen_material.use_nodes = True
    bsdf = stamen_material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (1.0, 0.9, 0.4, 1.0)  # 金黄色
    bsdf.inputs["Roughness"].default_value = 0.3
    bsdf.inputs["Metallic"].default_value = 0.1
    
    # 应用材质到花瓣
    for petal in all_petals:
        petal.data.materials.append(petal_material)
        bpy.context.view_layer.objects.active = petal
        bpy.ops.object.shade_smooth()
    
    # 应用材质到中心
    center_base.data.materials.append(center_material)
    center_base.select_set(True)
    bpy.context.view_layer.objects.active = center_base
    bpy.ops.object.shade_smooth()
    
    # 应用材质到花蕊
    for stamen in stamens:
        stamen.data.materials.append(stamen_material)
    
    # 选择所有对象以便查看
    all_objects = all_petals + [center_base] + stamens
    for obj in all_objects:
        obj.select_set(True)
    
    if all_objects:
        bpy.context.view_layer.objects.active = all_objects[0]
    
    # 设置渲染引擎为Cycles
    bpy.context.scene.render.engine = 'CYCLES'
    
    # 添加光源
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 3
    
    # 添加相机（可选）
    bpy.ops.object.camera_add(location=(5, -5, 3))
    camera = bpy.context.active_object
    camera.rotation_euler = (radians(60), 0, radians(45))
    
    print(f"莲花创建完成！")
    print(f"  - 共创建了 {len(all_petals)} 个花瓣")
    print(f"  - {len(layers_config)} 层花瓣结构")
    print(f"  - {len(stamens)} 个花蕊")

# 执行创建
create_lotus()

print("\n莲花建模完成！")
print("提示：您可以调整材质颜色和花瓣形状来创建不同风格的莲花。")



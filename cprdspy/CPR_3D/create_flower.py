import bpy
import mathutils
from mathutils import Vector
import bmesh
from math import radians, sin, cos, pi

# 清除场景中现有的网格对象
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 创建花瓣函数
def create_petal():
    """创建一个花瓣"""
    # 创建一个新的网格
    mesh = bpy.data.meshes.new(name="Petal")
    obj = bpy.data.objects.new("Petal", mesh)
    bpy.context.collection.objects.link(obj)
    
    # 使用bmesh创建花瓣形状
    bm = bmesh.new()
    
    # 创建花瓣的顶点（椭圆形，一端较尖）
    verts = []
    # 花瓣底部（宽）
    for i in range(8):
        angle = (i / 8) * 2 * pi
        x = cos(angle) * 0.3
        y = sin(angle) * 0.15
        z = 0
        verts.append(bm.verts.new((x, y, z)))
    
    # 花瓣顶部（尖）
    verts.append(bm.verts.new((0, 0.5, 0)))
    
    # 创建中心点
    center = bm.verts.new((0, 0, 0))
    
    # 创建面：底部到顶部的三角形
    for i in range(8):
        next_i = (i + 1) % 8
        bm.faces.new([verts[i], verts[next_i], verts[8]])
    
    # 创建底部面
    bm.faces.new(verts[:8])
    
    # 更新网格
    bm.to_mesh(mesh)
    bm.free()
    
    # 添加细分曲面修饰器使花瓣更平滑
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_add(type='SUBSURF')
    obj.modifiers["Subdivision Surface"].levels = 2
    
    return obj

# 创建花蕊函数
def create_stamen(length=0.5):
    """创建花蕊"""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(0, 0, 0))
    stamen_head = bpy.context.active_object
    stamen_head.name = "StamenHead"
    stamen_head.location.z = length * 0.8
    
    bpy.ops.mesh.primitive_cylinder_add(radius=0.01, depth=length, location=(0, 0, length/2))
    stamen_stem = bpy.context.active_object
    stamen_stem.name = "StamenStem"
    
    # 选择两个对象并合并
    stamen_head.select_set(True)
    stamen_stem.select_set(True)
    bpy.context.view_layer.objects.active = stamen_stem
    bpy.ops.object.join()
    stamen_stem.name = "Stamen"
    
    return stamen_stem

# 创建花朵
def create_flower():
    """创建完整的花朵"""
    petals = []
    
    # 创建5个外层花瓣
    for i in range(5):
        petal = create_petal()
        petals.append(petal)
        
        # 旋转并放置花瓣
        angle = (i / 5) * 360
        petal.rotation_euler.z = radians(angle)
        petal.location = Vector((0, 0, 0))
        petal.rotation_euler.x = radians(10)  # 轻微向上倾斜
    
    # 创建内层小花瓣（3个）
    for i in range(3):
        petal = create_petal()
        petal.scale = (0.6, 0.6, 0.6)
        petals.append(petal)
        
        angle = (i / 3) * 360 + 60  # 偏移角度
        petal.rotation_euler.z = radians(angle)
        petal.location.z = 0.1
        petal.rotation_euler.x = radians(5)
    
    # 创建花蕊（多个花蕊）
    stamens = []
    for i in range(5):
        angle = (i / 5) * 360
        stamen = create_stamen(0.3)
        stamens.append(stamen)
        
        radius = 0.08
        x = cos(radians(angle)) * radius
        y = sin(radians(angle)) * radius
        stamen.location = Vector((x, y, 0.15))
    
    # 中心花蕊
    center_stamen = create_stamen(0.4)
    center_stamen.location.z = 0.15
    center_stamen.scale = (1.5, 1.5, 1.5)
    stamens.append(center_stamen)
    
    # 添加材质
    # 花瓣材质（粉色）
    petal_material = bpy.data.materials.new(name="PetalMaterial")
    petal_material.use_nodes = True
    bsdf = petal_material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (1.0, 0.7, 0.8, 1.0)  # 粉红色
    bsdf.inputs["Roughness"].default_value = 0.5
    
    # 花蕊材质（黄色）
    stamen_material = bpy.data.materials.new(name="StamenMaterial")
    stamen_material.use_nodes = True
    bsdf = stamen_material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (1.0, 0.9, 0.3, 1.0)  # 黄色
    bsdf.inputs["Roughness"].default_value = 0.3
    
    # 应用材质到花瓣
    for petal in petals:
        petal.data.materials.append(petal_material)
    
    # 应用材质到花蕊
    for stamen in stamens:
        stamen.data.materials.append(stamen_material)
    
    # 平滑花瓣
    for petal in petals:
        bpy.context.view_layer.objects.active = petal
        bpy.ops.object.shade_smooth()
    
    # 选择所有对象
    all_objects = petals + stamens
    for obj in all_objects:
        obj.select_set(True)
    
    # 设置活动对象
    if all_objects:
        bpy.context.view_layer.objects.active = all_objects[0]
    
    print(f"花朵创建完成！共创建了 {len(petals)} 个花瓣和 {len(stamens)} 个花蕊")

# 执行创建
create_flower()

# 设置渲染引擎为Cycles以获得更好的效果
bpy.context.scene.render.engine = 'CYCLES'

print("花朵建模完成！")



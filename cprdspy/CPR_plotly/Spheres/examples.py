"""
Ellipsoid plotting examples and tests.
椭球绘制示例与测试。
"""

# 导入
from cprdspy.CPR_plotly.Spheres.ellipsoid import ellipsoid, ellipsoids
import numpy as np

# ============ 示例 1: 基础球体 ============
print("示例 1: 基础球体")
fig1 = ellipsoid(name="Unit Sphere")
# fig1.show()

# ============ 示例 2: 标准椭球 ============
print("示例 2: 椭球（a=2, b=1.5, c=0.8）")
fig2 = ellipsoid(a=2, b=1.5, c=0.8, name="Ellipsoid", u_res=40, v_res=40)
# fig2.show()

# ============ 示例 3: 平移椭球 ============
print("示例 3: 平移到 (3, 2, 1)")
fig3 = ellipsoid(a=1.5, b=1, c=1.2, center=(3, 2, 1), name="Translated")
# fig3.show()

# ============ 示例 4: 旋转椭球（欧拉角） ============
print("示例 4: 旋转 (45°, 30°, 60°)")
fig4 = ellipsoid(
    a=2, b=1, c=0.5, rotation=(45, 30, 60), name="Rotated", u_res=50, v_res=50
)
# fig4.show()

# ============ 示例 5: 网格模式 ============
print("示例 5: 网格模式（wireframe=True）")
fig5 = ellipsoid(
    a=1.5, b=1, c=0.8, wireframe=True, color="rgba(0, 0, 0, 0.8)", name="Wireframe"
)
# fig5.show()

# ============ 示例 6: 多个椭球 ============
print("示例 6: 多个椭球组合")
fig6 = ellipsoids(
    {"a": 1, "b": 1, "c": 1, "color": "rgba(255, 0, 0, 0.6)", "name": "Red Sphere"},
    {
        "a": 1.5,
        "b": 1,
        "c": 2,
        "center": (3, 0, 0),
        "color": "rgba(0, 255, 0, 0.6)",
        "name": "Green Ellipsoid",
        "u_res": 40,
    },
    {
        "a": 0.8,
        "b": 0.8,
        "c": 1.2,
        "rotation": (45, 30, 60),
        "center": (1.5, 1.5, 0),
        "color": "rgba(0, 0, 255, 0.6)",
        "name": "Blue Rotated",
    },
    title="Multiple Ellipsoids",
    figsize=(1000, 800),
)
# fig6.show()

# ============ 示例 7: 复杂组合（网格与实心） ============
print("示例 7: 混合网格与实心")
fig7 = ellipsoid(a=1, b=1, c=1, name="Base Sphere")
ellipsoid(
    a=1.5,
    b=0.8,
    c=2,
    center=(2.5, 0, 0),
    rotation=(20, 45, 0),
    color="rgba(100, 200, 255, 0.7)",
    wireframe=False,
    name="Rotated Ellipsoid",
    fig=fig7,
)
ellipsoid(
    a=0.5,
    b=0.5,
    c=0.5,
    center=(-1, 1, 0),
    wireframe=True,
    color="rgba(0, 0, 0, 0.8)",
    name="Small Wireframe",
    fig=fig7,
)
# fig7.show()

# ============ 示例 8: 参数化控制 ============
print("示例 8: 参数化生成多个椭球")
ellipsoid_configs = [
    {"a": 0.5 + 0.3 * i, "b": 0.8, "c": 1.2, "center": (i * 1.5, 0, 0)}
    for i in range(4)
]
fig8 = ellipsoids(*ellipsoid_configs, title="Parametric Ellipsoids")
# fig8.show()

print("\nAll examples created successfully!")
print("\nUsage:")
print("  fig = ellipsoid(a=1, b=2, c=3, center=(x,y,z), rotation=(rx,ry,rz))")
print("  ellipsoids(config1, config2, ...) - multiple ellipsoids in one figure")

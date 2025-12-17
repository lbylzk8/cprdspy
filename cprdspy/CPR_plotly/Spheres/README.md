# Ellipsoid Plotly Module

简洁强大的 Plotly 椭球绘制模块。支持完全可定制：3 种半轴、旋转、位置、颜色、透明度、网格密度。

## 核心函数

### `ellipsoid(...)`
绘制单个椭球。

**关键参数：**
| 参数           | 说明                            | 默认值                |
| -------------- | ------------------------------- | --------------------- |
| `a, b, c`      | 三个方向半轴长度                | 1, 1, 1               |
| `center`       | 椭球中心 (x, y, z)              | (0, 0, 0)             |
| `rotation`     | 欧拉角旋转 (rx, ry, rz)，单位度 | None                  |
| `u_res, v_res` | 网格分辨率                      | 30, 30                |
| `color`        | 颜色（rgba/hex/名字）           | rgba(100,150,255,0.7) |
| `wireframe`    | 网格模式                        | False                 |
| `name`         | 图例名                          | 'Ellipsoid'           |
| `show_axes`    | 显示坐标轴                      | False                 |
| `fig`          | 已有 Figure，None 创建新的      | None                  |
| `**kwargs`     | 其他 Plotly Surface 参数        | —                     |

**返回：** Plotly Figure 对象

### `ellipsoids(..., title='', figsize=(900, 700))`
一次性绘制多个椭球。

**参数：**
- `*args`：可变数量的字典，每个字典作为 `ellipsoid()` 的参数包
- `title`：图表标题
- `figsize`：(宽, 高)

**返回：** Plotly Figure 对象

## 快速示例

### 基础球体
```python
from cprdspy.CPR_plotly.Spheres import ellipsoid

fig = ellipsoid()
fig.show()
```

### 椭球（三轴不同）
```python
fig = ellipsoid(a=2, b=1.5, c=0.8)
fig.show()
```

### 平移 + 旋转
```python
fig = ellipsoid(
    a=2, b=1.5, c=0.8,
    center=(3, 2, 1),
    rotation=(45, 30, 60),  # 欧拉角，度数
    u_res=50, v_res=50      # 高精度
)
fig.show()
```

### 网格模式（只显示线框）
```python
fig = ellipsoid(
    a=1.5, b=1, c=0.8,
    wireframe=True,
    color='rgba(0, 0, 0, 0.8)'
)
fig.show()
```

### 多个椭球
```python
from cprdspy.CPR_plotly.Spheres import ellipsoids

fig = ellipsoids(
    {'a': 1, 'b': 1, 'c': 1, 'color': 'rgba(255, 0, 0, 0.6)'},
    {'a': 1.5, 'b': 1, 'c': 2, 'center': (3, 0, 0), 'color': 'rgba(0, 255, 0, 0.6)'},
    {'a': 0.8, 'b': 0.8, 'c': 1.2, 'rotation': (45, 30, 60), 'color': 'rgba(0, 0, 255, 0.6)'},
    title='Triple Ellipsoids',
    figsize=(1000, 800)
)
fig.show()
```

### 混合：网格 + 实心
```python
fig = ellipsoid(a=1, b=1, c=1, name='Base')

# 在同一 Figure 上添加旋转椭球
ellipsoid(
    a=1.5, b=0.8, c=2,
    center=(2.5, 0, 0),
    rotation=(20, 45, 0),
    fig=fig,
    name='Overlay'
)

fig.show()
```

### 参数扫描
```python
configs = [
    {'a': 0.5 + 0.3*i, 'b': 0.8, 'c': 1.2, 'center': (i*1.5, 0, 0)}
    for i in range(5)
]
fig = ellipsoids(*configs, title='Parametric Sweep')
fig.show()
```

## 特性

✓ **简洁 API**：仅 2 个函数  
✓ **高度定制**：半轴、位置、旋转、颜色、分辨率、网格/实心  
✓ **欧拉角旋转**：标准 Z-Y-X 旋转矩阵，易于理解  
✓ **批量绘制**：`ellipsoids()` 一次画多个  
✓ **灵活叠加**：传入 `fig` 参数在已有 Figure 上追加  
✓ **网格模式**：`wireframe=True` 显示仅框架  
✓ **无依赖**：仅依赖 `numpy` 和 `plotly`  

## 数学细节

- **参数化椭球面**：
  - $x = a \cos(u) \sin(v)$
  - $y = b \sin(u) \sin(v)$
  - $z = c \cos(v)$
  - 其中 $u \in [0, 2\pi)$，$v \in [0, \pi]$

- **旋转矩阵**：使用欧拉角 (rx, ry, rz)，按 Z-Y-X 顺序应用旋转：
  $$R = R_z(rz) \cdot R_y(ry) \cdot R_x(rx)$$

- **分辨率影响**：`u_res` × `v_res` 网格点数决定曲面光滑度

## 文件结构

```
cprdspy/CPR_plotly/Spheres/
  ├── ellipsoid.py      # 核心函数实现
  ├── __init__.py       # 模块导出
  ├── examples.py       # 8 个使用示例
  └── README.md         # 本文档
```

## 安装与使用

1. 确保已安装依赖：
   ```bash
   pip install plotly numpy
   ```

2. 导入使用：
   ```python
   from cprdspy.CPR_plotly.Spheres import ellipsoid, ellipsoids
   ```

3. 或直接运行示例：
   ```bash
   python -m cprdspy.CPR_plotly.Spheres.examples
   ```

## 常见问题

**Q: 如何调整质量（平滑度）？**  
A: 增大 `u_res` 和 `v_res`，如 `u_res=60, v_res=60`（默认 30）。

**Q: 如何透明化？**  
A: 用 `rgba` 颜色，如 `'rgba(255, 0, 0, 0.5)'`（最后数字 0~1）。

**Q: 旋转如何指定？**  
A: 使用欧拉角 `rotation=(rx, ry, rz)`，单位度。按 Z-Y-X 顺序应用。

**Q: 能否同时绘制多种椭球？**  
A: 可以，用 `fig=fig` 参数或使用 `ellipsoids()` 一次性多个。

**Q: 如何导出图像？**  
A: 用 Plotly UI 上的相机按钮导出 PNG，或用 `fig.write_html('file.html')`。

## 许可

MIT License

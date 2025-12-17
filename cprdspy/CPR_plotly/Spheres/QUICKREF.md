# Ellipsoid 模块快速参考

## 导入
```python
from cprdspy.CPR_plotly import ellipsoid, ellipsoids
# 或
from cprdspy.CPR_plotly.Spheres import ellipsoid, ellipsoids
```

## 一句话用法

| 需求     | 代码                                                    |
| -------- | ------------------------------------------------------- |
| 基础球体 | `ellipsoid().show()`                                    |
| 椭球     | `ellipsoid(a=2, b=1.5, c=0.8).show()`                   |
| 平移     | `ellipsoid(center=(3, 2, 1)).show()`                    |
| 旋转     | `ellipsoid(rotation=(45, 30, 60)).show()`               |
| 网格     | `ellipsoid(wireframe=True).show()`                      |
| 高精度   | `ellipsoid(u_res=60, v_res=60).show()`                  |
| 透明     | `ellipsoid(color='rgba(255,0,0,0.5)').show()`           |
| 多个     | `ellipsoids({'a':1}, {'a':2, 'center':(3,0,0)}).show()` |
| 添加到图 | `ellipsoid(a=1); ellipsoid(a=2, fig=fig).show()`        |

## API 速查表

### `ellipsoid(a=1, b=1, c=1, center=(0,0,0), rotation=None, u_res=30, v_res=30, color='rgba(100,150,255,0.7)', wireframe=False, name='Ellipsoid', show_axes=False, fig=None, **kwargs)`

**关键参数：**
- `a, b, c` — 三轴半径
- `center` — (x, y, z) 中心
- `rotation` — (rx, ry, rz) 欧拉角（度）
- `u_res, v_res` — 网格分辨率（越大越平滑）
- `color` — RGBA/Hex/名字
- `wireframe` — True 显示框架
- `fig` — 已有 Figure 用于叠加
- 返回 → Plotly Figure

### `ellipsoids(dict1, dict2, ..., title='', figsize=(900,700))`
- 参数是可变数量的字典（每个是 `ellipsoid()` 的参数）
- 返回 → Plotly Figure（包含所有椭球）

## 实用片段

### 创建多个不同的椭球
```python
fig = ellipsoids(
    {'a': 1, 'color': 'red'},
    {'a': 2, 'b': 1, 'c': 0.5, 'center': (3, 0, 0), 'color': 'blue'},
    {'rotation': (45, 45, 45), 'color': 'green'}
)
fig.show()
```

### 扫描参数空间
```python
configs = [
    {'a': 0.5 + 0.2*i, 'center': (i, 0, 0)}
    for i in range(5)
]
fig = ellipsoids(*configs, title='Parameter Sweep')
fig.show()
```

### 保存到 HTML
```python
fig = ellipsoid(a=2, b=1.5, c=0.8)
fig.write_html('my_ellipsoid.html')
```

### 高质量输出
```python
fig = ellipsoid(a=2, b=1.5, c=0.8, u_res=60, v_res=60)
fig.write_image('ellipsoid.png', width=1200, height=900)
```

## 颜色速查

```python
# 不透明
ellipsoid(color='red')                    # 命名颜色
ellipsoid(color='#FF0000')                # Hex
ellipsoid(color='rgb(255,0,0)')           # RGB

# 透明
ellipsoid(color='rgba(255,0,0,0.5)')      # 50% 透明红
ellipsoid(color='rgba(0,0,255,0.3)')      # 70% 透明蓝
```

## 常见模式

### 对比两个椭球
```python
fig = ellipsoid(a=1, b=1, c=1, name='Sphere')
ellipsoid(a=2, b=1, c=0.5, name='Ellipsoid', fig=fig)
fig.show()
```

### 网格版本
```python
fig = ellipsoid(wireframe=True, color='rgba(0,0,0,0.8)')
fig.show()
```

### 旋转对比
```python
fig = ellipsoids(
    {'a': 2, 'b': 1, 'c': 0.5, 'name': 'No Rotation'},
    {'a': 2, 'b': 1, 'c': 0.5, 'rotation': (45, 45, 0), 'center': (4, 0, 0), 'name': 'Rotated'}
)
fig.show()
```

## 性能提示

- **响应快速**：默认 `u_res=30, v_res=30` 够用
- **高质量**：用 `u_res=50, v_res=50` 或更高
- **超高质量**：`u_res=80, v_res=80`（可能较慢）
- **网格模式**更快（`wireframe=True`）

## 数学参数

- **半径**：a, b, c（椭圆周期 2π）
- **旋转顺序**：欧拉角 Z-Y-X（国际标准）
- **网格点数**：u_res × v_res

---

**完整文档**：见 `README.md`  
**示例代码**：`examples.py`  
**单元测试**：`test_ellipsoid.py`

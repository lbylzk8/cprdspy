# CPR 3D 参数化椭球生成与仿射变换：数学原理与代码实现

本文档从数学原理出发，逐步推导参数化椭球的生成公式、空间变换理论、网格构造算法，并结合 [blender_ellipsoid.py](blender_ellipsoid.py) 的源代码，展示如何在 Blender 中完成整个项目。

---

## 目录

1. [参数化椭球的数学基础](#1-参数化椭球的数学基础)
2. [球坐标参数化与网格采样](#2-球坐标参数化与网格采样)
3. [旋转的四种数学表示](#3-旋转的四种数学表示)
4. [仿射变换与齐次坐标](#4-仿射变换与齐次坐标)
5. [网格拓扑构造](#5-网格拓扑构造)
6. [Blender 集成：bmesh 与材质](#6-blender-集成bmesh-与材质)
7. [UV 映射](#7-uv-映射)
8. [Geometry Nodes 实例化](#8-geometry-nodes-实例化)
9. [高级应用：花瓣与花朵生成](#9-高级应用花瓣与花朵生成)
10. [完整项目搭建](#10-完整项目搭建)

---

## 1. 参数化椭球的数学基础

### 1.1 椭球的标准方程

在三维笛卡尔坐标系中，中心在原点的椭球隐式方程为：

$$
\frac{x^2}{a^2} + \frac{y^2}{b^2} + \frac{z^2}{c^2} = 1
$$

其中 $a, b, c$ 分别是椭球在 X、Y、Z 方向的半轴长度（radius）。

**特殊情况：**
- 当 $a = b = c$ 时，退化为球体（sphere），半径为 $a$
- 当 $a = b \neq c$ 时，为旋转椭球（spheroid），绕 Z 轴旋转对称
- 当 $a \neq b \neq c$ 时，为三轴椭球（triaxial ellipsoid），最一般的形式

### 1.2 参数化表示（球坐标推广）

椭球可以用两个角度参数 $(u, v)$ 来参数化，这是球坐标的直接推广：

$$
\begin{cases}
x(u, v) = a \cdot \cos(u) \cdot \sin(v) \\[4pt]
y(u, v) = b \cdot \sin(u) \cdot \sin(v) \\[4pt]
z(u, v) = c \cdot \cos(v)
\end{cases}
$$

**参数范围：**
- $u \in [0, 2\pi]$：经度角（longitude），绕 Z 轴旋转
- $v \in [0, \pi]$：余纬度角（colatitude），从 Z 轴正方向（北极）到 Z 轴负方向（南极）

**为什么这样定义？**

代入验证：将参数方程代入隐式方程：

$$
\frac{(a\cos u \sin v)^2}{a^2} + \frac{(b\sin u \sin v)^2}{b^2} + \frac{(c\cos v)^2}{c^2}
= \cos^2 u \sin^2 v + \sin^2 u \sin^2 v + \cos^2 v
= \sin^2 v (\cos^2 u + \sin^2 u) + \cos^2 v
= \sin^2 v + \cos^2 v = 1 \quad \checkmark
$$

**几何意义：**

- $v = 0$ 时，$(x, y, z) = (0, 0, c)$，即"北极"
- $v = \pi/2$ 时，$(x, y, z) = (a\cos u, b\sin u, 0)$，即赤道椭圆
- $v = \pi$ 时，$(x, y, z) = (0, 0, -c)$，即"南极"
- $u$ 从 $0$ 到 $2\pi$ 绕 Z 轴一周

### 1.3 部分椭球

通过限制参数范围，可以只生成椭球的一部分（partial ellipsoid）：

- 设置 `u_range = (0, π)` 生成右半部分（X ≥ 0 区域）
- 设置 `v_range = (0, π/2)` 生成北半球
- 设置 `v_range = (0, θ)` 生成一个"帽状"区域（从北极到纬度 θ）

这是后续构建花瓣（petal）的关键技术。

---

## 2. 球坐标参数化与网格采样

### 2.1 离散化采样

在实际渲染中，我们需要将连续的参数曲面离散化为顶点网格。给定分辨率参数：

- `u_res`：U 方向的采样点数（经度方向，列数）
- `v_res`：V 方向的采样点数（纬度方向，行数）

在参数空间 $[u_0, u_1] \times [v_0, v_1]$ 上均匀采样：

$$u_j = u_0 + \frac{u_1 - u_0}{u_{res} - 1} \cdot j, \quad j = 0, 1, \dots, u_{res}-1$$

$$v_i = v_0 + \frac{v_1 - v_0}{v_{res} - 1} \cdot i, \quad i = 0, 1, \dots, v_{res}-1$$

**代码实现（有/无 NumPy）：**

```python
def _get_uv_grid(u_res, v_res, u_range, v_range, cache_uv=True):
    """返回 (u_grid, v_grid)。在有 numpy 时返回 numpy arrays，否则返回嵌套列表。"""
    u_res = int(u_res)
    v_res = int(v_res)
    if u_res < 2 or v_res < 2:
        raise ValueError("u_res and v_res must be >= 2")

    u0, u1 = float(u_range[0]), float(u_range[1])
    v0, v1 = float(v_range[0]), float(v_range[1])

    # 缓存键，避免重复计算相同参数的网格
    key = (u_res, v_res, u0, u1, v0, v1)
    if cache_uv and _HAS_NUMPY and key in _UV_GRID_CACHE:
        return _UV_GRID_CACHE[key]

    if _HAS_NUMPY:
        u = np.linspace(u0, u1, u_res)
        v = np.linspace(v0, v1, v_res)
        u_grid, v_grid = np.meshgrid(u, v)
    else:
        # 纯 Python 回退方案（不依赖 numpy）
        u_vals = [u0 + (u1 - u0) * j / max(1, u_res - 1) for j in range(u_res)]
        v_vals = [v0 + (v1 - v0) * i / max(1, v_res - 1) for i in range(v_res)]
        u_grid = [[uv for uv in u_vals] for _ in range(v_res)]
        v_grid = [[vv for _ in range(u_res)] for vv in v_vals]

    if cache_uv and _HAS_NUMPY:
        _UV_GRID_CACHE[key] = (u_grid, v_grid)
    return u_grid, v_grid
```

### 2.2 从参数网格到三维顶点

有了 u/v 网格后，应用椭球参数方程批量计算顶点：

```python
sv = np.sin(v_grid)   # sin(v) 矩阵，shape (v_res, u_res)
cv = np.cos(v_grid)   # cos(v) 矩阵
cu = np.cos(u_grid)   # cos(u) 矩阵
su = np.sin(u_grid)   # sin(u) 矩阵

x = (a * cu * sv).astype(float)   # x = a·cos(u)·sin(v)
y = (b * su * sv).astype(float)   # y = b·sin(u)·sin(v)
z = (c * cv).astype(float)        # z = c·cos(v)

# 将网格展平为 (N, 3) 形状的顶点数组，便于批量变换
pts = np.column_stack([x.ravel(), y.ravel(), z.ravel()])  # shape (N, 3)
```

**NumPy 向量化优势：** 上述代码一次性计算了所有 $v_{res} \times u_{res}$ 个顶点的三维坐标，避免了 Python 层的显式循环，效率极高。

---

## 3. 旋转的四种数学表示

代码支持四种旋转表示方式，按优先级从高到低为：**欧拉角 → 四元数 → 轴角**。以下是每种方式的完整数学推导。

### 3.1 欧拉角与旋转矩阵

绕坐标轴的基本旋转矩阵（右手系，主动旋转）：

**绕 X 轴旋转 $\theta_x$（俯仰角，pitch）：**

$$R_x(\theta_x) = \begin{bmatrix} 1 & 0 & 0 \\ 0 & \cos\theta_x & -\sin\theta_x \\ 0 & \sin\theta_x & \cos\theta_x \end{bmatrix}$$

**绕 Y 轴旋转 $\theta_y$（偏航角，yaw）：**

$$R_y(\theta_y) = \begin{bmatrix} \cos\theta_y & 0 & \sin\theta_y \\ 0 & 1 & 0 \\ -\sin\theta_y & 0 & \cos\theta_y \end{bmatrix}$$

**绕 Z 轴旋转 $\theta_z$（滚转角，roll）：**

$$R_z(\theta_z) = \begin{bmatrix} \cos\theta_z & -\sin\theta_z & 0 \\ \sin\theta_z & \cos\theta_z & 0 \\ 0 & 0 & 1 \end{bmatrix}$$

**组合旋转（ZYX 顺序，即先绕 X，再绕 Y，最后绕 Z）：**

$$R = R_z(\theta_z) \cdot R_y(\theta_y) \cdot R_x(\theta_x)$$

> **注意：** 矩阵乘法顺序与旋转应用顺序相反。代码中按 Z→Y→X 的顺序左乘，意味着先绕 X 轴旋转，再绕 Y 轴，最后绕 Z 轴。

**代码实现：**

```python
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
R = Rz @ Ry @ Rx                # 组合旋转矩阵
pts_t = pts @ R.T               # 对所有顶点批量应用旋转
```

**万向节死锁（Gimbal Lock）提醒：** 当 $\theta_y = \pm 90^\circ$ 时，X 轴和 Z 轴的旋转轴重合，丢失一个旋转自由度。此时应使用四元数代替。

### 3.2 四元数旋转

#### 3.2.1 四元数定义

四元数 $q$ 是复数在四维的推广：

$$q = w + x\mathbf{i} + y\mathbf{j} + z\mathbf{k} = (w, \mathbf{v})$$

其中 $w \in \mathbb{R}$ 为标量部，$\mathbf{v} = (x, y, z) \in \mathbb{R}^3$ 为向量部。

虚单位乘法规则（Hamilton 规则）：

$$\mathbf{i}^2 = \mathbf{j}^2 = \mathbf{k}^2 = -1$$
$$\mathbf{ij} = \mathbf{k},\ \mathbf{ji} = -\mathbf{k}$$
$$\mathbf{jk} = \mathbf{i},\ \mathbf{kj} = -\mathbf{i}$$
$$\mathbf{ki} = \mathbf{j},\ \mathbf{ik} = -\mathbf{j}$$

#### 3.2.2 四元数乘法公式

两个四元数的乘法（标量-向量形式）：

$$q_1 q_2 = \big(w_1 w_2 - \mathbf{v}_1 \cdot \mathbf{v}_2,\ w_1 \mathbf{v}_2 + w_2 \mathbf{v}_1 + \mathbf{v}_1 \times \mathbf{v}_2\big)$$

#### 3.2.3 旋转四元数

绕单位轴 $\mathbf{k}$（$\|\mathbf{k}\| = 1$）旋转角度 $\theta$ 对应的单位四元数为：

$$q = \left(\cos\frac{\theta}{2},\ \sin\frac{\theta}{2} \cdot \mathbf{k}\right)$$

**为什么要用半角？** 因为四元数通过共轭作用 $p' = q p q^{-1}$ 旋转向量，这相当于两次作用，所以参数角度需要减半。

旋转向量的操作为：

$$\mathbf{v}' = \operatorname{Im}(q \cdot (0, \mathbf{v}) \cdot q^{-1})$$

由于 $q$ 是单位四元数，$q^{-1} = q^* = (w, -\mathbf{v})$。

#### 3.2.4 四元数转旋转矩阵

从四元数 $q = (w, x, y, z)$ 到 3×3 旋转矩阵的转换公式：

$$R = \begin{bmatrix}
1 - 2(y^2 + z^2) & 2(xy - wz) & 2(xz + wy) \\
2(xy + wz) & 1 - 2(x^2 + z^2) & 2(yz - wx) \\
2(xz - wy) & 2(yz + wx) & 1 - 2(x^2 + y^2)
\end{bmatrix}$$

**代码实现：**

```python
def _quaternion_to_rotation_matrix(q: list) -> Matrix:
    """将四元数转换为Blender的3x3旋转矩阵"""
    w, x, y, z = q
    # 标准化四元数
    norm = math.sqrt(w * w + x * x + y * y + z * z)
    if norm == 0:
        return Matrix.Identity(3)
    w, x, y, z = w / norm, x / norm, y / norm, z / norm

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
```

**为什么四元数优于欧拉角？**
- 避免了万向节死锁问题
- 旋转插值更自然（SLERP 球面线性插值）
- 运算更高效（只需乘法和加法，无需三角函数）

### 3.3 轴角表示（Axis-Angle）

轴角表示是最直观的旋转描述方式：用一个单位向量 $\mathbf{u}$ 指定旋转轴，用一个标量 $\theta$ 指定旋转角度。

**代码实现（轴角 → 四元数 → 旋转矩阵）：**

```python
def _axis_angle_to_quaternion(axis: list, angle: float) -> list:
    """将轴角表示转换为四元数"""
    axis = Vector(axis).normalized()
    half_angle = angle / 2
    sin_half = math.sin(half_angle)
    cos_half = math.cos(half_angle)
    return [cos_half, axis[0] * sin_half, axis[1] * sin_half, axis[2] * sin_half]
```

轴角 $(\mathbf{u}, \theta)$ 到四元数的转换：

$$q = \left(\cos\frac{\theta}{2},\ \sin\frac{\theta}{2} \cdot \mathbf{u}\right)$$

轴角 $(\mathbf{u}, \theta)$ 到旋转矩阵的 Rodriques 公式：

$$R = I + \sin\theta[\mathbf{u}]_\times + (1 - \cos\theta)[\mathbf{u}]_\times^2$$

其中 $[\mathbf{u}]_\times = \begin{bmatrix} 0 & -u_z & u_y \\ u_z & 0 & -u_x \\ -u_y & u_x & 0 \end{bmatrix}$ 是叉积矩阵。

---

## 4. 仿射变换与齐次坐标

### 4.1 齐次坐标原理

在三维计算机图形学中，仿射变换（旋转 + 缩放 + 平移 + 剪切）统一用 4×4 齐次矩阵表示。一个三维点 $(x, y, z)$ 扩展为齐次坐标 $(x, y, z, 1)$。

4×4 仿射矩阵的一般形式：

$$A = \begin{bmatrix}
r_{11} & r_{12} & r_{13} & t_x \\
r_{21} & r_{22} & r_{23} & t_y \\
r_{31} & r_{32} & r_{33} & t_z \\
0 & 0 & 0 & 1
\end{bmatrix}$$

其中：
- 左上 3×3 子矩阵 $R$ 编码旋转和缩放
- 右上 3×1 列向量 $\mathbf{t} = (t_x, t_y, t_z)^T$ 编码平移
- 底行 $(0, 0, 0, 1)$ 保证齐次性

点的变换：$\begin{bmatrix} x' \\ y' \\ z' \\ 1 \end{bmatrix} = A \cdot \begin{bmatrix} x \\ y \\ z \\ 1 \end{bmatrix}$

即：$\mathbf{p}' = R \cdot \mathbf{p} + \mathbf{t}$

### 4.2 代码中的变换处理逻辑

项目支持两种变换模式：

**模式 1：提供完整的仿射矩阵（最高优先级）**

```python
if affine_matrix is not None:
    # 支持多种形状的输入矩阵
    if isinstance(affine_matrix, Matrix):
        A = np.array(affine_matrix)
    else:
        A = np.asarray(affine_matrix, dtype=float)

    # 形状标准化：将 (3,3) 或 (3,4) 扩展为 (4,4)
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

    # 如果还提供了旋转参数，先应用旋转
    if rotation_euler_deg is not None:
        # ... 旋转所有顶点 ...

    # 应用仿射变换（所有顶点批量处理）
    pts_h = np.hstack([pts, np.ones((pts.shape[0], 1), dtype=float)])  # 齐次坐标扩展
    pts_t = (pts_h @ A4.T)[:, :3]  # 应用变换并取回 3D 坐标
```

**模式 2：分别指定旋转 + 平移（无仿射矩阵时）**

```python
else:
    pts_t = pts.copy()
    # 先旋转
    if rotation_euler_deg is not None:
        # ... 应用旋转矩阵 ...
    elif quaternion is not None:
        # ... 应用四元数旋转 ...
    elif axis_angle is not None:
        # ... 应用轴角旋转 ...

    # 再平移
    loc = np.asarray(location, dtype=float)
    pts_t = pts_t + loc.reshape(1, 3)
```

### 4.3 变换的数学本质

整个过程可以抽象为：

$$\mathbf{p}_{\text{final}} = A_{\text{affine}} \cdot R_{\text{rotation}} \cdot \mathbf{p}_{\text{ellipsoid}}$$

其中：
- $\mathbf{p}_{\text{ellipsoid}}$ 是参数方程生成的原始顶点
- $R_{\text{rotation}}$ 是纯旋转矩阵
- $A_{\text{affine}}$ 是用户提供的仿射矩阵（可包含额外的缩放、剪切、平移）

这等价于先旋转椭球的朝向，再将其变形并放置到目标位置。

---

## 5. 网格拓扑构造

### 5.1 顶点索引与面构造

参数网格采样后得到 $v_{res} \times u_{res}$ 个顶点，按行优先排列：

```
索引映射：顶点 (i, j) → 索引 = i * u_res + j
其中 i 是 V 方向索引（行），j 是 U 方向索引（列）
```

每个四边形面由四个顶点构成：

```
(i, j)  ---  (i, j+1)
  |             |
  |             |
(i+1, j) --- (i+1, j+1)
```

**面构造代码：**

```python
faces = []
for i in range(v_res - 1):          # 遍历行
    for j in range(u_res):          # 遍历列
        jn = (j + 1) % u_res        # U 方向周期性闭合（接缝处理）
        v0_idx = i * u_res + j
        v1_idx = i * u_res + jn
        v2_idx = (i + 1) * u_res + jn
        v3_idx = (i + 1) * u_res + j

        # 如果任何顶点被剔除则跳过该面
        if not (keep_mask[v0_idx] and keep_mask[v1_idx]
                and keep_mask[v2_idx] and keep_mask[v3_idx]):
            continue
        faces.append((v0_idx, v1_idx, v2_idx, v3_idx))
```

**U 方向的周期性：** 当 $u$ 参数范围覆盖完整的 $2\pi$ 时，$j = u_{res} - 1$ 的下一列应当回到 $j = 0$，这通过 `(j + 1) % u_res` 实现，从而在 U 方向形成闭合的"管状"拓扑。

**V 方向不需要周期性：** V 范围通常为 $[0, \pi]$，南北极是点而非环，因此 V 方向不闭合。

### 5.2 Y 正半部分裁剪

`keep_y_positive=True` 时，只保留变换后 Y 坐标 ≥ 0 的顶点及其所属的面：

```python
verts = [(float(px), float(py), float(pz)) for px, py, pz in pts_t]
if keep_y_positive:
    keep_mask = [pt[1] >= 0 for pt in verts]
else:
    keep_mask = [True] * len(verts)
```

当某个四边形的任意一个顶点被剔除时，整个面被丢弃——这是一种保守策略，确保裁剪边界的正确性。

### 5.3 顶点去冗余

裁剪后，有些顶点可能不再被任何面引用。通过重建索引映射来剔除这些孤儿顶点：

```python
if not faces:
    return None

used_indices = sorted({idx for f in faces for idx in f})
index_map = {old: new for new, old in enumerate(used_indices)}
verts_used = [verts[i] for i in used_indices]
faces_mapped = [[index_map[i] for i in f] for f in faces]
```

---

## 6. Blender 集成：bmesh 与材质

### 6.1 使用 bmesh 构建网格

Blender 的 `bmesh` 模块提供了比 `mesh.from_pydata()` 更高效的网格构建方式，特别是当需要三角化时：

```python
mesh = bpy.data.meshes.new(name + "_mesh")
if use_bmesh:
    bm = bmesh.new()
    bm_verts = [bm.verts.new(v) for v in verts_used]  # 添加所有顶点
    bm.verts.ensure_lookup_table()

    for f_idx in faces_mapped:
        try:
            bm.faces.new([bm_verts[i] for i in f_idx])  # 添加面
        except ValueError:
            pass  # 重复面或退化的面，静默跳过

    bm.faces.ensure_lookup_table()

    # 三角化：将四边形面转换为三角形
    if triangulate and len(bm.faces) > 0:
        bmesh.ops.triangulate(bm, faces=bm.faces[:])

    bm.to_mesh(mesh)
    bm.free()
```

**三角化为何重要：**
- 渲染管线最终都需要三角形
- 非共面的四边形在渲染时会产生歧义
- 三角化后每个面的法向量是唯一确定的

### 6.2 创建对象与材质

```python
obj = bpy.data.objects.new(name, mesh)
bpy.context.collection.objects.link(obj)

# 创建简单的漫反射材质
mat = bpy.data.materials.new(name + "_mat")
mat.diffuse_color = color  # RGBA, 每个分量 0~1
obj.data.materials.append(mat)
```

### 6.3 Blender 面板与操作符

为了让脚本在 Blender UI 中可用，我们注册自定义面板和操作符：

**操作符（Operator）：**

操作符是实现具体操作的类，包含属性和 `execute` 方法：

```python
class CPR_OT_add_ellipsoid(bpy.types.Operator):
    bl_idname = "cpr.add_ellipsoid"
    bl_label = "Add Ellipsoid (CPR)"
    bl_options = {"REGISTER", "UNDO"}

    # 定义所有可调参数为 bpy.props 属性
    a: bpy.props.FloatProperty(name="X Radius", default=1.0, min=0.01, max=100.0)
    b: bpy.props.FloatProperty(name="Y Radius", default=1.0, min=0.01, max=100.0)
    # ... 更多属性 ...

    def execute(self, context):
        obj = create_parametric_ellipsoid(
            a=float(self.a), b=float(self.b), c=float(self.c),
            # ... 传递所有参数 ...
        )
        return {"FINISHED"}

    def invoke(self, context, event):
        # 弹出参数对话框
        return context.window_manager.invoke_props_dialog(self, width=400)
```

**面板（Panel）：**

面板在 3D 视图的侧边栏中提供 UI：

```python
class CPR_PT_ellipsoid_panel(bpy.types.Panel):
    bl_label = "CPR Ellipsoid"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "CPR"        # 侧边栏标签页名称

    def draw(self, context):
        layout = self.layout
        # 快速创建按钮
        op = layout.operator("cpr.add_ellipsoid", text="Sphere")
        op.a = 1.0; op.b = 1.0; op.c = 1.0

        op = layout.operator("cpr.add_ellipsoid", text="Ellipsoid")
        op.a = 2.0; op.b = 1.0; op.c = 1.0
        # 完整参数对话框
        layout.operator("cpr.add_ellipsoid", text="Custom Ellipsoid...")
```

**注册机制：**

```python
def register():
    bpy.utils.register_class(CPR_OT_add_ellipsoid)
    bpy.utils.register_class(CPR_PT_ellipsoid_panel)
    bpy.utils.register_class(CPR_OT_create_gnodes_from_active)

def unregister():
    bpy.utils.unregister_class(CPR_OT_add_ellipsoid)
    bpy.utils.unregister_class(CPR_PT_ellipsoid_panel)
    bpy.utils.unregister_class(CPR_OT_create_gnodes_from_active)
```

---

## 7. UV 映射

### 7.1 UV 坐标的数学本质

UV 映射将三维网格的每个顶点关联到二维纹理空间中的坐标 $(u, v) \in [0,1]^2$。在参数化曲面中，自然的做法是直接使用参数网格的原始 $(u, v)$ 值作为 UV 坐标。

此项目中，U 和 V 本身就是参数曲面的坐标，因此 UV 生成非常直观：

```python
if generate_uv:
    if not mesh.uv_layers:
        uv_layer = mesh.uv_layers.new(name="UVMap")
    else:
        uv_layer = mesh.uv_layers.active

    # 从参数网格中提取对应的 UV 值
    if _HAS_NUMPY:
        u_flat = np.array(u_grid).ravel()
        v_flat = np.array(v_grid).ravel()
        uv_per_used = [(float(u_flat[i]), float(v_flat[i])) for i in used_indices]
    # ...

    # 为每个面的每个角点分配 UV
    for poly in mesh.polygons:
        for li, vi in enumerate(poly.vertices):
            uv = uv_per_used[vi]
            uv_layer.data[poly.loop_start + li].uv = uv
```

**UV 映射示意图：**

```
参数域 (u,v)                      纹理空间
v_max ┌─────────────┐              (0,0) ┌─────────────┐ (1,0)
      │             │                    │             │
      │  椭球表面   │          ──→       │  纹理贴图   │
      │             │                    │             │
v_min └─────────────┘              (0,1) └─────────────┘ (1,1)
      u_min       u_max
```

---

## 8. Geometry Nodes 实例化

### 8.1 数学思想

Geometry Nodes 是 Blender 的节点式程序化建模系统。本项目中使用它来创建椭球的阵列实例化——在一个网格的顶点上放置椭球副本。

**工作流程：**

1. 创建一个网格平面（Grid primitive），有 `rows × cols` 个顶点
2. 将网格转换为点云（Mesh to Points）
3. 在每个点上实例化基础椭球对象（Instance on Points）
4. 输出实例集合

### 8.2 节点图构建代码

```python
def create_geometry_nodes_instancer(base_obj, rows=5, cols=5,
                                     spacing=(2.0, 2.0), name="Ellipsoid_Instancer"):
    # 创建一个空对象作为 GN 容器
    gn_obj = bpy.data.objects.new(name + "_gn", None)
    bpy.context.collection.objects.link(gn_obj)

    # 创建 Geometry Nodes modifier 和节点组
    mod = gn_obj.modifiers.new(name="GeometryNodes", type="NODES")
    node_group = bpy.data.node_groups.new(name + "_nodegroup", "GeometryNodeTree")
    mod.node_group = node_group

    nodes = node_group.nodes
    links = node_group.links
    nodes.clear()

    # 创建节点
    node_in = nodes.new("NodeGroupInput")
    node_out = nodes.new("NodeGroupOutput")
    node_in.location = (-800, 0)
    node_out.location = (800, 0)

    # Grid: 生成 cols × rows 的均匀网格
    node_grid = nodes.new("GeometryNodeMeshPrimitiveGrid")
    node_grid.inputs["Vertices X"].default_value = cols
    node_grid.inputs["Vertices Y"].default_value = rows
    node_grid.inputs["Size X"].default_value = spacing[0] * (cols - 1)
    node_grid.inputs["Size Y"].default_value = spacing[1] * (rows - 1)

    # Mesh to Points: 将网格面转换为顶点
    node_m2p = nodes.new("GeometryNodeMeshToPoints")

    # Object Info: 获取基础对象的几何数据
    node_obj = nodes.new("GeometryNodeObjectInfo")
    node_obj.inputs["Object"].default_value = base_obj

    # Instance on Points: 在每个点上放置实例
    node_inst = nodes.new("GeometryNodeInstanceOnPoints")

    # 连接节点
    links.new(node_grid.outputs["Mesh"], node_m2p.inputs["Mesh"])
    links.new(node_m2p.outputs["Points"], node_inst.inputs["Points"])
    links.new(node_obj.outputs["Geometry"], node_inst.inputs["Instance"])
    links.new(node_inst.outputs["Instances"], node_out.inputs["Geometry"])

    return gn_obj
```

**节点图拓扑：**

```
Group Input → Grid(Mesh) → Mesh to Points → Instance on Points → Group Output
                                              ↑
                          Object Info(椭球) ──┘
```

---

## 9. 高级应用：花瓣与花朵生成

这是整个项目最精彩的部分——利用参数化椭球作为基本几何原语，通过仿射变换和空间排列，构建出自然界中的花瓣和花朵形态。

### 9.1 花瓣的数学构造

花瓣由**两半椭球**拼接而成：右半部分和左半部分，它们是中心椭球在特定角度截取下的两个对称片段。

**截取角度计算：**

对于有 $n$ 个花瓣的花朵，每个花瓣的中心角跨度为 $\frac{2\pi}{n}$。花瓣的半宽度决定需要从椭球上截取多大的角度 $\theta$：

```python
theta = np.pi / 2 - np.pi / n
```

**几何推导：**

在赤道平面（XY 平面）上，花瓣的两半在 X 轴两侧对称展开。右半花瓣的位置偏移量为：

$$x_{\text{dist}} = a \cdot \sin\theta$$
$$y_{\text{dist}} = c \cdot \cos\theta$$

其中 $a$ 和 $c$ 是椭球在 X 和 Z 方向的半轴长度。这些偏移量将椭球的截取部分"压扁"到花瓣平面中。

**代码实现：**

```python
def petal(a=2, b=1/3, c=2, n=4, u_res=100, v_res=100,
          color1=(1.0, 0.4, 1.0, 0.7), color2=(0, 1.0, 0, 0.7),
          affine_matrix=M, name="Petal", ...):
    theta = np.pi / 2 - np.pi / n
    y_dist = c * np.cos(theta)
    x_dist = a * np.sin(theta)

    # 右半部分：截取 u∈[0,π], v∈[0,θ] 的椭球片段
    A = affine_matrix.copy()
    A[0][3] += x_dist    # X 方向平移
    A[1][3] += -y_dist   # Y 方向平移（向下）
    right_obj = create_parametric_ellipsoid(
        a, b, c, u_res, v_res,
        u_range=(0, np.pi),           # 右半
        v_range=(0, theta),           # 截取到角度 θ
        name=name + "_right",
        color=color1,
        affine_matrix=A,
        rotation_euler_deg=(-90, 0, 0),  # 将 Z 轴朝上的椭球"放倒"
    )

    # 左半部分：X 和 Y 方向镜像
    B = affine_matrix.copy()
    B[0][0] = -B[0][0]    # X 轴翻转（镜像）
    B[1][1] = -B[1][1]    # Y 轴翻转（镜像）
    B[0][3] += x_dist
    B[1][3] += y_dist     # Y 方向平移（向上）
    left_obj = create_parametric_ellipsoid(
        a, b, c, u_res, v_res,
        u_range=(0, np.pi),           # 保持右半截取
        v_range=(0, theta),           # 但通过矩阵镜像翻到左边
        name=name + "_left",
        color=color2,
        affine_matrix=B,
        rotation_euler_deg=(-90, 0, 0),
    )
```

### 9.2 仿射矩阵的镜像操作

左半部分的核心技巧是对仿射矩阵的特定元素取负：

$$B = A \quad \text{但} \quad B_{00} \to -A_{00},\ B_{11} \to -A_{11}$$

这意味着左半椭球在 X 和 Y 方向上都做了镜像翻转。具体来说：
- $B_{00} = -A_{00}$ 使 X 坐标翻转（左右镜像）
- $B_{11} = -A_{11}$ 使 Y 坐标翻转（上下镜像）

结合偏移量的调整，左半部分恰好是右半部分关于花瓣中线的镜像对称。

### 9.3 花瓣的空间变换

花瓣创建后，通过一个父级空对象（Empty）来施加整体的旋转、平移和缩放：

```python
# 创建空对象作为父级
parent_empty = bpy.data.objects.new(name + "_parent", None)
bpy.context.collection.objects.link(parent_empty)

# 设置整体变换
if rotation_euler_deg is not None:
    parent_empty.rotation_euler = [math.radians(deg) for deg in rotation_euler_deg]
elif quaternion is not None:
    parent_empty.rotation_mode = "QUATERNION"
    parent_empty.rotation_quaternion = quaternion

parent_empty.location = location   # 平移
parent_empty.scale = scale         # 缩放

# 设置父子关系：子对象继承父对象的变换
right_obj.parent = parent_empty
left_obj.parent = parent_empty
```

**Blender 父子关系的数学意义：**

如果父对象的世界变换矩阵为 $M_{\text{parent}}$，子对象的局部变换矩阵为 $M_{\text{child}}$，则子对象的世界坐标为：

$$\mathbf{p}_{\text{world}} = M_{\text{parent}} \cdot M_{\text{child}} \cdot \mathbf{p}_{\text{local}}$$

### 9.4 花朵：花瓣的旋转排列

花朵由 $n_{\text{petals}}$ 个花瓣绕 Z 轴均匀旋转排列而成：

```python
def flower(a=2, b=1/3, c=2, n=4, ...):
    for i in range(12):  # 12 个花瓣
        petal(
            a, b, c, n, u_res, v_res, color1, color2,
            affine_matrix=affine_matrix,
            name=name + str(i + 1),
            rotation_euler_deg=(
                30 + rotation_euler_deg[0],
                -60 + rotation_euler_deg[1],
                i * 30 + 15 + rotation_euler_deg[2],  # 绕Z轴旋转，每个花瓣间隔30°
            ),
            location=location,
            scale=scale,
        )
```

**旋转角度计算：**

每个花瓣绕 Z 轴的旋转角度为：

$$\theta_i = i \cdot \frac{360^\circ}{n_{\text{petals}}} + \theta_{\text{offset}}, \quad i = 0, 1, \dots, n_{\text{petals}}-1$$

当 $n_{\text{petals}} = 12$ 时，间距为 $30^\circ$。

额外的 X 轴旋转 $30^\circ$ 和 Y 轴旋转 $-60^\circ$ 使花瓣从"平躺"状态倾斜为更自然的花朵姿态。

### 9.5 多层花朵

`flowers()` 函数通过多次调用 `flower()` 创建具有不同旋转参数的多层花瓣布局，每层花瓣可以有不同的缩放比例，形成层次感：

```python
def flowers(a=2, b=1/3, c=2, n=4, M=3, ...):
    for i in range(M):
        flower(a, b, c, n, u_res, v_res, color1, color2,
               affine_matrix=affine_matrix,
               name=name + "_" + str(i + 1),
               rotation_euler_deg=(30, -60, i * 30 + 15))
```

---

## 10. 完整项目搭建

### 10.1 环境准备

此脚本设计为在 Blender 内置的 Python 环境中运行，依赖：

| 依赖 | 说明 |
|------|------|
| `bpy` | Blender Python API（Blender 内置） |
| `mathutils` | Blender 数学工具库（Matrix, Vector, Euler, Quaternion） |
| `bmesh` | Blender 网格构建模块 |
| `numpy` | 数值计算（可选，有回退方案） |

**安装方式（推荐使用 uv）：**

```bash
uv pip install bpy numpy
```

或直接在 Blender 的脚本编辑器中运行（Blender 自带的 Python 已包含 `bpy` 和 `mathutils`）。

### 10.2 文件结构

```
cprdspy/cprdspy/CPR_3D/
├── blender_ellipsoid.py   # 主脚本文件
├── cpr_math.md            # 空间旋转数学参考
└── CPR_3D_math.md         # 本文档
```

### 10.3 使用流程

**步骤 1：在 Blender 中运行脚本**

在 Blender 的 Scripting 工作区中打开 `blender_ellipsoid.py`，点击 Run Script。

**步骤 2：通过 UI 面板创建**

切换到 3D Viewport，在右侧 N 面板中找到 "CPR" 标签页，可以看到：
- **Sphere** — 快速创建单位球体
- **Ellipsoid** — 快速创建椭球（a=2, b=1, c=1）
- **Custom Ellipsoid...** — 打开完整参数对话框

**步骤 3：创建花朵**

在脚本末尾取消注释相应代码，或直接在 Blender Python 控制台中执行：

```python
# 创建单朵花
flower(
    a=2, b=1/3, c=2, n=4,
    u_res=100, v_res=100,
    color1=(0.5, 1.0, 0.5, 0.7),
    color2=(0.5, 0.5, 1.0, 0.7),
    rotation_euler_deg=(30, -60, 0),
    location=(0, 0, 0),
    scale=(1, 1, 1),
)

# 创建多层花
petal(
    a=2, b=1/3, c=2, n=4,
    rotation_euler_deg=(15, -15, 0),
    scale=(2, 2, 2),
    color1=(0.5, 1.0, 0.5, 0.7),
    color2=(0.5, 0.5, 1.0, 0.7),
)
```

**步骤 4：使用 Geometry Nodes 阵列**

选中一个已创建的椭球对象，然后点击 "Create GN Instancer from Active" 按钮，设置行列数和间距，即可生成规则排列的椭球阵列。

### 10.4 参数速查表

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `a, b, c` | float | 1.0 | 椭球 X/Y/Z 半轴长度 |
| `u_res, v_res` | int | 32 | U/V 方向分辨率 |
| `u_range` | tuple | (0, 2π) | 经度参数范围 |
| `v_range` | tuple | (0, π) | 余纬度参数范围 |
| `color` | tuple[4] | (1, 0.3, 0.3, 1) | RGBA 颜色 |
| `affine_matrix` | 4×4 matrix | None | 4×4 齐次仿射矩阵 |
| `rotation_euler_deg` | tuple[3] | None | 欧拉角旋转（度） |
| `quaternion` | list[4] | None | 四元数 [w, x, y, z] |
| `axis_angle` | tuple | None | 轴角 (axis, angle_deg) |
| `location` | tuple[3] | (0, 0, 0) | 平移向量 |
| `keep_y_positive` | bool | False | 仅保留 Y ≥ 0 部分 |
| `generate_uv` | bool | False | 是否生成 UV 层 |
| `triangulate` | bool | True | 是否三角化面 |
| `use_bmesh` | bool | True | 是否使用 bmesh |
| `return_mapping` | bool | False | 是否返回顶点/面映射 |

### 10.5 扩展方向

基于本文的数学框架和代码架构，可以进一步扩展：

1. **超椭球（Superellipsoid）：** 修改参数方程为：
   $$\begin{cases} x = a \cdot \operatorname{sgn}(\cos u)|\cos u|^p \cdot \operatorname{sgn}(\sin v)|\sin v|^q \\ y = b \cdot \operatorname{sgn}(\sin u)|\sin u|^p \cdot \operatorname{sgn}(\sin v)|\sin v|^q \\ z = c \cdot \operatorname{sgn}(\cos v)|\cos v|^q \end{cases}$$
   通过调整指数 $p, q$ 可生成从立方体到星形的各种形状。

2. **曲面变形（Displacement）：** 在顶点上叠加噪声函数（Perlin/Simplex noise），生成有机形态。

3. **骨骼动画：** 为花瓣父级空对象添加 Armature 约束，实现花朵开合动画。

4. **物理模拟：** 结合 Blender 的布料或软体物理，模拟花瓣飘落。

---

## 附录 A：四元数快速参考

| 操作 | 公式 |
|------|------|
| 共轭 | $q^* = (w, -x, -y, -z) = (w, -\mathbf{v})$ |
| 模长 | $\|q\| = \sqrt{w^2 + x^2 + y^2 + z^2}$ |
| 逆元 | $q^{-1} = \frac{q^*}{\|q\|^2}$ |
| 单位四元数条件 | $\|q\| = 1$ |
| 旋转四元数 | $q = (\cos\frac{\theta}{2}, \sin\frac{\theta}{2} \cdot \mathbf{k})$ |
| 旋转操作 | $p' = q p q^{-1}$（$p$ 为纯虚四元数） |
| SLERP 插值 | $\operatorname{slerp}(q_1, q_2, t) = \frac{\sin((1-t)\Omega)}{\sin\Omega} q_1 + \frac{\sin(t\Omega)}{\sin\Omega} q_2$ |

其中 $\Omega = \arccos(q_1 \cdot q_2)$ 是两个四元数间的夹角。

## 附录 B：旋转矩阵速查

| 轴 | 矩阵 |
|----|------|
| X | $\begin{bmatrix} 1 & 0 & 0 \\ 0 & \cos\theta & -\sin\theta \\ 0 & \sin\theta & \cos\theta \end{bmatrix}$ |
| Y | $\begin{bmatrix} \cos\theta & 0 & \sin\theta \\ 0 & 1 & 0 \\ -\sin\theta & 0 & \cos\theta \end{bmatrix}$ |
| Z | $\begin{bmatrix} \cos\theta & -\sin\theta & 0 \\ \sin\theta & \cos\theta & 0 \\ 0 & 0 & 1 \end{bmatrix}$ |
| 任意轴 $\mathbf{u}$ | $I + \sin\theta[\mathbf{u}]_\times + (1-\cos\theta)[\mathbf{u}]_\times^2$ |

---

*本文档基于 [blender_ellipsoid.py](blender_ellipsoid.py) 源码撰写，结合 [cpr_math.md](cpr_math.md) 中的旋转数学理论，系统地展示了从数学公式到 Blender 3D 可视化的完整实现链路。*

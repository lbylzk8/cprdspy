# cprdspy.rotor — CPR 旋转器模块

## 数学原理

### 核心定义

**Rotor（旋转器）** 是 CPR 理论的基本运动原子。

#### 2D Rotor（复数表示）

$$
R(r, \omega, \varphi; t) = r \cdot e^{i(\omega t + \varphi)}
$$

其中：
- $r$：半径（振幅）
- $\omega$：角频率（转速）
- $\varphi$：初相位（起始角度）
- $t$：时间参数

几何上，一个 Rotor 表示复平面上半径为 $r$、角速度为 $\omega$ 的匀速圆周运动。

#### 3D Rotor（四元数表示）

$$
R(r, \omega, \varphi; t) = r \cdot [\cos(\omega t + \varphi) \cdot e_1 + \sin(\omega t + \varphi) \cdot e_2]
$$

其中 $e_1, e_2$ 是旋转平面内的两个正交单位向量。

等价的四元数形式：
$$
R(t) = r \cdot q(t) \cdot e_1 \cdot q(t)^*
$$
其中 $q(t) = \cos\frac{\omega t + \varphi}{2} + \sin\frac{\omega t + \varphi}{2} \cdot \mathbf{n}$，$\mathbf{n} = e_1 \times e_2$ 是旋转轴。

#### nD Rotor（Clifford 代数表示）

$$
R(r, \omega, \varphi; t) = r \cdot \exp\left(-\frac{B(\omega t + \varphi)}{2}\right) \cdot e_1 \cdot \exp\left(\frac{B(\omega t + \varphi)}{2}\right)
$$

其中：
- $B = e_1 \wedge e_2$ 是旋转平面的单位二重向量（bivector）
- $\exp(-B\theta/2)$ 是 Clifford rotor
- 三明治积（sandwich product）：$v' = R \cdot v \cdot \tilde{R}$

**维度统一性**：
| 维度 | 代数结构 | Rotor 形式 |
|------|---------|-----------|
| 2D | 复数 $\mathbb{C}$ | $e^{i\theta}$ |
| 3D | 四元数 $\mathbb{H}$ | $\exp(-B\theta/2)$ |
| nD | Clifford 代数 $Cl(n)$ | $\exp(-B\theta/2)$ |

### 运动组合

多个 Rotor 的叠加生成复杂曲线：

$$
\gamma(t) = \text{center} + \sum_{k=1}^{N} R_k(t)
$$

在 2D 中：
$$
\gamma(t) = \text{center} + \sum_{k=1}^{N} r_k \cdot e^{i(\omega_k t + \varphi_k)}
$$

这正是 **Fourier 级数的复指数形式**：
- 有限 Rotor 组合 = 有限 Fourier 和
- 无限 Rotor 级数 → 任意周期曲线的逼近

### 几何解释：本轮-均轮系统

每个 Rotor 可以看作一个"本轮"（epicycle），所有本轮的向量叠加形成最终轨迹。这正是托勒密的地心说模型，也是 Fourier 分析的几何表达。

```
         R2 (小圆)
        ↗
       / \
      /   \
     O-----→ R1 (大圆)
      \   /
       \ /
        ↘
```

### 闭合性判据

**定理**：曲线 $\gamma(t)$ 闭合  所有频率比为有理数

$$
\frac{\omega_i}{\omega_j} \in \mathbb{Q} \quad \forall i, j \quad \Longrightarrow \quad \text{闭合轨道（周期运动）}
$$

$$
\exists \frac{\omega_i}{\omega_j} \notin \mathbb{Q} \quad \Longrightarrow \quad \text{准周期轨道（Kronecker 稠密）}
$$

**最小正周期**：

$$
T = \frac{2\pi}{\gcd(\omega_1, \omega_2, \ldots, \omega_N)}
$$

对于分数频率，GCD 的计算公式：

$$
\gcd\left(\frac{a}{b}, \frac{c}{d}\right) = \frac{\gcd(a, c)}{\text{lcm}(b, d)}
$$

### 微分几何：GA 曲率公式

**曲率**（curvature）衡量曲线的弯曲程度。在几何代数（Geometric Algebra）中，曲率公式为：

$$
\kappa = \frac{|v \wedge a|}{|v|^3}
$$

其中：
- $v = \dot{\gamma}(t)$：速度向量
- $a = \ddot{\gamma}(t)$：加速度向量
- $v \wedge a$：外积（wedge product）

**任意维度的统一公式**：

$$
|v \wedge a|^2 = |v|^2|a|^2 - (v \cdot a)^2
$$

在 2D 中，外积的具体形式：
$$
v \wedge a = v_x a_y - v_y a_x
$$

在 3D 中，等价于叉积的模长：
$$
|v \wedge a| = |v \times a|
$$

这个公式的优势：
1. **维度无关**：直接推广到 3D、4D 等高维空间
2. **无需叉积**：叉积只在 3D 有定义，外积在任意维度都有定义
3. **几何意义清晰**：$|v \wedge a|$ 表示速度和加速度张成的平行四边形面积

### 3D 挠率公式

**挠率**（torsion）衡量曲线偏离平面的程度：

$$
\tau = \frac{v \cdot (a \times j)}{|v \times a|^2}
$$

其中 $j = \dddot{\gamma}(t)$ 是加加速度（jerk）。

2D 曲线恒有 $\tau \equiv 0$（始终在平面内）。

### 与经典曲线的关系

| 曲线类型 | Rotor 组合 | 参数 |
|---------|-----------|------|
| 圆 | $R(r, 1)$ | 半径 $r$ |
| 外摆线 | $R(R_0, 1) + R(r_0, k)$ | $k$ 控制花瓣数 |
| 利萨如图 | $R(a, 1) + R(b, 2)$ | 频率比 1:2 |
| 花朵曲线 | $\sum R(r_k, k)$ | 多频率叠加 |
| Fourier 逼近 | $\sum c_k e^{ikt}$ | Fourier 系数 |
| 3D 螺旋线 | $R(R, 1, \text{XY}) + R(r, k, \text{YZ})$ | 不同平面 |

---

## API 参考

### 核心类

#### `Rotor2D(radius, frequency, phase, center)`

二维旋转器。

**参数**：
- `radius` (float)：半径，默认 1.0
- `frequency` (int|float)：角频率，默认 1
- `phase` (float)：初相位，默认 0.0
- `center` (tuple)：中心偏移，默认 (0, 0)

**方法**：
- `evaluate(t)`：计算时刻 $t$ 的位置（复数）
- `evaluate_xy(t)`：返回 $(x, y)$ 元组
- `conjugate()`：共轭（反转旋转方向）
- `derivative()`：导数（速度向量）
- `to_math()`：LaTeX 表达式

**代数运算**：
- `R1 + R2`：运动叠加 → `RotorComposition`
- `c * R`：缩放 → `Rotor2D`
- `sum([R1, R2, R3])`：支持 Python 内置 `sum()`

**示例**：
```python
from cprdspy.rotor import Rotor2D

# 基本圆
circle = Rotor2D(3, 1)
print(circle(0))          # (3+0j)
print(circle(np.pi/2))    # (0+3j)

# 代数运算
r1 = Rotor2D(2, 1)
r2 = Rotor2D(1, 3)
curve = r1 + r2           # RotorComposition
scaled = 2 * r1           # Rotor2D(4, 1)
conj = r1.conjugate()     # Rotor2D(2, -1)
```

---

#### `RotorComposition(rotors, center)`

多个 Rotor 的组合。

**参数**：
- `rotors` (list[Rotor2D])：Rotor 列表
- `center` (tuple)：中心偏移

**方法**：
- `evaluate(t)`：计算合成位置
- `frequencies()`：所有频率（去重）
- `spectrum()`：频率谱 `[(ω, r, φ), ...]`
- `is_closed()`：判断是否闭合
- `period()`：最小正周期
- `simplify()`：合并同频率项
- `total_radius()`：总半径

**示例**：
```python
from cprdspy.rotor import Rotor2D, RotorComposition

# 方式 1：加法运算符
curve = Rotor2D(3, 1) + Rotor2D(1, 7)

# 方式 2：直接构造
curve = RotorComposition([
    Rotor2D(3, 1),
    Rotor2D(1, 7),
])

# 分析
print(curve.frequencies())  # [1, 7]
print(curve.is_closed())    # True
print(curve.period())       # 6.283185307179586 (2π)
```

---

### 采样与分析

#### `trace(composition, t_start, t_end, n_points, return_complex)`

采样 Rotor 组合为坐标数组。

**参数**：
- `composition`：Rotor2D 或 RotorComposition
- `t_start` (float)：起始时间，默认 0
- `t_end` (float)：结束时间，默认自动判断周期
- `n_points` (int)：采样点数，默认 2000
- `return_complex` (bool)：是否返回复数数组

**返回**：
- `(t, x, y)`：时间数组 + 坐标数组（默认）
- `(t, z)`：时间数组 + 复数数组（return_complex=True）

**示例**：
```python
from cprdspy.rotor import Rotor2D, trace

curve = Rotor2D(3, 1) + Rotor2D(1, 7)
t, x, y = trace(curve, n_points=1000)

import matplotlib.pyplot as plt
plt.plot(x, y)
plt.axis('equal')
plt.show()
```

---

#### `compute_curvature(x, y, t)`

计算曲率（GA 公式）。

**参数**：
- `x, y`：坐标数组
- `t`：时间数组（可选）

**返回**：
- `kappa`：曲率数组

**公式**：
$$
\kappa = \frac{|v_x a_y - v_y a_x|}{(v_x^2 + v_y^2)^{3/2}}
$$

---

#### `compute_velocity(x, y, t)` / `compute_acceleration(x, y, t)`

数值微分求速度/加速度。

---

#### `arc_length(x, y, t)` / `total_length(x, y, t)`

弧长计算。

$$
s(t) = \int_0^t |\gamma'(\tau)| d\tau
$$

---

### 可视化

#### `rotor_plot(composition, backend, color_by, ...)`

统一绘图接口。

**参数**：
- `composition`：Rotor2D 或 RotorComposition
- `backend` (str)：'matplotlib' 或 'plotly'
- `color_by` (str)：None | 'curvature' | 'arc_length'
- 其他参数透传给对应后端

**示例**：
```python
from cprdspy.rotor import Rotor2D, rotor_plot

curve = Rotor2D(3, 1) + Rotor2D(1, 7)

# matplotlib 静态图
rotor_plot(curve, backend='matplotlib')

# plotly 交互图
rotor_plot(curve, backend='plotly')

# 按曲率着色
rotor_plot(curve, color_by='curvature')
```

---

#### `rotor_plot_mpl(composition, ax, color_by, cmap, ...)`

matplotlib 后端。

**特性**：
- 支持按曲率/弧长着色（使用 `LineCollection`）
- 支持自定义 colormap
- 可嵌入到已有的 matplotlib figure

---

#### `rotor_plot_plotly(composition, color_by, colorscale, dark, ...)`

plotly 后端。

**特性**：
- 交互式图表
- 深色/浅色主题
- 自动分段着色

---

#### `plot_rotor_chain(composition, t_value, show_trace, ...)`

绘制 Rotor 链（本轮可视化）。

展示每个 Rotor 的"本轮"圆和当前位置，直观显示运动叠加的几何过程。

**参数**：
- `composition`：RotorComposition
- `t_value` (float)：当前时刻
- `show_trace` (bool)：是否同时绘制完整轨迹

**示例**：
```python
from cprdspy.rotor import Rotor2D, plot_rotor_chain

curve = Rotor2D(3, 1) + Rotor2D(1, 7)
plot_rotor_chain(curve, t_value=1.0, show_trace=True)
```

---

### 3D Rotor API

#### `Rotor3D(radius, frequency, phase, e1, e2, center)`

三维旋转器。

**参数**：
- `radius` (float)：半径
- `frequency` (int|float)：角频率
- `phase` (float)：初相位
- `e1` (list[float])：旋转平面第一个基向量，默认 [1,0,0]
- `e2` (list[float])：旋转平面第二个基向量，默认 [0,1,0]
- `center` (list[float])：中心偏移，默认 [0,0,0]

**方法**：
- `evaluate(t)`：计算时刻 $t$ 的位置（3D 向量）
- `evaluate_xyz(t)`：返回 $(x, y, z)$ 元组
- `conjugate()`：共轭（反转旋转方向）
- `derivative()`：导数（速度向量）

**示例**：
```python
from cprdspy.rotor import Rotor3D

# XY 平面内的圆
circle = Rotor3D(3, 1, 0, [1,0,0], [0,1,0])
print(circle(0))          # [3, 0, 0]
print(circle(np.pi/2))    # [0, 3, 0]

# 3D 外摆线
curve = Rotor3D(3, 1, 0, [1,0,0], [0,1,0]) + Rotor3D(1, 5, 0, [0,1,0], [0,0,1])
```

---

#### `Rotor3DComposition(rotors, center)`

多个 Rotor3D 的组合。

**方法**：
- `evaluate(t)`：计算合成位置
- `frequencies()`：所有频率（去重）
- `is_closed()`：判断是否闭合
- `period()`：最小正周期

---

### nD Rotor API (Clifford)

#### `RotorClifford(radius, frequency, phase, e1, e2, center, n_dim)`

n 维旋转器（Clifford 代数）。

**参数**：
- `radius` (float)：半径
- `frequency` (int|float)：角频率
- `phase` (float)：初相位
- `e1` (list[float])：旋转平面第一个基向量
- `e2` (list[float])：旋转平面第二个基向量
- `center` (list[float])：中心偏移
- `n_dim` (int)：空间维度，默认 3

**数学**：
$$
R(t) = r \cdot \exp\left(-\frac{B(\omega t + \varphi)}{2}\right) \cdot e_1 \cdot \exp\left(\frac{B(\omega t + \varphi)}{2}\right)
$$

其中 $B = e_1 \wedge e_2$。

**示例**：
```python
from cprdspy.rotor import RotorClifford

# 3D（与 Rotor3D 等价）
r3d = RotorClifford(3, 1, 0, [1,0,0], [0,1,0], n_dim=3)

# 4D
r4d = RotorClifford(2, 1, 0, [1,0,0,0], [0,1,0,0], n_dim=4)

# 4D 曲线
curve4d = RotorClifford(2, 1, 0, [1,0,0,0], [0,1,0,0], n_dim=4) + \
          RotorClifford(1, 3, 0, [0,0,1,0], [0,0,0,1], n_dim=4)
```

---

### nD 采样与分析

#### `trace_nd(composition, t_start, t_end, n_points)`

采样 nD Rotor 组合曲线。

**返回**：
- `(t, x1, x2, ..., xn)`：时间数组 + 各坐标分量

**示例**：
```python
from cprdspy.rotor import Rotor3D, trace_nd

curve = Rotor3D(3, 1, 0, [1,0,0], [0,1,0]) + Rotor3D(1, 5, 0, [0,1,0], [0,0,1])
t, x, y, z = trace_nd(curve, n_points=1000)
```

---

#### `compute_curvature_nd(*coords, t)`

nD 曲率（GA 公式）。

**公式**：
$$
\kappa = \frac{\sqrt{|v|^2|a|^2 - (v \cdot a)^2}}{|v|^3}
$$

---

#### `compute_torsion_3d(x, y, z, t)`

3D 挠率。

**公式**：
$$
\tau = \frac{v \cdot (a \times j)}{|v \times a|^2}
$$

---

#### `arc_length_nd(*coords, t)` / `total_length_nd(*coords, t)`

nD 弧长计算。

---

### 3D 可视化

#### `rotor_plot_3d(composition, backend, color_by, ...)`

统一 3D 绘图接口。

**参数**：
- `backend` (str)：'matplotlib' 或 'plotly'
- `color_by` (str)：None | 'curvature' | 'arc_length'

**示例**：
```python
from cprdspy.rotor import Rotor3D, rotor_plot_3d

curve = Rotor3D(3, 1, 0, [1,0,0], [0,1,0]) + Rotor3D(1, 5, 0, [0,1,0], [0,0,1])

# matplotlib 3D
rotor_plot_3d(curve, backend='matplotlib')

# plotly 3D 交互
rotor_plot_3d(curve, backend='plotly')

# 按曲率着色
rotor_plot_3d(curve, color_by='curvature')
```

---

## 快速开始

### 安装

```bash
# 确保已安装依赖
pip install numpy matplotlib plotly
```

### 基础示例

```python
from cprdspy.rotor import Rotor2D, rotor_plot

# 1. 一个圆
circle = Rotor2D(3, 1)
rotor_plot(circle, title='Circle')

# 2. 外摆线（两个 Rotor 叠加）
epicycle = Rotor2D(3, 1) + Rotor2D(1, 7)
rotor_plot(epicycle, title='Epicycle')

# 3. 按曲率着色
rotor_plot(epicycle, color_by='curvature', title='Curvature')

# 4. 三个 Rotor 叠加
curve = Rotor2D(5, 1) + Rotor2D(3, -2) + Rotor2D(1, 5)
rotor_plot(curve, backend='plotly', title='3-Rotor')
```

### 进阶示例

```python
import numpy as np
from cprdspy.rotor import Rotor2D, trace, compute_curvature, plot_rotor_chain
import matplotlib.pyplot as plt

# 构造复杂曲线
curve = Rotor2D(5, 1) + Rotor2D(3, -2) + Rotor2D(1, 5)

# 采样
t, x, y = trace(curve, n_points=2000)

# 计算曲率
kappa = compute_curvature(x, y, t)

# 可视化
fig, axes = plt.subplots(1, 2, figsize=(16, 8))

# 左图：曲线
axes[0].plot(x, y, 'b-', lw=1)
axes[0].set_title('Curve')
axes[0].axis('equal')

# 右图：曲率
axes[1].plot(t, kappa, 'r-', lw=1)
axes[1].set_title('Curvature κ(t)')
axes[1].set_xlabel('t')
axes[1].set_ylabel('κ')

plt.tight_layout()
plt.show()

# 本轮可视化
plot_rotor_chain(curve, t_value=1.0, show_trace=True)
```

---

## 设计哲学

### CPR 理论

**CPR = Circle Point Round Dot Surface Pyramid**

核心思想：**几何 = 运动的组合**

复杂的几何形状可以分解为简单圆周运动的叠加。这与 Fourier 分析的思想一致：
- 时域：复杂信号 = 简单正弦波的和
- 空域：复杂曲线 = 简单圆周运动的和

### 与现有模块的关系

`rotor` 模块是 cprdspy 的"内核升级"。现有的 `flowers()`, `star()`, `spiral()` 等函数未来都可以用 Rotor 组合来统一表达：

```python
# 传统方式
flower(n=5, R=3, r=1)

# Rotor 方式
flower = Rotor2D(3, 1) + Rotor2D(1, 5)
```

### 未来扩展

- ~~**Phase 0**：2D Rotor 内核~~ ✓ 已完成
- ~~**Phase 1**：3D Rotor（四元数）~~ ✓ 已完成
- **Phase 2**：微分几何深入（Frenet 标架、测地线）
- ~~**Phase 3**：Clifford 代数 nD 推广~~ ✓ 已完成
- **Phase 4**：Hopf 纤维化
- **Phase 5**：运动树（递归组合）
- **Phase 6**：CPR 语言（领域特定语言）
- **Phase 7**：音频映射

---

## 数学附录

### 复数与二维旋转

欧拉公式：
$$
e^{i\theta} = \cos\theta + i\sin\theta
$$

二维旋转：
$$
z' = e^{i\theta} \cdot z
$$

### 四元数与三维旋转

四元数 $q = w + xi + yj + zk$，其中 $i^2 = j^2 = k^2 = ijk = -1$。

单位四元数表示旋转：
$$
q = \cos\frac{\theta}{2} + \sin\frac{\theta}{2}(n_x i + n_y j + n_z k)
$$

其中 $\mathbf{n} = (n_x, n_y, n_z)$ 是旋转轴，$\theta$ 是旋转角度。

旋转向量：
$$
v' = q \cdot v \cdot q^*
$$

其中 $q^*$ 是共轭四元数。

### Clifford 代数与 nD 旋转

**Clifford 代数** $Cl(n)$ 由 $n$ 个生成元 $e_1, \ldots, e_n$ 生成，满足：
$$
e_i e_j + e_j e_i = -2\delta_{ij}
$$

**二重向量**（bivector）：
$$
B = e_i \wedge e_j = e_i e_j \quad (i \neq j)
$$

**Rotor**：
$$
R = \exp\left(-\frac{B\theta}{2}\right) = \cos\frac{\theta}{2} - \sin\frac{\theta}{2} B
$$

**旋转**（三明治积）：
$$
v' = R \cdot v \cdot \tilde{R}
$$

其中 $\tilde{R}$ 是 $R$ 的 reverse（反转）。

**维度对应**：
| 代数 | 维度 | Rotor 形式 |
|------|------|-----------|
| $\mathbb{C} \cong Cl(2)^+$ | 2D | $e^{i\theta}$ |
| $\mathbb{H} \cong Cl(3)^+$ | 3D | $\exp(-B\theta/2)$ |
| $Cl(n)^+$ | nD | $\exp(-B\theta/2)$ |

### Fourier 级数

周期函数 $f(t)$ 的 Fourier 展开：
$$
f(t) = \sum_{k=-\infty}^{\infty} c_k e^{ikt}
$$

其中 Fourier 系数：
$$
c_k = \frac{1}{2\pi} \int_0^{2\pi} f(t) e^{-ikt} dt
$$

Rotor 组合正是 Fourier 级数的有限截断。

### 几何代数（GA）

在 GA 中，外积（wedge product）的定义：
$$
a \wedge b = \frac{1}{2}(ab - ba)
$$

在 2D 中，$e_1 \wedge e_2$ 是伪标量（bivector），记作 $I$。

曲率公式的 GA 形式：
$$
\kappa = \frac{|v \wedge a|}{|v|^3}
$$

这个公式在任意维度都成立，无需叉积。

---

## 参考资料

1. **Fourier Analysis** — Stein & Shakarchi
2. **Geometric Algebra for Physicists** — Doran & Lasenby
3. **Visual Complex Analysis** — Needham
4. **Epicycles, Fourier, and the Art of Curve Drawing** — online resources

---

## 许可证

MIT License

---

## 作者

cprdspy team

**CPR** = Circle Point Round Dot Surface Pyramid

*Geometry by Composition of Motion.*

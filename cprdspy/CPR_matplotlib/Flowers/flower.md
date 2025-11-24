# Flower(Round Petal Flower)
## flower_arc
```python

```

## flower_petal
```python
from cprdspy.CPR_matplotlib.Arcs.arc import arc
import numpy as np


def flower_petal(
    R=1,
    r=1,
    n=4,
    rotation=0,
    color="#0f0",
    alpha=1,
    center=(0, 0),
    points=1000,
    linestyle="-",
    linewidth=1,
    label=None,
    marker=None,
    markersize=5,
    markerfacecolor="r",
    markeredgecolor="k",
    markeredgewidth=1,
    ax=None,
    plot_center=False,
    center_color="#0f0",
    center_size=8,
    use_degree=True,  # 默认使用角度制输入
    plot=True,
    direction="ccw",
    return_petal=False,
    **kwargs,
):
    """
    绘制一片花瓣。
    rotation: 如果 use_degree=True，则以度为单位；否则以弧度为单位。
    内部所有三角计算使用弧度（theta），传递给 arc 的角度参数应为不含旋转的基角，
    并把旋转通过 rotation 参数单独传给 arc（避免重复旋转）。
    """
    # 基本参数（弧度）
    angle = 2 * np.pi / n
    a = R * np.sin(np.pi / n)
    if r > 0:
        beta = np.arccos(min(1, max(-1, (a) / r)))  # 限制在[-1,1]范围内
    else:
        beta = 0
    theta_arc = np.pi / 2 - np.pi / n + np.arccos(min(1, max(-1, (a) / r)))

    # 将输入 rotation 转为弧度以便做三角运算
    rotation_rad = np.deg2rad(rotation) if use_degree else rotation

    # 计算基角（不包含 rotation）——这些是 arc 的 angle1/angle2 基本值
    center1_theta = rotation_rad + angle / 2
    center2_theta = rotation_rad - angle / 2

    # 计算圆心坐标（使用 rotation_rad 定位圆心）
    center1 = (
        np.cos(center1_theta) * R + center[0],
        np.sin(center1_theta) * R + center[1],
    )
    center2 = (
        np.cos(center2_theta) * R + center[0],
        np.sin(center2_theta) * R + center[1],
    )

    # 角度计算（相对于各自圆心的起始和结束角度）
    if abs(r - a) < 1e-12:
        # 特殊情况：r = a
        theta1_base_rad = np.pi + angle / 2
        theta2_base_rad = np.pi + angle / 2 + theta_arc
        theta3_base_rad = np.pi / 2
        theta4_base_rad = np.pi / 2 + theta_arc
    elif r > a:
        # 一般情况：r > a
        theta1_base_rad = np.pi + angle / 2
        theta2_base_rad = np.pi + angle / 2 + theta_arc
        theta3_base_rad = np.pi / 2 - beta
        theta4_base_rad = np.pi / 2 - beta + theta_arc
    else:
        print("r=", r, ",a=", a)
        print(f"r<a,不能形成花瓣。最小需要 r > {a:.3f}")
        return None

    # 传给 arc 的角度参数：如果 use_degree，需要把基角从弧度转换为度数；
    # rotation_for_arc 则传入原始输入（度或弧度），由 arc 内部统一处理
    if use_degree:
        theta1 = np.rad2deg(theta1_base_rad)
        theta2 = np.rad2deg(theta2_base_rad)
        theta3 = np.rad2deg(theta3_base_rad)
        theta4 = np.rad2deg(theta4_base_rad)
        rotation_for_arc = rotation  # 原始度数
    else:
        theta1 = theta1_base_rad
        theta2 = theta2_base_rad
        theta3 = theta3_base_rad
        theta4 = theta4_base_rad
        rotation_for_arc = rotation_rad  # 弧度

    # 只有在需要绘制时才导入 matplotlib
    if plot:
        import matplotlib.pyplot as plt

        if ax is None:
            ax = plt.gca()

    arc_d1 = None
    arc_d2 = None

    # 选择绘制分支（传入的角度和 rotation_for_arc 已与 use_degree 匹配）
    if abs(r - a) < 1e-12 or r > a:
        arc_d1 = arc(
            r,
            theta1,
            theta2,
            rotation_for_arc,
            color,
            alpha,
            center1,
            points,
            linestyle,
            linewidth,
            label,
            marker,
            markersize,
            markerfacecolor,
            markeredgecolor,
            markeredgewidth,
            ax,
            use_degree,
            plot,
            direction,
            return_petal,
            **kwargs,
        )
        arc_d2 = arc(
            r,
            theta3,
            theta4,
            rotation_for_arc,
            color,
            alpha,
            center2,
            points,
            linestyle,
            linewidth,
            label,
            marker,
            markersize,
            markerfacecolor,
            markeredgecolor,
            markeredgewidth,
            ax,
            use_degree,
            plot,
            direction,
            return_petal,
            **kwargs,
        )

    # 画圆心（用于调试）
    if plot_center and plot:
        import matplotlib.pyplot as plt

        plt.scatter(
            center1[0], center1[1], color=center_color, s=center_size, alpha=alpha
        )
        plt.scatter(
            center2[0], center2[1], color=center_color, s=center_size, alpha=alpha
        )

    # 如果不绘制但需要返回花瓣数据
    if not plot and arc_d1 is not None and arc_d2 is not None:
        return (center1[0], center1[1]), (center2[0], center2[1]), arc_d1, arc_d2
    
```

## 代码说明：






下面我会解释 `flower_petal`和它依赖的 `arc`（arc.py）的实现细节、数学推导与关键注意点，并在必要处给出建议和可执行的测试方法。
。

### 1) 接口与“契约”总结（inputs / outputs / 成功条件）
- `flower_petal(...)`
  - 主要输入：
    - R：中心大圆半径（花朵半径）
    - r：单瓣构成小圆半径（花瓣圆）
    - n：花瓣特性（整除圆周）
    - rotation：整体旋转（当 use_degree=True 时以度为单位；否则弧度）
    - use_degree：控制传入角度单位（True表示 degree）
    - center：全局中心坐标
  - 输出／效果：
    - 在 ax 上绘制两段弧（对应一片花瓣左右两侧的小圆弧）。
    - 若 plot=False，函数尝试返回 (center1, center2, arc_d1, arc_d2)（当前代码有分支返回）。
  - 成功准则：
    - 当 r > a = R * sin(pi/n) 时能绘制合理的花瓣（两圆有两个交点）。
    - 无论 use_degree True/False，最终在画面上产生几何上等价的花瓣。

- `arc(...)`（arc.py）
  - 接受 angle1, angle2, rotation，和 use_degree 标志。
  - 内部会把输入角度统一转换为弧度（如果 use_degree=True），然后生成一个以 theta 为基准的角度序列，并“应用旋转”：
    - 使用旋转矩阵等价公式把点旋转：
$$x = cx + r*(cos(theta)*cos(rot) - sin(theta)*sin(rot)),\\
 y = cy + r*(sin(theta)*cos(rot) + cos(theta)*sin(rot))$$
  - 支持 plot=True/False；plot=False 时返回 x,y 数组（这对数值比对很有用）。

### 2) 几何与公式（关键推导）
- 花瓣几何中常用量：
  - 单瓣角度（以弧度计）：  
    $$\text{angle} = \frac{2\pi}{n}$$
  - a：大圆与小圆圆心连线在极角处的投影（或决定是否有交点的阈值）：
    $$a = R\sin\frac{\pi}{n}$$
    花瓣能成形的条件是小圆半径 r 满足
    $$r > a$$
    否则两个小圆与大圆切不到合适位置，交点退化或不存在。
  - beta（用于计算交点位置角度的中间量）：
    $$\beta = \arccos\left(\frac{a}{r}\right)\quad(\text{当 }|a/r|\le 1)$$
    为避免浮点误差，代码里使用了裁减：`np.arccos(min(1,max(-1,a/r)))`。
  - theta_arc：代码中用来计算弧长所需的角度偏移：
    代码给出的表达（近似）为：

    $theta_{arc} = \pi/2 - \pi/n + \arccos(a/r)$

    （这是实现中用于推断弧的终止角的组合表达，具体几何意义和变量命名在代码里是工程化的）

- arc 的旋转应用（来自 `arc` 函数的实现）：
  - arc 接收到的基角序列为 theta（已在内部转为弧度），然后通过“旋转矩阵”将弧旋转 rot：
    $$x = c_x + r(\cos\theta\cos\mathrm{rot} - \sin\theta\sin\mathrm{rot})$$
    $$y = c_y + r(\sin\theta\cos\mathrm{rot} + \cos\theta\sin\mathrm{rot})$$
  - 这在代数上相当于把每个角度做 $\theta \mapsto \theta + \mathrm{rot}$（注意 rot 已为弧度）。

### 3) 代码关键点逐行解析（聚焦单元格4的实现逻辑）
- 角度基准与单位：
  - 代码把内部三角计算统一用弧度（良好实践），因此把传入的 `rotation` 根据 `use_degree` 转成 `rotation_rad`：
    - 当 `use_degree=True` 时：`rotation_rad = np.deg2rad(rotation)`，否则 `rotation_rad = rotation`。
- 计算两个小圆圆心：
  - 两个小圆心在大圆周上，位置以大圆极角偏移 angle/2 为基准，两个中心分别位于：
    $$\theta_{c1} = \text{rotation\_rad} + \frac{\text{angle}}{2}$$
    $$\theta_{c2} = \text{rotation\_rad} - \frac{\text{angle}}{2}$$
  - 圆心坐标：
    $$C_1 = (R\cos\theta_{c1} + c_x,\; R\sin\theta_{c1} + c_y)$$
    $$C_2 = (R\cos\theta_{c2} + c_x,\; R\sin\theta_{c2} + c_y)$$
- 计算弧的端点角（相对于各自圆心）：
  - 依据 r 与 a 的关系分支处理：r≈a、r>a、r<a（报错）。
  - 代码推导出四个基角（theta1_base_rad 等），分别作为两个小圆上两段弧的角度端点（在内部以弧度给出）。
- 传递给 `arc`：
  - 如果 `use_degree=True`，代码会把基角从弧度转换回度数（`np.rad2deg(...)`），并把 `rotation_for_arc` 设为原始 `rotation`（度），然后调用 `arc(..., use_degree=True, rotation=rotation_for_arc)`。
  - 如果 `use_degree=False`，直接以弧度调用 `arc(..., use_degree=False, rotation=rotation_for_arc)`。
  - 也就是说：当前实现会把“基角 + rotation”以两种方式传递——基角按 unit 转换，rotation 也按 unit 传递。由于 `arc` 在内部会再把角度转为弧度并将 `rot` 加到 `theta` 上，这会导致若在上游也把角度先加了 rotation（或以 rotation_rad 计算圆心时混用）就有“重复旋转”的风险——这正是之前你观察到的问题来源。

### 4) 导致 use_degree 行为差异的可能根源（诊断）
- 重复旋转：
  - 在 `flower_petal` 里，圆心位置是用 `rotation_rad` 已经应用了旋转来定位圆心；同时又把 `rotation_for_arc` 传给 `arc` 并由 `arc` 再应用旋转，会出现旋转应用两次或以不同单位重复应用的风险。
- 单位转换顺序差异：
  - 当 use_degree=True 时，`flower_petal` 把角度基值转换为度再传给 `arc`；`arc` 会再把度转为弧度。只要两端的转换与规范一致，等价性应成立，但细节上需保证：
    - 传给 `arc` 的角度对表示的是“相对于其中心且不含 arc 内部 rotation 的基角”，还是“已包含 rotation 的绝对角”。如果两端理解不一致会发生错位。
- 角度正规化与方向（ccw/cw）：
  - `arc` 内部会把 theta1/theta2 转成 [0,2π) 范围并根据 direction 调整顺序（若 theta2 <= theta1 则加 2π）。如果 `flower_petal` 传入角度时没有和 `arc` 的方向假设对齐（例如传入了负角或超 360° 的角），在 use_degree=True/False 时可能遇到不同的数值化差异（浮点或归一化分支触发不同）。
- 数值舍入与角度范围：
  - 度->弧度或弧度->度转换的微小舍入，联合条件判断（<= vs <）有时会导致某些分支（theta2 <= theta1）在一个模式触发而在另一个模式不触发，从而输出段不同。

### 5) 建议的稳健方案（两种可行做法）
我推荐两种明确而稳健的策略之一（任选其一）：

方案 A — 上游计算“绝对端点角”，并把 arc 的 rotation 设为 0
- 思路：上游（flower_petal）负责把弧的两个端点计算为“相对于图像全局并已包含旋转的绝对角度（或直接把交点坐标传给 arc_point）”，然后调用 `arc(..., rotation=0)`（或使用 `arc_point` 给出两个端点坐标）。这样就避免了 arc 内部的旋转再加一次。
- 优点：消除了重复旋转的可能性，上下游单位转换更简单（只需保证在传参时单位一致）。
- 实现提示：
  - 计算交点坐标 p1,p2（直接在全局坐标系），使用 `arc_point(center=..., point1=p1, point2=p2, plot=...)` 来绘弧；或把交点角通过 atan2 转为角度/弧度后传给 arc，但此时把 `rotation=0`。
- 适配 use_degree：
  - 如果用角度传参给 arc（use_degree=True），就将 atan2 的弧度转为度再传；若 use_degree=False，直接传弧度。关键是不要同时再把旋转传入 arc。

方案 B — 保持 angle/rotation 的“单源”并规范化所有角度（严格约定）
- 思路：明确约定 `flower_petal` 只传“基角（不含旋转）”给 arc，并把 rotation 单独以与 arc 约定的单位传入（正如现在代码的初衷）。但要确保：
  1. 上游计算圆心时不要提前把 rotation 应用到基角（或如果应用了，则在传给 arc 的基角上反向抵消），保持一致性；
  2. 在传参前将所有角度做明确的正规化（例如把角度标准化到 [0, 360) 或 [0, 2π)）；
  3. 对 <= 与 < 判断边界采用明确容差（如 eps=1e-9）避免分支不一致。
- 这个方案需要严谨地检查每个角是“基角”还是“带旋转的绝对角”。

个人建议更倾向方案 A（更直接、易验证）。

### 6) 推荐的验证测试（可直接在 notebook 运行）
做数值对比测试，尽量避免只看图像。测试思路：

- 取一个具体参数集，比如：
  - R = 1, r = 1.1, n = 6, rotation = 30（度）
- 在两种模式下分别得到 arc 的坐标数组：
  1. 用 radians 模式：
     - 计算角度基值为弧度，调用 arc(..., use_degree=False, rotation=rotation_rad, plot=False) 得到 x_r,y_r。
  2. 用 degrees 模式：
     - 使用相应的度数基角，调用 arc(..., use_degree=True, rotation=rotation_degrees, plot=False) 得到 x_d,y_d。
- 比较 x_r 与 x_d（先把 x_d 转为数值并/或角度与弧度统一）：
  - 用 np.allclose(x_r, x_d, atol=1e-8, rtol=1e-6) 检查一致性；若不一致，输出两个数组的最大差异并用第一个不同索引定位问题。
- 如果你采用方案 A（把 rotation 设为 0 并传入绝对角或点），则对比：
  - arc(...) with rotation=0 vs arc_point(...) with the two computed endpoints — 两者应一致。

如果你需要，我可以现在在 notebook 中添加并运行一个小单元来执行上述比较（并打印差异），定位到底是 `flower_petal` 的角处理问题还是 `arc` 的转换细节导致差异。

### 7) 常见边界与陷阱（简要清单）
- r ≤ a：没有或退化交点，无法绘制花瓣（函数应当提前报错或退回）。
- 浮点导致 acos 的输入超出 [-1,1]：必须裁减。
- 角度单位混用：确保所有传参（angle1, angle2, rotation）在单位上与 `use_degree` 参数一致。
- 重复旋转：在计算圆心时已应用 rotation，但还把 rotation 传入 `arc` 会导致双重旋转。
- 角度正规化分支差异（theta2 <= theta1 判断）在接近边界时可能导致不同分支被触发，从而出现方向或截断差异。
- arc 的 direction 参数（ccw / cw）：需要与传入 angle1/angle2 的顺序约定一致。


















## flower
```python
def flower(
    R=1,
    r=1,
    n=4,
    rotation=0,
    color="#0f0",
    alpha=1,
    center=(0, 0),
    points=1000,
    linestyle="-",
    linewidth=1,
    label=None,
    marker=None,
    markersize=5,
    markerfacecolor="r",
    markeredgecolor="k",
    markeredgewidth=1,
    ax=None,
    plot_center=False,
    center_color="#0f0",
    center_size=8,
    use_degree=True,  
    plot=True,
    direction="ccw",
    return_petal=False,
    **kwargs,
):
    for i in range(n):
        flower_petal(
            R,
            r,
            n,
            rotation + i * 360 / n if use_degree else i * 2 * np.pi / n,
            color,
            alpha,
            center,
            points,
            linestyle,
            linewidth,
            label,
            marker,
            markersize,
            markerfacecolor,
            markeredgecolor,
            markeredgewidth,
            ax,
            plot_center,
            center_color,
            center_size,
            use_degree,
            plot,
            direction,
            return_petal,
            **kwargs,
        )
```


## 代码说明：
通过对flower_petal()函数的调用，生成一朵单层花flower，可根据参数调整改变花的形状、颜色、大小等特征。






## flower_field
```python
```

## flower_stem
```python
```

# Oval Flower(Oval Petal Flower)
## oval_flower_arc
```python
```

## oval_flower_petal
```python
```

## oval_flower
```python
```

## oval_flower_field
```python
```

## oval_flower_stem
```python
```

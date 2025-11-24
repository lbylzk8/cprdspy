# Arc
## arc_point
```python
def arc_point(
    center=(0, 0),
    point1=(1, 0),
    point2=(-1, 0),
    color="#0f0",
    alpha=1,
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
    plot=True,
    direction="ccw",  # 'ccw' or 'cw'
    return_arc=False,
    **kwargs,
):
    """
    画通过 point1 到 point2 的圆弧（以 center 为圆心），
    如果 point1 和 point2 的半径不同，会使用 point1 的半径并打印警告。
    返回 (x, y) 数组; 如果 plot=True，会在给定的 ax 上绘图。
    """
    # 计算端点到圆心的向量
    v1 = np.array(point1) - np.array(center)
    v2 = np.array(point2) - np.array(center)

    # 计算向量的模长（半径）
    r1 = np.linalg.norm(v1)
    r2 = np.linalg.norm(v2)
    if r1 == 0 or r2 == 0:
        raise ValueError("point1/point2 不应与 center 重合")
    if abs(r1 - r2) > 1e-6:
        print(f"Warning: radii differ (r1={r1:.6g}, r2={r2:.6g}); using r1 for arc")
    r = r1

    # 计算两点对应的角（弧度）
    theta1 = np.arctan2(v1[1], v1[0]) % (2 * np.pi)
    theta2 = np.arctan2(v2[1], v2[0]) % (2 * np.pi)

    # 根据方向生成角度序列（确保按期望方向从 point1 到 point2）
    if direction == 'ccw':
        if theta2 <= theta1:
            theta2 = theta2 + 2 * np.pi
        theta = np.linspace(theta1, theta2, points)
    else:  # cw
        if theta1 <= theta2:
            theta1 = theta1 + 2 * np.pi
        theta = np.linspace(theta1, theta2, points)[::-1]

    # 计算弧上点坐标
    x = center[0] + r * np.cos(theta)
    y = center[1] + r * np.sin(theta)

    if not plot:
        return x, y

    # 绘图：校验 ax 并绘制
    if ax is None:
        ax = plt.gca()
    elif isinstance(ax, bool):
        raise ValueError("ax 参数不能是布尔值；如果不想绘图请使用 plot=False")

    arc = ax.plot(
        x,
        y,
        color=color,
        alpha=alpha,
        linestyle=linestyle,
        linewidth=linewidth,
        label=label,
        marker=marker,
        markersize=markersize,
        markerfacecolor=markerfacecolor,
        markeredgecolor=markeredgecolor,
        markeredgewidth=markeredgewidth,
        **kwargs,
    )
    ax.set_aspect("equal", adjustable="box")
    if label:
        ax.legend()
    if return_arc:
        return arc[0] if arc else None
```















## 代码说明：


下面按小节把 `arc_point` 的每一部分解释清楚，并给出输入/输出契约、边界情况和可改进建议，方便你快速理解和复用。

### 一句概况
`arc_point` 生成并（可选）绘制以 `center` 为圆心、连接 `point1`→`point2` 的圆弧。函数返回弧上点的坐标数组 (x, y)，并可在 `ax` 上绘图或返回绘制的 Line2D（由 `return_arc` 控制）。

---

### 输入/输出“契约”
- 输入（重要参数）：
  - center: (x0, y0) 圆心
  - point1, point2: 两个端点坐标（弧从 point1 到 point2）
  - points: 采样点数（生成弧上的点数量）
  - direction: 'ccw'（逆时针，默认）或 'cw'（顺时针）
  - ax: matplotlib Axes 对象或 None（None 时用 plt.gca()）
  - plot: bool；True 时绘制在 ax 上，False 时只返回 (x, y)
  - 其余：颜色、线型、marker 等绘图参数
- 输出：
  - 当 plot=False：返回 (x, y) 两个一维 numpy 数组
  - 当 plot=True 且 return_arc=True：返回绘制曲线的第一个 Line2D 对象（否则不返回）
- 错误/异常：
  - 若 point1 或 point2 与 center 重合（半径为 0），抛出 ValueError
  - 若传入 `ax` 为布尔值，会抛出 ValueError（提示使用 plot=False）

---

### 代码逐步解释

1. 函数签名与 docstring
   - `direction` 参数允许你选择弧的方向（'ccw' 或 'cw'）。
   - docstring 简要说明了行为：若两个端点半径不同，使用 point1 的半径并打印警告。

2. 计算向量 v1, v2
   - v1 = point1 - center，v2 = point2 - center：分别是从圆心指向两个端点的向量。
   - 这些向量用于计算半径和角度。

3. 计算半径 r1, r2
   - 使用 `np.linalg.norm` 计算长度（即各自的半径）。
   - 如果任一为 0（点位于圆心），抛错（因为无法定义角度或弧）。
   - 若两半径差异超过 1e-6，打印警告并以 r1（point1 的半径）为准 —— 这是简单策略：函数假设弧属于以 point1 为半径的圆。

4. 计算角度 theta1, theta2（弧度）
   - `np.arctan2(y, x)` 返回 [-pi, pi]，再取 `% (2*pi)` 归一到 [0, 2π)。
   - 这样处理便于比较角度与处理跨 2π 的情况。

5. 生成角度序列（按 direction）
   - 如果 direction == 'ccw'（逆时针）：
     - 若 theta2 <= theta1，说明从 point1 到 point2 要跨 2π（例如 point1 在 350°，point2 在 10°），因此把 theta2 加 2π，使序列单调上升。
     - 然后用 np.linspace(theta1, theta2, points) 生成从 theta1 到 theta2 的点。
   - 否则（'cw' 顺时针）：
     - 若 theta1 <= theta2，说明顺时针移动要跨 2π（把 theta1 加 2π），然后生成升序，但最后用 [::-1] 反转，使其从 point1 向 point2 的角度序列按顺时针方向递减。
   - 结果 `theta` 中的角度都是弧度，并按你期望的方向从 point1 到 point2 排列。

6. 计算弧上坐标
   - $x = center_x + r * cos(theta)$
   - $y = center_y + r * sin(theta)$
   - 这就是极坐标到笛卡尔坐标的标准转换；使用同一半径 r（上面决定为 r1）。

7. plot 控制
   - 如果 `plot=False`，直接返回 x, y（不绘图）。
   - 否则进入绘图流程：
     - 如果 `ax is None`，使用 `plt.gca()` 获取当前 Axes（或自动创建）。
     - 如果 `ax` 是布尔值（例如误写 `ax=False`），抛出 ValueError，避免后续调用 `ax.plot()` 时出现 "'bool' object has no attribute 'plot'" 的难解错误。
     - 使用 `ax.plot(x, y, ...)` 绘制，并设置坐标轴等比（保持圆的比例）。
     - 若提供了 `label`，会显示图例。
     - 如果 `return_arc` 为 True，会返回 `arc[0]`（第一个 Line2D），便于后续修改样式或保存引用。

---

### 数学/几何要点
- 旋转与角度处理：
  - 通过 arctan2 获取角度，再用 % (2π) 正规化到非负区间。
  - 为了处理从较大角度到较小角度需要“跨越 2π”的情况，故在比较后加 2π。
- 弧上点均匀分布是基于角度均匀采样（np.linspace）。注意：若你希望按弧长更均匀（当半径 constant 时角度均匀相当于弧长均匀），这里是可以接受的；但若半径变化或想用更复杂路径需调整。

---

### 使用示例
- 只获取数据（不绘图）：
  x, y = arc_point(center=(0,0), point1=(1,0), point2=(0,1), plot=False)
- 在当前 axes 上绘图（默认 ccw）：
  arc_point(center=(0,0), point1=(1,0), point2=(0,1))
- 指定顺时针：
  arc_point(center=(0,0), point1=(1,0), point2=(0,1), direction='cw')
- 获取绘制对象以便后续修改：
  line = arc_point(..., plot=True, return_arc=True)

---

### 常见边界与注意事项
- 半径不同（r1 != r2）：当前实现选择 r1（point1 的半径）。如果端点位于不同圆上，函数无法画出准确的“通过两点且以同一圆心为圆心”的圆弧——因为不存在这样的圆。你可能希望：
  - 抛错，而不是采用近似；
  - 或者选择两点的平均半径、或按参数让用户指定采用哪一个半径。
- angle wrap（跨 2π）：代码已处理，但要注意你期望的方向（ccw/cw）和角度的输入是否为度/弧度（此函数假设输入坐标直接为笛卡尔坐标，所以无 degree 参数问题）。
- 高精度需要更多 points：默认 1000 点通常足够，但绘制非常短的弧或用于精确测量时可增大该值。
- ax 参数不要传布尔值：若希望“不绘图”请传 plot=False，而不是 ax=False。

---

### 小改进建议（可选）
- 在 docstring 中明确返回类型：例如 `(x: np.ndarray, y: np.ndarray)`，并说明 `return_arc` 的行为。
- 当 r1 和 r2 差异较大时改为抛错而非默默打印警告（更安全）。
- 增加参数 `use_radius='point1'|'point2'|'mean'`，让调用者明确选择要使用的半径策略。
- 添加类型注解与单元测试（例如：点在同一圆上、跨 2π 的情况、direction 两种）。
- 提供 `start_marker=True/False` 参数，直接绘制起点/终点标注（现在可通过外部 `ax.scatter` 实现）。
- 支持返回完整的 matplotlib Line2D 对象（无论 return_arc 值，或者增加 `return_line=True`），以便进一步样式调整。











## arc_degree
```python
def arc(
    r=1,
    angle1=45,
    angle2=135,
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
    markerfacecolor="b",
    markeredgecolor="r",
    markeredgewidth=1,
    ax=None,
    use_degree=True,
    plot=True,
    direction="ccw",  # 'ccw' or 'cw'
    return_arc=False,
    **kwargs,
):
    # 1) 生成角度数组并统一为弧度
    if use_degree:
        theta1 = np.deg2rad(angle1)
        theta2 = np.deg2rad(angle2)
        rot = np.deg2rad(rotation)
    else:
        theta1 = angle1
        theta2 = angle2
        rot = rotation

    # 根据 direction 生成角度序列（支持 'ccw' 和 'cw'）
    if direction == 'ccw':
        if theta2 <= theta1:
            theta2 = theta2 + 2 * np.pi
        theta = np.linspace(theta1, theta2, points)
    else:  # cw
        if theta1 <= theta2:
            theta1 = theta1 + 2 * np.pi
        theta = np.linspace(theta1, theta2, points)[::-1]

    # 2) 计算旋转后的点（等价于 theta + rot）
    cos_rot = np.cos(rot)
    sin_rot = np.sin(rot)

    x = center[0] + r * (np.cos(theta) * cos_rot - np.sin(theta) * sin_rot)
    y = center[1] + r * (np.sin(theta) * cos_rot + np.cos(theta) * sin_rot)

    if not plot:
        return x, y
    else:
        if ax is None:
            ax = plt.gca()
        arc = ax.plot(
            x,
            y,
            color=color,
            alpha=alpha,
            linestyle=linestyle,
            linewidth=linewidth,
            label=label,
            marker=marker,
            markersize=markersize,
            markerfacecolor=markerfacecolor,
            markeredgecolor=markeredgecolor,
            markeredgewidth=markeredgewidth,
            **kwargs,
        )
        ax.axis("equal")
        if label:
            ax.legend()
        if return_arc:
            return arc[0] if arc else None
```



## 代码说明：

下面按小节把 `arc`（在代码中也叫 `arc_degree` 的变体）函数逐行解释，包含输入/输出契约、数学含义、边界/异常和若干改进建议，方便你快速理解与复用。

### 一句话概况  
- 这个函数生成并（可选）绘制以 `center` 为圆心、半径 r、从角度 angle1 到 angle2 的圆弧；支持以度为单位或弧度（由 `use_degree` 控制），并支持旋转（rotation）与绘图控制（ax/plot/return_arc），还可按 `direction` 指定顺时针或逆时针绘制顺序。

### 参数与返回（契约）
- 主要输入：
  - r: 半径（标量）
  - angle1, angle2: 起始、终止角（默认以度为单位，use_degree=True 时会转换为弧度）
  - rotation: 额外旋转角（同样按 use_degree 处理）
  - center: 圆心 (x0, y0)
  - points: 采样点数（弧上点数量）
  - direction: 'ccw'（逆时针，默认）或 'cw'（顺时针）
  - ax, plot, return_arc: 绘图控制（见下）
  - 其它样式参数：color, linewidth, linestyle, marker 等
- 返回：
  - 如果 plot=False：返回 (x, y) 两个 numpy 数组
  - 如果 plot=True 且 return_arc=True：返回第一个 Line2D（arc[0]）
  - 否则不返回（或返回 None）

### 代码逐步解析

1) 角度归一与旋转角处理
- 如果 use_degree 为 True，则先把 angle1、angle2、rotation 用 np.deg2rad 转成弧度：
  theta1 = deg2rad(angle1), theta2 = deg2rad(angle2), rot = deg2rad(rotation)
  否则它们已经被视为弧度。
- 这样后续所有三角函数都使用弧度，避免单位混淆。

2) 根据 direction 生成角度序列 theta
- 目标是生成按期望方向（从 angle1 到 angle2）排列的角数组 theta（长度 = points）。
- 逆时针（ccw）：
  - 如果 theta2 <= theta1，说明需要跨越 2π（例如从 350° 到 10°），因此把 theta2 增加 2π，使序列单调上升；
  - 用 theta = np.linspace(theta1, theta2, points)。
- 顺时针（cw）：
  - 如果 theta1 <= theta2，说明顺时针路径需要跨越 2π（把 theta1 加 2π）；
  - 先生成升序 np.linspace(theta1, theta2, points)，再用 [::-1] 反转为从 angle1 到 angle2 的顺时针角序列。
- 结果：theta 是按绘制顺序排列的一维弧度数组。

3) 应用 rotation（把 $(r cosθ, r sinθ)$ 旋转 rot）
- 计算旋转矩阵的 cos_rot = cos(rot)，sin_rot = sin(rot)。
- 先按极坐标得到未旋转坐标 $(r*cosθ, r*sinθ)$，再通过公式：
$$
  x = center_x + r*(cosθ * cos_{rot} - sinθ * sin_{rot})\\
  y = center_y + r*(sinθ * cos_{rot} + cosθ * sin_{rot})
$$
  这等价于把点 (r cosθ, r sinθ) 按角度 rot 旋转（使用和角公式 / 旋转矩阵）。

1) plot 控制与绘图
- 如果 plot=False：仅返回 x, y，不做绘图。
- 否则：
  - 若 ax is None，使用 plt.gca() 获取当前坐标轴（若不存在则会创建）。
  - 使用 ax.plot(x, y, **style) 绘制，并用 ax.axis("equal") 或 ax.set_aspect 保持 x,y 比例一致（保证圆看起来不是椭圆）。
  - 若给了 label，会显示图例。
  - 若 return_arc=True，则返回绘制的第一个 Line2D 对象 arc[0]。

### 数学/几何要点（快速）
- theta 的生成控制点在弧上的位置（角度均匀采样），当半径固定时角度均匀即弧长均匀。
- rotation 相当于在每个点上做额外的同一刚体旋转（绕圆心转动整个弧）。

常见边界与注意事项
- angle1 == angle2：当前逻辑若 angle2 <= angle1，会自动加 2π（ccw 情况），因此会绘制一整圈（从 angle1 回到 angle1 + 2π）。如果你希望 angle1==angle2 表示“空弧”，需要特别处理。
- 期望短弧或长弧：当前实现总是按从 angle1 到 angle2 的正向/反向，从而可能绘制跨越 >π 的长弧；如果你想始终取更短路径，需要额外逻辑判断并选择短的方向。
- use_degree=True 时用户传入弧度会被错误转换 —— 在 API 文档中应明确角度单位；已提供 use_degree 参数来切换。
- 若传入非常小的 points 或 points=1，会导致数组长度问题（通常 points >= 2）。
- ax 参数不要传布尔值（例如 ax=False 会导致 "'bool' object has no attribute plot"），如果想不绘图请用 plot=False。

### 改进建议（可选）
- 明确 docstring，列出参数类型、单位与返回值；添加 type hints。
- 提供参数 `wrap='shortest'|'forward'` 以支持“选择短弧”行为。
- 添加 `return_xy=True/False` 明确控制返回值，或统一总是返回 (x,y) 并用 `return_arc` 返回绘制对象，这样更一致。
- 把角度生成（处理跨 2π）抽成一个小函数并复用（arc_point 与 arc_degree 都用到）。
- 支持渐变绘色（内置或提供 hook）以便可视化方向（之前已实现了外部 demo）。
- 对 angle1==angle2 提供可选行为（空弧 / 全圈），不要隐式总加 2π。

### 使用示例
- 默认（度）绘制逆时针弧：
  arc(r=1, angle1=30, angle2=150)
- 用弧度，并顺时针：
  arc(r=1, angle1=np.pi/6, angle2=5*np.pi/6, use_degree=False, direction='cw')
- 只要坐标不绘图：
  x, y = arc(r=1, angle1=30, angle2=150, plot=False)

结论  
这个函数逻辑清晰：先把角度处理成弧度并生成按方向排列的角数组，然后把极坐标点旋转并位移到指定圆心，最后绘图或返回数据。常见问题集中在角度单位、跨 2π 的边界和对 angle1==angle2 的含义。若你希望我帮你做任一改进（例如：添加“取更短弧”选项、完善 docstring/类型注解、或把渐变直接内建到函数）。




## arc_dot
```python
def arc_dot(
    r=1,
    angle1=45,
    angle2=135,
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
    markerfacecolor="b",
    markeredgecolor="r",
    markeredgewidth=1,
    ax=None,
    use_degree=True,
    **kwargs,
):
    return arc(
        r,
        angle1,
        angle2,
        rotation,
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
        use_degree,
        plot=False,
        direction="ccw",
        return_arc=False,
        **kwargs,
    )
```
## 代码说明：
仅仅是arc()函数的调用，固定设置：
- plot=False
- direction="ccw"
- return_arc=False

## arc_point_inverse
```python
def arc_point_inverse(
    center=(0, 0),
    point1=(1, 0),
    point2=(-1, 0),
    color="#0f0",
    alpha=1,
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
    plot=True,
    direction="cw",  # 'ccw' or 'cw'
    return_arc=False,
    **kwargs,
):
    arc_point(
        center=center,
        point1=point1,
        point2=point2,
        color=color,
        alpha=alpha,
        points=points,
        linestyle=linestyle,
        linewidth=linewidth,
        label=label,
        marker=marker,
        markersize=markersize,
        markerfacecolor=markerfacecolor,
        markeredgecolor=markeredgecolor,
        markeredgewidth=markeredgewidth,
        ax=ax,
        plot=plot,
        direction=direction,
        return_arc=return_arc,
        **kwargs,
    )
```

## 代码说明：
仅仅是arc_point()函数的调用，固定设置：
- direction="cw"
  

## arc_degree_inverse
```python
def arc_inverse(
    r=1,
    angle1=45,
    angle2=135,
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
    markerfacecolor="b",
    markeredgecolor="r",
    markeredgewidth=1,
    ax=None,
    use_degree=True,
    plot=True,
    direction="cw",
    return_arc=False,
    **kwargs,
):
    arc(
        r,
        angle1,
        angle2,
        rotation,
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
        use_degree,
        plot,
        direction,
        return_arc,
        **kwargs,
    )

```
## 代码说明：
仅仅是arc()函数的调用，固定设置：
- direction="cw"



## arc_dot_inverse
```python
def arc_dot_inverse(
    r=1,
    angle1=45,
    angle2=135,
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
    markerfacecolor="b",
    markeredgecolor="r",
    markeredgewidth=1,
    ax=None,
    use_degree=True,
    **kwargs,
):
    return arc(
        r,
        angle1,
        angle2,
        rotation,
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
        use_degree,
        plot=False,
        direction="cw",
        return_arc=False,
        **kwargs,
    )
```
## 代码说明：
仅仅是arc()函数的调用，固定设置：
- plot=False
- direction="cw"
- return_arc=False
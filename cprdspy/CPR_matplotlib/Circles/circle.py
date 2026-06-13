import numpy as np
import matplotlib.pyplot as plt


def circle(
    radius=1,
    color="#0F0",
    alpha=1,
    center=(0, 0),
    points=100,
    linestyle="-",
    linewidth=1,
    label=None,
    marker=None,
    markersize=5,
    markerfacecolor="r",
    markeredgecolor="k",
    markeredgewidth=1,
    ax=None,
    **kwargs,
):
    """
    绘制一个圆。

    参数:
        radius (float): 圆的半径，默认为1。
        color (str): 圆的颜色，默认为绿色("#0F0")。
        alpha (float): 透明度，默认为1（不透明）。
        center (tuple): 圆心坐标，默认为(0, 0)。
        points (int): 用于绘制圆的点数，默认为100。
        linestyle (str): 线型，默认为实线("-")。
        linewidth (int): 线宽，默认为1。
        label (str): 图例标签，默认为None。
        marker (str): 标记样式，默认为None。
        markersize (int): 标记大小，默认为5。
        markerfacecolor (str): 标记填充颜色，默认为红色("r")。
        markeredgecolor (str): 标记边缘颜色，默认为黑色("k")。
        markeredgewidth (int): 标记边缘宽度，默认为1。
        ax (matplotlib.axes.Axes): 目标坐标轴，默认为None（使用当前坐标轴）。
        **kwargs: 其他传递给plt.plot的参数。

    返回:
        matplotlib.lines.Line2D: 绘制的圆对象。
    """
    angle = np.linspace(0, 2 * np.pi, points)
    x = center[0] + radius * np.cos(angle)
    y = center[1] + radius * np.sin(angle)

    if ax is None:
        ax = plt.gca()

    line = ax.plot(
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
    return line[0] if line else None


def draw_circle(
    radius=1,
    color="#0F0",
    alpha=1,
    center=(0, 0),
    points=100,
    linestyle="-",
    linewidth=1,
    label=None,
    marker=None,
    markersize=5,
    markerfacecolor="r",
    markeredgecolor="k",
    markeredgewidth=1,
):
    angle = np.linspace(0, 2 * np.pi, points)
    x = center[0] + radius * np.cos(angle)
    y = center[1] + radius * np.sin(angle)
    plt.axis("equal")
    plt.plot(
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
    )


# def circle(center, radius, color='b'):
#     angle = np.linspace(0, 2*np.pi, 1000)
#     x = center[0] + radius * np.cos(angle)
#     y = center[1] + radius * np.sin(angle)
#     plt.axis('equal')
#     plt.plot(x, y, color)


def circle_p(center, point, color="b"):
    # 计算圆的半径
    radius = np.sqrt((point[0] - center[0]) ** 2 + (point[1] - center[1]) ** 2)
    # 生成圆上的点
    theta = np.linspace(0, 2 * np.pi, 100)
    x = center[0] + radius * np.cos(theta)
    y = center[1] + radius * np.sin(theta)
    # 绘制图形
    plt.axis("equal")
    plt.plot(x, y, color)


# 椭圆


def ellipse(a=2, b=1, rotation=0, use_degree=True, color="#0f0", alpha=1, center=(0, 0), points=1000):
    """绘制椭圆。

    参数:
        a (float): 半长轴。
        b (float): 半短轴。
        rotation (float): 旋转角度（度或弧度取决于 use_degree），默认为 0。
        use_degree (bool): rotation 是否使用角度制，默认 True（度）。
        color, alpha, center, points: 样式参数。
    """
    theta = np.linspace(0, 2 * np.pi, points)
    angle_rad = np.deg2rad(rotation) if use_degree else rotation
    x = (
        a * np.cos(theta) * np.cos(angle_rad)
        - b * np.sin(theta) * np.sin(angle_rad)
        + center[0]
    )
    y = (
        a * np.cos(theta) * np.sin(angle_rad)
        + b * np.sin(theta) * np.cos(angle_rad)
        + center[1]
    )
    plt.plot(x, y, color, alpha)


# 统一的同心圆函数
def concentric_circles(
    center=(0, 0),
    n=3,
    radius=1,
    param=0.5,
    mode="arithmetic",
    direction="both",
    color="#0F0",
    marker="o",
    alpha=1,
    points=200,
    linestyle="-",
    linewidth=1,
    ax=None,
    show_center=True,
    **kwargs,
):
    """
    绘制同心圆的统一函数（兼容等差与等比序列）。

    参数:
        center (tuple): 圆心坐标。
        n (int): 每一侧的圈数（当 direction=='both' 时每侧各 n 个）。
        radius (float): 基准半径（绘制在中间）。
        param (float): 当 mode=='arithmetic' 时作为公差 d；当 mode=='geometric' 时作为公比 q (>0, q!=0, q!=1 推荐)。
        mode (str): 'arithmetic' 或 'geometric'，选择等差或等比。
        direction (str): 'both'|'out'|'in'，控制向外/向内/双向绘制。
        color, marker, alpha, points, linestyle, linewidth: 绘图样式参数。
        ax (Axes): 可选的 matplotlib 坐标轴对象。
        show_center (bool): 是否绘制圆心标记。
        **kwargs: 其它传入 `ax.plot` 的参数。

    说明:
        - 函数使用与 `circle()` 相同的参数风格（可接收 ax 与样式参数）。
        - 当 direction=='both' 时，会在基准半径两侧各生成 n 个半径值。
    """
    if ax is None:
        ax = plt.gca()

    if show_center:
        ax.plot(center[0], center[1], marker=marker, color=color)

    radii = []
    mode = mode.lower()
    direction = direction.lower()

    if mode.startswith("a"):
        # 等差: param 作为公差 d
        d = float(param)
        if direction == "both":
            for i in range(1, n + 1):
                radii.append(radius + i * d)
                radii.append(radius - i * d)
        elif direction == "out":
            for i in range(1, n + 1):
                radii.append(radius + i * d)
        elif direction == "in":
            for i in range(1, n + 1):
                radii.append(radius - i * d)
    elif mode.startswith("g"):
        # 等比: param 作为公比 q
        q = float(param)
        if q == 0:
            raise ValueError("ratio (param) must be non-zero for geometric mode")
        if direction == "both":
            for i in range(1, n + 1):
                radii.append(radius * (q**i))
                radii.append(radius / (q**i))
        elif direction == "out":
            for i in range(1, n + 1):
                radii.append(radius * (q**i))
        elif direction == "in":
            for i in range(1, n + 1):
                radii.append(radius / (q**i))

    # 确保半径为正且不重复，并保持基准半径也被绘制
    radii = [r for r in radii if r > 0]
    # 加入基准半径并去重、排序（近到远）
    radii.append(radius)
    radii = sorted(set(radii))

    for r in radii:
        angle = np.linspace(0, 2 * np.pi, points)
        x = center[0] + r * np.cos(angle)
        y = center[1] + r * np.sin(angle)
        ax.plot(
            x,
            y,
            color=color,
            alpha=alpha,
            linestyle=linestyle,
            linewidth=linewidth,
            **kwargs,
        )

    ax.axis("equal")


def concentric_ellipse(
    center=(0, 0),
    n=3,
    a=2,
    b=1,
    param=0.5,
    mode="arithmetic",
    direction="both",
    rotation=0,
    color="#0F0",
    marker="o",
    alpha=1,
    points=200,
    linestyle="-",
    linewidth=1,
    ax=None,
    show_center=True,
    **kwargs,
):
    """
    绘制同心椭圆（兼容等差与等比序列）。

    参数:
        center (tuple): 椭圆中心。
        n (int): 每侧的椭圆数量（direction=='both' 时每侧各 n 个）。
        a (float): 基准半长轴。
        b (float): 基准半短轴。
        param (float): 等差时为公差 d；等比时为公比 q。
        mode (str): 'arithmetic' 或 'geometric'。
        direction (str): 'both'|'out'|'in'，控制向外/向内/双向绘制。
        rotation (float): 椭圆旋转角度（度）。
        其它样式参数同 `concentric_circles`。
    """
    if ax is None:
        ax = plt.gca()

    if show_center:
        ax.plot(center[0], center[1], marker=marker, color=color)

    ellipses = []  # 存放 (a_i, b_i)
    mode = mode.lower()
    direction = direction.lower()

    if mode.startswith("a"):
        d = float(param)
        if direction == "both":
            for i in range(1, n + 1):
                ellipses.append((a + i * d, b + i * d))
                ellipses.append((a - i * d, b - i * d))
        elif direction == "out":
            for i in range(1, n + 1):
                ellipses.append((a + i * d, b + i * d))
        elif direction == "in":
            for i in range(1, n + 1):
                ellipses.append((a - i * d, b - i * d))
    elif mode.startswith("g"):
        q = float(param)
        if q == 0:
            raise ValueError("ratio (param) must be non-zero for geometric mode")
        if direction == "both":
            for i in range(1, n + 1):
                ellipses.append((a * (q**i), b * (q**i)))
                ellipses.append((a / (q**i), b / (q**i)))
        elif direction == "out":
            for i in range(1, n + 1):
                ellipses.append((a * (q**i), b * (q**i)))
        elif direction == "in":
            for i in range(1, n + 1):
                ellipses.append((a / (q**i), b / (q**i)))

    # 加入基准椭圆并过滤无效项
    ellipses.append((a, b))
    # 去重（按数值近似）并按面积排序（小到大）
    uniq = {}
    for aa, bb in ellipses:
        if aa > 0 and bb > 0:
            key = (round(float(aa), 12), round(float(bb), 12))
            uniq[key] = (float(aa), float(bb))

    sorted_ellipses = sorted(uniq.values(), key=lambda t: t[0] * t[1])

    theta = np.linspace(0, 2 * np.pi, points)
    angle_rad = np.deg2rad(rotation)

    for aa, bb in sorted_ellipses:
        x = (
            aa * np.cos(theta) * np.cos(angle_rad)
            - bb * np.sin(theta) * np.sin(angle_rad)
            + center[0]
        )
        y = (
            aa * np.cos(theta) * np.sin(angle_rad)
            + bb * np.sin(theta) * np.cos(angle_rad)
            + center[1]
        )
        ax.plot(
            x,
            y,
            color=color,
            alpha=alpha,
            linestyle=linestyle,
            linewidth=linewidth,
            **kwargs,
        )

    ax.axis("equal")

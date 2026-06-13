import matplotlib.pyplot as plt
import numpy as np


# 圆弧
## arc_point
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
    if direction == "ccw":
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


## arc_point_inverse
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


## arc_degree
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
    if direction == "ccw":
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


## arc_degree_inverse
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


## arc_dot


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


## arc_dot_inverse


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


# 中心旋转弧
def arc_rotate(
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
    markersize=6,
    markerfacecolor=None,
    markeredgecolor="k",
    markeredgewidth=1,
    ax=None,
    use_degree=True,
    plot=True,
    direction="ccw",
    return_arc=False,
    **kwargs,
):
    """
    绘制一段弧，其 angle2 端固定在 center，并可绕原点旋转。

    Parameters
    ----------
    r : float
        弧的半径。
    angle1, angle2 : float
        弧的起始角/终止角。use_degree=True 时为度数，否则为弧度。
    rotation : float
        绕原点旋转的角度。use_degree=True 时为度数，否则为弧度。
    center : tuple
        弧的 angle2 端点放置位置（即旋转后该点保持不动的前提是 center=(0,0)）。
    use_degree : bool
        True 表示 angle1/angle2/rotation 使用角度制，False 使用弧度制。
    plot : bool
        False 时返回旋转后的 (x, y) 数据而不绘图。
    return_arc : bool
        True 时返回 matplotlib Line2D 对象而非 None。
    """
    # ---------- 1. 角度制 → 弧度 ----------
    if use_degree:
        a1 = np.deg2rad(angle1)
        a2 = np.deg2rad(angle2)
        rot = np.deg2rad(rotation)
    else:
        a1 = angle1
        a2 = angle2
        rot = rotation

    # ---------- 2. 将弧的 a2 端点平移到 center ----------
    # circle 中心 = center - r*(cos(a2), sin(a2))，使圆弧在 a2 处恰好落在 center
    arc_center = (center[0] - r * np.cos(a2), center[1] - r * np.sin(a2))

    x, y = arc(
        r=r,
        angle1=a1,
        angle2=a2,
        rotation=0,
        center=arc_center,
        points=points,
        use_degree=False,  # 已转为弧度
        plot=False,
        direction=direction,
        **kwargs,
    )

    # ---------- 3. 绕原点旋转 ----------
    x_rot = x * np.cos(rot) - y * np.sin(rot)
    y_rot = x * np.sin(rot) + y * np.cos(rot)

    if not plot:
        return x_rot, y_rot

    # ---------- 4. 绘图 ----------
    if ax is None:
        ax = plt.gca()
    arc_line = ax.plot(
        x_rot,
        y_rot,
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
        return arc_line[0] if arc_line else None


# 椭圆弧
def oval_arc(
    a=2,
    b=1,
    angle1=45,
    angle2=135,
    angle=0,
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
    use_degree=True,
    plot=True,
    **kwargs,
):
    """
    绘制一段椭圆弧或返回计算得到的 x 和 y 值。

    参数:
        a (float): 椭圆的长轴长度。
        b (float): 椭圆的短轴长度。
        angle1 (float): 弧的起始角度（度或弧度，取决于 use_degree）。
        angle2 (float): 弧的结束角度（度或弧度，取决于 use_degree）。
        angle (float): 椭圆的旋转角度（度或弧度，取决于 use_degree），默认为0。
        color (str): 弧的颜色，默认为绿色("#0f0")。
        alpha (float): 透明度，默认为1（不透明）。
        center (tuple): 椭圆的中心坐标，默认为(0, 0)。
        points (int): 用于绘制弧的点数，默认为1000。
        linestyle (str): 线型，默认为实线("-")。
        linewidth (int): 线宽，默认为1。
        label (str): 图例标签，默认为None。
        marker (str): 标记样式，默认为None。
        markersize (int): 标记大小，默认为5。
        markerfacecolor (str): 标记填充颜色，默认为红色("r")。
        markeredgecolor (str): 标记边缘颜色，默认为黑色("k")。
        markeredgewidth (int): 标记边缘宽度，默认为1。
        ax (matplotlib.axes.Axes): 目标坐标轴，默认为None（使用当前坐标轴）。
        use_degree (bool): 是否使用角度制（True为角度，False为弧度），默认为True。
        plot (bool): 是否绘制图像，默认为True。如果为False，则返回计算得到的 x 和 y 值。
        **kwargs: 其他传递给 plt.plot 的参数。

    返回:
        如果 plot=True:
            matplotlib.lines.Line2D: 绘制的椭圆弧对象。
        如果 plot=False:
            tuple: (x, y) 计算得到的坐标值。
    """
    # 角度转换
    if use_degree:
        angle1_rad = np.deg2rad(angle1)
        angle2_rad = np.deg2rad(angle2)
        angle_rad = np.deg2rad(angle)
    else:
        angle1_rad = angle1
        angle2_rad = angle2
        angle_rad = angle

    # 生成弧上的点
    theta = np.linspace(angle1_rad, angle2_rad, points)
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

    # 如果不绘制图像，直接返回 x 和 y
    if not plot:
        return x, y

    # 获取目标坐标轴
    if ax is None:
        ax = plt.gca()

    # 绘制椭圆弧
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

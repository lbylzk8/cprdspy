import matplotlib.pyplot as plt
import numpy as np
from cprdspy.CPR_matplotlib.Arcs.arc import *


# 圆花瓣
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


"""
Flower Algorithms
"""


# 单层花
def flower(
    R=1,
    r=1,
    n=4,
    N=12,
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
    for i in range(N):
        flower_petal(
            R,
            r,
            n,
            (
                rotation + i * 360 / N + 90
                if use_degree
                else rotation + i * 2 * np.pi / N + np.pi / 2
            ),
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


# 多层花


def flowers(
    R=1,
    r=1,
    n=4,
    ratio=np.sqrt(2),
    M=3,
    N=12,
    color="b",
    alpha=1,
    theta=0,
    center=(0, 0),
    points=1000,
    linestyle="-",
    linewidth=1,
    label=None,
    marker=None,
    markersize=5,
    markerfacecolor="r",
    markeredgecolor="b",
    markeredgewidth=1,
    ax=None,
    plot_center=False,
    center_color="r",
    center_size=5,
    use_degree=False,
    plot=True,
    direction="ccw",
    return_flower=False,
    **kwargs,
):
    # 统一转为弧度，后续统一用弧度传给 flower_petal
    theta_rad = np.deg2rad(theta) if use_degree else theta

    for j in range(1, M + 1):
        for i in range(0, N):
            flower_petal(
                R * (ratio ** (j - 1)),
                r * (ratio ** (j - 1)),
                n,
                2 * i * np.pi / N + (j - 1) * np.pi / N + theta_rad + np.pi / 2,
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
                False,  # rotation 已是弧度，通知 flower_petal 不要再转
                plot,
                direction,
                return_flower,
                **kwargs,
            )


# 椭圆花瓣


def rotate_point(point, theta):
    """
    将点绕原点旋转 theta 角度（弧度）。

    参数:
        point (tuple): 点的坐标 (x, y)。
        theta (float): 旋转角度（弧度）。

    返回:
        tuple: 旋转后的新坐标 (x_new, y_new)。
    """
    x, y = point
    x_new = x * np.cos(theta) - y * np.sin(theta)
    y_new = x * np.sin(theta) + y * np.cos(theta)
    return (x_new, y_new)


def oval_petal_a(a, b, d, rotation=0, use_degree=True, color="b", alpha=1, center=(0, 0), points=1000):
    """椭圆花瓣（简化版）。

    rotation (float): 旋转角度（度或弧度取决于 use_degree）。
    use_degree (bool): rotation 是否使用角度制，默认 True（度）。
    """
    rotation_rad = np.deg2rad(rotation) if use_degree else rotation
    x0 = b / (2 * a) * np.sqrt(4 * a**2 - d**2) / (d / 2)
    beta = np.arctan(x0)
    beta_b1 = np.pi / 2 - beta
    beta_e1 = np.pi / 2 + beta
    beta_b2 = 3 * np.pi / 2 - beta
    beta_e2 = 3 * np.pi / 2 + beta
    center1 = (center[0], center[1] - d / 2)
    center2 = (center[0], center[1] + d / 2)
    center1_rot = rotate_point((a, center[1] - d / 2), rotation_rad)
    center2_rot = rotate_point((a, center[1] + d / 2), rotation_rad)
    oval_arc(
        a, b, beta_b1, beta_e1,
        angle=rotation,  # oval_arc 内部自己处理 use_degree
        color=color, alpha=alpha, center=center1_rot, points=points,
        use_degree=use_degree,
    )
    oval_arc(
        a, b, beta_b2, beta_e2,
        angle=rotation,
        color=color, alpha=alpha, center=center2_rot, points=points,
        use_degree=use_degree,
    )


def oval_petal(
    a=2,
    b=1,
    d=0.5,
    rotation=0,
    rot_by_center=True,
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
    绘制一个椭圆花瓣形状。

    参数:
        a (float): 椭圆的长轴长度。
        b (float): 椭圆的短轴长度。
        d (float): 花瓣的垂直距离。
        rotation (float): 旋转角度（度或弧度，取决于 use_degree），默认为0。
        color (str): 颜色，默认为绿色("#0f0")。
        alpha (float): 透明度，默认为1（不透明）。
        center (tuple): 中心坐标，默认为(0, 0)。
        points (int): 用于绘制弧的点数，默认为1000。
        use_degree (bool): 是否使用角度制（True为角度，False为弧度），默认为True。
        linestyle (str): 线型，默认为实线("-")。
        linewidth (int): 线宽，默认为1。
        label (str): 图例标签，默认为None。
        marker (str): 标记样式，默认为None。
        markersize (int): 标记大小，默认为5。
        markerfacecolor (str): 标记填充颜色，默认为红色("r")。
        markeredgecolor (str): 标记边缘颜色，默认为黑色("k")。
        markeredgewidth (int): 标记边缘宽度，默认为1。
        ax (matplotlib.axes.Axes): 目标坐标轴，默认为None（使用当前坐标轴）。
        plot (bool): 是否绘制图像，默认为True。如果为False，则返回计算得到的坐标。
        **kwargs: 其他传递给 plt.plot 的参数。

    返回:
        如果 plot=True:
            None
        如果 plot=False:
            tuple: (x1, y1, x2, y2) 计算得到的两个弧的坐标值。
    """
    # 计算 beta 角度
    x0 = b / (2 * a) * np.sqrt(4 * a**2 - d**2) / (d / 2)
    beta = np.arctan(x0)
    beta_b1 = np.pi / 2 - beta
    beta_e1 = np.pi / 2 + beta
    beta_b2 = 3 * np.pi / 2 - beta
    beta_e2 = 3 * np.pi / 2 + beta

    # 角度转换
    if use_degree:
        beta_b1 = np.rad2deg(beta_b1)
        beta_e1 = np.rad2deg(beta_e1)
        beta_b2 = np.rad2deg(beta_b2)
        beta_e2 = np.rad2deg(beta_e2)
        rotation_rad = np.deg2rad(rotation)
    else:
        rotation_rad = rotation

    # 计算中心点
    center1 = (center[0], center[1] - d / 2)
    center2 = (center[0], center[1] + d / 2)
    if rot_by_center:
        center1_rot = rotate_point(center1, rotation_rad)
        center2_rot = rotate_point(center2, rotation_rad)
    else:
        center1_rot = rotate_point((a, center[1] - d / 2), rotation_rad)
        center2_rot = rotate_point((a, center[1] + d / 2), rotation_rad)
    # 如果不绘制图像，返回坐标值
    if not plot:
        # 计算第一个弧的坐标
        theta1 = np.linspace(beta_b1, beta_e1, points)
        x1 = (
            a * np.cos(theta1) * np.cos(rotation_rad)
            - b * np.sin(theta1) * np.sin(rotation_rad)
            + center1_rot[0]
        )
        y1 = (
            a * np.cos(theta1) * np.sin(rotation_rad)
            + b * np.sin(theta1) * np.cos(rotation_rad)
            + center1_rot[1]
        )

        # 计算第二个弧的坐标
        theta2 = np.linspace(beta_b2, beta_e2, points)
        x2 = (
            a * np.cos(theta2) * np.cos(rotation_rad)
            - b * np.sin(theta2) * np.sin(rotation_rad)
            + center2_rot[0]
        )
        y2 = (
            a * np.cos(theta2) * np.sin(rotation_rad)
            + b * np.sin(theta2) * np.cos(rotation_rad)
            + center2_rot[1]
        )

        return (x1, y1, x2, y2)

    # 绘制第一个弧
    oval_arc(
        a,
        b,
        beta_b1,
        beta_e1,
        angle=rotation,
        color=color,
        alpha=alpha,
        center=center1_rot,
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
        use_degree=use_degree,
        **kwargs,
    )

    # 绘制第二个弧
    oval_arc(
        a,
        b,
        beta_b2,
        beta_e2,
        angle=rotation,
        color=color,
        alpha=alpha,
        center=center2_rot,
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
        use_degree=use_degree,
        **kwargs,
    )


"""
Oval Flower Algorithm
"""


def oval_flower(
    a=2, b=1, d=0.1, n=12, rotation=0, use_degree=True,
    color="#0f0", alpha=1, center=(0, 0), points=1000,
):
    """椭圆花瓣花朵。

    rotation (float): 旋转角度（度或弧度取决于 use_degree）。
    use_degree (bool): rotation 是否使用角度制，默认 True（度）。
    """
    rotation_rad = np.deg2rad(rotation) if use_degree else rotation
    for i in range(n):
        oval_petal(
            a, b, d,
            rotation_rad + i * 2 * np.pi / n,
            1,  # rot_by_center
            color, alpha, center, points,
            use_degree=False,  # 内部已经转为弧度
        )


def oval_flower_a(
    a=2, b=1, d=0.1, n=12, rotation=0, use_degree=True,
    color="#0f0", alpha=1, center=(0, 0), points=1000,
):
    """椭圆花瓣花朵（旋转模式 a）。

    rotation (float): 旋转角度（度或弧度取决于 use_degree）。
    use_degree (bool): rotation 是否使用角度制，默认 True（度）。
    """
    rotation_rad = np.deg2rad(rotation) if use_degree else rotation
    for i in range(n):
        oval_petal(
            a, b, d,
            rotation_rad + i * 2 * np.pi / n,
            False,  # rot_by_center
            color, alpha, center, points,
            use_degree=False,  # 内部已经转为弧度
        )

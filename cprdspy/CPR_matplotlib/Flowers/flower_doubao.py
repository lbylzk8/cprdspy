import matplotlib.pyplot as plt
import numpy as np
from cprdspy.CPR_matplotlib.Arcs.arc import *

# from cprdspy.CPR_matplotlib.Arcs.oval_arc import *


# ===================== 圆花瓣系列（已修正） =====================
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
    use_degree=True,
    plot=True,
    direction="ccw",
    return_petal=False,
    # 花瓣顶点点配置
    petal_peak_dot=True,
    peak_size=6,
    peak_facecolor="#ff69b4",
    peak_edgecolor="#fff",
    peak_edgewidth=0.5,
    **kwargs,
):
    angle = 2 * np.pi / n
    a = R * np.sin(np.pi / n)
    if r > 0:
        beta = np.arccos(min(1, max(-1, (a) / r)))
    else:
        beta = 0
    theta_arc = np.pi / 2 - np.pi / n + np.arccos(min(1, max(-1, (a) / r)))
    rotation_rad = np.deg2rad(rotation) if use_degree else rotation

    center1_theta = rotation_rad + angle / 2
    center2_theta = rotation_rad - angle / 2
    center1 = (
        np.cos(center1_theta) * R + center[0],
        np.sin(center1_theta) * R + center[1],
    )
    center2 = (
        np.cos(center2_theta) * R + center[0],
        np.sin(center2_theta) * R + center[1],
    )

    # 花瓣顶点坐标
    petal_peak = (
        center[0] + R * np.cos(rotation_rad),
        center[1] + R * np.sin(rotation_rad),
    )

    if abs(r - a) < 1e-12:
        theta1_base_rad = np.pi + angle / 2
        theta2_base_rad = np.pi + angle / 2 + theta_arc
        theta3_base_rad = np.pi / 2
        theta4_base_rad = np.pi / 2 + theta_arc
    elif r > a:
        theta1_base_rad = np.pi + angle / 2
        theta2_base_rad = np.pi + angle / 2 + theta_arc
        theta3_base_rad = np.pi / 2 - beta
        theta4_base_rad = np.pi / 2 - beta + theta_arc
    else:
        print("r=", r, ",a=", a)
        print(f"r<a,不能形成花瓣。最小需要 r > {a:.3f}")
        return None

    if use_degree:
        theta1 = np.rad2deg(theta1_base_rad)
        theta2 = np.rad2deg(theta2_base_rad)
        theta3 = np.rad2deg(theta3_base_rad)
        theta4 = np.rad2deg(theta4_base_rad)
        rotation_for_arc = rotation
    else:
        theta1 = theta1_base_rad
        theta2 = theta2_base_rad
        theta3 = theta3_base_rad
        theta4 = theta4_base_rad
        rotation_for_arc = rotation_rad

    if plot:
        if ax is None:
            ax = plt.gca()

    arc_d1 = None
    arc_d2 = None
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

    if plot_center and plot:
        plt.scatter(
            center1[0], center1[1], color=center_color, s=center_size, alpha=alpha
        )
        plt.scatter(
            center2[0], center2[1], color=center_color, s=center_size, alpha=alpha
        )

    # 绘制花瓣顶点点
    if petal_peak_dot and plot:
        ax.scatter(
            petal_peak[0],
            petal_peak[1],
            s=peak_size,
            c=peak_facecolor,
            edgecolor=peak_edgecolor,
            linewidth=peak_edgewidth,
            alpha=alpha,
            zorder=10,
        )

    if not plot and arc_d1 is not None and arc_d2 is not None:
        return (center1[0], center1[1]), (center2[0], center2[1]), arc_d1, arc_d2


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
    # 中心圆配置（修正参数名：radius）
    draw_center_circle=True,
    c_circle_radius=0.1,  # 修正：radio → radius
    c_circle_facecolor="#1e90ff",
    c_circle_edgecolor="#fff",
    c_circle_edgewidth=0.5,
    # 花瓣点参数
    petal_peak_dot=True,
    peak_size=6,
    peak_facecolor="#ff69b4",
    peak_edgecolor="#fff",
    peak_edgewidth=0.5,
    **kwargs,
):
    if plot:
        if ax is None:
            ax = plt.gca()
        # 绘制中心实心圆
        if draw_center_circle:
            circle = plt.Circle(
                center,
                c_circle_radius,
                facecolor=c_circle_facecolor,
                edgecolor=c_circle_edgecolor,
                linewidth=c_circle_edgewidth,
                alpha=alpha,
                zorder=5,
            )
            ax.add_patch(circle)
            ax.set_aspect("equal")

    for i in range(N):
        flower_petal(
            R,
            r,
            n,
            (
                rotation + i * 360 / N + 90
                if use_degree
                else i * 2 * np.pi / N + np.pi / 2
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
            petal_peak_dot=petal_peak_dot,
            peak_size=peak_size,
            peak_facecolor=peak_facecolor,
            peak_edgecolor=peak_edgecolor,
            peak_edgewidth=peak_edgewidth,
            **kwargs,
        )


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
    # 中心圆配置（修正参数名）
    draw_center_circle=True,
    c_circle_radius=0.1,  # 修正：radio → radius
    c_circle_facecolor="#1e90ff",
    c_circle_edgecolor="#fff",
    c_circle_edgewidth=0.5,
    # 花瓣点参数
    petal_peak_dot=True,
    peak_size=6,
    peak_facecolor="#ff69b4",
    peak_edgecolor="#fff",
    peak_edgewidth=0.5,
    **kwargs,
):
    if plot:
        if ax is None:
            ax = plt.gca()
        # 绘制中心实心圆
        if draw_center_circle:
            circle = plt.Circle(
                center,
                c_circle_radius,
                facecolor=c_circle_facecolor,
                edgecolor=c_circle_edgecolor,
                linewidth=c_circle_edgewidth,
                alpha=alpha,
                zorder=5,
            )
            ax.add_patch(circle)
            ax.set_aspect("equal")

    for j in range(1, M + 1):
        for i in range(0, N):
            flower_petal(
                R * (ratio ** (j - 1)),
                r * (ratio ** (j - 1)),
                n,
                2 * i * np.pi / N + (j - 1) * np.pi / N + theta + np.pi / 2,
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
                return_flower,
                petal_peak_dot=petal_peak_dot,
                peak_size=peak_size,
                peak_facecolor=peak_facecolor,
                peak_edgecolor=peak_edgecolor,
                peak_edgewidth=peak_edgewidth,
                **kwargs,
            )


# ===================== 椭圆花瓣系列（修正参数名+兼容） =====================
def rotate_point(point, theta):
    """将点绕原点旋转 theta 角度（弧度）"""
    x, y = point
    x_new = x * np.cos(theta) - y * np.sin(theta)
    y_new = x * np.sin(theta) + y * np.cos(theta)
    return (x_new, y_new)


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
    # 花瓣顶点点配置
    petal_peak_dot=True,
    peak_size=6,
    peak_facecolor="#ff69b4",
    peak_edgecolor="#fff",
    peak_edgewidth=0.5,
    **kwargs,
):
    # 计算核心参数
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

    # 椭圆花瓣顶点坐标
    petal_peak = (
        center[0] + a * np.cos(rotation_rad),
        center[1] + a * np.sin(rotation_rad),
    )

    # 椭圆弧中心点
    center1 = (center[0], center[1] - d / 2)
    center2 = (center[0], center[1] + d / 2)
    if rot_by_center:
        center1_rot = rotate_point(center1, rotation_rad)
        center2_rot = rotate_point(center2, rotation_rad)
    else:
        center1_rot = rotate_point((a, center[1] - d / 2), rotation_rad)
        center2_rot = rotate_point((a, center[1] + d / 2), rotation_rad)

    # 不绘制时返回坐标
    if not plot:
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

    # 初始化坐标轴
    if ax is None:
        ax = plt.gca()

    # 绘制椭圆弧
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

    # 绘制椭圆花瓣顶点点
    if petal_peak_dot:
        ax.scatter(
            petal_peak[0],
            petal_peak[1],
            s=peak_size,
            c=peak_facecolor,
            edgecolor=peak_edgecolor,
            linewidth=peak_edgewidth,
            alpha=alpha,
            zorder=10,
        )


def oval_flower(
    a=2,
    b=1,
    d=0.1,
    n=12,
    rotation=0,
    color="#0f0",
    alpha=1,
    center=(0, 0),
    points=1000,
    # 中心圆配置（修正参数名：radius）
    draw_center_circle=True,
    c_circle_radius=0.1,  # 修正：radio → radius
    c_circle_facecolor="#1e90ff",
    c_circle_edgecolor="#fff",
    c_circle_edgewidth=0.5,
    # 花瓣点参数
    petal_peak_dot=True,
    peak_size=6,
    peak_facecolor="#ff69b4",
    peak_edgecolor="#fff",
    peak_edgewidth=0.5,
    **kwargs,
):

    # 初始化坐标轴
    ax = plt.gca()
    ax.set_aspect("equal")

    # 绘制中心实心圆
    if draw_center_circle:
        circle = plt.Circle(
            center,
            c_circle_radius,
            facecolor=c_circle_facecolor,
            edgecolor=c_circle_edgecolor,
            linewidth=c_circle_edgewidth,
            alpha=alpha,
            zorder=5,
        )
        ax.add_patch(circle)

    # 循环绘制椭圆花瓣
    for i in range(n):
        oval_petal(
            a,
            b,
            d,
            rotation + i * 2 * np.pi / n,
            rot_by_center=True,
            color=color,
            alpha=alpha,
            center=center,
            points=points,
            use_degree=False,
            petal_peak_dot=petal_peak_dot,
            peak_size=peak_size,
            peak_facecolor=peak_facecolor,
            peak_edgecolor=peak_edgecolor,
            peak_edgewidth=peak_edgewidth,
            **kwargs,
        )


def oval_flower_a(
    a=2,
    b=1,
    d=0.1,
    n=12,
    rotation=0,
    color="#0f0",
    alpha=1,
    center=(0, 0),
    points=1000,
    # 中心圆配置（修正参数名）
    draw_center_circle=True,
    c_circle_radius=0.1,  # 修正：radio → radius
    c_circle_facecolor="#1e90ff",
    c_circle_edgecolor="#fff",
    c_circle_edgewidth=0.5,
    # 花瓣点参数
    petal_peak_dot=True,
    peak_size=6,
    peak_facecolor="#ff69b4",
    peak_edgecolor="#fff",
    peak_edgewidth=0.5,
    **kwargs,
):

    ax = plt.gca()
    ax.set_aspect("equal")

    # 绘制中心实心圆
    if draw_center_circle:
        circle = plt.Circle(
            center,
            c_circle_radius,
            facecolor=c_circle_facecolor,
            edgecolor=c_circle_edgecolor,
            linewidth=c_circle_edgewidth,
            alpha=alpha,
            zorder=5,
        )
        ax.add_patch(circle)

    # 循环绘制椭圆花瓣
    for i in range(n):
        oval_petal(
            a,
            b,
            d,
            rotation + i * 2 * np.pi / n,
            rot_by_center=False,
            color=color,
            alpha=alpha,
            center=center,
            points=points,
            use_degree=False,
            petal_peak_dot=petal_peak_dot,
            peak_size=peak_size,
            peak_facecolor=peak_facecolor,
            peak_edgecolor=peak_edgecolor,
            peak_edgewidth=peak_edgewidth,
            **kwargs,
        )


def oval_petal_a(a, b, d, rotation=0, color="b", alpha=1, center=(0, 0), points=1000):
    x0 = b / (2 * a) * np.sqrt(4 * a**2 - d**2) / (d / 2)
    beta = np.arctan(x0)
    beta_b1 = np.pi / 2 - beta
    beta_e1 = np.pi / 2 + beta
    beta_b2 = 3 * np.pi / 2 - beta
    beta_e2 = 3 * np.pi / 2 + beta
    center1 = (center[0], center[1] - d / 2)
    center2 = (center[0], center[1] + d / 2)
    center1_rot = rotate_point((a, center[1] - d / 2), rotation)
    center2_rot = rotate_point((a, center[1] + d / 2), rotation)

    # 绘制椭圆弧
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
        use_degree=False,
    )
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
        use_degree=False,
    )

    # 绘制花瓣顶点点
    petal_peak = (center[0] + a * np.cos(rotation), center[1] + a * np.sin(rotation))
    plt.scatter(
        petal_peak[0],
        petal_peak[1],
        s=6,
        c="#ff69b4",
        edgecolor="#fff",
        linewidth=0.5,
        alpha=alpha,
        zorder=10,
    )

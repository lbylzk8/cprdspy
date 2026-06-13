"""
Flower Algorithms - Plotly Version
"""

import numpy as np
import plotly.graph_objects as go
from ..Arcs.arc import arc, oval_arc


def rotate_point(point, theta):
    """
    将点绕原点旋转 theta 角度（弧度）。
    """
    x, y = point
    x_new = x * np.cos(theta) - y * np.sin(theta)
    y_new = x * np.sin(theta) + y * np.cos(theta)
    return (x_new, y_new)


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
    line_width=1,
    label=None,
    use_degree=True,
    plot=True,
    direction="ccw",
    return_petal=False,
    **kwargs,
):
    """
    绘制一片花瓣。
    """
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
        print(f"r<a，不能形成花瓣。最小需要 r > {a:.3f}")
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

    arc_d1 = None
    arc_d2 = None

    if abs(r - a) < 1e-12 or r > a:
        arc_d1 = arc(
            r=r,
            angle1=theta1,
            angle2=theta2,
            rotation=rotation_for_arc,
            color=color,
            alpha=alpha,
            center=center1,
            points=points,
            line_width=line_width,
            label=label,
            use_degree=use_degree,
            plot=plot,
            direction=direction,
            return_arc=return_petal,
            **kwargs,
        )
        arc_d2 = arc(
            r=r,
            angle1=theta3,
            angle2=theta4,
            rotation=rotation_for_arc,
            color=color,
            alpha=alpha,
            center=center2,
            points=points,
            line_width=line_width,
            label=label,
            use_degree=use_degree,
            plot=plot,
            direction=direction,
            return_arc=return_petal,
            **kwargs,
        )

    if not plot and arc_d1 is not None and arc_d2 is not None:
        return (center1[0], center1[1]), (center2[0], center2[1]), arc_d1, arc_d2

    return arc_d1, arc_d2


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
    line_width=1,
    label=None,
    use_degree=False,
    plot=True,
    direction="ccw",
    return_petal=False,
    **kwargs,
):
    """
    绘制单层花。
    """
    traces = []
    for i in range(N):
        petal_rot = (
            rotation + i * 360 / N + 90
            if use_degree
            else i * 2 * np.pi / N + np.pi / 2
        )
        arc_d1, arc_d2 = flower_petal(
            R,
            r,
            n,
            petal_rot,
            color,
            alpha,
            center,
            points,
            line_width,
            label,
            use_degree=use_degree,
            plot=plot,
            direction=direction,
            return_petal=return_petal,
            **kwargs,
        )
        if plot and arc_d1:
            traces.append(arc_d1)
        if plot and arc_d2:
            traces.append(arc_d2)
    return traces


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
    line_width=1,
    label=None,
    use_degree=False,
    plot=True,
    direction="ccw",
    return_flower=False,
    **kwargs,
):
    """
    绘制多层花。
    """
    traces = []
    for j in range(1, M + 1):
        for i in range(0, N):
            arc_d1, arc_d2 = flower_petal(
                R * (ratio ** (j - 1)),
                r * (ratio ** (j - 1)),
                n,
                2 * i * np.pi / N + (j - 1) * np.pi / N + theta + np.pi / 2,
                color,
                alpha,
                center,
                points,
                line_width,
                label,
                use_degree,
                plot,
                direction,
                return_flower,
                **kwargs,
            )
            if plot and arc_d1:
                traces.append(arc_d1)
            if plot and arc_d2:
                traces.append(arc_d2)
    return traces


# 椭圆花瓣
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
    line_width=1,
    label=None,
    use_degree=True,
    plot=True,
    **kwargs,
):
    """
    绘制一个椭圆花瓣形状。
    """
    x0 = b / (2 * a) * np.sqrt(4 * a**2 - d**2) / (d / 2)
    beta = np.arctan(x0)
    beta_b1 = np.pi / 2 - beta
    beta_e1 = np.pi / 2 + beta
    beta_b2 = 3 * np.pi / 2 - beta
    beta_e2 = 3 * np.pi / 2 + beta

    if use_degree:
        beta_b1 = np.rad2deg(beta_b1)
        beta_e1 = np.rad2deg(beta_e1)
        beta_b2 = np.rad2deg(beta_b2)
        beta_e2 = np.rad2deg(beta_e2)
        rotation_rad = np.deg2rad(rotation)
    else:
        rotation_rad = rotation

    center1 = (center[0], center[1] - d / 2)
    center2 = (center[0], center[1] + d / 2)
    if rot_by_center:
        center1_rot = rotate_point(center1, rotation_rad)
        center2_rot = rotate_point(center2, rotation_rad)
    else:
        center1_rot = rotate_point((a, center[1] - d / 2), rotation_rad)
        center2_rot = rotate_point((a, center[1] + d / 2), rotation_rad)

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

    arc1 = oval_arc(
        a,
        b,
        beta_b1,
        beta_e1,
        angle=rotation,
        color=color,
        alpha=alpha,
        center=center1_rot,
        points=points,
        line_width=line_width,
        label=label,
        use_degree=use_degree,
        **kwargs,
    )

    arc2 = oval_arc(
        a,
        b,
        beta_b2,
        beta_e2,
        angle=rotation,
        color=color,
        alpha=alpha,
        center=center2_rot,
        points=points,
        line_width=line_width,
        label=label,
        use_degree=use_degree,
        **kwargs,
    )

    return arc1, arc2


# 椭圆花
def oval_flower(
    a=2, b=1, d=0.1, n=12, rotation=0, color="#0f0", alpha=1, center=(0, 0), points=1000
):
    """
    绘制椭圆花。
    """
    traces = []
    for i in range(n):
        arc1, arc2 = oval_petal(
            a,
            b,
            d,
            rotation + i * 2 * np.pi / n,
            True,
            color,
            alpha,
            center,
            points,
            use_degree=False,
        )
        if arc1:
            traces.append(arc1)
        if arc2:
            traces.append(arc2)
    return traces


def oval_flower_a(
    a=2, b=1, d=0.1, n=12, rotation=0, color="#0f0", alpha=1, center=(0, 0), points=1000
):
    """
    绘制椭圆花（方式 a）。
    """
    traces = []
    for i in range(n):
        arc1, arc2 = oval_petal(
            a,
            b,
            d,
            rotation + i * 2 * np.pi / n,
            False,
            color,
            alpha,
            center,
            points,
            use_degree=False,
        )
        if arc1:
            traces.append(arc1)
        if arc2:
            traces.append(arc2)
    return traces

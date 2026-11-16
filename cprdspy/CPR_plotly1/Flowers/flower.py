"""
Flower Algorithms - Plotly Version
"""

import numpy as np
import plotly.graph_objects as go
from ..Arcs.arc import arc, oval_arc


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
    name=None,
    showlegend=None,
    plot_center=False,
    center_color="#0f0",
    center_size=8,
    use_degree=True,
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
        beta = np.arccos(min(1, max(-1, (a) / r)))
    else:
        beta = 0
    theta_arc = np.pi / 2 - np.pi / n + np.arccos(min(1, max(-1, (a) / r)))

    # 将输入 rotation 转为弧度
    rotation_rad = np.deg2rad(rotation) if use_degree else rotation

    # 计算圆心坐标
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

    # 角度计算
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
        if not plot:
            return None
        return []  # plot=True 时返回空列表，避免 for t in ... 迭代 None

    # 角度转换
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
            name=name,
            showlegend=showlegend,
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
            name=name,
            showlegend=showlegend,
            use_degree=use_degree,
            plot=plot,
            direction=direction,
            return_arc=return_petal,
            **kwargs,
        )

    if not plot and arc_d1 is not None and arc_d2 is not None:
        return (center1[0], center1[1]), (center2[0], center2[1]), arc_d1, arc_d2

    # 圆心标记
    center_traces = []
    if plot_center and plot:
        center_traces.append(
            go.Scatter(
                x=[center1[0]],
                y=[center1[1]],
                mode="markers",
                marker=dict(color=center_color, size=center_size),
                opacity=alpha,
                showlegend=False,
            )
        )
        center_traces.append(
            go.Scatter(
                x=[center2[0]],
                y=[center2[1]],
                mode="markers",
                marker=dict(color=center_color, size=center_size),
                opacity=alpha,
                showlegend=False,
            )
        )

    if plot:
        result = []
        if arc_d1:
            result.extend(arc_d1)
        if arc_d2:
            result.extend(arc_d2)
        result.extend(center_traces)
        return result if len(result) > 1 else (result[0] if result else None)

    return arc_d1, arc_d2


# 圆花瓣（带填充）
def flower_petal_fill(
    R=1,
    r=1,
    n=4,
    rotation=0,
    color="#0f0",
    alpha=1,
    fill_color=None,
    fill_alpha=0.3,
    edge_color=None,
    edge_width=None,
    center=(0, 0),
    points=1000,
    line_width=1,
    label=None,
    name=None,
    showlegend=None,
    plot_center=False,
    center_color="#0f0",
    center_size=8,
    use_degree=True,
    plot=True,
    direction="ccw",
    **kwargs,
):
    """
    绘制一片带填充的花瓣。

    参数（新增/覆盖）:
        fill_color (str): 填充颜色，默认与 edge_color（或 color）一致。
        fill_alpha (float): 填充透明度，默认为 0.3。
        edge_color (str): 边缘线条颜色，默认与 color 一致。
        edge_width (float): 边缘线条宽度，默认与 line_width 一致。

    其余参数与 flower_petal 相同。
    """
    # ---------- 几何计算 ----------
    angle = 2 * np.pi / n
    a = R * np.sin(np.pi / n)
    if r > 0:
        beta = np.arccos(min(1, max(-1, a / r)))
    else:
        beta = 0
    theta_arc = np.pi / 2 - np.pi / n + np.arccos(min(1, max(-1, a / r)))

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

    # ---------- 分支：根据 r 与 a 的关系计算角度 ----------
    if r < a:
        print(f"r={r:.3f}, a={a:.3f}, R={R:.3f}")
        print(f"r<a，不能形成花瓣。最小需要 r > {a:.3f}")
        if not plot:
            return None
        return []  # plot=True 时返回空列表，避免 for t in ... 迭代 None

    elif abs(r - a) < 1e-12:
        theta1_base_rad = np.pi + angle / 2
        theta2_base_rad = np.pi + angle / 2 + theta_arc
        theta3_base_rad = np.pi / 2
        theta4_base_rad = np.pi / 2 + theta_arc

    else:  # r > a
        theta1_base_rad = np.pi + angle / 2
        theta2_base_rad = np.pi + angle / 2 + theta_arc
        theta3_base_rad = np.pi / 2 - beta
        theta4_base_rad = np.pi / 2 - beta + theta_arc

    # ---------- 角度转换 ----------
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

    # ---------- 获取弧数据（不绘制） ----------
    x1, y1 = arc(
        r, theta1, theta2, rotation_for_arc,
        center=center1, points=points,
        use_degree=use_degree, plot=False, direction=direction,
    )
    x2, y2 = arc(
        r, theta3, theta4, rotation_for_arc,
        center=center2, points=points,
        use_degree=use_degree, plot=False, direction=direction,
    )

    if not plot:
        return (x1, y1, x2, y2)

    # ---------- 填充与边缘参数 ----------
    fc = fill_color if fill_color is not None else (edge_color if edge_color is not None else color)
    ec = edge_color if edge_color is not None else color
    ew = edge_width if edge_width is not None else line_width

    traces = []

    # 填充：两弧直接拼接即形成闭合多边形
    x_fill = np.concatenate([x1, x2])
    y_fill = np.concatenate([y1, y2])
    fill_trace = go.Scatter(
        x=x_fill,
        y=y_fill,
        mode="lines",
        line=dict(width=0),
        opacity=fill_alpha,
        fill="toself",
        fillcolor=fc,
        name=name if name else label,
        showlegend=False,
        hoverinfo="skip",
    )
    traces.append(fill_trace)

    # 边缘线
    edge1 = go.Scatter(
        x=x1,
        y=y1,
        mode="lines",
        line=dict(color=ec, width=ew),
        opacity=alpha,
        name=name if name else label,
        showlegend=showlegend if showlegend is not None else (label is not None),
        **kwargs,
    )
    edge2 = go.Scatter(
        x=x2,
        y=y2,
        mode="lines",
        line=dict(color=ec, width=ew),
        opacity=alpha,
        showlegend=False,
        **kwargs,
    )
    traces.append(edge1)
    traces.append(edge2)

    # 圆心
    if plot_center:
        traces.append(
            go.Scatter(
                x=[center1[0]], y=[center1[1]],
                mode="markers",
                marker=dict(color=center_color, size=center_size),
                opacity=alpha, showlegend=False,
            )
        )
        traces.append(
            go.Scatter(
                x=[center2[0]], y=[center2[1]],
                mode="markers",
                marker=dict(color=center_color, size=center_size),
                opacity=alpha, showlegend=False,
            )
        )

    return traces


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
    name=None,
    showlegend=None,
    plot_center=False,
    center_color="#0f0",
    center_size=8,
    use_degree=True,
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
            else rotation + i * 2 * np.pi / N + np.pi / 2
        )
        result = flower_petal(
            R, r, n, petal_rot,
            color=color, alpha=alpha, center=center, points=points,
            line_width=line_width, label=label, name=name, showlegend=showlegend,
            plot_center=plot_center, center_color=center_color, center_size=center_size,
            use_degree=use_degree, plot=plot, direction=direction,
            return_petal=return_petal,
            **kwargs,
        )
        if result:
            if isinstance(result, list):
                traces.extend(result)
            else:
                traces.append(result)
    return traces


# 单层花（带填充）
def flower_fill(
    R=1,
    r=1,
    n=4,
    N=12,
    rotation=0,
    color="#0f0",
    alpha=1,
    fill_color=None,
    fill_alpha=0.3,
    edge_color=None,
    edge_width=None,
    center=(0, 0),
    points=1000,
    line_width=1,
    label=None,
    name=None,
    showlegend=None,
    plot_center=False,
    center_color="#0f0",
    center_size=8,
    use_degree=True,
    plot=True,
    direction="ccw",
    **kwargs,
):
    """单层填充花朵——N 片带填充的圆花瓣均匀排列。

    新增参数（传递给每片花瓣的填充参数）:
        fill_color, fill_alpha, edge_color, edge_width
    其余参数与 flower 相同。
    """
    traces = []
    for i in range(N):
        petal_rot = (
            rotation + i * 360 / N + 90
            if use_degree
            else rotation + i * 2 * np.pi / N + np.pi / 2
        )
        result = flower_petal_fill(
            R, r, n, petal_rot,
            color=color, alpha=alpha,
            fill_color=fill_color, fill_alpha=fill_alpha,
            edge_color=edge_color, edge_width=edge_width,
            center=center, points=points,
            line_width=line_width, label=label,
            name=name, showlegend=showlegend,
            plot_center=plot_center, center_color=center_color, center_size=center_size,
            use_degree=use_degree, plot=plot, direction=direction,
            **kwargs,
        )
        if result:
            traces.extend(result)
    return traces


# 多层花
def flowers(
    R=1,
    r=1,
    n=4,
    ratio=np.sqrt(2),
    M=3,
    N=12,
    color="blue",
    alpha=1,
    theta=0,
    center=(0, 0),
    points=1000,
    line_width=1,
    label=None,
    name=None,
    showlegend=None,
    plot_center=False,
    center_color="red",
    center_size=5,
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
            result = flower_petal(
                R * (ratio ** (j - 1)),
                r * (ratio ** (j - 1)),
                n,
                2 * i * np.pi / N + (j - 1) * np.pi / N + theta + np.pi / 2,
                color=color, alpha=alpha, center=center, points=points,
                line_width=line_width, label=label, name=name, showlegend=showlegend,
                plot_center=plot_center, center_color=center_color, center_size=center_size,
                use_degree=False, plot=plot, direction=direction,
                return_petal=return_flower,
                **kwargs,
            )
            if result:
                if isinstance(result, list):
                    traces.extend(result)
                else:
                    traces.append(result)
    return traces


# 椭圆花瓣
def oval_petal_a(a, b, d, rotation=0, use_degree=True, color="blue", alpha=1, center=(0, 0), points=1000):
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

    traces = []
    t1 = oval_arc(
        a, b, beta_b1, beta_e1,
        angle=rotation,
        color=color, alpha=alpha, center=center1_rot, points=points,
        use_degree=use_degree,
    )
    t2 = oval_arc(
        a, b, beta_b2, beta_e2,
        angle=rotation,
        color=color, alpha=alpha, center=center2_rot, points=points,
        use_degree=use_degree,
    )
    if t1:
        traces.extend(t1)
    if t2:
        traces.extend(t2)
    return traces


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
    name=None,
    showlegend=None,
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
        rot_by_center (bool): 旋转方式。
        color (str): 颜色，默认为绿色("#0f0")。
        alpha (float): 透明度，默认为1（不透明）。
        center (tuple): 中心坐标，默认为(0, 0)。
        points (int): 用于绘制弧的点数，默认为1000。
        use_degree (bool): 是否使用角度制（True为角度，False为弧度），默认为True。
        line_width (float): 线宽，默认为1。
        label (str): 图例标签，默认为None。
        plot (bool): 是否绘制图像，默认为True。如果为False，则返回计算得到的坐标。
        **kwargs: 其他传递给 oval_arc 的参数。

    返回:
        如果 plot=True: list of traces
        如果 plot=False: tuple: (x1, y1, x2, y2)
    """
    # 计算 beta 角度（弧度）
    x0 = b / (2 * a) * np.sqrt(4 * a**2 - d**2) / (d / 2)
    beta = np.arctan(x0)
    beta_b1_rad = np.pi / 2 - beta
    beta_e1_rad = np.pi / 2 + beta
    beta_b2_rad = 3 * np.pi / 2 - beta
    beta_e2_rad = 3 * np.pi / 2 + beta

    # rotation 转弧度
    rotation_rad = np.deg2rad(rotation) if use_degree else rotation

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
        theta1 = np.linspace(beta_b1_rad, beta_e1_rad, points)
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

        theta2 = np.linspace(beta_b2_rad, beta_e2_rad, points)
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

    # 绘制时，将弧的起止角按需转为角度制传给 oval_arc
    if use_degree:
        beta_b1 = np.rad2deg(beta_b1_rad)
        beta_e1 = np.rad2deg(beta_e1_rad)
        beta_b2 = np.rad2deg(beta_b2_rad)
        beta_e2 = np.rad2deg(beta_e2_rad)
    else:
        beta_b1, beta_e1 = beta_b1_rad, beta_e1_rad
        beta_b2, beta_e2 = beta_b2_rad, beta_e2_rad

    traces = []

    arc1 = oval_arc(
        a, b, beta_b1, beta_e1,
        angle=rotation,
        color=color, alpha=alpha, center=center1_rot, points=points,
        line_width=line_width, label=label, name=name, showlegend=showlegend,
        use_degree=use_degree,
        **kwargs,
    )
    if arc1:
        traces.extend(arc1)

    arc2 = oval_arc(
        a, b, beta_b2, beta_e2,
        angle=rotation,
        color=color, alpha=alpha, center=center2_rot, points=points,
        line_width=line_width, label=label, name=name,
        use_degree=use_degree,
        **kwargs,
    )
    if arc2:
        traces.extend(arc2)

    return traces


# 椭圆花瓣（带填充）
def oval_petal_fill(
    a=2,
    b=1,
    d=0.5,
    rotation=0,
    rot_by_center=True,
    color="#0f0",
    alpha=1,
    fill_color=None,
    fill_alpha=0.3,
    edge_color=None,
    edge_width=None,
    center=(0, 0),
    points=1000,
    line_width=1,
    label=None,
    name=None,
    showlegend=None,
    use_degree=True,
    plot=True,
    **kwargs,
):
    """
    绘制一个带填充的椭圆花瓣形状。

    参数（新增/覆盖）:
        fill_color (str): 填充颜色，默认与 edge_color（或 color）一致。
        fill_alpha (float): 填充透明度，默认为 0.3。
        edge_color (str): 边缘线条颜色，默认与 color 一致。
        edge_width (float): 边缘线条宽度，默认与 line_width 一致。

    其余参数与 oval_petal 相同。
    """
    # 获取椭圆花瓣数据（不绘制）
    result = oval_petal(
        a=a, b=b, d=d, rotation=rotation, rot_by_center=rot_by_center,
        color=color, alpha=alpha, center=center, points=points,
        line_width=line_width, label=label,
        use_degree=use_degree, plot=False,
        **kwargs,
    )

    if result is None:
        return None

    x1, y1, x2, y2 = result

    fc = fill_color if fill_color is not None else (edge_color if edge_color is not None else color)
    ec = edge_color if edge_color is not None else color
    ew = edge_width if edge_width is not None else line_width

    if not plot:
        return (x1, y1, x2, y2)

    traces = []

    # 填充：两弧直接拼接即形成闭合多边形
    x_fill = np.concatenate([x1, x2])
    y_fill = np.concatenate([y1, y2])
    fill_trace = go.Scatter(
        x=x_fill,
        y=y_fill,
        mode="lines",
        line=dict(width=0),
        opacity=fill_alpha,
        fill="toself",
        fillcolor=fc,
        name=name if name else label,
        showlegend=False,
        hoverinfo="skip",
    )
    traces.append(fill_trace)

    # 边缘线
    edge1 = go.Scatter(
        x=x1, y=y1,
        mode="lines",
        line=dict(color=ec, width=ew),
        opacity=alpha,
        name=name if name else label,
        showlegend=showlegend if showlegend is not None else (label is not None),
        **kwargs,
    )
    edge2 = go.Scatter(
        x=x2, y=y2,
        mode="lines",
        line=dict(color=ec, width=ew),
        opacity=alpha,
        showlegend=False,
        **kwargs,
    )
    traces.append(edge1)
    traces.append(edge2)

    return traces


"""
Oval Flower Algorithms
"""


def oval_flower(
    a=2, b=1, d=0.1, n=12, rotation=0, use_degree=True,
    color="#0f0", alpha=1, center=(0, 0), points=1000,
    line_width=1, label=None,
):
    """椭圆花瓣花朵。

    rotation (float): 旋转角度（度或弧度取决于 use_degree）。
    use_degree (bool): rotation 是否使用角度制，默认 True（度）。
    """
    rotation_rad = np.deg2rad(rotation) if use_degree else rotation
    traces = []
    for i in range(n):
        petal_traces = oval_petal(
            a, b, d,
            rotation_rad + i * 2 * np.pi / n,
            rot_by_center=True,
            color=color, alpha=alpha, center=center, points=points,
            line_width=line_width, label=label,
            use_degree=False,
        )
        if petal_traces:
            traces.extend(petal_traces)
    return traces


def oval_flower_fill(
    a=2, b=1, d=0.1, n=12, rotation=0, use_degree=True,
    color="#0f0", alpha=1,
    fill_color=None, fill_alpha=0.3,
    edge_color=None, edge_width=None,
    center=(0, 0), points=1000,
    line_width=1, label=None,
    **kwargs,
):
    """椭圆花瓣花朵（带填充，rot_by_center=True）。

    新增参数（传递给每片花瓣的填充参数）:
        fill_color, fill_alpha, edge_color, edge_width
    其余参数与 oval_flower 相同。
    """
    rotation_rad = np.deg2rad(rotation) if use_degree else rotation
    traces = []
    for i in range(n):
        petal_traces = oval_petal_fill(
            a, b, d,
            rotation_rad + i * 2 * np.pi / n,
            rot_by_center=True,
            color=color, alpha=alpha,
            fill_color=fill_color, fill_alpha=fill_alpha,
            edge_color=edge_color, edge_width=edge_width,
            center=center, points=points,
            line_width=line_width, label=label,
            use_degree=False,
            **kwargs,
        )
        if petal_traces:
            traces.extend(petal_traces)
    return traces


def oval_flower_a(
    a=2, b=1, d=0.1, n=12, rotation=0, use_degree=True,
    color="#0f0", alpha=1, center=(0, 0), points=1000,
    line_width=1, label=None,
):
    """椭圆花瓣花朵（旋转模式 a）。

    rotation (float): 旋转角度（度或弧度取决于 use_degree）。
    use_degree (bool): rotation 是否使用角度制，默认 True（度）。
    """
    rotation_rad = np.deg2rad(rotation) if use_degree else rotation
    traces = []
    for i in range(n):
        petal_traces = oval_petal(
            a, b, d,
            rotation_rad + i * 2 * np.pi / n,
            rot_by_center=False,
            color=color, alpha=alpha, center=center, points=points,
            line_width=line_width, label=label,
            use_degree=False,
        )
        if petal_traces:
            traces.extend(petal_traces)
    return traces


def oval_flower_a_fill(
    a=2, b=1, d=0.1, n=12, rotation=0, use_degree=True,
    color="#0f0", alpha=1,
    fill_color=None, fill_alpha=0.3,
    edge_color=None, edge_width=None,
    center=(0, 0), points=1000,
    line_width=1, label=None,
    **kwargs,
):
    """椭圆花瓣花朵（带填充，rot_by_center=False）。

    新增参数（传递给每片花瓣的填充参数）:
        fill_color, fill_alpha, edge_color, edge_width
    其余参数与 oval_flower_a 相同。
    """
    rotation_rad = np.deg2rad(rotation) if use_degree else rotation
    traces = []
    for i in range(n):
        petal_traces = oval_petal_fill(
            a, b, d,
            rotation_rad + i * 2 * np.pi / n,
            rot_by_center=False,
            color=color, alpha=alpha,
            fill_color=fill_color, fill_alpha=fill_alpha,
            edge_color=edge_color, edge_width=edge_width,
            center=center, points=points,
            line_width=line_width, label=label,
            use_degree=False,
            **kwargs,
        )
        if petal_traces:
            traces.extend(petal_traces)
    return traces


__all__ = [
    "flower_petal",
    "flower_petal_fill",
    "flower",
    "flower_fill",
    "flowers",
    "rotate_point",
    "oval_petal_a",
    "oval_petal",
    "oval_petal_fill",
    "oval_flower",
    "oval_flower_fill",
    "oval_flower_a",
    "oval_flower_a_fill",
]

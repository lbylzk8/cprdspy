import plotly.graph_objects as go
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
    line_width=1,
    label=None,
    name=None,
    showlegend=None,
    plot=True,
    direction="ccw",  # 'ccw' or 'cw'
    return_arc=False,
    **kwargs,
):
    """
    画通过 point1 到 point2 的圆弧（以 center 为圆心），
    如果 point1 和 point2 的半径不同，会使用 point1 的半径并打印警告。
    返回 (x, y) 数组; 如果 plot=True，会返回 go.Scatter 轨迹。
    """
    v1 = np.array(point1) - np.array(center)
    v2 = np.array(point2) - np.array(center)

    r1 = np.linalg.norm(v1)
    r2 = np.linalg.norm(v2)
    if r1 == 0 or r2 == 0:
        raise ValueError("point1/point2 不应与 center 重合")
    if abs(r1 - r2) > 1e-6:
        print(f"Warning: radii differ (r1={r1:.6g}, r2={r2:.6g}); using r1 for arc")
    r = r1

    theta1 = np.arctan2(v1[1], v1[0]) % (2 * np.pi)
    theta2 = np.arctan2(v2[1], v2[0]) % (2 * np.pi)

    if direction == "ccw":
        if theta2 <= theta1:
            theta2 = theta2 + 2 * np.pi
        theta = np.linspace(theta1, theta2, points)
    else:  # cw
        if theta1 <= theta2:
            theta1 = theta1 + 2 * np.pi
        theta = np.linspace(theta1, theta2, points)[::-1]

    x = center[0] + r * np.cos(theta)
    y = center[1] + r * np.sin(theta)

    if not plot:
        return x, y

    trace = go.Scatter(
        x=x,
        y=y,
        mode="lines",
        line=dict(color=color, width=line_width),
        opacity=alpha,
        name=name if name else label,
        showlegend=showlegend if showlegend is not None else (label is not None),
        **kwargs,
    )

    if return_arc:
        return trace
    return trace


## arc_point_inverse
def arc_point_inverse(
    center=(0, 0),
    point1=(1, 0),
    point2=(-1, 0),
    color="#0f0",
    alpha=1,
    points=1000,
    line_width=1,
    label=None,
    plot=True,
    direction="cw",
    return_arc=False,
    **kwargs,
):
    return arc_point(
        center=center,
        point1=point1,
        point2=point2,
        color=color,
        alpha=alpha,
        points=points,
        line_width=line_width,
        label=label,
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
    line_width=1,
    label=None,
    name=None,
    showlegend=None,
    use_degree=True,
    plot=True,
    direction="ccw",  # 'ccw' or 'cw'
    return_arc=False,
    **kwargs,
):
    """
    绘制圆弧。

    参数:
        r (float): 半径。
        angle1 (float): 起始角度（度或弧度）。
        angle2 (float): 结束角度（度或弧度）。
        rotation (float): 旋转角度。
        color (str): 颜色。
        alpha (float): 透明度。
        center (tuple): 圆心坐标。
        points (int): 点数。
        line_width (float): 线宽。
        label (str): 标签。
        use_degree (bool): 是否使用角度制。
        plot (bool): 是否绘制。
        direction (str): 'ccw' 或 'cw'。
        return_arc (bool): 是否返回轨迹对象。

    返回:
        plotly.graph_objs.Scatter 或 tuple: 轨迹对象或坐标。
    """
    if use_degree:
        theta1 = np.deg2rad(angle1)
        theta2 = np.deg2rad(angle2)
        rot = np.deg2rad(rotation)
    else:
        theta1 = angle1
        theta2 = angle2
        rot = rotation

    if direction == "ccw":
        if theta2 <= theta1:
            theta2 = theta2 + 2 * np.pi
        theta = np.linspace(theta1, theta2, points)
    else:  # cw
        if theta1 <= theta2:
            theta1 = theta1 + 2 * np.pi
        theta = np.linspace(theta1, theta2, points)[::-1]

    cos_rot = np.cos(rot)
    sin_rot = np.sin(rot)

    x = center[0] + r * (np.cos(theta) * cos_rot - np.sin(theta) * sin_rot)
    y = center[1] + r * (np.sin(theta) * cos_rot + np.cos(theta) * sin_rot)

    if not plot:
        return x, y

    trace = go.Scatter(
        x=x,
        y=y,
        mode="lines",
        line=dict(color=color, width=line_width),
        opacity=alpha,
        name=name if name else label,
        showlegend=showlegend if showlegend is not None else (label is not None),
        **kwargs,
    )

    if return_arc:
        return trace
    return trace


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
    line_width=1,
    label=None,
    use_degree=True,
    plot=True,
    direction="cw",
    return_arc=False,
    **kwargs,
):
    return arc(
        r=r,
        angle1=angle1,
        angle2=angle2,
        rotation=rotation,
        color=color,
        alpha=alpha,
        center=center,
        points=points,
        line_width=line_width,
        label=label,
        use_degree=use_degree,
        plot=plot,
        direction=direction,
        return_arc=return_arc,
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
    line_width=1,
    label=None,
    use_degree=True,
    **kwargs,
):
    return arc(
        r=r,
        angle1=angle1,
        angle2=angle2,
        rotation=rotation,
        color=color,
        alpha=alpha,
        center=center,
        points=points,
        line_width=line_width,
        label=label,
        use_degree=use_degree,
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
    line_width=1,
    label=None,
    use_degree=True,
    **kwargs,
):
    return arc(
        r=r,
        angle1=angle1,
        angle2=angle2,
        rotation=rotation,
        color=color,
        alpha=alpha,
        center=center,
        points=points,
        line_width=line_width,
        label=label,
        use_degree=use_degree,
        plot=False,
        direction="cw",
        return_arc=False,
        **kwargs,
    )


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
    line_width=1,
    label=None,
    name=None,
    showlegend=None,
    use_degree=True,
    plot=True,
    **kwargs,
):
    """
    绘制一段椭圆弧或返回计算得到的 x 和 y 值。

    参数:
        a (float): 椭圆的长轴长度。
        b (float): 椭圆的短轴长度。
        angle1 (float): 弧的起始角度。
        angle2 (float): 弧的结束角度。
        angle (float): 椭圆的旋转角度。
        color (str): 弧的颜色。
        alpha (float): 透明度。
        center (tuple): 椭圆的中心坐标。
        points (int): 点数。
        line_width (float): 线宽。
        label (str): 标签。
        use_degree (bool): 是否使用角度制。
        plot (bool): 是否绘制。

    返回:
        plotly.graph_objs.Scatter 或 tuple: 轨迹对象或坐标。
    """
    if use_degree:
        angle1_rad = np.deg2rad(angle1)
        angle2_rad = np.deg2rad(angle2)
        angle_rad = np.deg2rad(angle)
    else:
        angle1_rad = angle1
        angle2_rad = angle2
        angle_rad = angle

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

    if not plot:
        return x, y

    trace = go.Scatter(
        x=x,
        y=y,
        mode="lines",
        line=dict(color=color, width=line_width),
        opacity=alpha,
        name=name if name else label,
        showlegend=showlegend if showlegend is not None else (label is not None),
        **kwargs,
    )

    return trace

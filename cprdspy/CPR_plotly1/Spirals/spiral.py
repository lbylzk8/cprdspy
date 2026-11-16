import plotly.graph_objects as go
import numpy as np


def logSpiral(
    n=4,
    a=1,
    b=1,
    cyc=0.5,
    color="blue",
    theta=0,
    rotation=0,
    direction="both",
    alpha=1,
    line_width=1.0,
    use_degree=True,
    plot=True,
):
    """绘制广义对数螺线。

    参数:
        n: 花瓣/对称数（影响基底 cos(pi/n)）
        a, b: x/y 方向缩放（可做椭圆化）
        cyc: 周期数（每个周期为 2π）
        color: 线颜色
        theta: 全局相位偏移（度或弧度取决于 use_degree）
        rotation: 额外角度偏移（度或弧度取决于 use_degree）
        direction: 'both'|'in'|'out' 控制绘制方向
        alpha: 透明度
        line_width: 线宽
        use_degree (bool): theta 和 rotation 是否使用角度制，默认 True（度）。
        plot (bool): 是否返回 go.Scatter 轨迹。

    返回:
        plotly.graph_objs.Scatter 或 tuple (x, y)
    """
    theta_rad = np.deg2rad(theta) if use_degree else theta
    rot_rad = np.deg2rad(rotation) if use_degree else rotation

    if direction not in ("both", "in", "out"):
        raise ValueError("direction must be 'both', 'in' or 'out'")

    if direction == "both":
        t = np.linspace(-cyc * 2 * np.pi, cyc * 2 * np.pi, 1000)
    elif direction == "out":
        t = np.linspace(0, cyc * 2 * np.pi, 1000)
    else:  # in
        t = np.linspace(0, -cyc * 2 * np.pi, 1000)

    # r 随角度成几何增长/衰减：基于 (cos(pi/n)) ** (-n * t / pi)
    r = (np.cos(np.pi / n)) ** (-n * t / np.pi)
    ang = t + theta_rad + rot_rad
    x = a * r * np.cos(ang)
    y = b * r * np.sin(ang)

    if not plot:
        return x, y

    trace = go.Scatter(
        x=x,
        y=y,
        mode="lines",
        line=dict(color=color, width=line_width),
        opacity=alpha,
        showlegend=False,
    )
    return [trace]


def nSpiral(
    n=4,
    a=1,
    N=4,
    cyc=0.5,
    color="blue",
    theta=0,
    rotation=0,
    direction="both",
    line_width=1.0,
    use_degree=True,
):
    """n 边形螺旋。

    theta, rotation: 度或弧度取决于 use_degree。
    use_degree (bool): 默认 True（度）。

    返回:
        list: 包含所有轨迹的列表。
    """
    theta_rad = np.deg2rad(theta) if use_degree else theta
    rot_rad = np.deg2rad(rotation) if use_degree else rotation
    traces = []
    for i in range(N):
        t1 = logSpiral(n, a, 1, cyc, color, theta_rad + i * 2 * np.pi / N, rot_rad,
                       direction, 1, line_width, use_degree=False)
        t2 = logSpiral(n, a, 1, cyc, color, -theta_rad + i * 2 * np.pi / N, -rot_rad,
                       direction, 1, line_width, use_degree=False)
        if t1:
            traces.extend(t1)
        if t2:
            traces.extend(t2)
    return traces


def nSpirals(
    n=4,
    N=4,
    cyc=0.5,
    color="blue",
    theta=0,
    rotation=0,
    direction="both",
    line_width=1.0,
    use_degree=True,
):
    """多头 n 边形螺旋。

    theta, rotation: 度或弧度取决于 use_degree。
    use_degree (bool): 默认 True（度）。

    返回:
        list: 包含所有轨迹的列表。
    """
    theta_rad = np.deg2rad(theta) if use_degree else theta
    rot_rad = np.deg2rad(rotation) if use_degree else rotation
    traces = []
    for i in range(N):
        t1 = logSpiral(n, 1, 1, cyc, color, theta_rad + i * 2 * np.pi / N, rot_rad,
                       direction, 1, line_width, use_degree=False)
        t2 = logSpiral(n, -1, 1, cyc, color, -theta_rad + i * 2 * np.pi / N, -rot_rad,
                       direction, 1, line_width, use_degree=False)
        if t1:
            traces.extend(t1)
        if t2:
            traces.extend(t2)
    return traces


def calla_petal(
    n=4,
    a=1,
    cyc=1.25,
    theta=0,
    color="blue",
    rotation=0,
    direction="both",
    line_width=1.0,
    use_degree=True,
):
    """马蹄莲花瓣。

    theta, rotation: 度或弧度取决于 use_degree。
    use_degree (bool): 默认 True（度）。

    返回:
        list: 包含两个螺旋轨迹的列表。
    """
    theta_rad = np.deg2rad(theta) if use_degree else theta
    rot_rad = np.deg2rad(rotation) if use_degree else rotation
    traces = []
    t1 = logSpiral(n, a, 1, cyc, color, theta_rad, rot_rad, direction, 1, line_width, use_degree=False)
    t2 = logSpiral(n, -a, 1, cyc, color, -theta_rad, -rot_rad, direction, 1, line_width, use_degree=False)
    if t1:
        traces.extend(t1)
    if t2:
        traces.extend(t2)
    return traces


def calla(
    n=4,
    a=1,
    cyc=1.25,
    N=12,
    theta=0,
    colors=None,
    rotation=0,
    direction="both",
    line_width=1.0,
    use_degree=True,
):
    """完整马蹄莲。

    theta, rotation: 度或弧度取决于 use_degree。
    use_degree (bool): 默认 True（度）。

    返回:
        list: 包含所有轨迹的列表。
    """
    if colors is None:
        colors = ["red", "green", "blue"] * 4
    theta_rad = np.deg2rad(theta) if use_degree else theta
    rot_rad = np.deg2rad(rotation) if use_degree else rotation
    traces = []
    for i in range(N):
        petal_traces = calla_petal(n, a, cyc, theta_rad + i * 2 * np.pi / N, colors[i],
                                   rot_rad, direction, line_width, use_degree=False)
        traces.extend(petal_traces)
    return traces


__all__ = [
    "logSpiral",
    "nSpiral",
    "nSpirals",
    "calla_petal",
    "calla",
]

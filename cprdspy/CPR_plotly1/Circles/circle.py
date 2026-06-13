import numpy as np
import plotly.graph_objects as go


def circle(
    radius=1,
    color="#0F0",
    alpha=1,
    center=(0, 0),
    points=100,
    line_width=1,
    label=None,
    mode="lines",
    name=None,
    showlegend=None,
    **kwargs,
):
    """
    绘制一个圆。

    参数:
        radius (float): 圆的半径，默认为 1。
        color (str): 圆的颜色，默认为绿色 ("#0F0")。
        alpha (float): 透明度，默认为 1（不透明）。
        center (tuple): 圆心坐标，默认为 (0, 0)。
        points (int): 用于绘制圆的点数，默认为 100。
        line_width (float): 线宽，默认为 1。
        label (str): 图例标签，默认为 None。
        mode (str): 绘图模式，默认为 "lines"。
        name (str): 轨迹名称，默认为 None。
        showlegend (bool): 是否显示图例，默认为 None。
        **kwargs: 其他传递给 go.Scatter 的参数。

    返回:
        plotly.graph_objs.Scatter: 圆的轨迹对象。
    """
    angle = np.linspace(0, 2 * np.pi, points)
    x = center[0] + radius * np.cos(angle)
    y = center[1] + radius * np.sin(angle)

    trace = go.Scatter(
        x=x,
        y=y,
        mode=mode,
        line=dict(color=color, width=line_width, dash="solid"),
        fill="none",
        opacity=alpha,
        name=name if name else label,
        showlegend=showlegend,
        hoverinfo="none" if not label else "x+y+text",
        text=label,
        **kwargs,
    )

    return trace


def draw_circle(
    radius=1,
    color="#0F0",
    alpha=1,
    center=(0, 0),
    points=100,
    line_width=1,
    label=None,
):
    """
    绘制圆并返回 Figure（便捷函数）。
    """
    trace = circle(
        radius=radius,
        color=color,
        alpha=alpha,
        center=center,
        points=points,
        line_width=line_width,
        label=label,
    )
    fig = go.Figure(data=[trace])
    fig.update_layout(
        xaxis=dict(scaleanchor="y", scaleratio=1),
        yaxis=dict(scaleanchor="x", scaleratio=1),
        width=600,
        height=600,
    )
    return fig


def circle_p(center, point, color="b"):
    """
    通过圆心和圆上一点绘制圆。
    """
    radius = np.sqrt((point[0] - center[0]) ** 2 + (point[1] - center[1]) ** 2)
    return circle(radius=radius, color=color, center=center)


# 椭圆
def ellipse(
    a=2,
    b=1,
    rotation=0,
    color="#0f0",
    alpha=1,
    center=(0, 0),
    points=1000,
    line_width=1,
    label=None,
):
    """
    绘制椭圆。

    参数:
        a (float): 半长轴。
        b (float): 半短轴。
        rotation (float): 旋转角度（度）。
        color (str): 颜色。
        alpha (float): 透明度。
        center (tuple): 中心坐标。
        points (int): 点数。
        line_width (float): 线宽。
        label (str): 标签。

    返回:
        plotly.graph_objs.Scatter: 椭圆轨迹。
    """
    theta = np.linspace(0, 2 * np.pi, points)
    angle_rad = np.deg2rad(rotation)
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

    trace = go.Scatter(
        x=x,
        y=y,
        mode="lines",
        line=dict(color=color, width=line_width),
        opacity=alpha,
        name=label,
        showlegend=label is not None,
    )
    return trace


# 统一的同心圆函数
def concentric_circles(
    center=(0, 0),
    n=3,
    radius=1,
    param=0.5,
    mode="arithmetic",
    direction="both",
    color="#0F0",
    alpha=1,
    points=200,
    line_width=1,
    show_center=True,
    **kwargs,
):
    """
    绘制同心圆的统一函数（兼容等差与等比序列）。

    参数:
        center (tuple): 圆心坐标。
        n (int): 每一侧的圈数（当 direction=='both' 时每侧各 n 个）。
        radius (float): 基准半径（绘制在中间）。
        param (float): 当 mode=='arithmetic' 时作为公差 d；当 mode=='geometric' 时作为公比 q。
        mode (str): 'arithmetic' 或 'geometric'，选择等差或等比。
        direction (str): 'both'|'out'|'in'，控制向外/向内/双向绘制。
        color (str): 颜色。
        alpha (float): 透明度。
        points (int): 点数。
        line_width (float): 线宽。
        show_center (bool): 是否绘制圆心标记。
        **kwargs: 其它传入 go.Scatter 的参数。

    返回:
        list: 包含所有轨迹的列表。
    """
    traces = []

    if show_center:
        center_trace = go.Scatter(
            x=[center[0]],
            y=[center[1]],
            mode="markers",
            marker=dict(color=color, size=6),
            showlegend=False,
        )
        traces.append(center_trace)

    radii = []
    mode = mode.lower()
    direction = direction.lower()

    if mode.startswith("a"):
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

    radii = [r for r in radii if r > 0]
    radii.append(radius)
    radii = sorted(set(radii))

    for r in radii:
        angle = np.linspace(0, 2 * np.pi, points)
        x = center[0] + r * np.cos(angle)
        y = center[1] + r * np.sin(angle)
        trace = go.Scatter(
            x=x,
            y=y,
            mode="lines",
            line=dict(color=color, width=line_width),
            opacity=alpha,
            showlegend=False,
            **kwargs,
        )
        traces.append(trace)

    return traces


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
    alpha=1,
    points=200,
    line_width=1,
    show_center=True,
    **kwargs,
):
    """
    绘制同心椭圆（兼容等差与等比序列）。

    参数:
        center (tuple): 椭圆中心。
        n (int): 每侧的椭圆数量。
        a (float): 基准半长轴。
        b (float): 基准半短轴。
        param (float): 等差时为公差 d；等比时为公比 q。
        mode (str): 'arithmetic' 或 'geometric'。
        direction (str): 'both'|'out'|'in'。
        rotation (float): 椭圆旋转角度（度）。
        color (str): 颜色。
        alpha (float): 透明度。
        points (int): 点数。
        line_width (float): 线宽。
        show_center (bool): 是否绘制中心标记。

    返回:
        list: 包含所有轨迹的列表。
    """
    traces = []

    if show_center:
        center_trace = go.Scatter(
            x=[center[0]],
            y=[center[1]],
            mode="markers",
            marker=dict(color=color, size=6),
            showlegend=False,
        )
        traces.append(center_trace)

    ellipses = []
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

    ellipses.append((a, b))
    uniq = {}
    for aa, bb in ellipses:
        if aa > 0 and bb > 0:
            key = (round(float(aa), 12), round(float(bb), 12))
            uniq[key] = (float(aa), float(bb))

    sorted_ellipses = sorted(uniq.values(), key=lambda t: t[0] * t[1])

    angle_rad = np.deg2rad(rotation)

    for aa, bb in sorted_ellipses:
        theta = np.linspace(0, 2 * np.pi, points)
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
        trace = go.Scatter(
            x=x,
            y=y,
            mode="lines",
            line=dict(color=color, width=line_width),
            opacity=alpha,
            showlegend=False,
            **kwargs,
        )
        traces.append(trace)

    return traces

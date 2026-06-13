import plotly.graph_objects as go
import numpy as np


def logSpiral(
    n=4,
    a=1,
    b=1,
    cyc=0.5,
    color="b",
    theta=0,
    rotation=0,
    direction="both",
    alpha=1,
    line_width=1.0,
    plot=True,
):
    """绘制广义对数螺线。

    参数说明：
    - n: 花瓣/对称数（影响基底 cos(pi/n)）
    - a, b: x/y 方向缩放（可做椭圆化）
    - cyc: 周期数（每个周期为 2π）
    - color: 线颜色
    - theta: 全局相位偏移
    - rotation: 额外角度偏移
    - direction: 'both'|'in'|'out' 控制绘制方向
    - alpha: 透明度
    - line_width: 线宽
    - plot: 是否返回 go.Scatter 轨迹
    """
    if direction not in ("both", "in", "out"):
        raise ValueError("direction must be 'both', 'in' or 'out'")

    if direction == "both":
        t = np.linspace(-cyc * 2 * np.pi, cyc * 2 * np.pi, 1000)
    elif direction == "out":
        t = np.linspace(0, cyc * 2 * np.pi, 1000)
    else:  # in
        t = np.linspace(0, -cyc * 2 * np.pi, 1000)

    r = (np.cos(np.pi / n)) ** (-n * t / np.pi)
    ang = t + theta + rotation
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
    return trace


def nSpiral(n=4, N=4, cyc=0.5, color="b", theta=0, rotation=0, line_width=1.0):
    """绘制 n 瓣螺旋。"""
    traces = []
    for i in range(N):
        t1 = logSpiral(
            n,
            1,
            1,
            cyc,
            color,
            theta + i * 2 * np.pi / N,
            rotation,
            "both",
            1,
            line_width,
        )
        t2 = logSpiral(
            n,
            -1,
            1,
            cyc,
            color,
            -theta + i * 2 * np.pi / N,
            -rotation,
            "both",
            1,
            line_width,
        )
        if t1:
            traces.append(t1)
        if t2:
            traces.append(t2)
    return traces


def logSpiral_in_out(n, a, b, cyc, color="b", theta=0):
    """绘制双向对数螺线。"""
    t = np.linspace(-cyc * 2 * np.pi, cyc * 2 * np.pi, 1000)
    x = a * (np.cos(np.pi / n)) ** (-n * t / np.pi) * np.cos(t + theta)
    y = b * (np.cos(np.pi / n)) ** (-n * t / np.pi) * np.sin(t + theta)
    trace = go.Scatter(
        x=x, y=y, mode="lines", line=dict(color=color), showlegend=False
    )
    return trace


def logSpiral_out(n, a, b, cyc, color="b", theta=0):
    """绘制外向对数螺线。"""
    t = np.linspace(0, cyc * 2 * np.pi, 100)
    x = a * (np.cos(np.pi / n)) ** (-n * t / np.pi) * np.cos(t + theta)
    y = b * (np.cos(np.pi / n)) ** (-n * t / np.pi) * np.sin(t + theta)
    trace = go.Scatter(
        x=x, y=y, mode="lines", line=dict(color=color), showlegend=False
    )
    return trace


def logSpiral_in(n, a, b, cyc, color="b", theta=0):
    """绘制内向对数螺线。"""
    t = np.linspace(0, -cyc * 2 * np.pi, 100)
    x = a * (np.cos(np.pi / n)) ** (-n * t / np.pi) * np.cos(t + theta)
    y = b * (np.cos(np.pi / n)) ** (-n * t / np.pi) * np.sin(t + theta)
    trace = go.Scatter(
        x=x, y=y, mode="lines", line=dict(color=color), showlegend=False
    )
    return trace


def n_spiral(n, cyc, color, theta=0):
    """绘制 n 个螺旋。"""
    traces = []
    for i in range(n):
        t1 = logSpiral(n, 1, 1, cyc, color, theta + i * 2 * np.pi / n)
        t2 = logSpiral(n, -1, 1, cyc, color, theta + i * 2 * np.pi / n)
        if t1:
            traces.append(t1)
        if t2:
            traces.append(t2)
    return traces


def n_spiral_rotate(n, cyc, color, alpha=0, theta=0):
    """绘制旋转的 n 个螺旋。"""
    traces = []
    for i in range(n):
        t1 = logSpiral(n, 1, 1, cyc, color, alpha + theta + i * 2 * np.pi / n)
        t2 = logSpiral(n, -1, 1, cyc, color, alpha - theta + i * 2 * np.pi / n)
        if t1:
            traces.append(t1)
        if t2:
            traces.append(t2)
    return traces


def n_spiral_rotate_out(n, cyc, color, theta=0):
    """绘制旋转的外向 n 个螺旋。"""
    traces = []
    for i in range(n):
        t1 = logSpiral_out(n, 1, 1, cyc, color, theta + i * 2 * np.pi / n)
        t2 = logSpiral_out(n, -1, 1, cyc, color, -theta + i * 2 * np.pi / n)
        if t1:
            traces.append(t1)
        if t2:
            traces.append(t2)
    return traces


def n_spiral_rotate_in(n, cyc, color, theta=0):
    """绘制旋转的内向 n 个螺旋。"""
    traces = []
    for i in range(n):
        t1 = logSpiral_in(n, 1, 1, cyc, color, theta + i * 2 * np.pi / n)
        t2 = logSpiral_in(n, -1, 1, cyc, color, -theta + i * 2 * np.pi / n)
        if t1:
            traces.append(t1)
        if t2:
            traces.append(t2)
    return traces


def calla_petal(n, cyc, theta, color):
    """绘制马蹄莲花瓣。"""
    traces = []
    t1 = logSpiral(n, 1, 1, cyc * 1.25, color, theta)
    t2 = logSpiral(n, -1, 1, cyc * 1.25, color, -theta)
    if t1:
        traces.append(t1)
    if t2:
        traces.append(t2)
    return traces


def calla_by_petal(n, cyc, N, theta, colors):
    """绘制多个马蹄莲花瓣。"""
    traces = []
    for i in range(N):
        petal_traces = calla_petal(n, cyc, theta + i * 2 * np.pi / N, colors[i])
        traces.extend(petal_traces)
    return traces

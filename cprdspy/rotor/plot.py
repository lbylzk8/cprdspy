"""
plot.py — Rotor 曲线可视化

支持 matplotlib 和 plotly 双后端。

功能:
    - rotor_plot(): 快速绘制 Rotor 曲线（自动选择后端）
    - rotor_plot_mpl(): matplotlib 静态图
    - rotor_plot_plotly(): plotly 交互图
    - 支持按曲率/弧长着色
    - 支持绘制 Rotor 链（本轮可视化）
"""

import numpy as np
from typing import Union, Tuple, Optional


# ============================================================
# matplotlib 后端
# ============================================================

def rotor_plot_mpl(
    composition=None,
    x=None, y=None, t=None,
    color="b",
    alpha=1.0,
    linewidth=1.0,
    linestyle="-",
    color_by=None,
    cmap="plasma",
    show_curvature=False,
    title=None,
    figsize=(8, 8),
    ax=None,
    plot=True,
):
    """
    matplotlib 绘制 Rotor 曲线

    参数:
        composition: Rotor2D 或 RotorComposition（自动采样）
        x, y: 手动传入坐标数组（与 composition 二选一）
        color: 颜色（color_by 不为 None 时忽略）
        color_by: 'curvature' | 'arc_length' | None
        cmap: matplotlib colormap 名称
        show_curvature: 是否在下方额外显示 κ(t) 曲线
        ax: matplotlib Axes 对象
    """
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    from .trace import trace, compute_curvature, arc_length

    # 采样
    if x is None or y is None:
        if composition is None:
            raise ValueError("需要提供 composition 或 (x, y) 坐标")
        t, x, y = trace(composition)

    fig = None
    if ax is None:
        if show_curvature:
            fig, (ax, ax2) = plt.subplots(2, 1, figsize=(figsize[0], figsize[1] * 1.3))
        else:
            fig, ax = plt.subplots(1, 1, figsize=figsize)

    # 着色
    if color_by == "curvature":
        kappa = compute_curvature(x, y, t)
        points = np.column_stack([x, y]).reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        lc = LineCollection(segments, cmap=cmap, linewidth=linewidth, alpha=alpha)
        lc.set_array(kappa[:-1])
        line = ax.add_collection(lc)
        if fig:
            fig.colorbar(line, ax=ax, shrink=0.8, label="κ 曲率")
    elif color_by == "arc_length":
        s = arc_length(x, y, t)
        points = np.column_stack([x, y]).reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        lc = LineCollection(segments, cmap=cmap, linewidth=linewidth, alpha=alpha)
        lc.set_array(s[:-1])
        line = ax.add_collection(lc)
        if fig:
            fig.colorbar(line, ax=ax, shrink=0.8, label="s 弧长")
    else:
        ax.plot(x, y, color=color, alpha=alpha, lw=linewidth, ls=linestyle)

    ax.set_aspect("equal")
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=13, pad=10)

    # 额外显示曲率曲线
    if show_curvature and 'ax2' in dir():
        kappa = compute_curvature(x, y, t)
        ax2.plot(t, kappa, color="crimson", lw=0.8)
        ax2.set_xlabel("t", fontsize=10)
        ax2.set_ylabel("κ(t)", fontsize=10)
        ax2.set_title("曲率", fontsize=11)
        ax2.grid(True, alpha=0.3)

    if fig:
        plt.tight_layout()
    if plot:
        plt.show()

    return ax


# ============================================================
# plotly 后端
# ============================================================

def rotor_plot_plotly(
    composition=None,
    x=None, y=None, t=None,
    color=None,
    color_by=None,
    colorscale="Viridis",
    line_width=2,
    opacity=1.0,
    title=None,
    show=True,
    dark=True,
):
    """
    plotly 交互绘制 Rotor 曲线

    参数:
        composition: Rotor2D 或 RotorComposition
        color_by: 'curvature' | 'arc_length' | None
        colorscale: plotly 颜色标度
        dark: 是否使用深色主题
    """
    import plotly.graph_objects as go
    from .trace import trace, compute_curvature, arc_length

    # 采样
    if x is None or y is None:
        if composition is None:
            raise ValueError("需要提供 composition 或 (x, y) 坐标")
        t, x, y = trace(composition)

    # 颜色数据
    if color_by == "curvature":
        c = compute_curvature(x, y, t)
        c_label = "κ 曲率"
    elif color_by == "arc_length":
        c = arc_length(x, y, t)
        c_label = "s 弧长"
    else:
        c = None
        c_label = ""

    # 构建 traces
    traces = []
    if c is not None:
        # plotly 不支持 line.color 数组，需要分段绘制
        # 为性能考虑，限制最大段数
        max_segments = 500
        step = max(1, len(x) // max_segments)
        indices = list(range(0, len(x), step))
        if indices[-1] != len(x) - 1:
            indices.append(len(x) - 1)

        # 归一化颜色值
        c_min, c_max = c.min(), c.max()
        c_norm = (c - c_min) / (c_max - c_min + 1e-15)

        # 使用 matplotlib colormap 转换为颜色
        import matplotlib.pyplot as plt
        cmap = plt.get_cmap(colorscale if colorscale != "Viridis" else "viridis")

        for i in range(len(indices) - 1):
            idx_start = indices[i]
            idx_end = indices[i + 1]
            seg_color = cmap(c_norm[idx_start])
            hex_color = f"rgb({int(seg_color[0]*255)},{int(seg_color[1]*255)},{int(seg_color[2]*255)})"

            seg_trace = go.Scatter(
                x=x[idx_start:idx_end+1],
                y=y[idx_start:idx_end+1],
                mode="lines",
                line=dict(color=hex_color, width=line_width),
                opacity=opacity,
                showlegend=False,
                hovertemplate="x: %{x:.3f}<br>y: %{y:.3f}<extra></extra>",
            )
            traces.append(seg_trace)

        # 添加一个隐藏的 scatter 用于 colorbar
        colorbar_trace = go.Scatter(
            x=[None], y=[None],
            mode="markers",
            marker=dict(
                colorscale=colorscale if colorscale != "Viridis" else "viridis",
                cmin=c_min,
                cmax=c_max,
                colorbar=dict(title=c_label, thickness=15, len=0.6),
                color=[c_min, c_max],
                showscale=True,
            ),
            showlegend=False,
        )
        traces.append(colorbar_trace)
    else:
        # 单色线条
        trace_data = go.Scatter(
            x=x, y=y,
            mode="lines",
            line=dict(color=color, width=line_width),
            opacity=opacity,
            hovertemplate="x: %{x:.3f}<br>y: %{y:.3f}<extra></extra>",
        )
        traces.append(trace_data)

    layout = go.Layout(
        title=title or "Rotor Curve",
        xaxis=dict(visible=False, scaleanchor="y", scaleratio=1),
        yaxis=dict(visible=False),
        width=800,
        height=700,
        template="plotly_dark" if dark else "plotly_white",
    )

    fig = go.Figure(data=traces, layout=layout)

    if show:
        fig.show()

    return fig


# ============================================================
# 统一接口
# ============================================================

def rotor_plot(
    composition=None,
    backend="matplotlib",
    x=None, y=None, t=None,
    color="b",
    color_by=None,
    linewidth=1.0,
    alpha=1.0,
    title=None,
    figsize=(8, 8),
    show=True,
    **kwargs,
):
    """
    统一绘图接口

    参数:
        composition: Rotor2D 或 RotorComposition
        backend: 'matplotlib' | 'plotly' | 'mpl' | 'plt'
        color_by: None | 'curvature' | 'arc_length'
        其他参数透传给对应后端

    示例:
        >>> curve = Rotor2D(3, 1) + Rotor2D(1, 7)
        >>> rotor_plot(curve)                          # matplotlib
        >>> rotor_plot(curve, backend='plotly')        # plotly 交互
        >>> rotor_plot(curve, color_by='curvature')    # 按曲率着色
    """
    backend = backend.lower()
    if backend in ("matplotlib", "mpl"):
        return rotor_plot_mpl(
            composition, x=x, y=y, t=t,
            color=color, linewidth=linewidth, alpha=alpha,
            color_by=color_by, title=title, figsize=figsize,
            plot=show, **kwargs,
        )
    elif backend in ("plotly", "plt"):
        return rotor_plot_plotly(
            composition, x=x, y=y, t=t,
            color=color, color_by=color_by,
            line_width=linewidth, opacity=alpha,
            title=title, show=show, **kwargs,
        )
    else:
        raise ValueError(f"不支持的后端: {backend}，请使用 'matplotlib' 或 'plotly'")


# ============================================================
# Rotor 链可视化（本轮演示）
# ============================================================

def plot_rotor_chain(
    composition,
    t_value: float = 0,
    backend: str = "matplotlib",
    ax=None,
    show_trace: bool = True,
    n_trace: int = 2000,
):
    """
    绘制 Rotor 链（本轮可视化）

    展示每个 Rotor 的"本轮"圆和当前位置，
    直观显示运动叠加的几何过程。

    参数:
        composition: RotorComposition
        t_value: 当前时刻
        show_trace: 是否同时绘制完整轨迹
        n_trace: 轨迹采样点数
    """
    from .rotor2d import Rotor2D, RotorComposition
    from .trace import trace

    if isinstance(composition, Rotor2D):
        composition = RotorComposition([composition])

    if backend in ("matplotlib", "mpl"):
        import matplotlib.pyplot as plt

        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(8, 8))

        # 绘制完整轨迹
        if show_trace:
            t, x, y = trace(composition, n_points=n_trace)
            ax.plot(x, y, "gray", lw=0.5, alpha=0.4)

        # 绘制每个 Rotor 的本轮
        pos = 0 + 0j
        colors = plt.cm.tab10(np.linspace(0, 1, len(composition)))

        for i, rotor in enumerate(composition):
            # 本轮圆
            theta = np.linspace(0, 2 * np.pi, 200)
            circle_x = pos.real + rotor.radius * np.cos(theta)
            circle_y = pos.imag + rotor.radius * np.sin(theta)
            ax.plot(circle_x, circle_y, "--", color=colors[i], lw=0.5, alpha=0.5)

            # 当前位置
            z = rotor.evaluate(t_value)
            ax.plot([pos.real, pos.real + z.real], [pos.imag, pos.imag + z.imag],
                    "-", color=colors[i], lw=1.5)

            # 标注
            ax.annotate(f"R{i+1}", (pos.real, pos.imag),
                       fontsize=8, color=colors[i], fontweight="bold")

            pos += z

        # 末端点
        ax.plot(pos.real, pos.imag, "ro", ms=6, zorder=5)
        ax.annotate("P(t)", (pos.real, pos.imag), fontsize=9, color="red",
                   xytext=(5, 5), textcoords="offset points")

        ax.set_aspect("equal")
        ax.grid(True, alpha=0.2)
        ax.set_title(f"Rotor Chain at t = {t_value:.3f}", fontsize=12)

        if show_trace:
            ax.axis("off")
        plt.tight_layout()
        plt.show()

        return ax

    else:
        raise NotImplementedError("plotly 后端暂未实现 rotor_chain")

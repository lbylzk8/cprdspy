"""
plot3d.py — 3D/nD Rotor 曲线可视化

支持 matplotlib 3D 和 plotly 3D 双后端。

功能:
    - rotor_plot_3d(): 快速绘制 3D Rotor 曲线
    - rotor_plot_3d_mpl(): matplotlib 3D 静态图
    - rotor_plot_3d_plotly(): plotly 3D 交互图
    - 支持按曲率/弧长着色

作者: cprdspy team
"""

import numpy as np
from typing import Optional


# ============================================================
# matplotlib 3D 后端
# ============================================================

def rotor_plot_3d_mpl(
    composition=None,
    coords=None,
    t=None,
    color="b",
    color_by=None,
    linewidth=1.5,
    alpha=1.0,
    title=None,
    figsize=(10, 10),
    plot=True,
    **kwargs,
):
    """
    matplotlib 3D 绘制 Rotor 曲线

    参数:
        composition: Rotor3D, Rotor3DComposition, RotorClifford, RotorCliffordComposition
        coords: (x, y, z) 坐标元组（如果 composition 为 None）
        color_by: None | 'curvature' | 'arc_length'
        cmap: 颜色映射（默认 'viridis'）
    """
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    from .trace import trace_nd, compute_curvature_nd, arc_length_nd

    # 采样
    if coords is None:
        if composition is None:
            raise ValueError("需要提供 composition 或 coords")
        result = trace_nd(composition)
        t = result[0]
        coords = result[1:]

    x, y, z = coords[0], coords[1], coords[2]

    # 颜色数据
    if color_by == "curvature":
        c = compute_curvature_nd(*coords, t=t)
        c_label = "κ curvature"
    elif color_by == "arc_length":
        c = arc_length_nd(*coords, t=t)
        c_label = "s arc length"
    else:
        c = None
        c_label = ""

    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection='3d')

    if c is not None:
        # 按颜色着色（使用 scatter 模拟）
        cmap = kwargs.get('cmap', 'viridis')
        scatter = ax.scatter(x, y, z, c=c, cmap=cmap, s=linewidth*2, alpha=alpha)
        plt.colorbar(scatter, ax=ax, label=c_label, shrink=0.6)
    else:
        ax.plot(x, y, z, color=color, lw=linewidth, alpha=alpha)

    ax.set_title(title or "3D Rotor Curve", fontsize=14)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    if plot:
        plt.tight_layout()
        plt.show()

    return ax


# ============================================================
# plotly 3D 后端
# ============================================================

def rotor_plot_3d_plotly(
    composition=None,
    coords=None,
    t=None,
    color=None,
    color_by=None,
    colorscale="Viridis",
    line_width=3,
    opacity=1.0,
    title=None,
    show=True,
    dark=True,
):
    """
    plotly 3D 交互绘制 Rotor 曲线

    参数:
        composition: Rotor3D, Rotor3DComposition, RotorClifford, RotorCliffordComposition
        color_by: None | 'curvature' | 'arc_length'
        colorscale: plotly 颜色标度
        dark: 是否使用深色主题
    """
    import plotly.graph_objects as go
    from .trace import trace_nd, compute_curvature_nd, arc_length_nd

    # 采样
    if coords is None:
        if composition is None:
            raise ValueError("需要提供 composition 或 coords")
        result = trace_nd(composition)
        t = result[0]
        coords = result[1:]

    x, y, z = coords[0], coords[1], coords[2]

    # 颜色数据
    if color_by == "curvature":
        c = compute_curvature_nd(*coords, t=t)
        c_label = "κ curvature"
    elif color_by == "arc_length":
        c = arc_length_nd(*coords, t=t)
        c_label = "s arc length"
    else:
        c = None
        c_label = ""

    # 构建 trace
    if c is not None:
        # 分段着色
        max_segments = 500
        step = max(1, len(x) // max_segments)
        indices = list(range(0, len(x), step))
        if indices[-1] != len(x) - 1:
            indices.append(len(x) - 1)

        c_min, c_max = c.min(), c.max()
        c_norm = (c - c_min) / (c_max - c_min + 1e-15)

        import matplotlib.pyplot as plt
        cmap = plt.get_cmap(colorscale if colorscale != "Viridis" else "viridis")

        traces = []
        for i in range(len(indices) - 1):
            idx_start = indices[i]
            idx_end = indices[i + 1]
            seg_color = cmap(c_norm[idx_start])
            hex_color = f"rgb({int(seg_color[0]*255)},{int(seg_color[1]*255)},{int(seg_color[2]*255)})"

            seg_trace = go.Scatter3d(
                x=x[idx_start:idx_end+1],
                y=y[idx_start:idx_end+1],
                z=z[idx_start:idx_end+1],
                mode="lines",
                line=dict(color=hex_color, width=line_width),
                opacity=opacity,
                showlegend=False,
                hovertemplate="x: %{x:.3f}<br>y: %{y:.3f}<br>z: %{z:.3f}<extra></extra>",
            )
            traces.append(seg_trace)

        # 添加 colorbar
        colorbar_trace = go.Scatter3d(
            x=[None], y=[None], z=[None],
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
        trace_data = go.Scatter3d(
            x=x, y=y, z=z,
            mode="lines",
            line=dict(color=color or "blue", width=line_width),
            opacity=opacity,
            hovertemplate="x: %{x:.3f}<br>y: %{y:.3f}<br>z: %{z:.3f}<extra></extra>",
        )
        traces = [trace_data]

    layout = go.Layout(
        title=title or "3D Rotor Curve",
        scene=dict(
            xaxis=dict(title='X', visible=False),
            yaxis=dict(title='Y', visible=False),
            zaxis=dict(title='Z', visible=False),
        ),
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

def rotor_plot_3d(
    composition=None,
    backend="matplotlib",
    coords=None,
    t=None,
    color="b",
    color_by=None,
    linewidth=1.5,
    alpha=1.0,
    title=None,
    figsize=(10, 10),
    show=True,
    **kwargs,
):
    """
    统一 3D 绘图接口

    参数:
        composition: Rotor3D, Rotor3DComposition, RotorClifford, RotorCliffordComposition
        backend: 'matplotlib' | 'plotly' | 'mpl' | 'plt'
        color_by: None | 'curvature' | 'arc_length'
    """
    backend = backend.lower()
    if backend in ("matplotlib", "mpl"):
        return rotor_plot_3d_mpl(
            composition, coords=coords, t=t,
            color=color, linewidth=linewidth, alpha=alpha,
            color_by=color_by, title=title, figsize=figsize,
            plot=show, **kwargs,
        )
    elif backend in ("plotly", "plt"):
        return rotor_plot_3d_plotly(
            composition, coords=coords, t=t,
            color=color, color_by=color_by,
            line_width=linewidth, opacity=alpha,
            title=title, show=show, **kwargs,
        )
    else:
        raise ValueError(f"不支持的后端: {backend}，请使用 'matplotlib' 或 'plotly'")

import plotly.graph_objects as go
import numpy as np
from ..Circles.circle import concentric_circles


def wave_ari(
    A=1,
    F=3,
    P=12,
    rotation=0,
    direction="both",
    color="#0f0",
    alpha=1,
    R=1,
    center=(0, 0),
    points=1000,
    line_width=1,
    show_center=True,
    **kwargs,
):
    """
    绘制等差波形。
    """
    traces = []
    for i in range(P + 1):
        circle_traces = concentric_circles(
            center=(
                center[0] + np.cos(i * 2 * np.pi / P + np.pi / 2 + rotation),
                center[1] + np.sin(i * 2 * np.pi / P + np.pi / 2 + rotation),
            ),
            n=F,
            radius=R,
            param=A,
            mode="arithmetic",
            direction=direction,
            color=color,
            alpha=alpha,
            points=points,
            line_width=line_width,
            show_center=show_center,
            **kwargs,
        )
        traces.extend(circle_traces)
    return traces


def wave_geo(
    A=1,
    F=3,
    P=12,
    rotation=0,
    direction="both",
    color="#0f0",
    alpha=1,
    R=1,
    center=(0, 0),
    points=1000,
    line_width=1,
    show_center=True,
    **kwargs,
):
    """
    绘制等比波形。
    """
    traces = []
    for i in range(P + 1):
        circle_traces = concentric_circles(
            center=(
                center[0] + np.cos(i * 2 * np.pi / P + np.pi / 2 + rotation),
                center[1] + np.sin(i * 2 * np.pi / P + np.pi / 2 + rotation),
            ),
            n=F,
            radius=R,
            param=A,
            mode="geometric",
            direction=direction,
            color=color,
            alpha=alpha,
            points=points,
            line_width=line_width,
            show_center=show_center,
            **kwargs,
        )
        traces.extend(circle_traces)
    return traces


def wave(
    A=1,
    F=3,
    P=12,
    rotation=0,
    mode="geometric",
    direction="both",
    color="#0f0",
    alpha=1,
    R=1,
    center=(0, 0),
    points=1000,
    line_width=1,
    show_center=True,
    **kwargs,
):
    """
    绘制波形（通用）。
    """
    traces = []
    for i in range(P + 1):
        circle_traces = concentric_circles(
            center=(
                center[0] + np.cos(i * 2 * np.pi / P + np.pi / 2 + rotation),
                center[1] + np.sin(i * 2 * np.pi / P + np.pi / 2 + rotation),
            ),
            n=F,
            radius=R,
            param=A,
            mode=mode,
            direction=direction,
            color=color,
            alpha=alpha,
            points=points,
            line_width=line_width,
            show_center=show_center,
            **kwargs,
        )
        traces.extend(circle_traces)
    return traces


def wave_wave(
    A=1,
    F=3,
    P=12,
    rotation=0,
    mode="geometric",
    direction="both",
    color="#0f0",
    alpha=1,
    R=1,
    center=(0, 0),
    points=1000,
    line_width=1,
    show_center=True,
    **kwargs,
):
    """
    绘制嵌套波形。
    """
    traces = []
    for i in range(P + 1):
        wave_traces = wave(
            A=A,
            F=F,
            P=P,
            rotation=rotation,
            mode=mode,
            direction=direction,
            color=color,
            alpha=alpha,
            R=R,
            center=(
                center[0] + np.cos(i * 2 * np.pi / P + np.pi / 2 + rotation),
                center[1] + np.sin(i * 2 * np.pi / P + np.pi / 2 + rotation),
            ),
            points=points,
            line_width=line_width,
            show_center=show_center,
            **kwargs,
        )
        traces.extend(wave_traces)
    return traces

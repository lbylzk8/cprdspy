import plotly.graph_objects as go
import numpy as np
from ..Circles.circle import concentric_circles, concentric_circles_fill


def wave_ari(
    A=1,
    F=3,
    P=12,
    rotation=0,
    use_degree=True,
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
    """等差波形。

    rotation (float): 旋转角度（度或弧度取决于 use_degree）。
    use_degree (bool): 默认 True（度）。

    返回:
        list: 包含所有轨迹的列表。
    """
    rot_rad = np.deg2rad(rotation) if use_degree else rotation
    traces = []
    for i in range(P + 1):
        circle_traces = concentric_circles(
            center=(
                center[0] + np.cos(i * 2 * np.pi / P + np.pi / 2 + rot_rad),
                center[1] + np.sin(i * 2 * np.pi / P + np.pi / 2 + rot_rad),
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


def wave_ari_fill(
    A=1,
    F=3,
    P=12,
    rotation=0,
    use_degree=True,
    direction="both",
    color="#0f0",
    alpha=1,
    fill_color=None,
    fill_alpha=0.3,
    edge_color=None,
    edge_width=None,
    R=1,
    center=(0, 0),
    points=1000,
    line_width=1,
    show_center=True,
    **kwargs,
):
    """带填充的等差波形。

    新增参数:
        fill_color, fill_alpha, edge_color, edge_width
    其余参数同 wave_ari。

    返回:
        list: 包含所有轨迹的列表。
    """
    rot_rad = np.deg2rad(rotation) if use_degree else rotation
    traces = []
    for i in range(P + 1):
        circle_traces = concentric_circles_fill(
            center=(
                center[0] + np.cos(i * 2 * np.pi / P + np.pi / 2 + rot_rad),
                center[1] + np.sin(i * 2 * np.pi / P + np.pi / 2 + rot_rad),
            ),
            n=F,
            radius=R,
            param=A,
            mode="arithmetic",
            direction=direction,
            color=color,
            alpha=alpha,
            fill_color=fill_color,
            fill_alpha=fill_alpha,
            edge_color=edge_color,
            edge_width=edge_width,
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
    use_degree=True,
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
    """等比波形。

    rotation (float): 旋转角度（度或弧度取决于 use_degree）。
    use_degree (bool): 默认 True（度）。

    返回:
        list: 包含所有轨迹的列表。
    """
    rot_rad = np.deg2rad(rotation) if use_degree else rotation
    traces = []
    for i in range(P + 1):
        circle_traces = concentric_circles(
            center=(
                center[0] + np.cos(i * 2 * np.pi / P + np.pi / 2 + rot_rad),
                center[1] + np.sin(i * 2 * np.pi / P + np.pi / 2 + rot_rad),
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


def wave_geo_fill(
    A=1,
    F=3,
    P=12,
    rotation=0,
    use_degree=True,
    direction="both",
    color="#0f0",
    alpha=1,
    fill_color=None,
    fill_alpha=0.3,
    edge_color=None,
    edge_width=None,
    R=1,
    center=(0, 0),
    points=1000,
    line_width=1,
    show_center=True,
    **kwargs,
):
    """带填充的等比波形。

    新增参数:
        fill_color, fill_alpha, edge_color, edge_width
    其余参数同 wave_geo。

    返回:
        list: 包含所有轨迹的列表。
    """
    rot_rad = np.deg2rad(rotation) if use_degree else rotation
    traces = []
    for i in range(P + 1):
        circle_traces = concentric_circles_fill(
            center=(
                center[0] + np.cos(i * 2 * np.pi / P + np.pi / 2 + rot_rad),
                center[1] + np.sin(i * 2 * np.pi / P + np.pi / 2 + rot_rad),
            ),
            n=F,
            radius=R,
            param=A,
            mode="geometric",
            direction=direction,
            color=color,
            alpha=alpha,
            fill_color=fill_color,
            fill_alpha=fill_alpha,
            edge_color=edge_color,
            edge_width=edge_width,
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
    use_degree=True,
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
    """统一波形函数。

    rotation (float): 旋转角度（度或弧度取决于 use_degree）。
    use_degree (bool): 默认 True（度）。

    返回:
        list: 包含所有轨迹的列表。
    """
    rot_rad = np.deg2rad(rotation) if use_degree else rotation
    traces = []
    for i in range(P + 1):
        circle_traces = concentric_circles(
            center=(
                center[0] + np.cos(i * 2 * np.pi / P + np.pi / 2 + rot_rad),
                center[1] + np.sin(i * 2 * np.pi / P + np.pi / 2 + rot_rad),
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


def wave_fill(
    A=1,
    F=3,
    P=12,
    rotation=0,
    use_degree=True,
    mode="geometric",
    direction="both",
    color="#0f0",
    alpha=1,
    fill_color=None,
    fill_alpha=0.3,
    edge_color=None,
    edge_width=None,
    R=1,
    center=(0, 0),
    points=1000,
    line_width=1,
    show_center=True,
    **kwargs,
):
    """带填充的统一波形函数。

    新增参数:
        fill_color, fill_alpha, edge_color, edge_width
    其余参数同 wave。

    返回:
        list: 包含所有轨迹的列表。
    """
    rot_rad = np.deg2rad(rotation) if use_degree else rotation
    traces = []
    for i in range(P + 1):
        circle_traces = concentric_circles_fill(
            center=(
                center[0] + np.cos(i * 2 * np.pi / P + np.pi / 2 + rot_rad),
                center[1] + np.sin(i * 2 * np.pi / P + np.pi / 2 + rot_rad),
            ),
            n=F,
            radius=R,
            param=A,
            mode=mode,
            direction=direction,
            color=color,
            alpha=alpha,
            fill_color=fill_color,
            fill_alpha=fill_alpha,
            edge_color=edge_color,
            edge_width=edge_width,
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
    use_degree=True,
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
    """简化波形函数。

    rotation (float): 旋转角度（度或弧度取决于 use_degree）。
    use_degree (bool): 默认 True（度）。

    返回:
        list: 包含所有轨迹的列表。
    """
    rot_rad = np.deg2rad(rotation) if use_degree else rotation
    traces = []
    for i in range(P + 1):
        wave_traces = wave(
            A=A,
            F=F,
            P=P,
            rotation=rot_rad,
            use_degree=False,
            mode=mode,
            direction=direction,
            color=color,
            alpha=alpha,
            R=R,
            center=(
                center[0] + np.cos(i * 2 * np.pi / P + np.pi / 2 + rot_rad),
                center[1] + np.sin(i * 2 * np.pi / P + np.pi / 2 + rot_rad),
            ),
            points=points,
            line_width=line_width,
            show_center=show_center,
            **kwargs,
        )
        traces.extend(wave_traces)
    return traces


def wave_wave_fill(
    A=1,
    F=3,
    P=12,
    rotation=0,
    use_degree=True,
    mode="geometric",
    direction="both",
    color="#0f0",
    alpha=1,
    fill_color=None,
    fill_alpha=0.3,
    edge_color=None,
    edge_width=None,
    R=1,
    center=(0, 0),
    points=1000,
    line_width=1,
    show_center=True,
    **kwargs,
):
    """带填充的简化波形函数（wave of wave_fill）。

    新增参数:
        fill_color, fill_alpha, edge_color, edge_width
    其余参数同 wave_wave。

    返回:
        list: 包含所有轨迹的列表。
    """
    rot_rad = np.deg2rad(rotation) if use_degree else rotation
    traces = []
    for i in range(P + 1):
        wave_traces = wave_fill(
            A=A,
            F=F,
            P=P,
            rotation=rot_rad,
            use_degree=False,
            mode=mode,
            direction=direction,
            color=color,
            alpha=alpha,
            fill_color=fill_color,
            fill_alpha=fill_alpha,
            edge_color=edge_color,
            edge_width=edge_width,
            R=R,
            center=(
                center[0] + np.cos(i * 2 * np.pi / P + np.pi / 2 + rot_rad),
                center[1] + np.sin(i * 2 * np.pi / P + np.pi / 2 + rot_rad),
            ),
            points=points,
            line_width=line_width,
            show_center=show_center,
            **kwargs,
        )
        traces.extend(wave_traces)
    return traces


__all__ = [
    "wave",
    "wave_fill",
    "wave_wave",
    "wave_wave_fill",
    "wave_ari",
    "wave_ari_fill",
    "wave_geo",
    "wave_geo_fill",
]

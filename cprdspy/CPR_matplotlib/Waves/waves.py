import matplotlib.pyplot as plt
import numpy as np
import sys
import os

from ..Arcs.arc import *
from ..Circles.circle import *

# from cprdspy.CPR_matplotlib.Arcs.arc import *

# # 方法 1: 使用相对导入（推荐用于包结构）
# from cprdspy.CPR_matplotlib.Circles.circle import *

# 方法 2: 使用 sys.path 绝对导入（适用于 Jupyter Notebook 或直接运行）
# 获取当前文件所在目录的父目录（CPR_matplotlib 目录）
# current_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.dirname(current_dir)
# sys.path.insert(0, parent_dir)

# # 现在可以使用绝对导入
# from Circles.circle import *


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
    linestyle="-",
    linewidth=1,
    ax=None,
    show_center=True,
    **kwargs,
):
    """等差波形。

    rotation (float): 旋转角度（度或弧度取决于 use_degree）。
    use_degree (bool): 默认 True（度）。
    """
    rot_rad = np.deg2rad(rotation) if use_degree else rotation
    for i in range(P + 1):
        concentric_circles(
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
            linestyle=linestyle,
            linewidth=linewidth,
            ax=ax,
            show_center=show_center,
            **kwargs,
        )


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
    linestyle="-",
    linewidth=1,
    ax=None,
    show_center=True,
    **kwargs,
):
    """等比波形。

    rotation (float): 旋转角度（度或弧度取决于 use_degree）。
    use_degree (bool): 默认 True（度）。
    """
    rot_rad = np.deg2rad(rotation) if use_degree else rotation
    for i in range(P + 1):
        concentric_circles(
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
            linestyle=linestyle,
            linewidth=linewidth,
            ax=ax,
            show_center=show_center,
            **kwargs,
        )


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
    linestyle="-",
    linewidth=1,
    ax=None,
    show_center=True,
    **kwargs,
):
    """统一波形函数。

    rotation (float): 旋转角度（度或弧度取决于 use_degree）。
    use_degree (bool): 默认 True（度）。
    """
    rot_rad = np.deg2rad(rotation) if use_degree else rotation
    for i in range(P + 1):
        concentric_circles(
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
            linestyle=linestyle,
            linewidth=linewidth,
            ax=ax,
            show_center=show_center,
            **kwargs,
        )


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
    linestyle="-",
    linewidth=1,
    ax=None,
    show_center=True,
    **kwargs,
):
    """简化波形函数。

    rotation (float): 旋转角度（度或弧度取决于 use_degree）。
    use_degree (bool): 默认 True（度）。
    """
    rot_rad = np.deg2rad(rotation) if use_degree else rotation
    for i in range(P + 1):
        wave(
            A=A, F=F, P=P,
            rotation=rot_rad, use_degree=False,
            mode=mode, direction=direction,
            color=color, alpha=alpha, R=R,
            center=(
                center[0] + np.cos(i * 2 * np.pi / P + np.pi / 2 + rot_rad),
                center[1] + np.sin(i * 2 * np.pi / P + np.pi / 2 + rot_rad),
            ),
            points=points, linestyle=linestyle, linewidth=linewidth,
            ax=ax, show_center=show_center, **kwargs,
        )

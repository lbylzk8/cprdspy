import numpy as np
import matplotlib.pyplot as plt
from cprdspy.CPR_matplotlib.Flowers.flower import *


def star(
    R=1,
    r=1,
    n=4,
    N=12,
    rotation=0,
    use_degree=True,
    color="#0F0",
    alpha=1,
    center=(0, 0),
    linestyle="-",
    linewidth=1,
    edgecolor="black",
    edgealpha=1,
    ax=None,
    points=4,
    **kwargs,
):
    """绘制星形图案。

    rotation (float): 旋转角度（度或弧度取决于 use_degree）。
    use_degree (bool): 默认 True（度）。
    """
    flower(
        R, r, n, N,
        rotation,
        color, alpha, center,
        points, linestyle, linewidth,
        use_degree=use_degree,
        **kwargs,
    )


def stars(
    R=1,
    r=1,
    n=4,
    ratio=np.sqrt(2),
    M=3,
    N=12,
    color="#0F0",
    alpha=1,
    rotation=0,
    use_degree=True,
    center=(0, 0),
    linestyle="-",
    linewidth=1,
    edgecolor="black",
    edgealpha=1,
    ax=None,
    points=4,
    **kwargs,
):
    """绘制多层星形图案。

    rotation (float): 旋转角度（度或弧度取决于 use_degree）。
    use_degree (bool): 默认 True（度）。
    """
    flowers(
        R, r, n, ratio, M, N,
        color, alpha, rotation,
        center, points, linestyle, linewidth,
        use_degree=use_degree,
        **kwargs,
    )

import numpy as np
from ..Flowers.flower import flower, flowers


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
    line_width=1,
    points=4,
    **kwargs,
):
    """绘制星形图案。

    rotation (float): 旋转角度（度或弧度取决于 use_degree）。
    use_degree (bool): 默认 True（度）。

    返回:
        list: 包含所有花瓣轨迹的列表。
    """
    return flower(
        R, r, n, N,
        rotation=rotation,
        color=color, alpha=alpha, center=center,
        points=points, line_width=line_width,
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
    line_width=1,
    points=4,
    **kwargs,
):
    """绘制多层星形图案。

    rotation (float): 旋转角度（度或弧度取决于 use_degree）。
    use_degree (bool): 默认 True（度）。

    返回:
        list: 包含所有花瓣轨迹的列表。
    """
    return flowers(
        R, r, n, ratio, M, N,
        color=color, alpha=alpha, theta=rotation,
        center=center, points=points, line_width=line_width,
        use_degree=use_degree,
        **kwargs,
    )


__all__ = [
    "star",
    "stars",
]

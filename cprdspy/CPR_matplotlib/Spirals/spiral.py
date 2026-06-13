import matplotlib.pyplot as plt
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
    linewidth=1.0,
    use_degree=True,
):
    """绘制广义对数螺线。

    参数:
        n: 花瓣/对称数（影响基底 cos(pi/n)）
        a, b: x/y 方向缩放（可做椭圆化）
        cyc: 周期数（每个周期为 2π）
        color: 线颜色（传给 matplotlib）
        theta: 全局相位偏移（度或弧度取决于 use_degree）
        rotation: 额外角度偏移（度或弧度取决于 use_degree）
        direction: 'both'|'in'|'out' 控制绘制方向
        alpha: 透明度
        linewidth: 线宽
        use_degree (bool): theta 和 rotation 是否使用角度制，默认 True（度）。
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

    plt.plot(x, y, color=color, alpha=alpha, linewidth=linewidth)
    plt.axis("equal")


def nSpiral(
    n=4,
    a=1,
    N=4,
    cyc=0.5,
    color="b",
    theta=0,
    rotation=0,
    direction="both",
    linewidth=1.0,
    use_degree=True,
):
    """n 边形螺旋。

    theta, rotation: 度或弧度取决于 use_degree。
    use_degree (bool): 默认 True（度）。
    """
    theta_rad = np.deg2rad(theta) if use_degree else theta
    rot_rad = np.deg2rad(rotation) if use_degree else rotation
    for i in range(N):
        logSpiral(n, a, 1, cyc, color, theta_rad + i * 2 * np.pi / N, rot_rad,
                  direction, 1, linewidth, use_degree=False)
        logSpiral(n, a, 1, cyc, color, -theta_rad + i * 2 * np.pi / N, -rot_rad,
                  direction, 1, linewidth, use_degree=False)


def nSpirals(
    n=4,
    N=4,
    cyc=0.5,
    color="b",
    theta=0,
    rotation=0,
    direction="both",
    linewidth=1.0,
    use_degree=True,
):
    """多头 n 边形螺旋。

    theta, rotation: 度或弧度取决于 use_degree。
    use_degree (bool): 默认 True（度）。
    """
    theta_rad = np.deg2rad(theta) if use_degree else theta
    rot_rad = np.deg2rad(rotation) if use_degree else rotation
    for i in range(N):
        logSpiral(n, 1, 1, cyc, color, theta_rad + i * 2 * np.pi / N, rot_rad,
                  direction, 1, linewidth, use_degree=False)
        logSpiral(n, -1, 1, cyc, color, -theta_rad + i * 2 * np.pi / N, -rot_rad,
                  direction, 1, linewidth, use_degree=False)


def calla_petal(
    n=4,
    a=1,
    cyc=1.25,
    theta=0,
    color="b",
    rotation=0,
    direction="both",
    linewidth=1.0,
    use_degree=True,
):
    """马蹄莲花瓣。

    theta, rotation: 度或弧度取决于 use_degree。
    use_degree (bool): 默认 True（度）。
    """
    theta_rad = np.deg2rad(theta) if use_degree else theta
    rot_rad = np.deg2rad(rotation) if use_degree else rotation
    logSpiral(n, a, 1, cyc, color, theta_rad, rot_rad, direction, 1, linewidth, use_degree=False)
    logSpiral(n, -a, 1, cyc, color, -theta_rad, -rot_rad, direction, 1, linewidth, use_degree=False)


def calla(
    n=4,
    a=1,
    cyc=1.25,
    N=12,
    theta=0,
    colors=["r", "g", "b"] * 4,
    rotation=0,
    direction="both",
    linewidth=1.0,
    use_degree=True,
):
    """完整马蹄莲。

    theta, rotation: 度或弧度取决于 use_degree。
    use_degree (bool): 默认 True（度）。
    """
    theta_rad = np.deg2rad(theta) if use_degree else theta
    rot_rad = np.deg2rad(rotation) if use_degree else rotation
    for i in range(N):
        calla_petal(n, a, cyc, theta_rad + i * 2 * np.pi / N, colors[i],
                    rot_rad, direction, linewidth, use_degree=False)


# def logSpiral_in_out(n, a, b, cyc, color="b", theta=0):
#     t = np.linspace(-cyc * 2 * np.pi, cyc * 2 * np.pi, 1000)
#     x = a * (np.cos(np.pi / n)) ** (-n * t / np.pi) * np.cos(t + theta)
#     y = b * (np.cos(np.pi / n)) ** (-n * t / np.pi) * np.sin(t + theta)
#     plt.plot(x, y, color)
#     plt.axis("equal")


# def logSpiral_out(n, a, b, cyc, color="b", theta=0):
#     t = np.linspace(0, cyc * 2 * np.pi, 100)
#     x = a * (np.cos(np.pi / n)) ** (-n * t / np.pi) * np.cos(t + theta)
#     y = b * (np.cos(np.pi / n)) ** (-n * t / np.pi) * np.sin(t + theta)
#     plt.plot(x, y, color)


# def logSpiral_in(n, a, b, cyc, color="b", theta=0):
#     t = np.linspace(0, -cyc * 2 * np.pi, 100)
#     x = a * (np.cos(np.pi / n)) ** (-n * t / np.pi) * np.cos(t + theta)
#     y = b * (np.cos(np.pi / n)) ** (-n * t / np.pi) * np.sin(t + theta)
#     plt.plot(x, y, color)


# def n_spiral(n, cyc, color, theta=0):
#     for i in range(n):
#         logSpiral(n, 1, 1, cyc, color, theta + i * 2 * np.pi / n)
#         logSpiral(n, -1, 1, cyc, color, theta + i * 2 * np.pi / n)


# def n_spiral_rotate(n, cyc, color, alpha=0, theta=0):
#     for i in range(n):
#         logSpiral(n, 1, 1, cyc, color, alpha + theta + i * 2 * np.pi / n)
#         logSpiral(n, -1, 1, cyc, color, alpha - theta + i * 2 * np.pi / n)


# def n_spiral_rotate_out(n, cyc, color, theta=0):
#     for i in range(n):
#         logSpiral_out(n, 1, 1, cyc, color, theta + i * 2 * np.pi / n)
#         logSpiral_out(n, -1, 1, cyc, color, -theta + i * 2 * np.pi / n)


# def n_spiral_rotate_in(n, cyc, color, theta=0):
#     for i in range(n):
#         logSpiral_in(n, 1, 1, cyc, color, theta + i * 2 * np.pi / n)
#         logSpiral_in(n, -1, 1, cyc, color, -theta + i * 2 * np.pi / n)


# def calla_petal(n, cyc, theta, color):
#     logSpiral(n, 1, 1, cyc * 1.25, color, theta)
#     logSpiral(n, -1, 1, cyc * 1.25, color, -theta)


# def calla_by_petal(n, cyc, N, theta, colors):
#     for i in range(N):
#         calla_petal(n, cyc, theta + i * 2 * np.pi / N, colors[i])

"""
圆模块 — 圆的绘制与填充

提供圆、椭圆、同心圆、同心椭圆等基本图形的中文接口。
"""

import numpy as np
import matplotlib.pyplot as plt


# ======================== 圆 ========================

def 圆(
    半径=1,
    颜色='#0F0',
    透明度=1,
    圆心=(0, 0),
    点数=100,
    线型='-',
    线宽=1,
    标签=None,
    标记=None,
    标记大小=5,
    标记填充颜色='r',
    标记边缘颜色='k',
    标记边缘宽度=1,
    ax=None,
    **kwargs,
):
    """绘制一个圆。

    参数:
        半径 (float): 圆的半径，默认为1。
        颜色 (str): 圆的颜色，默认为绿色('#0F0')。
        透明度 (float): 透明度，默认为1。
        圆心 (tuple): 圆心坐标，默认为(0, 0)。
        点数 (int): 用于绘制圆的点数，默认为100。
        线型 (str): 线型，默认为实线('-')。
        线宽 (int): 线宽，默认为1。
        标签 (str): 图例标签。
        标记 (str): 标记样式。
        ax (matplotlib.axes.Axes): 目标坐标轴。
    """
    角 = np.linspace(0, 2 * np.pi, 点数)
    x = 圆心[0] + 半径 * np.cos(角)
    y = 圆心[1] + 半径 * np.sin(角)

    if ax is None:
        ax = plt.gca()

    line = ax.plot(
        x, y,
        color=颜色,
        alpha=透明度,
        linestyle=线型,
        linewidth=线宽,
        label=标签,
        marker=标记,
        markersize=标记大小,
        markerfacecolor=标记填充颜色,
        markeredgecolor=标记边缘颜色,
        markeredgewidth=标记边缘宽度,
        **kwargs,
    )
    ax.axis("equal")
    return line[0] if line else None


def 圆_填充(
    半径=1,
    颜色='#0F0',
    透明度=1,
    填充颜色=None,
    填充透明度=0.3,
    边缘颜色=None,
    边缘宽度=None,
    边缘线型=None,
    圆心=(0, 0),
    点数=100,
    线型='-',
    线宽=1,
    标签=None,
    标记=None,
    标记大小=5,
    标记填充颜色='r',
    标记边缘颜色='k',
    标记边缘宽度=1,
    ax=None,
    **kwargs,
):
    """绘制一个带填充的圆。

    新增参数:
        填充颜色 (str): 填充颜色，默认回退到边缘颜色→颜色。
        填充透明度 (float): 填充透明度，默认0.3。
        边缘颜色 (str): 边缘线颜色，默认回退到颜色。
        边缘宽度 (float): 边缘线宽度，默认回退到线宽。
        边缘线型 (str): 边缘线样式，默认回退到线型。
    """
    角 = np.linspace(0, 2 * np.pi, 点数)
    x = 圆心[0] + 半径 * np.cos(角)
    y = 圆心[1] + 半径 * np.sin(角)

    if ax is None:
        ax = plt.gca()

    fc = 填充颜色 if 填充颜色 is not None else (边缘颜色 if 边缘颜色 is not None else 颜色)
    ec = 边缘颜色 if 边缘颜色 is not None else 颜色
    ew = 边缘宽度 if 边缘宽度 is not None else 线宽
    es = 边缘线型 if 边缘线型 is not None else 线型

    ax.fill(x, y, color=fc, alpha=填充透明度, linewidth=0)
    ax.plot(
        x, y,
        color=ec, alpha=透明度, linestyle=es, linewidth=ew,
        marker=标记, markersize=标记大小,
        markerfacecolor=标记填充颜色, markeredgecolor=标记边缘颜色,
        markeredgewidth=标记边缘宽度, label=标签,
        **kwargs,
    )
    ax.axis("equal")
    if 标签:
        ax.legend()


def 圆_p(圆心, 点, 颜色='b'):
    """通过圆心和圆上一点画圆。

    参数:
        圆心 (tuple): 圆心坐标。
        点 (tuple): 圆上一点坐标。
        颜色 (str): 颜色。
    """
    半径 = np.sqrt((点[0] - 圆心[0]) ** 2 + (点[1] - 圆心[1]) ** 2)
    旋转角 = np.linspace(0, 2 * np.pi, 100)
    x = 圆心[0] + 半径 * np.cos(旋转角)
    y = 圆心[1] + 半径 * np.sin(旋转角)
    plt.axis("equal")
    plt.plot(x, y, 颜色)


# ======================== 椭圆 ========================

def 椭圆(
    a=2, b=1, 旋转=0, 使用角度制=True,
    颜色='#0f0', 透明度=1,
    圆心=(0, 0), 点数=1000,
    **kwargs,
):
    """绘制椭圆。

    参数:
        a (float): 半长轴。
        b (float): 半短轴。
        旋转 (float): 旋转角度（度或弧度取决于使用角度制）。
        使用角度制 (bool): 旋转是否使用角度制。
    """
    角 = np.linspace(0, 2 * np.pi, 点数)
    旋转角弧度 = np.deg2rad(旋转) if 使用角度制 else 旋转
    x = (
        a * np.cos(角) * np.cos(旋转角弧度)
        - b * np.sin(角) * np.sin(旋转角弧度)
        + 圆心[0]
    )
    y = (
        a * np.cos(角) * np.sin(旋转角弧度)
        + b * np.sin(角) * np.cos(旋转角弧度)
        + 圆心[1]
    )
    plt.plot(x, y, 颜色, alpha=透明度, **kwargs)
    plt.axis("equal")


def 椭圆_填充(
    a=2, b=1, 旋转=0, 使用角度制=True,
    颜色='#0f0', 透明度=1,
    填充颜色=None, 填充透明度=0.3,
    边缘颜色=None, 边缘宽度=None, 边缘线型=None,
    圆心=(0, 0), 点数=1000,
    线型='-', 线宽=1, 标签=None,
    ax=None,
    **kwargs,
):
    """绘制一个带填充的椭圆。"""
    角 = np.linspace(0, 2 * np.pi, 点数)
    旋转角弧度 = np.deg2rad(旋转) if 使用角度制 else 旋转
    x = (
        a * np.cos(角) * np.cos(旋转角弧度)
        - b * np.sin(角) * np.sin(旋转角弧度)
        + 圆心[0]
    )
    y = (
        a * np.cos(角) * np.sin(旋转角弧度)
        + b * np.sin(角) * np.cos(旋转角弧度)
        + 圆心[1]
    )

    if ax is None:
        ax = plt.gca()

    fc = 填充颜色 if 填充颜色 is not None else (边缘颜色 if 边缘颜色 is not None else 颜色)
    ec = 边缘颜色 if 边缘颜色 is not None else 颜色
    ew = 边缘宽度 if 边缘宽度 is not None else 线宽
    es = 边缘线型 if 边缘线型 is not None else 线型

    ax.fill(x, y, color=fc, alpha=填充透明度, linewidth=0)
    ax.plot(x, y, color=ec, alpha=透明度, linestyle=es, linewidth=ew, label=标签, **kwargs)
    ax.axis("equal")
    if 标签:
        ax.legend()


# ======================== 同心圆 ========================

def 同心圆(
    圆心=(0, 0),
    n=3,
    半径=1,
    参数=0.5,
    模式='等差',
    方向='双向',
    颜色='#0F0',
    标记='o',
    透明度=1,
    点数=200,
    线型='-',
    线宽=1,
    ax=None,
    显示圆心=True,
    **kwargs,
):
    """绘制同心圆（兼容等差与等比序列）。

    参数:
        圆心 (tuple): 圆心坐标。
        n (int): 每一侧的圈数。
        半径 (float): 基准半径。
        参数 (float): 等差时为公差d；等比时为公比q。
        模式 (str): '等差' 或 '等比'。
        方向 (str): '双向'|'向外'|'向内'。
    """
    if ax is None:
        ax = plt.gca()

    if 显示圆心:
        ax.plot(圆心[0], 圆心[1], marker=标记, color=颜色)

    半径列表 = []

    if 模式 == '等差':
        d = float(参数)
        if 方向 == '双向':
            for i in range(1, n + 1):
                半径列表.append(半径 + i * d)
                半径列表.append(半径 - i * d)
        elif 方向 == '向外':
            for i in range(1, n + 1):
                半径列表.append(半径 + i * d)
        elif 方向 == '向内':
            for i in range(1, n + 1):
                半径列表.append(半径 - i * d)
    elif 模式 == '等比':
        q = float(参数)
        if q == 0:
            raise ValueError("等比模式下参数不能为0")
        if 方向 == '双向':
            for i in range(1, n + 1):
                半径列表.append(半径 * (q ** i))
                半径列表.append(半径 / (q ** i))
        elif 方向 == '向外':
            for i in range(1, n + 1):
                半径列表.append(半径 * (q ** i))
        elif 方向 == '向内':
            for i in range(1, n + 1):
                半径列表.append(半径 / (q ** i))

    半径列表 = [r for r in 半径列表 if r > 0]
    半径列表.append(半径)
    半径列表 = sorted(set(半径列表))

    for r in 半径列表:
        角 = np.linspace(0, 2 * np.pi, 点数)
        x = 圆心[0] + r * np.cos(角)
        y = 圆心[1] + r * np.sin(角)
        ax.plot(x, y, color=颜色, alpha=透明度, linestyle=线型, linewidth=线宽, **kwargs)

    ax.axis("equal")


def 同心圆_填充(
    圆心=(0, 0),
    n=3,
    半径=1,
    参数=0.5,
    模式='等差',
    方向='双向',
    颜色='#0F0',
    透明度=1,
    填充颜色=None,
    填充透明度=0.3,
    边缘颜色=None,
    边缘宽度=None,
    边缘线型=None,
    标记='o',
    点数=200,
    线型='-',
    线宽=1,
    ax=None,
    显示圆心=True,
    **kwargs,
):
    """绘制带填充的同心圆。"""
    if ax is None:
        ax = plt.gca()

    if 显示圆心:
        ax.plot(圆心[0], 圆心[1], marker=标记, color=颜色)

    半径列表 = []

    if 模式 == '等差':
        d = float(参数)
        if 方向 == '双向':
            for i in range(1, n + 1):
                半径列表.append(半径 + i * d)
                半径列表.append(半径 - i * d)
        elif 方向 == '向外':
            for i in range(1, n + 1):
                半径列表.append(半径 + i * d)
        elif 方向 == '向内':
            for i in range(1, n + 1):
                半径列表.append(半径 - i * d)
    elif 模式 == '等比':
        q = float(参数)
        if q == 0:
            raise ValueError("等比模式下参数不能为0")
        if 方向 == '双向':
            for i in range(1, n + 1):
                半径列表.append(半径 * (q ** i))
                半径列表.append(半径 / (q ** i))
        elif 方向 == '向外':
            for i in range(1, n + 1):
                半径列表.append(半径 * (q ** i))
        elif 方向 == '向内':
            for i in range(1, n + 1):
                半径列表.append(半径 / (q ** i))

    半径列表 = [r for r in 半径列表 if r > 0]
    半径列表.append(半径)
    半径列表 = sorted(set(半径列表))

    fc = 填充颜色 if 填充颜色 is not None else (边缘颜色 if 边缘颜色 is not None else 颜色)
    ec = 边缘颜色 if 边缘颜色 is not None else 颜色
    ew = 边缘宽度 if 边缘宽度 is not None else 线宽
    es = 边缘线型 if 边缘线型 is not None else 线型

    # 从大到小填充
    for r in sorted(半径列表, reverse=True):
        角 = np.linspace(0, 2 * np.pi, 点数)
        x = 圆心[0] + r * np.cos(角)
        y = 圆心[1] + r * np.sin(角)
        ax.fill(x, y, color=fc, alpha=填充透明度, linewidth=0)

    # 所有同心圆边线
    for r in 半径列表:
        角 = np.linspace(0, 2 * np.pi, 点数)
        x = 圆心[0] + r * np.cos(角)
        y = 圆心[1] + r * np.sin(角)
        ax.plot(x, y, color=ec, alpha=透明度, linestyle=es, linewidth=ew, **kwargs)

    ax.axis("equal")


def 同心椭圆(
    圆心=(0, 0),
    n=3,
    a=2,
    b=1,
    参数=0.5,
    模式='等差',
    方向='双向',
    旋转=0,
    颜色='#0F0',
    标记='o',
    透明度=1,
    点数=200,
    线型='-',
    线宽=1,
    ax=None,
    显示圆心=True,
    **kwargs,
):
    """绘制同心椭圆（兼容等差与等比序列）。"""
    if ax is None:
        ax = plt.gca()

    if 显示圆心:
        ax.plot(圆心[0], 圆心[1], marker=标记, color=颜色)

    椭圆列表 = []

    if 模式 == '等差':
        d = float(参数)
        if 方向 == '双向':
            for i in range(1, n + 1):
                椭圆列表.append((a + i * d, b + i * d))
                椭圆列表.append((a - i * d, b - i * d))
        elif 方向 == '向外':
            for i in range(1, n + 1):
                椭圆列表.append((a + i * d, b + i * d))
        elif 方向 == '向内':
            for i in range(1, n + 1):
                椭圆列表.append((a - i * d, b - i * d))
    elif 模式 == '等比':
        q = float(参数)
        if q == 0:
            raise ValueError("等比模式下参数不能为0")
        if 方向 == '双向':
            for i in range(1, n + 1):
                椭圆列表.append((a * (q ** i), b * (q ** i)))
                椭圆列表.append((a / (q ** i), b / (q ** i)))
        elif 方向 == '向外':
            for i in range(1, n + 1):
                椭圆列表.append((a * (q ** i), b * (q ** i)))
        elif 方向 == '向内':
            for i in range(1, n + 1):
                椭圆列表.append((a / (q ** i), b / (q ** i)))

    椭圆列表.append((a, b))
    uniq = {}
    for aa, bb in 椭圆列表:
        if aa > 0 and bb > 0:
            key = (round(float(aa), 12), round(float(bb), 12))
            uniq[key] = (float(aa), float(bb))

    sorted_椭圆列表 = sorted(uniq.values(), key=lambda t: t[0] * t[1])
    角 = np.linspace(0, 2 * np.pi, 点数)
    旋转角弧度 = np.deg2rad(旋转)

    for aa, bb in sorted_椭圆列表:
        x = (
            aa * np.cos(角) * np.cos(旋转角弧度)
            - bb * np.sin(角) * np.sin(旋转角弧度)
            + 圆心[0]
        )
        y = (
            aa * np.cos(角) * np.sin(旋转角弧度)
            + bb * np.sin(角) * np.cos(旋转角弧度)
            + 圆心[1]
        )
        ax.plot(x, y, color=颜色, alpha=透明度, linestyle=线型, linewidth=线宽, **kwargs)

    ax.axis("equal")


def 同心椭圆_填充(
    圆心=(0, 0),
    n=3,
    a=2,
    b=1,
    参数=0.5,
    模式='等差',
    方向='双向',
    旋转=0,
    颜色='#0F0',
    透明度=1,
    填充颜色=None,
    填充透明度=0.3,
    边缘颜色=None,
    边缘宽度=None,
    边缘线型=None,
    标记='o',
    点数=200,
    线型='-',
    线宽=1,
    ax=None,
    显示圆心=True,
    **kwargs,
):
    """绘制带填充的同心椭圆。"""
    if ax is None:
        ax = plt.gca()

    if 显示圆心:
        ax.plot(圆心[0], 圆心[1], marker=标记, color=颜色)

    椭圆列表 = []

    if 模式 == '等差':
        d = float(参数)
        if 方向 == '双向':
            for i in range(1, n + 1):
                椭圆列表.append((a + i * d, b + i * d))
                椭圆列表.append((a - i * d, b - i * d))
        elif 方向 == '向外':
            for i in range(1, n + 1):
                椭圆列表.append((a + i * d, b + i * d))
        elif 方向 == '向内':
            for i in range(1, n + 1):
                椭圆列表.append((a - i * d, b - i * d))
    elif 模式 == '等比':
        q = float(参数)
        if q == 0:
            raise ValueError("等比模式下参数不能为0")
        if 方向 == '双向':
            for i in range(1, n + 1):
                椭圆列表.append((a * (q ** i), b * (q ** i)))
                椭圆列表.append((a / (q ** i), b / (q ** i)))
        elif 方向 == '向外':
            for i in range(1, n + 1):
                椭圆列表.append((a * (q ** i), b * (q ** i)))
        elif 方向 == '向内':
            for i in range(1, n + 1):
                椭圆列表.append((a / (q ** i), b / (q ** i)))

    椭圆列表.append((a, b))
    uniq = {}
    for aa, bb in 椭圆列表:
        if aa > 0 and bb > 0:
            key = (round(float(aa), 12), round(float(bb), 12))
            uniq[key] = (float(aa), float(bb))

    sorted_椭圆列表 = sorted(uniq.values(), key=lambda t: t[0] * t[1])

    fc = 填充颜色 if 填充颜色 is not None else (边缘颜色 if 边缘颜色 is not None else 颜色)
    ec = 边缘颜色 if 边缘颜色 is not None else 颜色
    ew = 边缘宽度 if 边缘宽度 is not None else 线宽
    es = 边缘线型 if 边缘线型 is not None else 线型

    角 = np.linspace(0, 2 * np.pi, 点数)
    旋转角弧度 = np.deg2rad(旋转)

    for aa, bb in sorted(sorted_椭圆列表, key=lambda t: t[0] * t[1], reverse=True):
        x = (
            aa * np.cos(角) * np.cos(旋转角弧度)
            - bb * np.sin(角) * np.sin(旋转角弧度)
            + 圆心[0]
        )
        y = (
            aa * np.cos(角) * np.sin(旋转角弧度)
            + bb * np.sin(角) * np.cos(旋转角弧度)
            + 圆心[1]
        )
        ax.fill(x, y, color=fc, alpha=填充透明度, linewidth=0)

    for aa, bb in sorted_椭圆列表:
        x = (
            aa * np.cos(角) * np.cos(旋转角弧度)
            - bb * np.sin(角) * np.sin(旋转角弧度)
            + 圆心[0]
        )
        y = (
            aa * np.cos(角) * np.sin(旋转角弧度)
            + bb * np.sin(角) * np.cos(旋转角弧度)
            + 圆心[1]
        )
        ax.plot(x, y, color=ec, alpha=透明度, linestyle=es, linewidth=ew, **kwargs)

    ax.axis("equal")


__all__ = [
    "圆", "圆_填充", "圆_p",
    "椭圆", "椭圆_填充",
    "同心圆", "同心圆_填充",
    "同心椭圆", "同心椭圆_填充",
]

"""
弧模块 — 圆弧与椭圆弧的绘制

提供点对点弧、角度弧、椭圆弧等中文接口。
"""

import numpy as np
import matplotlib.pyplot as plt


# ======================== 点对点弧 ========================

def 弧_点(
    圆心=(0, 0),
    点1=(1, 0),
    点2=(-1, 0),
    颜色='#0f0',
    透明度=1,
    点数=1000,
    线型='-',
    线宽=1,
    标签=None,
    标记=None,
    标记大小=5,
    标记填充颜色='r',
    标记边缘颜色='k',
    标记边缘宽度=1,
    ax=None,
    绘图=True,
    方向='逆时针',  # '逆时针' 或 '顺时针'
    **kwargs,
):
    """通过两点画圆弧（以圆心为中心）。

    参数:
        圆心 (tuple): 圆心坐标。
        点1 (tuple): 弧的起点。
        点2 (tuple): 弧的终点。
        方向 (str): '逆时针'(ccw) 或 '顺时针'(cw)。
    """
    v1 = np.array(点1) - np.array(圆心)
    v2 = np.array(点2) - np.array(圆心)

    r1 = np.linalg.norm(v1)
    r2 = np.linalg.norm(v2)
    if r1 == 0 or r2 == 0:
        raise ValueError("点不应与圆心重合")
    if abs(r1 - r2) > 1e-6:
        print(f"警告: 半径不同 (r1={r1:.6g}, r2={r2:.6g}); 使用 r1 画弧")
    r = r1

    角1 = np.arctan2(v1[1], v1[0]) % (2 * np.pi)
    角2 = np.arctan2(v2[1], v2[0]) % (2 * np.pi)

    if 方向 == '逆时针':
        if 角2 <= 角1:
            角2 += 2 * np.pi
        角序列 = np.linspace(角1, 角2, 点数)
    else:  # 顺时针
        if 角1 <= 角2:
            角1 += 2 * np.pi
        角序列 = np.linspace(角1, 角2, 点数)[::-1]

    x = 圆心[0] + r * np.cos(角序列)
    y = 圆心[1] + r * np.sin(角序列)

    if not 绘图:
        return x, y

    if ax is None:
        ax = plt.gca()

    ax.plot(x, y, color=颜色, alpha=透明度, linestyle=线型, linewidth=线宽,
            label=标签, marker=标记, markersize=标记大小,
            markerfacecolor=标记填充颜色, markeredgecolor=标记边缘颜色,
            markeredgewidth=标记边缘宽度, **kwargs)
    ax.set_aspect("equal", adjustable="box")
    if 标签:
        ax.legend()


def 弧_点_反(
    圆心=(0, 0),
    点1=(1, 0),
    点2=(-1, 0),
    颜色='#0f0',
    透明度=1,
    点数=1000,
    线型='-',
    线宽=1,
    标签=None,
    标记=None,
    标记大小=5,
    标记填充颜色='r',
    标记边缘颜色='k',
    标记边缘宽度=1,
    ax=None,
    绘图=True,
    **kwargs,
):
    """通过两点画圆弧（反向/顺时针）。

    默认方向为顺时针，其他同弧_点。
    """
    弧_点(
        圆心=圆心, 点1=点1, 点2=点2, 颜色=颜色, 透明度=透明度,
        点数=点数, 线型=线型, 线宽=线宽, 标签=标签, 标记=标记,
        标记大小=标记大小, 标记填充颜色=标记填充颜色,
        标记边缘颜色=标记边缘颜色, 标记边缘宽度=标记边缘宽度,
        ax=ax, 绘图=绘图, 方向='顺时针', **kwargs,
    )


# ======================== 角度弧 ========================

def 弧(
    r=1,
    角1=45,
    角2=135,
    旋转=0,
    颜色='#0f0',
    透明度=1,
    圆心=(0, 0),
    点数=1000,
    线型='-',
    线宽=1,
    标签=None,
    标记=None,
    标记大小=5,
    标记填充颜色='b',
    标记边缘颜色='r',
    标记边缘宽度=1,
    ax=None,
    使用角度制=True,
    绘图=True,
    方向='逆时针',
    **kwargs,
):
    """通过角度画圆弧。

    参数:
        r (float): 半径。
        角1 (float): 起始角。
        角2 (float): 终止角。
        旋转 (float): 旋转角。
        使用角度制 (bool): 角1/角2/旋转是否使用角度制。
        方向 (str): '逆时针' 或 '顺时针'。
    """
    if 使用角度制:
        角1弧度 = np.deg2rad(角1)
        角2弧度 = np.deg2rad(角2)
        旋转弧度 = np.deg2rad(旋转)
    else:
        角1弧度 = 角1
        角2弧度 = 角2
        旋转弧度 = 旋转

    if 方向 == '逆时针':
        if 角2弧度 <= 角1弧度:
            角2弧度 += 2 * np.pi
        角序列 = np.linspace(角1弧度, 角2弧度, 点数)
    else:
        if 角1弧度 <= 角2弧度:
            角1弧度 += 2 * np.pi
        角序列 = np.linspace(角1弧度, 角2弧度, 点数)[::-1]

    cos_rot = np.cos(旋转弧度)
    sin_rot = np.sin(旋转弧度)

    x = 圆心[0] + r * (np.cos(角序列) * cos_rot - np.sin(角序列) * sin_rot)
    y = 圆心[1] + r * (np.sin(角序列) * cos_rot + np.cos(角序列) * sin_rot)

    if not 绘图:
        return x, y

    if ax is None:
        ax = plt.gca()

    ax.plot(x, y, color=颜色, alpha=透明度, linestyle=线型, linewidth=线宽,
            label=标签, marker=标记, markersize=标记大小,
            markerfacecolor=标记填充颜色, markeredgecolor=标记边缘颜色,
            markeredgewidth=标记边缘宽度, **kwargs)
    ax.axis("equal")
    if 标签:
        ax.legend()


def 弧_反(
    r=1,
    角1=45,
    角2=135,
    旋转=0,
    颜色='#0f0',
    透明度=1,
    圆心=(0, 0),
    点数=1000,
    线型='-',
    线宽=1,
    标签=None,
    标记=None,
    标记大小=5,
    标记填充颜色='b',
    标记边缘颜色='r',
    标记边缘宽度=1,
    ax=None,
    使用角度制=True,
    绘图=True,
    **kwargs,
):
    """通过角度画圆弧（反向/顺时针）。默认方向为顺时针。"""
    弧(r, 角1, 角2, 旋转, 颜色, 透明度, 圆心, 点数, 线型, 线宽,
       标签, 标记, 标记大小, 标记填充颜色, 标记边缘颜色,
       标记边缘宽度, ax, 使用角度制, 绘图, '顺时针', **kwargs)


# ======================== 弧数据函数（返回坐标，不绘图） ========================

def 弧_点_p(圆心, 点1, 点2):
    """通过两点获取弧的坐标数据（不绘图，逆时针方向）。"""
    v1 = np.array(点1) - np.array(圆心)
    v2 = np.array(点2) - np.array(圆心)
    r1 = np.linalg.norm(v1)
    角1 = np.arctan2(v1[1], v1[0])
    角2 = np.arctan2(v2[1], v2[0])
    if 角1 < 角2:
        角1 += 2 * np.pi
    t = np.linspace(角1, 角2, 100)
    x = 圆心[0] + r1 * np.cos(t)
    y = 圆心[1] + r1 * np.sin(t)
    return [x, y]


def 弧_点_p_反(圆心, 点1, 点2):
    """通过两点获取弧的坐标数据（不绘图，顺时针方向）。"""
    v1 = np.array(点1) - np.array(圆心)
    v2 = np.array(点2) - np.array(圆心)
    r1 = np.linalg.norm(v1)
    角1 = np.arctan2(v1[1], v1[0])
    角2 = np.arctan2(v2[1], v2[0])
    if 角2 < 角1:
        角2 += 2 * np.pi
    t = np.linspace(角1, 角2, 100)
    x = 圆心[0] + r1 * np.cos(t)
    y = 圆心[1] + r1 * np.sin(t)
    return [x, y]


def 弧_角度_p(圆心, 半径, 角1, 角2):
    """通过角度获取弧的坐标数据（不绘图）。"""
    if 角1 < 角2:
        角 = np.linspace(角1, 角2, 1000)
        x = 圆心[0] + 半径 * np.cos(角)
        y = 圆心[1] + 半径 * np.sin(角)
    return [x, y]


def 弧_角度_p_反(圆心, 半径, 角1, 角2):
    """通过角度获取弧的坐标数据（不绘图，反向）。"""
    角 = np.linspace(角2 - 2 * np.pi, 角1, 1000)
    x = 圆心[0] + 半径 * np.cos(角)
    y = 圆心[1] + 半径 * np.sin(角)
    return [x, y]


# ======================== 椭圆弧 ========================

def 椭圆弧(
    a=2,
    b=1,
    角1=45,
    角2=135,
    旋转角=0,
    颜色='#0f0',
    透明度=1,
    圆心=(0, 0),
    点数=1000,
    线型='-',
    线宽=1,
    标签=None,
    标记=None,
    标记大小=5,
    标记填充颜色='r',
    标记边缘颜色='k',
    标记边缘宽度=1,
    ax=None,
    使用角度制=True,
    绘图=True,
    **kwargs,
):
    """绘制一段椭圆弧。

    参数:
        a (float): 半长轴。
        b (float): 半短轴。
        角1 (float): 起始角。
        角2 (float): 终止角。
        旋转角 (float): 椭圆旋转角度。
    """
    if 使用角度制:
        角1弧度 = np.deg2rad(角1)
        角2弧度 = np.deg2rad(角2)
        旋转角弧度 = np.deg2rad(旋转角)
    else:
        角1弧度 = 角1
        角2弧度 = 角2
        旋转角弧度 = 旋转角

    角序列 = np.linspace(角1弧度, 角2弧度, 点数)
    x = (
        a * np.cos(角序列) * np.cos(旋转角弧度)
        - b * np.sin(角序列) * np.sin(旋转角弧度)
        + 圆心[0]
    )
    y = (
        a * np.cos(角序列) * np.sin(旋转角弧度)
        + b * np.sin(角序列) * np.cos(旋转角弧度)
        + 圆心[1]
    )

    if not 绘图:
        return x, y

    if ax is None:
        ax = plt.gca()

    ax.plot(x, y, color=颜色, alpha=透明度, linestyle=线型, linewidth=线宽,
            label=标签, marker=标记, markersize=标记大小,
            markerfacecolor=标记填充颜色, markeredgecolor=标记边缘颜色,
            markeredgewidth=标记边缘宽度, **kwargs)
    ax.axis("equal")


# ======================== 旋转弧 ========================

def 弧_旋转(
    r=1,
    角1=45,
    角2=135,
    旋转=0,
    颜色='#0f0',
    透明度=1,
    圆心=(0, 0),
    点数=1000,
    线型='-',
    线宽=1,
    标签=None,
    标记=None,
    标记大小=6,
    标记填充颜色=None,
    标记边缘颜色='k',
    标记边缘宽度=1,
    ax=None,
    使用角度制=True,
    绘图=True,
    方向='逆时针',
    **kwargs,
):
    """绘制一段弧，其角2端固定在圆心，并可绕原点旋转。"""
    if 使用角度制:
        a1 = np.deg2rad(角1)
        a2 = np.deg2rad(角2)
        rot = np.deg2rad(旋转)
    else:
        a1 = 角1
        a2 = 角2
        rot = 旋转

    arc_圆心 = (圆心[0] - r * np.cos(a2), 圆心[1] - r * np.sin(a2))

    x, y = 弧(
        r=r, 角1=a1, 角2=a2, 旋转=0,
        圆心=arc_圆心, 点数=点数,
        使用角度制=False, 绘图=False, 方向=方向,
    )

    x_rot = x * np.cos(rot) - y * np.sin(rot)
    y_rot = x * np.sin(rot) + y * np.cos(rot)

    if not 绘图:
        return x_rot, y_rot

    if ax is None:
        ax = plt.gca()

    ax.plot(x_rot, y_rot, color=颜色, alpha=透明度, linestyle=线型,
            linewidth=线宽, label=标签, marker=标记, markersize=标记大小,
            markerfacecolor=标记填充颜色, markeredgecolor=标记边缘颜色,
            markeredgewidth=标记边缘宽度, **kwargs)
    ax.axis("equal")
    if 标签:
        ax.legend()


__all__ = [
    "弧_点", "弧_点_反", "弧", "弧_反",
    "弧_点_p", "弧_点_p_反", "弧_角度_p", "弧_角度_p_反",
    "椭圆弧", "弧_旋转",
]

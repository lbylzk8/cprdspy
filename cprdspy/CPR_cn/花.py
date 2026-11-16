"""
花模块 — 花瓣与花朵的绘制

提供圆花瓣、椭圆花瓣、单层花、多层花等中文接口。
"""

import numpy as np
import matplotlib.pyplot as plt
from .弧 import 弧, 椭圆弧


# ======================== 辅助函数 ========================

def 旋转点(点, 角度):
    """将点绕原点旋转指定角度（弧度）。

    参数:
        点 (tuple): 坐标 (x, y)。
        角度 (float): 旋转角度（弧度）。

    返回:
        tuple: 旋转后的新坐标。
    """
    x, y = 点
    x_new = x * np.cos(角度) - y * np.sin(角度)
    y_new = x * np.sin(角度) + y * np.cos(角度)
    return (x_new, y_new)


# ======================== 圆花瓣 ========================

def 花_花瓣(
    主半径=1,
    r=1,
    n=4,
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
    标记填充颜色='r',
    标记边缘颜色='k',
    标记边缘宽度=1,
    ax=None,
    显示圆心=False,
    圆心颜色='#0f0',
    圆心大小=8,
    使用角度制=True,
    绘图=True,
    方向='逆时针',
    **kwargs,
):
    """绘制一片圆花瓣。

    参数:
        主半径 (float): 主圆半径R。
        r (float): 花瓣弧的半径。
        n (int): 花瓣基础数（决定花瓣宽度）。
        旋转 (float): 旋转角度。
        使用角度制 (bool): 旋转是否使用角度制。
    """
    alpha = 2 * np.pi / n
    a = 主半径 * np.sin(np.pi / n)
    if r > 0:
        beta = np.arccos(min(1, max(-1, a / r)))
    else:
        beta = 0
    弧角 = np.pi / 2 - np.pi / n + np.arccos(min(1, max(-1, a / r)))

    旋转弧度 = np.deg2rad(旋转) if 使用角度制 else 旋转

    圆心1角度 = 旋转弧度 + alpha / 2
    圆心2角度 = 旋转弧度 - alpha / 2

    圆心1 = (
        np.cos(圆心1角度) * 主半径 + 圆心[0],
        np.sin(圆心1角度) * 主半径 + 圆心[1],
    )
    圆心2 = (
        np.cos(圆心2角度) * 主半径 + 圆心[0],
        np.sin(圆心2角度) * 主半径 + 圆心[1],
    )

    if abs(r - a) < 1e-12:
        theta1_base = np.pi + alpha / 2
        theta2_base = np.pi + alpha / 2 + 弧角
        theta3_base = np.pi / 2
        theta4_base = np.pi / 2 + 弧角
    elif r > a:
        theta1_base = np.pi + alpha / 2
        theta2_base = np.pi + alpha / 2 + 弧角
        theta3_base = np.pi / 2 - beta
        theta4_base = np.pi / 2 - beta + 弧角
    else:
        print(f"r={r:.3f}, a={a:.3f}")
        print(f"r<a, 不能形成花瓣。最小需要 r > {a:.3f}")
        return None

    if 使用角度制:
        theta1 = np.rad2deg(theta1_base)
        theta2 = np.rad2deg(theta2_base)
        theta3 = np.rad2deg(theta3_base)
        theta4 = np.rad2deg(theta4_base)
        弧旋转 = 旋转
    else:
        theta1 = theta1_base
        theta2 = theta2_base
        theta3 = theta3_base
        theta4 = theta4_base
        弧旋转 = 旋转弧度

    if 绘图 and ax is None:
        ax = plt.gca()

    弧(
        r, theta1, theta2, 弧旋转,
        颜色, 透明度, 圆心1, 点数, 线型, 线宽,
        标签, 标记, 标记大小, 标记填充颜色, 标记边缘颜色, 标记边缘宽度,
        ax, 使用角度制, 绘图, 方向, **kwargs,
    )
    弧(
        r, theta3, theta4, 弧旋转,
        颜色, 透明度, 圆心2, 点数, 线型, 线宽,
        标签, 标记, 标记大小, 标记填充颜色, 标记边缘颜色, 标记边缘宽度,
        ax, 使用角度制, 绘图, 方向, **kwargs,
    )

    if 显示圆心 and 绘图:
        plt.scatter(圆心1[0], 圆心1[1], color=圆心颜色, s=圆心大小, alpha=透明度)
        plt.scatter(圆心2[0], 圆心2[1], color=圆心颜色, s=圆心大小, alpha=透明度)


def 花_花瓣_填充(
    主半径=1,
    r=1,
    n=4,
    旋转=0,
    颜色='#0f0',
    透明度=1,
    填充颜色=None,
    填充透明度=0.3,
    边缘颜色=None,
    边缘宽度=None,
    边缘线型=None,
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
    显示圆心=False,
    圆心颜色='#0f0',
    圆心大小=8,
    使用角度制=True,
    绘图=True,
    方向='逆时针',
    **kwargs,
):
    """绘制一片带填充的圆花瓣。"""
    alpha = 2 * np.pi / n
    a = 主半径 * np.sin(np.pi / n)
    if r > 0:
        beta = np.arccos(min(1, max(-1, a / r)))
    else:
        beta = 0
    弧角 = np.pi / 2 - np.pi / n + np.arccos(min(1, max(-1, a / r)))

    旋转弧度 = np.deg2rad(旋转) if 使用角度制 else 旋转

    圆心1角度 = 旋转弧度 + alpha / 2
    圆心2角度 = 旋转弧度 - alpha / 2

    圆心1 = (
        np.cos(圆心1角度) * 主半径 + 圆心[0],
        np.sin(圆心1角度) * 主半径 + 圆心[1],
    )
    圆心2 = (
        np.cos(圆心2角度) * 主半径 + 圆心[0],
        np.sin(圆心2角度) * 主半径 + 圆心[1],
    )

    if r < a:
        print(f"r={r:.3f}, a={a:.3f}")
        print(f"r<a, 不能形成花瓣。最小需要 r > {a:.3f}")
        return None
    elif abs(r - a) < 1e-12:
        theta1_base = np.pi + alpha / 2
        theta2_base = np.pi + alpha / 2 + 弧角
        theta3_base = np.pi / 2
        theta4_base = np.pi / 2 + 弧角
    else:
        theta1_base = np.pi + alpha / 2
        theta2_base = np.pi + alpha / 2 + 弧角
        theta3_base = np.pi / 2 - beta
        theta4_base = np.pi / 2 - beta + 弧角

    if 使用角度制:
        theta1 = np.rad2deg(theta1_base)
        theta2 = np.rad2deg(theta2_base)
        theta3 = np.rad2deg(theta3_base)
        theta4 = np.rad2deg(theta4_base)
        弧旋转 = 旋转
    else:
        theta1 = theta1_base
        theta2 = theta2_base
        theta3 = theta3_base
        theta4 = theta4_base
        弧旋转 = 旋转弧度

    x1, y1 = 弧(r, theta1, theta2, 弧旋转, 圆心=圆心1, 点数=点数,
                   使用角度制=使用角度制, 绘图=False, 方向=方向)
    x2, y2 = 弧(r, theta3, theta4, 弧旋转, 圆心=圆心2, 点数=点数,
                   使用角度制=使用角度制, 绘图=False, 方向=方向)

    if not 绘图:
        return (x1, y1, x2, y2)

    if ax is None:
        ax = plt.gca()

    fc = 填充颜色 if 填充颜色 is not None else (边缘颜色 if 边缘颜色 is not None else 颜色)
    ec = 边缘颜色 if 边缘颜色 is not None else 颜色
    ew = 边缘宽度 if 边缘宽度 is not None else 线宽
    es = 边缘线型 if 边缘线型 is not None else 线型

    x_fill = np.concatenate([x1, x2])
    y_fill = np.concatenate([y1, y2])
    ax.fill(x_fill, y_fill, color=fc, alpha=填充透明度, linewidth=0)

    ax.plot(x1, y1, color=ec, alpha=透明度, linestyle=es, linewidth=ew,
            marker=标记, markersize=标记大小,
            markerfacecolor=标记填充颜色, markeredgecolor=标记边缘颜色,
            markeredgewidth=标记边缘宽度, **kwargs)
    ax.plot(x2, y2, color=ec, alpha=透明度, linestyle=es, linewidth=ew,
            marker=标记, markersize=标记大小,
            markerfacecolor=标记填充颜色, markeredgecolor=标记边缘颜色,
            markeredgewidth=标记边缘宽度, **kwargs)

    ax.set_aspect("equal", adjustable="box")
    if 标签:
        ax.legend()

    if 显示圆心:
        plt.scatter(圆心1[0], 圆心1[1], color=圆心颜色, s=圆心大小, alpha=透明度)
        plt.scatter(圆心2[0], 圆心2[1], color=圆心颜色, s=圆心大小, alpha=透明度)


# ======================== 单层花 ========================

def 花(
    主半径=1,
    r=1,
    n=4,
    N=12,
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
    标记填充颜色='r',
    标记边缘颜色='k',
    标记边缘宽度=1,
    ax=None,
    显示圆心=False,
    圆心颜色='#0f0',
    圆心大小=8,
    使用角度制=True,
    绘图=True,
    方向='逆时针',
    **kwargs,
):
    """绘制单层花朵——N片圆花瓣均匀排列。

    参数:
        主半径 (float): 主圆半径R。
        r (float): 花瓣弧半径。
        n (int): 花瓣基础数。
        N (int): 花瓣数量。
        旋转 (float): 旋转角度。
    """
    for i in range(N):
        花_花瓣(
            主半径, r, n,
            (旋转 + i * 360 / N + 90) if 使用角度制 else (旋转 + i * 2 * np.pi / N + np.pi / 2),
            颜色, 透明度, 圆心, 点数, 线型, 线宽,
            标签, 标记, 标记大小, 标记填充颜色, 标记边缘颜色, 标记边缘宽度,
            ax, 显示圆心, 圆心颜色, 圆心大小, 使用角度制, 绘图, 方向,
            **kwargs,
        )


def 花_填充(
    主半径=1,
    r=1,
    n=4,
    N=12,
    旋转=0,
    颜色='#0f0',
    透明度=1,
    填充颜色=None,
    填充透明度=0.3,
    边缘颜色=None,
    边缘宽度=None,
    边缘线型=None,
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
    显示圆心=False,
    圆心颜色='#0f0',
    圆心大小=8,
    使用角度制=True,
    绘图=True,
    方向='逆时针',
    **kwargs,
):
    """绘制单层填充花朵——N片带填充的圆花瓣均匀排列。"""
    for i in range(N):
        花_花瓣_填充(
            主半径, r, n,
            (旋转 + i * 360 / N + 90) if 使用角度制 else (旋转 + i * 2 * np.pi / N + np.pi / 2),
            颜色=颜色, 透明度=透明度,
            填充颜色=填充颜色, 填充透明度=填充透明度,
            边缘颜色=边缘颜色, 边缘宽度=边缘宽度, 边缘线型=边缘线型,
            圆心=圆心, 点数=点数,
            线型=线型, 线宽=线宽, 标签=标签,
            标记=标记, 标记大小=标记大小,
            标记填充颜色=标记填充颜色, 标记边缘颜色=标记边缘颜色,
            标记边缘宽度=标记边缘宽度, ax=ax,
            显示圆心=显示圆心, 圆心颜色=圆心颜色, 圆心大小=圆心大小,
            使用角度制=使用角度制, 绘图=绘图, 方向=方向,
            **kwargs,
        )


# ======================== 多层花 ========================

def 多层花(
    主半径=1,
    r=1,
    n=4,
    公比=np.sqrt(2),
    M=3,
    N=12,
    颜色='b',
    透明度=1,
    旋转=0,
    圆心=(0, 0),
    点数=1000,
    线型='-',
    线宽=1,
    标签=None,
    标记=None,
    标记大小=5,
    标记填充颜色='r',
    标记边缘颜色='b',
    标记边缘宽度=1,
    ax=None,
    显示圆心=False,
    圆心颜色='r',
    圆心大小=5,
    使用角度制=False,
    绘图=True,
    方向='逆时针',
    **kwargs,
):
    """绘制多层花朵——M层花瓣，每层按公比缩放。

    参数:
        主半径 (float): 最内层主圆半径R。
        r (float): 最内层花瓣弧半径。
        n (int): 花瓣基础数。
        公比 (float): 层间缩放比。
        M (int): 层数。
        N (int): 每层花瓣数。
    """
    旋转弧度 = np.deg2rad(旋转) if 使用角度制 else 旋转

    for j in range(1, M + 1):
        for i in range(N):
            花_花瓣(
                主半径 * (公比 ** (j - 1)),
                r * (公比 ** (j - 1)),
                n,
                2 * i * np.pi / N + (j - 1) * np.pi / N + 旋转弧度 + np.pi / 2,
                颜色, 透明度, 圆心, 点数, 线型, 线宽,
                标签, 标记, 标记大小, 标记填充颜色, 标记边缘颜色, 标记边缘宽度,
                ax, 显示圆心, 圆心颜色, 圆心大小,
                False,  # 旋转已是弧度
                绘图, 方向,
                **kwargs,
            )


# ======================== 椭圆花瓣 ========================

def 椭圆花瓣_a(a, b, d, 旋转=0, 使用角度制=True, 颜色='b', 透明度=1, 圆心=(0, 0), 点数=1000):
    """椭圆花瓣（简化版）。

    旋转 (float): 旋转角度。
    使用角度制 (bool): 旋转是否使用角度制。
    """
    旋转弧度 = np.deg2rad(旋转) if 使用角度制 else 旋转
    x0 = b / (2 * a) * np.sqrt(4 * a**2 - d**2) / (d / 2)
    beta = np.arctan(x0)
    beta_b1 = np.pi / 2 - beta
    beta_e1 = np.pi / 2 + beta
    beta_b2 = 3 * np.pi / 2 - beta
    beta_e2 = 3 * np.pi / 2 + beta
    圆心1 = (圆心[0], 圆心[1] - d / 2)
    圆心2 = (圆心[0], 圆心[1] + d / 2)
    圆心1旋转 = 旋转点((a, 圆心[1] - d / 2), 旋转弧度)
    圆心2旋转 = 旋转点((a, 圆心[1] + d / 2), 旋转弧度)
    椭圆弧(a, b, beta_b1, beta_e1, 旋转角=旋转, 颜色=颜色, 透明度=透明度, 圆心=圆心1旋转, 点数=点数, 使用角度制=使用角度制)
    椭圆弧(a, b, beta_b2, beta_e2, 旋转角=旋转, 颜色=颜色, 透明度=透明度, 圆心=圆心2旋转, 点数=点数, 使用角度制=使用角度制)


def 椭圆花瓣(
    a=2, b=1, d=0.5,
    旋转=0,
    旋转中心=True,
    颜色='#0f0', 透明度=1,
    圆心=(0, 0), 点数=1000,
    线型='-', 线宽=1,
    标签=None,
    标记=None, 标记大小=5,
    标记填充颜色='r', 标记边缘颜色='k', 标记边缘宽度=1,
    ax=None,
    使用角度制=True,
    绘图=True,
    **kwargs,
):
    """绘制一个椭圆花瓣形状。

    参数:
        a (float): 椭圆半长轴。
        b (float): 椭圆半短轴。
        d (float): 花瓣垂直距离。
        旋转 (float): 旋转角度。
        旋转中心 (bool): 是否绕中心旋转。
    """
    x0 = b / (2 * a) * np.sqrt(4 * a**2 - d**2) / (d / 2)
    beta = np.arctan(x0)
    beta_b1弧度 = np.pi / 2 - beta
    beta_e1弧度 = np.pi / 2 + beta
    beta_b2弧度 = 3 * np.pi / 2 - beta
    beta_e2弧度 = 3 * np.pi / 2 + beta

    旋转弧度 = np.deg2rad(旋转) if 使用角度制 else 旋转

    圆心1 = (圆心[0], 圆心[1] - d / 2)
    圆心2 = (圆心[0], 圆心[1] + d / 2)
    if 旋转中心:
        圆心1旋转 = 旋转点(圆心1, 旋转弧度)
        圆心2旋转 = 旋转点(圆心2, 旋转弧度)
    else:
        圆心1旋转 = 旋转点((a, 圆心[1] - d / 2), 旋转弧度)
        圆心2旋转 = 旋转点((a, 圆心[1] + d / 2), 旋转弧度)

    if not 绘图:
        theta1 = np.linspace(beta_b1弧度, beta_e1弧度, 点数)
        x1 = (
            a * np.cos(theta1) * np.cos(旋转弧度)
            - b * np.sin(theta1) * np.sin(旋转弧度)
            + 圆心1旋转[0]
        )
        y1 = (
            a * np.cos(theta1) * np.sin(旋转弧度)
            + b * np.sin(theta1) * np.cos(旋转弧度)
            + 圆心1旋转[1]
        )
        theta2 = np.linspace(beta_b2弧度, beta_e2弧度, 点数)
        x2 = (
            a * np.cos(theta2) * np.cos(旋转弧度)
            - b * np.sin(theta2) * np.sin(旋转弧度)
            + 圆心2旋转[0]
        )
        y2 = (
            a * np.cos(theta2) * np.sin(旋转弧度)
            + b * np.sin(theta2) * np.cos(旋转弧度)
            + 圆心2旋转[1]
        )
        return (x1, y1, x2, y2)

    if 使用角度制:
        beta_b1 = np.rad2deg(beta_b1弧度)
        beta_e1 = np.rad2deg(beta_e1弧度)
        beta_b2 = np.rad2deg(beta_b2弧度)
        beta_e2 = np.rad2deg(beta_e2弧度)
    else:
        beta_b1, beta_e1 = beta_b1弧度, beta_e1弧度
        beta_b2, beta_e2 = beta_b2弧度, beta_e2弧度

    椭圆弧(a, b, beta_b1, beta_e1, 旋转角=旋转, 颜色=颜色, 透明度=透明度, 圆心=圆心1旋转,
            点数=点数, 线型=线型, 线宽=线宽, 标签=标签,
            标记=标记, 标记大小=标记大小,
            标记填充颜色=标记填充颜色, 标记边缘颜色=标记边缘颜色,
            标记边缘宽度=标记边缘宽度, ax=ax, 使用角度制=使用角度制, **kwargs)
    椭圆弧(a, b, beta_b2, beta_e2, 旋转角=旋转, 颜色=颜色, 透明度=透明度, 圆心=圆心2旋转,
            点数=点数, 线型=线型, 线宽=线宽, 标签=标签,
            标记=标记, 标记大小=标记大小,
            标记填充颜色=标记填充颜色, 标记边缘颜色=标记边缘颜色,
            标记边缘宽度=标记边缘宽度, ax=ax, 使用角度制=使用角度制, **kwargs)


def 椭圆花瓣_填充(
    a=2, b=1, d=0.5,
    旋转=0, 旋转中心=True,
    颜色='#0f0', 透明度=1,
    填充颜色=None, 填充透明度=0.3,
    边缘颜色=None, 边缘宽度=None, 边缘线型=None,
    圆心=(0, 0), 点数=1000,
    线型='-', 线宽=1, 标签=None,
    标记=None, 标记大小=5,
    标记填充颜色='r', 标记边缘颜色='k', 标记边缘宽度=1,
    ax=None, 使用角度制=True, 绘图=True,
    **kwargs,
):
    """绘制一个带填充的椭圆花瓣形状。"""
    if ax is None:
        ax = plt.gca()

    结果 = 椭圆花瓣(
        a=a, b=b, d=d, 旋转=旋转, 旋转中心=旋转中心,
        颜色=颜色, 透明度=透明度, 圆心=圆心, 点数=点数,
        线型=线型, 线宽=线宽, 标签=标签,
        标记=标记, 标记大小=标记大小,
        标记填充颜色=标记填充颜色, 标记边缘颜色=标记边缘颜色,
        标记边缘宽度=标记边缘宽度, ax=ax,
        使用角度制=使用角度制, 绘图=False,
        **kwargs,
    )

    if 结果 is None:
        return None

    x1, y1, x2, y2 = 结果

    fc = 填充颜色 if 填充颜色 is not None else (边缘颜色 if 边缘颜色 is not None else 颜色)
    ec = 边缘颜色 if 边缘颜色 is not None else 颜色
    ew = 边缘宽度 if 边缘宽度 is not None else 线宽
    es = 边缘线型 if 边缘线型 is not None else 线型

    if not 绘图:
        return (x1, y1, x2, y2)

    x_fill = np.concatenate([x1, x2])
    y_fill = np.concatenate([y1, y2])
    ax.fill(x_fill, y_fill, color=fc, alpha=填充透明度, linewidth=0)

    ax.plot(x1, y1, color=ec, alpha=透明度, linestyle=es, linewidth=ew,
            marker=标记, markersize=标记大小,
            markerfacecolor=标记填充颜色, markeredgecolor=标记边缘颜色,
            markeredgewidth=标记边缘宽度, **kwargs)
    ax.plot(x2, y2, color=ec, alpha=透明度, linestyle=es, linewidth=ew,
            marker=标记, markersize=标记大小,
            markerfacecolor=标记填充颜色, markeredgecolor=标记边缘颜色,
            markeredgewidth=标记边缘宽度, **kwargs)

    ax.set_aspect("equal", adjustable="box")
    if 标签:
        ax.legend()


# ======================== 椭圆花 ========================

def 椭圆花(a=2, b=1, d=0.1, n=12, 旋转=0, 使用角度制=True, 颜色='#0f0', 透明度=1, 圆心=(0, 0), 点数=1000):
    """椭圆花瓣花朵（旋转中心模式）。

    旋转 (float): 旋转角度。
    """
    旋转弧度 = np.deg2rad(旋转) if 使用角度制 else 旋转
    for i in range(n):
        椭圆花瓣(a, b, d, 旋转弧度 + i * 2 * np.pi / n, True, 颜色, 透明度, 圆心, 点数, 使用角度制=False)


def 椭圆花_a(a=2, b=1, d=0.1, n=12, 旋转=0, 使用角度制=True, 颜色='#0f0', 透明度=1, 圆心=(0, 0), 点数=1000):
    """椭圆花瓣花朵（旋转模式A）。

    旋转 (float): 旋转角度。
    """
    旋转弧度 = np.deg2rad(旋转) if 使用角度制 else 旋转
    for i in range(n):
        椭圆花瓣(a, b, d, 旋转弧度 + i * 2 * np.pi / n, False, 颜色, 透明度, 圆心, 点数, 使用角度制=False)


def 椭圆花_填充(
    a=2, b=1, d=0.1, n=12, 旋转=0, 使用角度制=True,
    颜色='#0f0', 透明度=1,
    填充颜色=None, 填充透明度=0.3,
    边缘颜色=None, 边缘宽度=None, 边缘线型=None,
    圆心=(0, 0), 点数=1000,
    线型='-', 线宽=1, 标签=None,
    标记=None, 标记大小=5,
    标记填充颜色='r', 标记边缘颜色='k', 标记边缘宽度=1,
    ax=None, 绘图=True,
    **kwargs,
):
    """椭圆花瓣花朵（带填充，旋转中心模式）。"""
    旋转弧度 = np.deg2rad(旋转) if 使用角度制 else 旋转
    for i in range(n):
        椭圆花瓣_填充(
            a, b, d, 旋转弧度 + i * 2 * np.pi / n, 旋转中心=True,
            颜色=颜色, 透明度=透明度,
            填充颜色=填充颜色, 填充透明度=填充透明度,
            边缘颜色=边缘颜色, 边缘宽度=边缘宽度, 边缘线型=边缘线型,
            圆心=圆心, 点数=点数,
            线型=线型, 线宽=线宽, 标签=标签,
            标记=标记, 标记大小=标记大小,
            标记填充颜色=标记填充颜色, 标记边缘颜色=标记边缘颜色,
            标记边缘宽度=标记边缘宽度, ax=ax,
            使用角度制=False, 绘图=绘图,
            **kwargs,
        )


def 椭圆花_a_填充(
    a=2, b=1, d=0.1, n=12, 旋转=0, 使用角度制=True,
    颜色='#0f0', 透明度=1,
    填充颜色=None, 填充透明度=0.3,
    边缘颜色=None, 边缘宽度=None, 边缘线型=None,
    圆心=(0, 0), 点数=1000,
    线型='-', 线宽=1, 标签=None,
    标记=None, 标记大小=5,
    标记填充颜色='r', 标记边缘颜色='k', 标记边缘宽度=1,
    ax=None, 绘图=True,
    **kwargs,
):
    """椭圆花瓣花朵（带填充，旋转模式A）。"""
    旋转弧度 = np.deg2rad(旋转) if 使用角度制 else 旋转
    for i in range(n):
        椭圆花瓣_填充(
            a, b, d, 旋转弧度 + i * 2 * np.pi / n, 旋转中心=False,
            颜色=颜色, 透明度=透明度,
            填充颜色=填充颜色, 填充透明度=填充透明度,
            边缘颜色=边缘颜色, 边缘宽度=边缘宽度, 边缘线型=边缘线型,
            圆心=圆心, 点数=点数,
            线型=线型, 线宽=线宽, 标签=标签,
            标记=标记, 标记大小=标记大小,
            标记填充颜色=标记填充颜色, 标记边缘颜色=标记边缘颜色,
            标记边缘宽度=标记边缘宽度, ax=ax,
            使用角度制=False, 绘图=绘图,
            **kwargs,
        )


__all__ = [
    "旋转点",
    "花_花瓣", "花_花瓣_填充",
    "花", "花_填充", "多层花",
    "椭圆花瓣_a", "椭圆花瓣", "椭圆花瓣_填充",
    "椭圆花", "椭圆花_填充", "椭圆花_a", "椭圆花_a_填充",
]

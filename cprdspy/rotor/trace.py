"""
trace.py — 曲线采样与几何分析

功能:
    - trace(): 将 Rotor 组合采样为坐标数组
    - compute_velocity(): 数值微分求速度
    - compute_curvature(): GA 曲率公式 κ = |v∧a| / |v|³
    - compute_torsion(): GA 挠率公式（需要 3D，2D 返回 0）
    - arc_length(): 弧长计算

注意:
    曲率公式 κ = |v∧a| / |v|³ 是几何代数 (GA) 的无坐标形式，
    在任意维度中都成立，无需叉积。
    在 2D 中，v∧a 是二重向量（伪标量），其模长 = |v_x a_y - v_y a_x|。
"""

import numpy as np
from typing import Union, Tuple, Optional


def trace(
    composition,
    t_start: float = 0,
    t_end: float = None,
    n_points: int = 2000,
    return_complex: bool = False,
):
    """
    采样 Rotor 组合曲线

    参数:
        composition: Rotor2D, RotorComposition, 或任何可调用对象 f(t) → complex
        t_start: 起始时间
        t_end: 结束时间（默认: 自动判断周期）
        n_points: 采样点数
        return_complex: True 返回复数数组, False 返回 (x, y) 元组

    返回:
        (x, y): numpy 数组元组（默认）
        z: 复数 numpy 数组（return_complex=True）

    示例:
        >>> curve = Rotor2D(3, 1) + Rotor2D(1, 7)
        >>> x, y = trace(curve)
        >>> plt.plot(x, y)
    """
    # 自动判断周期
    if t_end is None:
        if hasattr(composition, "is_closed") and hasattr(composition, "period"):
            if composition.is_closed():
                T = composition.period()
                t_end = T if T is not None else 2 * np.pi
            else:
                t_end = 2 * np.pi * 10  # 准周期: 多绕几圈
        else:
            t_end = 2 * np.pi

    t = np.linspace(t_start, t_end, n_points)
    z = composition(t)

    if return_complex:
        return t, z
    return t, z.real, z.imag


def compute_velocity(x, y, t):
    """
    数值速度 (一阶差分)

    v = dγ/dt ≈ (γ[i+1] - γ[i-1]) / (2dt)
    """
    dt = t[1] - t[0]
    vx = np.gradient(x, dt)
    vy = np.gradient(y, dt)
    return vx, vy


def compute_acceleration(x, y, t):
    """
    数值加速度 (二阶差分)

    a = d²γ/dt²
    """
    dt = t[1] - t[0]
    ax = np.gradient(np.gradient(x, dt), dt)
    ay = np.gradient(np.gradient(y, dt), dt)
    return ax, ay


def compute_curvature(x, y, t=None):
    """
    曲率 — GA 公式

    κ = |v ∧ a| / |v|³

    在 2D 中:
        v ∧ a = v_x · a_y - v_y · a_x  (伪标量/二重向量)
        |v ∧ a| = |v_x · a_y - v_y · a_x|

    这是几何代数中的无坐标公式，直接推广到任意维度。
    不需要叉积（叉积只在 3D 有定义）。

    参数:
        x, y: 坐标数组
        t: 时间数组（可选，默认均匀采样）

    返回:
        kappa: 曲率数组
    """
    if t is None:
        t = np.linspace(0, 2 * np.pi, len(x))

    vx, vy = compute_velocity(x, y, t)
    ax, ay = compute_acceleration(x, y, t)

    # 2D 外积 (伪标量): v ∧ a = v_x * a_y - v_y * a_x
    cross = vx * ay - vy * ax

    speed = np.sqrt(vx**2 + vy**2)
    speed = np.maximum(speed, 1e-15)  # 防止除零

    kappa = np.abs(cross) / speed**3
    return kappa


def compute_torsion(x, y, t=None):
    """
    挠率 — 2D 曲线恒为 0

    挠率衡量曲线偏离平面的程度。
    2D 曲线始终在平面内，所以 τ ≡ 0。

    在 3D 中 (GA 公式):
        τ = (v ∧ a ∧ ȧ) · I⁻¹ / |v ∧ a|²

    这个公式在 3D Rotor 模块中实现。
    """
    return np.zeros_like(x)


def arc_length(x, y, t=None):
    """
    弧长函数 s(t)

    s(t) = ∫₀ᵗ |γ'(τ)| dτ ≈ Σ |Δγ|
    """
    vx, vy = compute_velocity(x, y, t if t is not None else np.linspace(0, 2*np.pi, len(x)))
    speed = np.sqrt(vx**2 + vy**2)
    if t is not None:
        dt = t[1] - t[0]
    else:
        dt = 2 * np.pi / len(x)
    s = np.cumsum(speed) * dt
    s = s - s[0]  # 从 0 开始
    return s


def total_length(x, y, t=None):
    """曲线总弧长"""
    s = arc_length(x, y, t)
    return s[-1]


# ============================================================
# nD 曲线采样与分析
# ============================================================

def trace_nd(
    composition,
    t_start: float = 0,
    t_end: float = None,
    n_points: int = 2000,
):
    """
    采样 nD Rotor 组合曲线

    参数:
        composition: Rotor3D, Rotor3DComposition, RotorClifford, RotorCliffordComposition
        t_start: 起始时间
        t_end: 结束时间（默认: 自动判断周期）
        n_points: 采样点数

    返回:
        (t, coords): 时间数组 + 坐标数组元组 (x1, x2, ..., xn)

    示例:
        >>> curve = Rotor3D(3, 1, 0, [1,0,0], [0,1,0]) + Rotor3D(1, 5, 0, [0,1,0], [0,0,1])
        >>> t, x, y, z = trace_nd(curve)
    """
    # 自动判断周期
    if t_end is None:
        if hasattr(composition, "is_closed") and hasattr(composition, "period"):
            if composition.is_closed():
                T = composition.period()
                t_end = T if T is not None else 2 * np.pi
            else:
                t_end = 2 * np.pi * 10
        else:
            t_end = 2 * np.pi

    t = np.linspace(t_start, t_end, n_points)
    pos = composition(t)

    # pos 形状: (n_points, n_dim)
    if pos.ndim == 1:
        # 标量输入返回 1D，但我们应该有数组
        pos = pos.reshape(1, -1)

    coords = tuple(pos[:, i] for i in range(pos.shape[1]))
    return (t,) + coords


def compute_velocity_nd(*coords, t=None):
    """
    nD 数值速度

    参数:
        *coords: x1, x2, ..., xn 坐标数组
        t: 时间数组（可选）

    返回:
        (v1, v2, ..., vn): 速度分量数组
    """
    if t is None:
        t = np.linspace(0, 2 * np.pi, len(coords[0]))
    dt = t[1] - t[0]
    return tuple(np.gradient(c, dt) for c in coords)


def compute_acceleration_nd(*coords, t=None):
    """
    nD 数值加速度

    返回:
        (a1, a2, ..., an): 加速度分量数组
    """
    if t is None:
        t = np.linspace(0, 2 * np.pi, len(coords[0]))
    dt = t[1] - t[0]
    return tuple(np.gradient(np.gradient(c, dt), dt) for c in coords)


def compute_curvature_nd(*coords, t=None):
    """
    nD 曲率 — GA 公式

    κ = |v ∧ a| / |v|³

    在任意维度中:
        |v ∧ a|² = |v|²|a|² - (v·a)²

    这是几何代数中的无坐标公式。

    参数:
        *coords: x1, x2, ..., xn 坐标数组
        t: 时间数组（可选）

    返回:
        kappa: 曲率数组
    """
    n = len(coords)
    if t is None:
        t = np.linspace(0, 2 * np.pi, len(coords[0]))

    velocities = compute_velocity_nd(*coords, t=t)
    accelerations = compute_acceleration_nd(*coords, t=t)

    # |v|² = Σ v_i²
    speed_sq = sum(v**2 for v in velocities)
    speed = np.sqrt(speed_sq)
    speed = np.maximum(speed, 1e-15)

    # |a|² = Σ a_i²
    acc_sq = sum(a**2 for a in accelerations)

    # v·a = Σ v_i * a_i
    dot_va = sum(v * a for v, a in zip(velocities, accelerations))

    # |v ∧ a|² = |v|²|a|² - (v·a)²
    wedge_sq = speed_sq * acc_sq - dot_va**2
    wedge_sq = np.maximum(wedge_sq, 0)  # 数值稳定性
    wedge_norm = np.sqrt(wedge_sq)

    kappa = wedge_norm / speed**3
    return kappa


def compute_torsion_3d(x, y, z, t=None):
    """
    3D 挠率

    τ = (v · (a × ȧ)) / |v × a|²

    参数:
        x, y, z: 坐标数组
        t: 时间数组（可选）

    返回:
        torsion: 挠率数组
    """
    if t is None:
        t = np.linspace(0, 2 * np.pi, len(x))

    vx, vy, vz = compute_velocity_nd(x, y, z, t=t)
    ax, ay, az = compute_acceleration_nd(x, y, z, t=t)

    # 三阶导数
    dt = t[1] - t[0]
    jx = np.gradient(ax, dt)
    jy = np.gradient(ay, dt)
    jz = np.gradient(az, dt)

    # v × a
    cross_x = vy * az - vz * ay
    cross_y = vz * ax - vx * az
    cross_z = vx * ay - vy * ax

    # |v × a|²
    cross_sq = cross_x**2 + cross_y**2 + cross_z**2
    cross_sq = np.maximum(cross_sq, 1e-30)

    # v · (a × j) = (v × a) · j
    torsion = (cross_x * jx + cross_y * jy + cross_z * jz) / cross_sq
    return torsion


def arc_length_nd(*coords, t=None):
    """
    nD 弧长函数

    s(t) = ∫₀ᵗ |γ'(τ)| dτ
    """
    n = len(coords)
    if t is None:
        t = np.linspace(0, 2 * np.pi, len(coords[0]))

    velocities = compute_velocity_nd(*coords, t=t)
    speed = np.sqrt(sum(v**2 for v in velocities))

    dt = t[1] - t[0]
    s = np.cumsum(speed) * dt
    s = s - s[0]
    return s


def total_length_nd(*coords, t=None):
    """nD 曲线总弧长"""
    s = arc_length_nd(*coords, t=t)
    return s[-1]

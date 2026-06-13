"""
fourier_flower.py — 基于傅里叶级数的参数化花瓣与花朵生成
============================================================

支持三种数学表示（从具体到抽象，从低维到高维）：

1. 极坐标 (Polar Coordinates) —— 一维实函数
   r(θ) = a₀/2 + Σₘ₌₁ᴹ [aₘ cos(mωθ) + bₘ sin(mωθ)]
   花瓣定义在 θ ∈ [-π/n, π/n]，满足 r(±π/n) = 0（根部闭合）

2. 直角坐标 (Cartesian Parametric) —— 二维实向量函数
   x(t) = a₀ˣ/2 + Σₘ₌₁ᴹ [aₘˣ cos(mt) + bₘˣ sin(mt)]
   y(t) = a₀ʸ/2 + Σₘ₌₁ᴹ [aₘʸ cos(mt) + bₘʸ sin(mt)]
   花瓣为 t ∈ [0, 2π] 上通过原点的闭合曲线

3. 复数坐标 (Complex Fourier / Epicycles) —— 一维复函数（最高抽象）
   z(t) = x(t) + i·y(t) = Σₖ₌₋ᴷᴷ cₖ e^{ikt}
   每个系数 cₖ = |cₖ|e^{iφₖ} 对应一个半径为 |cₖ|、频率为 k 的旋转向量（本轮）

三种表示的关系：
  - 极坐标 → 复数: z(θ) = r(θ)·e^{iθ}
  - 复数 → 直角: x(t)=Re(z), y(t)=Im(z)
  - 直角 → 极坐标: r=√(x²+y²), θ=atan2(y,x)
  - 直角 → 复数: z = x + iy

核心优势：
  - 复数表示最紧凑：旋转 = 乘 e^{iφ}，平移 = 加常数
  - n 重旋转对称性在复数域有简洁代数表达：cₖ ≠ 0 仅当 k ≡ 1 (mod n)
  - 可直接生成整朵花（非逐瓣拼接），只需约束非零频率
  - 每个系数 cₖ 对应本轮 (epicycle)，可视化极其优雅
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from typing import Callable, Optional, Union, List, Tuple, Dict
import warnings

__all__ = [
    # 数学工具
    "rotate_point", "complex_to_cartesian", "cartesian_to_complex",
    # 极坐标
    "fourier_polar_petal", "POLAR_PRESETS",
    "_preset_polar_cos", "_preset_polar_sincos", "_preset_polar_bell",
    "_preset_polar_ripple", "_preset_polar_pointed",
    # 直角坐标
    "fourier_cartesian_petal", "CARTESIAN_PRESETS",
    "_preset_cartesian_teardrop", "_preset_cartesian_leaf",
    "_preset_cartesian_heart", "_preset_cartesian_diamond",
    # 复数花瓣
    "fourier_complex_petal", "COMPLEX_PETAL_PRESETS",
    "_preset_complex_teardrop", "_preset_complex_pointed",
    "_preset_complex_round", "_preset_complex_asymmetric",
    # 复数整花
    "fourier_complex_flower", "COMPLEX_FLOWER_PRESETS",
    "_auto_flower_coeffs",
    "_preset_flower_simple", "_preset_flower_classic",
    "_preset_flower_lotus", "_preset_flower_star", "_preset_flower_daisy",
    # 花朵排列
    "fourier_flower", "fourier_flowers",
    # 本轮可视化
    "plot_epicycle_flower", "animate_epicycle_flower",
    # 演示
    "demo_all", "demo_compare_coordinates",
]

# ============================================================================
# 第一部分：数学工具
# ============================================================================


def rotate_point(point: Tuple[float, float], theta: float) -> Tuple[float, float]:
    """将二维点绕原点旋转 theta 弧度。"""
    x, y = point
    c, s = np.cos(theta), np.sin(theta)
    return (x * c - y * s, x * s + y * c)


def complex_to_cartesian(z: complex) -> Tuple[float, float]:
    """复数 → 直角坐标"""
    return (z.real, z.imag)


def cartesian_to_complex(x: float, y: float) -> complex:
    """直角坐标 → 复数"""
    return complex(x, y)


# ============================================================================
# 第二部分：极坐标傅里叶花瓣 (Polar Fourier Petal)
# ============================================================================
#
# 花瓣轮廓表示为极角 θ 上的实值函数 r(θ)，通过傅里叶余弦级数逼近。
# 为保证花瓣在根部闭合，要求 r(±π/n) = 0。
#
# 对称性简化：如果花瓣关于中线 θ=0 对称，则只需余弦项（bₘ = 0）：
#   r(θ) = Σₘ₌₀ᴹ aₘ cos(m·n·θ/2)
#
# 其中 a₀ 控制整体尺度，a₁ 控制基本形状，
# a₂, a₃, ... 控制细微波纹（higher harmonics）。


def fourier_polar_petal(
    coeffs: List[float],
    n: int = 6,
    rotation: float = 0.0,
    color: str = "#0f0",
    alpha: float = 1.0,
    center: Tuple[float, float] = (0, 0),
    points: int = 500,
    linestyle: str = "-",
    linewidth: float = 1.0,
    label: Optional[str] = None,
    marker: Optional[str] = None,
    markersize: float = 5.0,
    markerfacecolor: str = "r",
    markeredgecolor: str = "k",
    markeredgewidth: float = 1.0,
    ax=None,
    use_degree: bool = True,
    plot: bool = True,
    **kwargs,
):
    """
    基于极坐标傅里叶级数绘制一片花瓣。

    数学公式：
      r(θ) = Σₘ₌₀ᴹ⁻¹ coeffs[m] · cos(m · n · θ / 2)
      θ ∈ [-π/n, π/n]

      x(θ) = r(θ) · cos(θ + rotation) + center[0]
      y(θ) = r(θ) · sin(θ + rotation) + center[1]

    参数:
        coeffs: 傅里叶余弦系数 [a₀, a₁, a₂, ...]
                a₀ 是 DC 分量，a₁ 是基频（决定基本形状），
                a₂, a₃ 控制高频细节（花瓣边缘的波纹）
        n: 花瓣的"瓣数感"（控制花瓣宽度）
        rotation: 旋转角（度/弧度取决于 use_degree）
        color, alpha, linestyle, linewidth: matplotlib 绘图参数
        center: 花瓣根部中心坐标
        points: 采样点数
        use_degree: True=角度制，False=弧度制
        plot: False 时返回 (x, y) 坐标而不绘图
    """
    if use_degree:
        rotation_rad = np.deg2rad(rotation)
    else:
        rotation_rad = rotation

    M = len(coeffs)
    half_width = np.pi / n
    theta = np.linspace(-half_width, half_width, points)

    # 计算 r(θ) = Σ aₘ cos(m · n · θ / 2)
    r = np.zeros_like(theta)
    for m, am in enumerate(coeffs):
        r += am * np.cos(m * n * theta / 2)

    # 转换到笛卡尔坐标
    x = r * np.cos(theta + rotation_rad) + center[0]
    y = r * np.sin(theta + rotation_rad) + center[1]

    if not plot:
        return x, y

    if ax is None:
        ax = plt.gca()

    ax.plot(
        x, y,
        color=color, alpha=alpha, linestyle=linestyle,
        linewidth=linewidth, label=label, marker=marker,
        markersize=markersize, markerfacecolor=markerfacecolor,
        markeredgecolor=markeredgecolor, markeredgewidth=markeredgewidth,
        **kwargs,
    )
    ax.set_aspect("equal", adjustable="box")
    return ax


# ---- 极坐标预设花瓣形状 ----

def _preset_polar_cos(n: int, harmonics: int = 1) -> List[float]:
    """余弦花瓣：r(θ) = cos(nθ/2)，即 coeffs = [0, 1, 0, 0, ...]"""
    c = [0.0] * (harmonics + 1)
    c[1] = 1.0
    return c


def _preset_polar_sincos(n: int, harmonics: int = 1) -> List[float]:
    """
    sin+cos 花瓣：r(θ) = 0.5cos(nθ/2) + 0.5cos²(nθ/2)
    等效于 coeffs = [0.25, 0.5, 0.25, 0, ...]
    比纯余弦花瓣更饱满
    """
    c = [0.0] * (harmonics + 1)
    if len(c) > 0:
        c[0] = 0.25
    if len(c) > 1:
        c[1] = 0.5
    if len(c) > 2:
        c[2] = 0.25
    return c


def _preset_polar_bell(n: int, harmonics: int = 3) -> List[float]:
    """
    钟形花瓣（Gaussian 近似）：
    r(θ) = exp(-(nθ/π)²) ≈ Σ aₘ cos(mnθ/2)（傅里叶逼近）

    使用前三项傅里叶系数近似高斯函数
    """
    # 对 exp(-(nθ/π)²) 在 [-π/n, π/n] 做数值积分获取系数
    pts = 1000
    half = np.pi / n
    t = np.linspace(-half, half, pts)
    f = np.exp(-(n * t / np.pi) ** 2)
    c = [0.0] * (harmonics + 1)
    for m in range(harmonics + 1):
        integrand = f * np.cos(m * n * t / 2)
        c[m] = 2 * np.trapz(integrand, t) / (2 * half)
        if m == 0:
            c[m] /= 2  # a₀ 是半幅
    return c


def _preset_polar_ripple(n: int, harmonics: int = 3) -> List[float]:
    """
    波纹花瓣：主瓣 + 微小的高频波纹
    r(θ) = cos(nθ/2) + 0.1cos(3nθ/2)
    """
    c = [0.0] * (harmonics + 1)
    c[1] = 1.0
    if len(c) > 3:
        c[3] = 0.1
    return c


def _preset_polar_pointed(n: int, harmonics: int = 2) -> List[float]:
    """
    尖瓣：r(θ) = cos²(nθ/4) 缩放，尖端更锐利
    coeffs = [0.5, 0, 0.5, 0, ...]（但基频是 n/2）
    等效于 coeffs = [0.5, 0.5] 在基频 n 上
    """
    c = [0.0] * (harmonics + 1)
    c[0] = 0.5
    if len(c) > 1:
        c[1] = 0.5
    return c


POLAR_PRESETS = {
    "cos": _preset_polar_cos,
    "sincos": _preset_polar_sincos,
    "bell": _preset_polar_bell,
    "ripple": _preset_polar_ripple,
    "pointed": _preset_polar_pointed,
}


# ============================================================================
# 第三部分：直角坐标傅里叶花瓣 (Cartesian Fourier Petal)
# ============================================================================
#
# 花瓣不再是"角度→半径"的映射，而是参数 t 在区间上描出的 (x(t), y(t)) 轨迹。
# x 和 y 各自用独立的傅里叶级数表示：
#
#   x(t) = a₀ˣ/2 + Σₘ₌₁ᴹ [aₘˣ cos(mt) + bₘˣ sin(mt)]
#   y(t) = a₀ʸ/2 + Σₘ₌₁ᴹ [aₘʸ cos(mt) + bₘʸ sin(mt)]
#
# t ∈ [0, 2π] 描出整片花瓣。花瓣根部在 t=0 和 t=2π 处（闭合于原点）。
#
# 优势：可以描述非星形曲线（极坐标无法表示的形状，如一瓣内的自交）


def fourier_cartesian_petal(
    coeffs_x: Tuple[List[float], List[float]],  # (a_coeffs, b_coeffs)
    coeffs_y: Tuple[List[float], List[float]],  # (a_coeffs, b_coeffs)
    rotation: float = 0.0,
    color: str = "#0f0",
    alpha: float = 1.0,
    center: Tuple[float, float] = (0, 0),
    points: int = 500,
    scale: float = 1.0,
    linestyle: str = "-",
    linewidth: float = 1.0,
    label: Optional[str] = None,
    marker: Optional[str] = None,
    markersize: float = 5.0,
    markerfacecolor: str = "r",
    markeredgecolor: str = "k",
    markeredgewidth: float = 1.0,
    ax=None,
    use_degree: bool = True,
    plot: bool = True,
    **kwargs,
):
    """
    基于直角坐标傅里叶级数绘制一片花瓣。

    数学公式：
      x(t) = scale · [Σₘ aₘˣ cos(mt) + Σₘ bₘˣ sin(mt)]   (a₀ˣ 为 DC)
      y(t) = scale · [Σₘ aₘʸ cos(mt) + Σₘ bₘʸ sin(mt)]   (a₀ʸ 为 DC)
      t ∈ [0, 2π]

    参数:
        coeffs_x: (a_list, b_list) — x(t) 的余弦和正弦系数
                  其中 a[0] 是 DC 分量 (a₀ˣ), b[0] 固定为 0（可填任意值占位）
        coeffs_y: (a_list, b_list) — y(t) 的余弦和正弦系数
        rotation: 旋转角度
        scale: 整体缩放因子
        其他参数同 fourier_polar_petal
    """
    if use_degree:
        rotation_rad = np.deg2rad(rotation)
    else:
        rotation_rad = rotation

    ax_cos, ax_sin = coeffs_x
    ay_cos, ay_sin = coeffs_y

    t = np.linspace(0, 2 * np.pi, points)

    # x(t)
    x = np.full_like(t, ax_cos[0] / 2) if len(ax_cos) > 0 else np.zeros_like(t)
    for m, am in enumerate(ax_cos[1:], 1):
        x += am * np.cos(m * t)
    for m, bm in enumerate(ax_sin[1:], 1):
        x += bm * np.sin(m * t)

    # y(t)
    y = np.full_like(t, ay_cos[0] / 2) if len(ay_cos) > 0 else np.zeros_like(t)
    for m, am in enumerate(ay_cos[1:], 1):
        y += am * np.cos(m * t)
    for m, bm in enumerate(ay_sin[1:], 1):
        y += bm * np.sin(m * t)

    x *= scale
    y *= scale

    # 旋转
    c, s = np.cos(rotation_rad), np.sin(rotation_rad)
    x_rot = x * c - y * s + center[0]
    y_rot = x * s + y * c + center[1]

    if not plot:
        return x_rot, y_rot

    if ax is None:
        ax = plt.gca()

    ax.plot(
        x_rot, y_rot,
        color=color, alpha=alpha, linestyle=linestyle,
        linewidth=linewidth, label=label, marker=marker,
        markersize=markersize, markerfacecolor=markerfacecolor,
        markeredgecolor=markeredgecolor, markeredgewidth=markeredgewidth,
        **kwargs,
    )
    ax.set_aspect("equal", adjustable="box")
    return ax


# ---- 直角坐标预设花瓣形状 ----

def _preset_cartesian_teardrop() -> Tuple[Tuple, Tuple]:
    """
    泪滴花瓣 —— 经典 petal 形状
    x(t) = sin(2t)/2    （仅 sin 项）
    y(t) = 1/2 - cos(2t)/2  （DC + cos 项）

    这是 z(t) = sin(t)·e^{it} 的直角坐标等价形式
    t ∈ [0, π] 描出完整花瓣，但这里用 t ∈ [0, 2π] 描两次
    """
    ax = [0.0, 0.0, 0.0]    # a₀ˣ=0, a₁ˣ=0, a₂ˣ=0
    bx = [0.0, 0.0, 0.5]    # b₁ˣ=0, b₂ˣ=0.5
    ay = [1.0, 0.0, -0.5]   # a₀ʸ=1, a₁ʸ=0, a₂ʸ=-0.5
    by = [0.0, 0.0, 0.0]    # b₁ʸ=0, b₂ʸ=0
    return ((ax, bx), (ay, by))


def _preset_cartesian_leaf() -> Tuple[Tuple, Tuple]:
    """
    叶形花瓣 —— 略扁的 petal
    x(t) = sin(t)
    y(t) = sin(t)·cos(t) = sin(2t)/2
    """
    ax = [0.0, 0.0]         # a₀ˣ=0, a₁ˣ=0
    bx = [0.0, 1.0]         # b₁ˣ=1
    ay = [0.0, 0.0, 0.0]    # a₀ʸ=0, a₁ʸ=0, a₂ʸ=0
    by = [0.0, 0.0, 0.5]    # b₁ʸ=0, b₂ʸ=0.5
    return ((ax, bx), (ay, by))


def _preset_cartesian_heart() -> Tuple[Tuple, Tuple]:
    """
    心形花瓣 —— 有"肩部"的 petal
    x(t) = sin(t) + sin(2t)/2   （不等宽）
    y(t) = 1 - cos(t)            （从原点出发回到原点）
    """
    ax = [0.0, -1.0]         # a₀ˣ=0, a₁ˣ=-1 (cos→转换)
    bx = [0.0, 1.0, 0.5]    # b₁ˣ=1, b₂ˣ=0.5
    ay = [2.0, 0.0]          # a₀ʸ=2
    by = [0.0, 0.0]
    return ((ax, bx), (ay, by))


def _preset_cartesian_diamond() -> Tuple[Tuple, Tuple]:
    """
    钻石形花瓣 —— 更几何化的形状
    x(t) = sin(t)
    y(t) = |sin(t)| 的平滑近似
    使用傅里叶级数：|sin(t)| ≈ 2/π - 4/π Σ cos(2kt)/(4k²-1)
    """
    # y(t) = 2/π - (4/π)·cos(2t)/3 - (4/π)·cos(4t)/15
    pi = np.pi
    ax = [0.0, 0.0]
    bx = [0.0, 1.0]
    ay = [4/pi, 0.0, -4/(3*pi), 0.0, -4/(15*pi)]
    by = [0.0, 0.0, 0.0, 0.0, 0.0]
    return ((ax, bx), (ay, by))


CARTESIAN_PRESETS = {
    "teardrop": _preset_cartesian_teardrop,
    "leaf": _preset_cartesian_leaf,
    "heart": _preset_cartesian_heart,
    "diamond": _preset_cartesian_diamond,
}


# ============================================================================
# 第四部分：复数坐标傅里叶花瓣 (Complex Fourier Petal)
# ============================================================================
#
# 这是三种表示中最优雅的一种。
#
# 复数傅里叶级数将 x(t) 和 y(t) 统一为一个复函数：
#
#   z(t) = x(t) + i·y(t) = Σₖ₌₋ᴷᴷ cₖ · e^{ikt}
#
# 其中 cₖ = |cₖ|·e^{iφₖ} ∈ ℂ 是第 k 个傅里叶系数。
#
# 每个 cₖ 的几何意义：
#   - |cₖ|：第 k 个"本轮"(epicycle) 的半径
#   - arg(cₖ)：该本轮的初始相位
#   - k：该本轮的旋转频率（正=逆时针，负=顺时针）
#
# 代数运算的优美性：
#   - 旋转 φ：z(t) → e^{iφ}·z(t)（乘以单位复数）
#   - 平移 (dx,dy)：z(t) → z(t) + (dx + i·dy)
#   - 缩放 s：z(t) → s·z(t)


def fourier_complex_petal(
    coeffs: Dict[int, complex],
    rotation: float = 0.0,
    color: str = "#0f0",
    alpha: float = 1.0,
    center: Tuple[float, float] = (0, 0),
    points: int = 500,
    scale: float = 1.0,
    reverse: bool = False,
    linestyle: str = "-",
    linewidth: float = 1.0,
    label: Optional[str] = None,
    marker: Optional[str] = None,
    markersize: float = 5.0,
    markerfacecolor: str = "r",
    markeredgecolor: str = "k",
    markeredgewidth: float = 1.0,
    ax=None,
    use_degree: bool = True,
    plot: bool = True,
    **kwargs,
):
    """
    基于复数傅里叶级数绘制一片花瓣。

    数学公式：
      z(t) = scale · e^{i·rot} · Σₖ cₖ e^{ikt} + center_complex
      t ∈ [0, 2π]

    参数:
        coeffs: {频率k: 复系数cₖ} 的字典
                例如 {1: 0.5j, 2: -0.25j} 表示 c₁=0.5i, c₂=-0.25i
        rotation: 旋转角度
        scale: 整体缩放
        reverse: True 则反向遍历 t（翻转花瓣朝向）
        其他参数同 fourier_polar_petal
    """
    if use_degree:
        rotation_rad = np.deg2rad(rotation)
    else:
        rotation_rad = rotation

    t = np.linspace(0, 2 * np.pi, points)

    # 计算 z(t) = Σ cₖ e^{ikt}
    z = np.zeros(points, dtype=complex)
    for k, ck in coeffs.items():
        z += ck * np.exp(1j * k * t)

    # 缩放、旋转、平移
    z = scale * np.exp(1j * rotation_rad) * z
    center_c = complex(center[0], center[1])
    z += center_c

    x, y = z.real, z.imag

    if not plot:
        return x, y

    if ax is None:
        ax = plt.gca()

    ax.plot(
        x, y,
        color=color, alpha=alpha, linestyle=linestyle,
        linewidth=linewidth, label=label, marker=marker,
        markersize=markersize, markerfacecolor=markerfacecolor,
        markeredgecolor=markeredgecolor, markeredgewidth=markeredgewidth,
        **kwargs,
    )
    ax.set_aspect("equal", adjustable="box")
    return ax


# ---- 复数预设花瓣形状 ----

def _preset_complex_teardrop() -> Dict[int, complex]:
    """
    泪滴花瓣 —— 最经典的 petal
    z(t) = sin(t)·e^{it} = i/2 - (i/2)·e^{2it}
    即 c₀ = i/2, c₂ = -i/2
    t ∈ [0, π] 描出单个瓣，t ∈ [0, 2π] 描两次
    """
    return {0: 0.5j, 2: -0.5j}


def _preset_complex_pointed() -> Dict[int, complex]:
    """
    尖瓣 —— 比泪滴更锐利的尖端
    z(t) = sin²(t)·e^{it} = -e^{-it}/4 + e^{it}/2 - e^{3it}/4
    即 c₋₁ = -0.25, c₁ = 0.5, c₃ = -0.25
    """
    return {-1: -0.25 + 0j, 1: 0.5 + 0j, 3: -0.25 + 0j}


def _preset_complex_round() -> Dict[int, complex]:
    """
    圆瓣 —— 更圆润的花瓣
    z(t) = sqrt(sin(t))·e^{it} 的傅里叶逼近

    通过数值积分获取前几项系数
    """
    pts = 2000
    t = np.linspace(0, np.pi, pts)
    # 避免 sin(0)=sin(π)=0 处的奇点
    sin_t = np.maximum(np.sin(t), 1e-10)
    z_t = np.sqrt(sin_t) * np.exp(1j * t)
    # 对 z(t) 在 [0, 2π] 上做傅里叶分析
    # 扩展到 [π, 2π]（设为零或镜像）
    z_full = np.zeros(2 * pts, dtype=complex)
    z_full[:pts] = z_t
    t_full = np.linspace(0, 2 * np.pi, 2 * pts)
    coeffs = {}
    for k in range(-5, 6):
        ck = np.trapz(z_full * np.exp(-1j * k * t_full), t_full) / (2 * np.pi)
        if abs(ck) > 0.005:
            coeffs[k] = ck
    return coeffs


def _preset_complex_asymmetric() -> Dict[int, complex]:
    """
    不对称花瓣 —— 类似马蹄莲
    z(t) = sin(t)·e^{it} + 0.2·sin(3t)·e^{i(2t)}
    一边比另一边更突出
    """
    return {0: 0.5j, 2: -0.5j, -1: 0.1, 3: -0.1}


COMPLEX_PETAL_PRESETS = {
    "teardrop": _preset_complex_teardrop,
    "pointed": _preset_complex_pointed,
    "round": _preset_complex_round,
    "asymmetric": _preset_complex_asymmetric,
}


# ============================================================================
# 第五部分：复数傅里叶整花 (Complex Fourier Flower)
# ============================================================================
#
# 这是傅里叶方法最强大的特性：整朵花可以用一个复数傅里叶级数直接生成，
# 而不需要逐瓣拼接。
#
# 核心定理（n 重旋转对称性约束）：
#
#   若 z(t) = Σ cₖ e^{ikt} 满足 n 重旋转对称性：
#     z(t + 2π/n) = e^{2πi/n} · z(t)
#
#   则 cₖ ≠ 0 仅当 k ≡ 1 (mod n)，即：
#     k ∈ {..., 1-2n, 1-n, 1, 1+n, 1+2n, ...}
#
# 证明：
#   z(t + 2π/n) = Σ cₖ e^{ik(t+2π/n)} = Σ cₖ e^{2πik/n} e^{ikt}
#   e^{2πi/n} z(t) = Σ cₖ e^{2πi/n} e^{ikt}
#   等式成立 ⇔ ∀k: cₖ e^{2πik/n} = cₖ e^{2πi/n}
#   ⇔ 若 cₖ ≠ 0 则 e^{2πik/n} = e^{2πi/n} ⇔ k ≡ 1 (mod n)
#
# 这个约束极其强大：只需指定少数几个系数就能生成有 n 片完整花瓣的花朵！


def fourier_complex_flower(
    n_petals: int = 6,
    coeffs: Optional[Dict[int, complex]] = None,
    num_harmonics: int = 5,
    rotation: float = 0.0,
    color: str = "#0f0",
    alpha: float = 1.0,
    center: Tuple[float, float] = (0, 0),
    points: int = 2000,
    scale: float = 1.0,
    linestyle: str = "-",
    linewidth: float = 1.0,
    label: Optional[str] = None,
    marker: Optional[str] = None,
    markersize: float = 5.0,
    markerfacecolor: str = "r",
    markeredgecolor: str = "k",
    markeredgewidth: float = 1.0,
    ax=None,
    use_degree: bool = True,
    plot: bool = True,
    show_epicycles: bool = False,
    epicycle_frame: Optional[int] = None,
    **kwargs,
):
    """
    用单个复数傅里叶级数生成整朵花（n 重旋转对称）。

    数学公式：
      z(t) = scale · e^{i·rot} · Σ cₖ e^{ikt} + center
      其中 k 满足 k ≡ 1 (mod n_petals)

    参数:
        n_petals: 花瓣数量
        coeffs: 手动指定系数。若为 None，使用自动生成系数
        num_harmonics: 自动生成系数时的谐波数量
        rotation: 整体旋转角
        scale: 整体缩放
        show_epicycles: True 则在图上叠加本轮圆（可视化傅里叶分量）
        epicycle_frame: 若不为 None，显示该帧的本轮状态（与 animation 配合）
        其他参数同 fourier_polar_petal

    返回:
        (x, y) 坐标数组（若 plot=False），否则返回 artist list（若 show_epicycles）
    """
    if use_degree:
        rotation_rad = np.deg2rad(rotation)
    else:
        rotation_rad = rotation

    # 自动生成系数（若未手动指定）
    if coeffs is None:
        coeffs = _auto_flower_coeffs(n_petals, num_harmonics)

    # 验证对称性约束
    for k in coeffs:
        if (k - 1) % n_petals != 0:
            warnings.warn(
                f"系数 c_{k} 不满足 n={n_petals} 重对称性约束 (k≡1 mod n)。"
                f"花朵可能不对称。"
            )

    t = np.linspace(0, 2 * np.pi, points)

    # 计算 z(t)
    z = np.zeros(points, dtype=complex)
    for k, ck in coeffs.items():
        z += ck * np.exp(1j * k * t)

    z = scale * np.exp(1j * rotation_rad) * z
    center_c = complex(center[0], center[1])
    z += center_c

    if not plot:
        return z.real, z.imag

    if ax is None:
        ax = plt.gca()

    ax.plot(
        z.real, z.imag,
        color=color, alpha=alpha, linestyle=linestyle,
        linewidth=linewidth, label=label, marker=marker,
        markersize=markersize, markerfacecolor=markerfacecolor,
        markeredgecolor=markeredgecolor, markeredgewidth=markeredgewidth,
        **kwargs,
    )
    ax.set_aspect("equal", adjustable="box")

    # 本轮可视化
    if show_epicycles and epicycle_frame is not None:
        _draw_epicycles_at_frame(
            ax, coeffs, t[epicycle_frame], rotation_rad, scale, center_c
        )

    return ax


def _auto_flower_coeffs(n_petals: int, num_harmonics: int = 5) -> Dict[int, complex]:
    """
    自动生成有视觉吸引力的花朵系数。

    策略：从基频 k=1 开始，向高低两端扩展。
    系数幅度随 |k-1| 增大而衰减，相位交替以形成花瓣凹陷。
    """
    coeffs = {}
    # 基频：k = 1（主圆分量）
    coeffs[1] = complex(1.0, 0.0)

    # 负频率方向（产生花瓣的"内凹"）
    for j in range(1, num_harmonics):
        k_neg = 1 - j * n_petals
        amp = 0.35 / j  # 幅度随阶数衰减
        phase = np.pi / 2  # 纯虚数系数产生内凹
        coeffs[k_neg] = amp * np.exp(1j * phase)

    # 正频率方向（添加细节）
    for j in range(1, min(num_harmonics, 3)):
        k_pos = 1 + j * n_petals
        amp = 0.12 / j
        phase = 0
        coeffs[k_pos] = amp * np.exp(1j * phase)

    return coeffs


def _draw_epicycles_at_frame(
    ax, coeffs: Dict[int, complex], t_val: float,
    rotation_rad: float, scale: float, center_c: complex,
):
    """在 ax 上绘制给定时刻的本轮圆和连线。"""
    # 按频率排序
    sorted_keys = sorted(coeffs.keys())

    # 从原点开始叠加本轮
    current = complex(0, 0)
    for k in sorted_keys:
        ck = coeffs[k] * scale
        arm = ck * np.exp(1j * k * t_val)
        next_point = current + arm
        # 绘制本轮圆
        radius = abs(ck)
        if radius > 0.005:
            circle = plt.Circle(
                (current.real, current.imag), radius,
                fill=False, color='gray', alpha=0.3, linewidth=0.5,
            )
            ax.add_patch(circle)
        # 绘制连线
        ax.plot(
            [current.real, next_point.real],
            [current.imag, next_point.imag],
            color='gray', alpha=0.5, linewidth=0.8,
        )
        current = next_point

    # 旋转 + 平移
    current = current * np.exp(1j * rotation_rad) + center_c
    ax.scatter([current.real], [current.imag], color='red', s=20, zorder=10)


# ---- 复数整花预设 ----

def _preset_flower_simple(n: int) -> Dict[int, complex]:
    """简单花朵：仅两个频率分量"""
    return {1: 1.0 + 0j, 1 - n: 0.3j}


def _preset_flower_classic(n: int) -> Dict[int, complex]:
    """经典花朵：三频率，有花瓣深度和轻微细节"""
    return {1: 1.0 + 0j, 1 - n: 0.3j, 1 + n: 0.1 + 0j}


def _preset_flower_lotus(n: int) -> Dict[int, complex]:
    """莲花：多重谐波产生层叠效果"""
    return {
        1: 1.0 + 0j,
        1 - n: 0.35j,
        1 + n: 0.12 + 0j,
        1 - 2 * n: 0.08j,
    }


def _preset_flower_star(n: int) -> Dict[int, complex]:
    """星形花：更深的凹陷"""
    return {1: 1.0 + 0j, 1 - n: 0.5j, 1 - 2 * n: 0.15j}


def _preset_flower_daisy(n: int) -> Dict[int, complex]:
    """雏菊：浅凹陷、高频波纹"""
    return {
        1: 1.0 + 0j,
        1 - n: 0.2j,
        1 + n: 0.08 + 0j,
        1 - 2 * n: 0.05j,
        1 + 2 * n: 0.03 + 0j,
    }


COMPLEX_FLOWER_PRESETS = {
    "simple": _preset_flower_simple,
    "classic": _preset_flower_classic,
    "lotus": _preset_flower_lotus,
    "star": _preset_flower_star,
    "daisy": _preset_flower_daisy,
}


# ============================================================================
# 第六部分：花朵排列 (Flower Arrangement)
# ============================================================================
#
# 将上述三种花瓣原语排列成完整花朵。
# 对于复数整花 (fourier_complex_flower)，不需要此步骤（花已是整体生成）。


def fourier_flower(
    petal_func: Callable,
    n_petals: int = 12,
    petal_kwargs: Optional[dict] = None,
    rotation: float = 0.0,
    use_degree: bool = True,
    color: str = "#0f0",
    alpha: float = 1.0,
    center: Tuple[float, float] = (0, 0),
    ax=None,
    plot: bool = True,
    **global_kwargs,
):
    """
    将任意花瓣函数排列成完整花朵。

    参数:
        petal_func: 花瓣绘制函数，必须接受 rotation= 和 color= 参数
        n_petals: 花瓣数量
        petal_kwargs: 传递给 petal_func 的额外参数
        rotation: 整体旋转角
        color: 花瓣颜色（所有花瓣统一颜色）
        其他参数传递给 petal_func

    示例:
        # 极坐标花瓣花朵
        coeffs = [0.0, 1.0]  # cos 花瓣
        fourier_flower(
            fourier_polar_petal,
            n_petals=8,
            petal_kwargs={'coeffs': coeffs, 'n': 6, 'use_degree': False},
            color='#ff6b6b',
        )
    """
    if petal_kwargs is None:
        petal_kwargs = {}

    if use_degree:
        rot_step = 360.0 / n_petals
        rot_start = rotation
    else:
        rot_step = 2 * np.pi / n_petals
        rot_start = np.deg2rad(rotation) if use_degree else rotation

    for i in range(n_petals):
        petal_rot = rot_start + i * rot_step
        petal_func(
            rotation=petal_rot,
            color=color,
            alpha=alpha,
            center=center,
            ax=ax,
            plot=plot,
            use_degree=use_degree,
            **petal_kwargs,
            **global_kwargs,
        )


def fourier_flowers(
    petal_func: Callable,
    n_petals: int = 12,
    n_layers: int = 3,
    ratio: float = np.sqrt(2),
    petal_kwargs: Optional[dict] = None,
    rotation: float = 0.0,
    use_degree: bool = False,  # 多层花默认弧度制
    color: str = "b",
    alpha: float = 1.0,
    center: Tuple[float, float] = (0, 0),
    ax=None,
    plot: bool = True,
    **global_kwargs,
):
    """
    多层花朵：等比缩放 + 层间错位。

    第 j 层（j=1,2,...,n_layers）：
      - 缩放因子 s_j = ratio^{j-1}
      - 旋转偏移 Δθ_j = (j-1)·π/n_petals（半瓣错位）

    参数:
        petal_func: 花瓣绘制函数
        n_petals: 每层花瓣数
        n_layers: 层数
        ratio: 层间缩放比（>1 外层更大，<1 外层更小）
        petal_kwargs: 基础花瓣参数（不含旋转）
        rotation: 整体旋转（弧度）
    """
    if petal_kwargs is None:
        petal_kwargs = {}

    for j in range(1, n_layers + 1):
        sj = ratio ** (j - 1)
        layer_rotation_offset = (j - 1) * np.pi / n_petals

        for i in range(n_petals):
            rot = 2 * np.pi * i / n_petals + layer_rotation_offset + rotation + np.pi / 2

            # 计算本层缩放后的参数
            layer_kwargs = dict(petal_kwargs)
            # 如果花瓣函数接受 scale 参数
            if 'scale' not in layer_kwargs:
                layer_kwargs['scale'] = sj
            else:
                layer_kwargs['scale'] = layer_kwargs.get('scale', 1.0) * sj

            petal_func(
                rotation=rot,
                color=color,
                alpha=alpha,
                center=center,
                ax=ax,
                plot=plot,
                use_degree=False,
                **layer_kwargs,
                **global_kwargs,
            )


# ============================================================================
# 第七部分：本轮可视化与动画 (Epicycle Visualization)
# ============================================================================


def plot_epicycle_flower(
    n_petals: int = 6,
    coeffs: Optional[Dict[int, complex]] = None,
    num_harmonics: int = 5,
    figsize: Tuple[float, float] = (10, 10),
    color: str = "#0f0",
    alpha: float = 1.0,
    scale: float = 1.0,
    rotation: float = 0.0,
    use_degree: bool = True,
    save_path: Optional[str] = None,
):
    """
    绘制带本轮可视化的花朵静态图。

    显示两个子图：
      左：完整的本轮图（所有圆 + 连线在 t=0 时刻）
      右：花朵曲线 + 单个本轮快照
    """
    if coeffs is None:
        coeffs = _auto_flower_coeffs(n_petals, num_harmonics)

    if use_degree:
        rotation_rad = np.deg2rad(rotation)
    else:
        rotation_rad = rotation

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    # 左图：本轮结构
    sorted_keys = sorted(coeffs.keys(), key=lambda k: (-abs(k), k))
    ax1.set_title(f"Epicycle Structure\nn={n_petals} petals, {len(coeffs)} frequencies")
    ax1.set_aspect("equal")
    ax1.axis("off")

    current = complex(0, 0)
    for k in sorted_keys:
        ck = coeffs[k] * scale
        radius = abs(ck)
        if radius > 0.001:
            circle = plt.Circle(
                (current.real, current.imag), radius,
                fill=False, color='steelblue', alpha=0.6, linewidth=1.2,
            )
            ax1.add_patch(circle)
            # 标注频率
            ax1.annotate(
                f"k={k}", (current.real, current.imag),
                fontsize=8, color='steelblue',
                xytext=(5, 5), textcoords='offset points',
            )
        # 连线到下一个中心
        next_center = current + ck  # t=0 时 e^{ikt}=1
        ax1.plot(
            [current.real, next_center.real],
            [current.imag, next_center.imag],
            'o-', color='coral', linewidth=0.8, markersize=2,
        )
        current = next_center

    ax1.autoscale_view()

    # 右图：花朵曲线 + 一个时刻的本轮
    ax2.set_title(f"Flower Curve + Epicycle Snapshot (t=0)")
    ax2.set_aspect("equal")

    t = np.linspace(0, 2 * np.pi, 2000)
    z = np.zeros(2000, dtype=complex)
    for k, ck in coeffs.items():
        z += ck * np.exp(1j * k * t)
    z = scale * np.exp(1j * rotation_rad) * z

    ax2.plot(z.real, z.imag, color=color, alpha=alpha, linewidth=1.5)
    _draw_epicycles_at_frame(ax2, coeffs, 0.0, rotation_rad, scale, complex(0, 0))
    ax2.axis("off")

    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")

    return fig


def animate_epicycle_flower(
    n_petals: int = 6,
    coeffs: Optional[Dict[int, complex]] = None,
    num_harmonics: int = 5,
    figsize: Tuple[float, float] = (8, 8),
    color: str = "#0f0",
    alpha: float = 1.0,
    scale: float = 1.0,
    rotation: float = 0.0,
    use_degree: bool = True,
    n_frames: int = 360,
    interval: int = 30,
    save_path: Optional[str] = None,
):
    """
    动画：本轮旋转画出花朵。

    显示：
      - 花朵的完整轮廓（浅色背景）
      - 实时旋转的本轮和连线
      - 红色轨迹点，其路径画出花朵

    参数:
        n_frames: 动画帧数
        interval: 帧间隔（毫秒）
        save_path: 若提供，保存为 GIF/MP4
    """
    if coeffs is None:
        coeffs = _auto_flower_coeffs(n_petals, num_harmonics)

    if use_degree:
        rotation_rad = np.deg2rad(rotation)
    else:
        rotation_rad = rotation

    # 预计算完整花朵曲线
    t_full = np.linspace(0, 2 * np.pi, 1000)
    z_full = np.zeros(1000, dtype=complex)
    for k, ck in coeffs.items():
        z_full += ck * np.exp(1j * k * t_full)
    z_full = scale * np.exp(1j * rotation_rad) * z_full

    sorted_keys = sorted(coeffs.keys())

    fig, ax = plt.subplots(figsize=figsize)
    ax.set_aspect("equal")
    ax.axis("off")

    # 背景：淡色完整花朵
    ax.plot(z_full.real, z_full.imag, color=color, alpha=0.2, linewidth=1)

    # 动态元素
    epicycle_lines = []
    epicycle_circles = []
    for _ in sorted_keys:
        line, = ax.plot([], [], color='gray', alpha=0.5, linewidth=0.8)
        epicycle_lines.append(line)
        # circles 作为 patches 动态添加
    trace_line, = ax.plot([], [], color=color, alpha=alpha, linewidth=1.5)
    tip_point, = ax.plot([], [], 'ro', markersize=4)

    trace_x, trace_y = [], []

    def init():
        for line in epicycle_lines:
            line.set_data([], [])
        trace_line.set_data([], [])
        tip_point.set_data([], [])
        return epicycle_lines + [trace_line, tip_point]

    def update(frame):
        t_val = 2 * np.pi * frame / n_frames

        # 清除旧的圆圈
        for patch in list(ax.patches):
            patch.remove()

        # 计算本轮
        current = complex(0, 0)
        for idx, k in enumerate(sorted_keys):
            ck = coeffs[k] * scale
            arm = ck * np.exp(1j * k * t_val)
            next_point = current + arm

            # 本轮圆
            radius = abs(ck)
            if radius > 0.001:
                circle = plt.Circle(
                    (current.real, current.imag), radius,
                    fill=False, color='gray', alpha=0.3, linewidth=0.5,
                )
                ax.add_patch(circle)

            # 连线
            epicycle_lines[idx].set_data(
                [current.real, next_point.real],
                [current.imag, next_point.imag],
            )
            current = next_point

        # 旋转并平移
        tip = current * np.exp(1j * rotation_rad)
        trace_x.append(tip.real)
        trace_y.append(tip.imag)

        tip_point.set_data([tip.real], [tip.imag])
        trace_line.set_data(trace_x, trace_y)

        return epicycle_lines + [trace_line, tip_point]

    ani = FuncAnimation(
        fig, update, frames=n_frames, init_func=init,
        interval=interval, blit=True,
    )

    if save_path:
        ani.save(save_path, writer='pillow', fps=30, dpi=100)

    return fig, ani


# ============================================================================
# 第八部分：综合示例
# ============================================================================


def demo_all():
    """
    运行完整演示，展示三种坐标系 + 复数整花 + 本轮可视化。

    用法：
        from cprdspy.CPR_matplotlib.Flowers.fourier_flower import demo_all
        demo_all()
    """
    fig, axes = plt.subplots(3, 3, figsize=(18, 18))
    fig.suptitle(
        "Fourier Flowers — 3 Coordinate Systems x Multiple Styles",
        fontsize=16, fontweight='bold', y=0.98,
    )

    # ---- 第一行：极坐标 ----
    axes[0, 0].set_title("Polar: cos petal (n=6, N=12)")
    polar_coeffs = _preset_polar_cos(6, harmonics=2)
    for i in range(12):
        rot_deg = i * 30
        fourier_polar_petal(
            polar_coeffs, n=6, rotation=rot_deg,
            color="#ff6b6b", alpha=0.8, ax=axes[0, 0],
            use_degree=True, linewidth=1.5,
        )
    axes[0, 0].set_aspect("equal")
    axes[0, 0].axis("off")

    axes[0, 1].set_title("Polar: ripple petal (n=8, N=8)")
    ripple_coeffs = _preset_polar_ripple(8, harmonics=4)
    for i in range(8):
        fourier_polar_petal(
            ripple_coeffs, n=8, rotation=i * 45 + 22.5,
            color="#6bc5ff", alpha=0.8, ax=axes[0, 1],
            use_degree=True, linewidth=1.5,
        )
    axes[0, 1].set_aspect("equal")
    axes[0, 1].axis("off")

    axes[0, 2].set_title("Polar: bell petal (n=5, N=10)")
    bell_coeffs = _preset_polar_bell(5, harmonics=4)
    for i in range(10):
        fourier_polar_petal(
            bell_coeffs, n=5, rotation=i * 36,
            color="#ffd93d", alpha=0.8, ax=axes[0, 2],
            use_degree=True, linewidth=1.5,
        )
    axes[0, 2].set_aspect("equal")
    axes[0, 2].axis("off")

    # ---- 第二行：直角坐标 + 复数花瓣 ----
    axes[1, 0].set_title("Cartesian: teardrop (N=8)")
    cx, cy = _preset_cartesian_teardrop()
    for i in range(8):
        fourier_cartesian_petal(
            cx, cy, rotation=i * 45,
            color="#ff9ff3", alpha=0.8, scale=0.8,
            ax=axes[1, 0], use_degree=True, linewidth=1.5,
        )
    axes[1, 0].set_aspect("equal")
    axes[1, 0].axis("off")

    axes[1, 1].set_title("Cartesian: leaf (N=6)")
    cx, cy = _preset_cartesian_leaf()
    for i in range(6):
        fourier_cartesian_petal(
            cx, cy, rotation=i * 60 + 30,
            color="#48dbfb", alpha=0.8, scale=1.2,
            ax=axes[1, 1], use_degree=True, linewidth=1.5,
        )
    axes[1, 1].set_aspect("equal")
    axes[1, 1].axis("off")

    axes[1, 2].set_title("Cartesian: heart (N=5)")
    cx, cy = _preset_cartesian_heart()
    for i in range(5):
        fourier_cartesian_petal(
            cx, cy, rotation=i * 72 + 36,
            color="#f368e0", alpha=0.8, scale=0.6,
            ax=axes[1, 2], use_degree=True, linewidth=1.5,
        )
    axes[1, 2].set_aspect("equal")
    axes[1, 2].axis("off")

    # ---- 第三行：复数整花 ----
    axes[2, 0].set_title("Complex Flower: classic (n=6)")
    fourier_complex_flower(
        n_petals=6, coeffs=_preset_flower_classic(6),
        color="#00d2d3", alpha=0.9, scale=1.2,
        ax=axes[2, 0], use_degree=False, linewidth=1.5,
    )
    axes[2, 0].set_aspect("equal")
    axes[2, 0].axis("off")

    axes[2, 1].set_title("Complex Flower: lotus (n=8)")
    fourier_complex_flower(
        n_petals=8, coeffs=_preset_flower_lotus(8),
        color="#feca57", alpha=0.9, scale=1.2,
        ax=axes[2, 1], use_degree=False, linewidth=1.5,
    )
    axes[2, 1].set_aspect("equal")
    axes[2, 1].axis("off")

    axes[2, 2].set_title("Complex Flower: star (n=5)")
    fourier_complex_flower(
        n_petals=5, coeffs=_preset_flower_star(5),
        color="#ff6348", alpha=0.9, scale=1.2,
        ax=axes[2, 2], use_degree=False, linewidth=1.5,
    )
    axes[2, 2].set_aspect("equal")
    axes[2, 2].axis("off")

    fig.tight_layout()
    return fig


def demo_compare_coordinates():
    """
    演示：同一几何形状在三种坐标系下的等价表示。

    泪滴花瓣 (teardrop) 在三种表示下的等价形式：

    直角坐标:  x(t) = sin(2t)/2,  y(t) = 1/2 - cos(2t)/2
    复数坐标:  z(t) = sin(t)·e^{it}  →  c₀=i/2, c₂=-i/2
    极坐标:    r(θ) = |z(θ)|, 需要从 z(t) 反解 t → θ
    """
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle("Same Teardrop Petal in 3 Equivalent Representations", fontsize=14, fontweight='bold')

    # 直角坐标
    axes[0].set_title("Cartesian\nx=sin(2t)/2, y=1/2-cos(2t)/2")
    cx, cy = _preset_cartesian_teardrop()
    fourier_cartesian_petal(cx, cy, ax=axes[0], use_degree=False, scale=1.5, linewidth=2)
    axes[0].set_xlim(-1.5, 1.5)
    axes[0].set_ylim(-0.5, 2.5)
    axes[0].set_aspect("equal")
    axes[0].grid(True, alpha=0.3)

    # 复数坐标
    axes[1].set_title("Complex\nz = sin(t)·e^{it}, c₀=i/2, c₂=-i/2")
    cz = _preset_complex_teardrop()
    fourier_complex_petal(cz, ax=axes[1], use_degree=False, scale=1.5, linewidth=2)
    axes[1].set_xlim(-1.5, 1.5)
    axes[1].set_ylim(-0.5, 2.5)
    axes[1].set_aspect("equal")
    axes[1].grid(True, alpha=0.3)

    # 极坐标
    axes[2].set_title("Polar\nr(θ)=sin(θ) for θ∈[0,π]")
    # 极坐标中 r(θ) = sin(θ)（在 θ ∈ [0,π] 上）描出圆
    # cos petal 近似
    for i in range(6):
        rot_deg = i * 60
        fourier_polar_petal(
            [0, 1], n=6, rotation=rot_deg, color="#0f0",
            alpha=0.8, ax=axes[2], use_degree=True, linewidth=1.5,
        )
    axes[2].set_xlim(-2, 2)
    axes[2].set_ylim(-2, 2)
    axes[2].set_aspect("equal")
    axes[2].grid(True, alpha=0.3)

    fig.tight_layout()
    return fig


# ============================================================================
# 使用说明
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Fourier Flower — 傅里叶花瓣/花朵生成模块")
    print("=" * 60)
    print()
    print("三种坐标系：")
    print("  1. 极坐标  — fourier_polar_petal()")
    print("     r(θ) = Σ aₘ cos(m·n·θ/2)")
    print()
    print("  2. 直角坐标 — fourier_cartesian_petal()")
    print("     x(t) = Σ aₘˣ cos(mt) + bₘˣ sin(mt)")
    print("     y(t) = Σ aₘʸ cos(mt) + bₘʸ sin(mt)")
    print()
    print("  3. 复数坐标 — fourier_complex_petal()")
    print("     z(t) = Σ cₖ e^{ikt}")
    print()
    print("  4. 复数整花 — fourier_complex_flower()")
    print("     利用 n 重旋转对称性约束，单条公式生成整朵花")
    print("     cₖ ≠ 0 仅当 k ≡ 1 (mod n)")
    print()
    print("本轮可视化：")
    print("  - plot_epicycle_flower() — 静态本轮结构图")
    print("  - animate_epicycle_flower() — 动画：本轮旋转画出花朵")
    print()
    print("运行 demo_all() 查看所有风格的综合演示。")
    print("运行 demo_compare_coordinates() 查看同一形状的三种等价表示。")
    print()

    # 运行演示
    try:
        print("正在运行演示...")
        demo_all()
        plt.show()
    except Exception as e:
        print(f"演示运行失败（可能在无 GUI 环境中）: {e}")
        print("模块导入成功，函数可在 Jupyter/脚本中正常使用。")

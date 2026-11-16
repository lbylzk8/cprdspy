"""
cprdspy.rotor — CPR 旋转器模块

CPR 理论的核心实现：用运动组合生成几何。

支持维度:
    - 2D: Rotor2D (复数)
    - 3D: Rotor3D (四元数)
    - nD: RotorClifford (Clifford 代数)

核心概念:
    Rotor (旋转器) = 基本运动原子
    RotorComposition (组合) = 运动叠加
    trace = 采样为坐标
    plot = 可视化

数学基础:
    2D: γ(t) = Σ r_k · e^{i(ω_k · t + φ_k)}
    3D: γ(t) = Σ r_k · [cos(ω_k t + φ_k)·e1 + sin(ω_k t + φ_k)·e2]
    nD: γ(t) = Σ r_k · exp(-B_k·(ω_k t + φ_k)/2) · e1 · exp(B_k·(ω_k t + φ_k)/2)

    这等价于 Fourier 级数的复指数形式。
    有限 Rotor 组合 = 有限 Fourier 和。
    无限 Rotor 级数 → 任意周期曲线的逼近。

快速开始:
    >>> from cprdspy.rotor import Rotor2D, rotor_plot
    >>>
    >>> # 2D 圆
    >>> circle = Rotor2D(3, 1)
    >>> rotor_plot(circle)
    >>>
    >>> # 3D 曲线
    >>> from cprdspy.rotor import Rotor3D, rotor_plot_3d
    >>> curve3d = Rotor3D(3, 1, 0, [1,0,0], [0,1,0]) + Rotor3D(1, 5, 0, [0,1,0], [0,0,1])
    >>> rotor_plot_3d(curve3d)
    >>>
    >>> # nD 曲线 (Clifford 代数)
    >>> from cprdspy.rotor import RotorClifford
    >>> curve4d = RotorClifford(2, 1, 0, [1,0,0,0], [0,1,0,0], n_dim=4)

与现有 cprdspy 的关系:
    本模块是 cprdspy 的"内核升级"。
    现有的 flowers(), star(), spiral() 等函数
    未来都可以用 Rotor 组合来统一表达。

作者: cprdspy team
"""

from .rotor2d import Rotor2D, RotorComposition
from .rotor3d import Rotor3D, Rotor3DComposition
from .rotor_clifford import RotorClifford, RotorCliffordComposition
from .trace import (
    trace,
    trace_nd,
    compute_velocity,
    compute_velocity_nd,
    compute_acceleration,
    compute_acceleration_nd,
    compute_curvature,
    compute_curvature_nd,
    compute_torsion,
    compute_torsion_3d,
    arc_length,
    arc_length_nd,
    total_length,
    total_length_nd,
)
from .plot import (
    rotor_plot,
    rotor_plot_mpl,
    rotor_plot_plotly,
    plot_rotor_chain,
)
from .plot3d import (
    rotor_plot_3d,
    rotor_plot_3d_mpl,
    rotor_plot_3d_plotly,
)

__all__ = [
    # 2D 核心类
    "Rotor2D",
    "RotorComposition",
    # 3D 核心类
    "Rotor3D",
    "Rotor3DComposition",
    # nD 核心类 (Clifford)
    "RotorClifford",
    "RotorCliffordComposition",
    # 2D 采样与分析
    "trace",
    "compute_velocity",
    "compute_acceleration",
    "compute_curvature",
    "compute_torsion",
    "arc_length",
    "total_length",
    # nD 采样与分析
    "trace_nd",
    "compute_velocity_nd",
    "compute_acceleration_nd",
    "compute_curvature_nd",
    "compute_torsion_3d",
    "arc_length_nd",
    "total_length_nd",
    # 2D 可视化
    "rotor_plot",
    "rotor_plot_mpl",
    "rotor_plot_plotly",
    "plot_rotor_chain",
    # 3D 可视化
    "rotor_plot_3d",
    "rotor_plot_3d_mpl",
    "rotor_plot_3d_plotly",
]

"""
rotor3d.py — 三维旋转器 (3D Rotor)

CPR 理论在 3D 的推广。

数学定义:
    R(r, ω, φ; t) = r · [cos(ωt + φ) · e₁ + sin(ωt + φ) · e₂]

其中 e₁, e₂ 是旋转平面内的两个正交单位向量。

与四元数的关系:
    3D 旋转可以用单位四元数表示:
    q = cos(θ/2) + sin(θ/2) · (n_x i + n_y j + n_z k)

    其中 n 是旋转轴，θ 是旋转角度。

    Rotor 的 circular motion 等价于:
    R(t) = q(t) · v₀ · q(t)*

    其中 q(t) = cos(ωt/2 + φ/2) + sin(ωt/2 + φ/2) · n

几何含义:
    一个在 3D 空间中做匀速圆周运动的点。
    - radius (r): 圆周运动的半径
    - frequency (ω): 角频率
    - phase (φ): 初相位
    - plane: 旋转平面（由两个正交向量定义）

核心公式:
    γ(t) = center + Σ R_k(t)

作者: cprdspy team
"""

import numpy as np
from fractions import Fraction
from typing import Union, Tuple, List, Optional


# ============================================================
# 四元数工具函数
# ============================================================

def _quat_multiply(q1: np.ndarray, q2: np.ndarray) -> np.ndarray:
    """
    四元数乘法: q1 * q2

    四元数表示为 [w, x, y, z]
    """
    w1, x1, y1, z1 = q1
    w2, x2, y2, z2 = q2
    return np.array([
        w1*w2 - x1*x2 - y1*y2 - z1*z2,
        w1*x2 + x1*w2 + y1*z2 - z1*y2,
        w1*y2 - x1*z2 + y1*w2 + z1*x2,
        w1*z2 + x1*y2 - y1*x2 + z1*w2,
    ])


def _quat_conjugate(q: np.ndarray) -> np.ndarray:
    """四元数共轭: [w, -x, -y, -z]"""
    return np.array([q[0], -q[1], -q[2], -q[3]])


def _quat_rotate(q: np.ndarray, v: np.ndarray) -> np.ndarray:
    """
    用四元数旋转向量: v' = q * v * q*

    参数:
        q: 单位四元数 [w, x, y, z]
        v: 3D 向量 [x, y, z]
    """
    v_quat = np.array([0.0, v[0], v[1], v[2]])
    result = _quat_multiply(_quat_multiply(q, v_quat), _quat_conjugate(q))
    return result[1:]  # 返回 [x, y, z]


def _quat_from_axis_angle(axis: np.ndarray, angle: float) -> np.ndarray:
    """
    从旋转轴和角度构造四元数

    q = cos(θ/2) + sin(θ/2) * (n_x i + n_y j + n_z k)
    """
    axis = np.asarray(axis, dtype=float)
    axis = axis / np.linalg.norm(axis)  # 归一化
    half_angle = angle / 2.0
    w = np.cos(half_angle)
    xyz = np.sin(half_angle) * axis
    return np.array([w, xyz[0], xyz[1], xyz[2]])


# ============================================================
# Rotor3D — 三维旋转器
# ============================================================

class Rotor3D:
    """
    三维旋转器 — CPR 的 3D 运动原子

    数学定义:
        R(r, ω, φ; t) = r · [cos(ωt + φ) · e₁ + sin(ωt + φ) · e₂]

    其中 e₁, e₂ 是旋转平面内的两个正交单位向量。

    参数:
        radius: 圆周运动的半径
        frequency: 角频率
        phase: 初相位
        e1: 旋转平面的第一个基向量 (3D)
        e2: 旋转平面的第二个基向量 (3D)，必须与 e1 正交
        center: 运动中心偏移 (3D)

    示例:
        >>> # XY 平面内的圆
        >>> r = Rotor3D(3, 1, 0, e1=[1,0,0], e2=[0,1,0])
        >>> r.evaluate(0)
        array([3., 0., 0.])

        >>> # 两个 Rotor 叠加
        >>> curve = Rotor3D(3, 1, 0, [1,0,0], [0,1,0]) + Rotor3D(1, 5, 0, [0,1,0], [0,0,1])
    """

    def __init__(
        self,
        radius: float = 1.0,
        frequency: Union[int, float] = 1,
        phase: float = 0.0,
        e1: Tuple[float, float, float] = (1.0, 0.0, 0.0),
        e2: Tuple[float, float, float] = (0.0, 1.0, 0.0),
        center: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    ):
        self.radius = float(radius)
        self.frequency = frequency
        self.phase = float(phase)
        self.e1 = np.asarray(e1, dtype=float)
        self.e2 = np.asarray(e2, dtype=float)
        self.center = np.asarray(center, dtype=float)

        # 归一化基向量
        self.e1 = self.e1 / np.linalg.norm(self.e1)
        self.e2 = self.e2 / np.linalg.norm(self.e2)

        # 验证正交性
        if abs(np.dot(self.e1, self.e2)) > 1e-10:
            # Gram-Schmidt 正交化
            self.e2 = self.e2 - np.dot(self.e2, self.e1) * self.e1
            self.e2 = self.e2 / np.linalg.norm(self.e2)

    # ---- 求值 ----

    def evaluate(self, t) -> Union[np.ndarray, np.ndarray]:
        """
        在时刻 t 计算位置 (3D 向量)

        R(t) = center + r · [cos(ωt + φ) · e₁ + sin(ωt + φ) · e₂]

        参数:
            t: 时间参数，标量或 numpy 数组

        返回:
            3D 向量（t 为标量时）或 3D 向量数组（t 为数组时）
        """
        angle = self.frequency * t + self.phase
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)

        if np.isscalar(t):
            # 标量输入
            pos = self.radius * (cos_a * self.e1 + sin_a * self.e2)
            return pos + self.center
        else:
            # 数组输入
            # cos_a, sin_a 形状: (N,)
            # e1, e2 形状: (3,)
            # 结果形状: (N, 3)
            pos = self.radius * (
                cos_a[:, np.newaxis] * self.e1[np.newaxis, :] +
                sin_a[:, np.newaxis] * self.e2[np.newaxis, :]
            )
            return pos + self.center[np.newaxis, :]

    def evaluate_xyz(self, t) -> Tuple:
        """
        在时刻 t 计算 (x, y, z) 坐标

        返回:
            (x, y, z): 标量元组或 numpy 数组元组
        """
        pos = self.evaluate(t)
        if np.isscalar(t):
            return pos[0], pos[1], pos[2]
        else:
            return pos[:, 0], pos[:, 1], pos[:, 2]

    def __call__(self, t):
        """快捷调用: rotor(t) == rotor.evaluate(t)"""
        return self.evaluate(t)

    # ---- 代数运算 ----

    def __add__(self, other):
        """运动叠加: R1 + R2"""
        if isinstance(other, Rotor3D):
            return Rotor3DComposition([self, other])
        if isinstance(other, Rotor3DComposition):
            return Rotor3DComposition([self] + other.rotors, other.center)
        return NotImplemented

    def __radd__(self, other):
        """支持 sum([r1, r2, r3]) 语法"""
        if other == 0:
            return self
        return self.__add__(other)

    def __sub__(self, other):
        """运动差: R1 - R2"""
        return self + (-other)

    def __neg__(self):
        """反向旋转器"""
        return Rotor3D(
            -self.radius, self.frequency, self.phase,
            self.e1, self.e2, self.center
        )

    def __mul__(self, scalar):
        """缩放: c · R = Rotor(c*r, ω, φ)"""
        s = float(scalar)
        return Rotor3D(
            self.radius * s, self.frequency, self.phase,
            self.e1, self.e2, self.center * s
        )

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    # ---- 变换 ----

    def conjugate(self):
        """
        共轭旋转器: 反转旋转方向

        R̄(t) = r · [cos(ωt + φ) · e₁ - sin(ωt + φ) · e₂]
        """
        return Rotor3D(
            self.radius, -self.frequency, -self.phase,
            self.e1, self.e2, self.center
        )

    def derivative(self):
        """
        导数旋转器: 速度向量

        dR/dt = rω · [-sin(ωt + φ) · e₁ + cos(ωt + φ) · e₂]
        """
        return Rotor3D(
            self.radius * abs(self.frequency),
            self.frequency,
            self.phase + np.pi / 2 * np.sign(self.frequency),
            self.e1, self.e2,
            np.zeros(3)
        )

    # ---- 表示 ----

    def to_math(self) -> str:
        """LaTeX 数学表达式"""
        r = self.radius
        w = self.frequency
        p = self.phase
        if np.isclose(p, 0):
            return f"{r:.3g} * [cos({w}t)*e1 + sin({w}t)*e2]"
        return f"{r:.3g} * [cos({w}t+{p:.3g})*e1 + sin({w}t+{p:.3g})*e2]"

    def __repr__(self):
        return (
            f"Rotor3D(r={self.radius}, ω={self.frequency}, φ={self.phase:.4f}, "
            f"e1={self.e1.tolist()}, e2={self.e2.tolist()})"
        )

    def __str__(self):
        return self.to_math()


# ============================================================
# Rotor3DComposition — 三维旋转器组合
# ============================================================

class Rotor3DComposition:
    """
    多个 Rotor3D 的叠加组合

    数学定义:
        γ(t) = center + Σ R_k(t)

    几何含义:
        多个 3D 圆周运动的合成。

    示例:
        >>> # 3D 外摆线
        >>> curve = Rotor3D(3, 1, 0, [1,0,0], [0,1,0]) + Rotor3D(1, 5, 0, [0,1,0], [0,0,1])
    """

    def __init__(
        self,
        rotors: Optional[List[Rotor3D]] = None,
        center: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    ):
        self.rotors = list(rotors) if rotors else []
        self.center = np.asarray(center, dtype=float)

    # ---- 求值 ----

    def evaluate(self, t) -> Union[np.ndarray, np.ndarray]:
        """
        在时刻 t 计算合成位置

        γ(t) = center + Σ R_k(t)
        """
        if np.isscalar(t):
            result = sum(r.evaluate(t) for r in self.rotors)
            return result + self.center
        else:
            result = sum(r.evaluate(t) for r in self.rotors)
            return result + self.center[np.newaxis, :]

    def evaluate_xyz(self, t):
        """在时刻 t 计算 (x, y, z) 坐标"""
        pos = self.evaluate(t)
        if np.isscalar(t):
            return pos[0], pos[1], pos[2]
        else:
            return pos[:, 0], pos[:, 1], pos[:, 2]

    def __call__(self, t):
        """快捷调用"""
        return self.evaluate(t)

    # ---- 代数运算 ----

    def __add__(self, other):
        if isinstance(other, Rotor3D):
            return Rotor3DComposition(self.rotors + [other], self.center)
        if isinstance(other, Rotor3DComposition):
            return Rotor3DComposition(
                self.rotors + other.rotors,
                self.center + other.center
            )
        return NotImplemented

    def __radd__(self, other):
        if other == 0:
            return self
        return self.__add__(other)

    def __mul__(self, scalar):
        s = float(scalar)
        new_rotors = [r * s for r in self.rotors]
        return Rotor3DComposition(new_rotors, self.center * s)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __neg__(self):
        return self * (-1)

    def __sub__(self, other):
        return self + (-other)

    # ---- 容器接口 ----

    def __len__(self):
        return len(self.rotors)

    def __iter__(self):
        return iter(self.rotors)

    def __getitem__(self, idx):
        return self.rotors[idx]

    # ---- 分析 ----

    def frequencies(self) -> List[float]:
        """所有频率值（去重）"""
        return sorted(set(r.frequency for r in self.rotors))

    def spectrum(self) -> List[Tuple[float, float, float]]:
        """频率谱: [(ω, r, φ), ...]"""
        return [
            (r.frequency, r.radius, r.phase)
            for r in sorted(self.rotors, key=lambda r: r.frequency)
        ]

    def total_radius(self) -> float:
        """总半径"""
        return sum(r.radius for r in self.rotors)

    def is_closed(self, tol=1e-8) -> bool:
        """判断曲线是否闭合"""
        freqs = [float(f) for f in self.frequencies()]
        if len(freqs) <= 1:
            return True

        f0 = freqs[0]
        if abs(f0) < tol:
            f0 = next((f for f in freqs if abs(f) > tol), None)
            if f0 is None:
                return True

        denoms = []
        for f in freqs:
            if abs(f) < tol:
                continue
            ratio = f / f0
            frac = Fraction(ratio).limit_denominator(1000)
            if abs(float(frac) - ratio) > tol:
                return False
            denoms.append(frac.denominator)

        lcm_val = denoms[0]
        for d in denoms[1:]:
            lcm_val = lcm_val * d // np.gcd(lcm_val, d)
        return lcm_val < 10000

    def period(self) -> Optional[float]:
        """最小正周期"""
        if not self.is_closed():
            return None
        freqs = [abs(float(f)) for f in self.frequencies() if abs(f) > 1e-10]
        if not freqs:
            return 2 * np.pi

        from math import gcd as int_gcd

        def fraction_gcd(f1: Fraction, f2: Fraction) -> Fraction:
            num = int_gcd(f1.numerator, f2.numerator)
            den = (f1.denominator * f2.denominator) // int_gcd(
                f1.denominator, f2.denominator
            )
            return Fraction(num, den)

        fracs = [Fraction(f).limit_denominator(10000) for f in freqs]
        g = fracs[0]
        for f in fracs[1:]:
            g = fraction_gcd(g, f)

        return 2 * np.pi / float(g)

    # ---- 表示 ----

    def to_math(self) -> str:
        """LaTeX 数学表达式"""
        terms = [r.to_math() for r in self.rotors]
        return " + ".join(terms) if terms else "0"

    def __repr__(self):
        terms = ", ".join(repr(r) for r in self.rotors)
        return f"Rotor3DComposition([{terms}])"

    def __str__(self):
        if not self.rotors:
            return "0"
        return " + ".join(str(r) for r in self.rotors)

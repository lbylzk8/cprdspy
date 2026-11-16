"""
rotor2d.py — 二维旋转器 (2D Rotor)

CPR 理论的核心原语。

数学定义:
    R(r, ω, φ; t) = r · e^{i(ωt + φ)}

几何含义:
    一个半径为 r、角频率为 ω、初相位为 φ 的匀速圆周运动。
    多个 Rotor 的叠加可以生成摆线、花朵、星形等复杂曲线。

核心公式:
    γ(t) = center + Σ R_k(t)
         = center + Σ r_k · e^{i(ω_k · t + φ_k)}

与 Fourier 级数的关系:
    有限 Rotor 组合 = 有限 Fourier 级数的复指数形式
    无限 Rotor 级数 → 任意周期曲线的逼近

作者: cprdspy team
"""

import numpy as np
from fractions import Fraction
from typing import Union, Tuple, List, Optional


# ============================================================
# Rotor2D — 二维旋转器
# ============================================================

class Rotor2D:
    """
    二维旋转器 — CPR 的基本运动原子

    数学定义:
        R(r, ω, φ; t) = r · e^{i(ωt + φ)}

    几何含义:
        一个在复平面上做匀速圆周运动的点。
        - radius (r): 圆周运动的半径（振幅）
        - frequency (ω): 角频率（转速），整数表示周期运动
        - phase (φ): 初相位（起始角度偏移）
        - center: 运动中心偏移

    示例:
        >>> r = Rotor2D(radius=3, frequency=1)
        >>> r(0)          # t=0 时的位置
        (3+0j)
        >>> r(np.pi/2)    # t=π/2 时的位置
        (0+3j)

        >>> # 两个 Rotor 叠加 → 外摆线
        >>> curve = Rotor2D(3, 1) + Rotor2D(1, 7)
    """

    def __init__(
        self,
        radius: float = 1.0,
        frequency: Union[int, float] = 1,
        phase: float = 0.0,
        center: Tuple[float, float] = (0.0, 0.0),
    ):
        self.radius = float(radius)
        self.frequency = frequency
        self.phase = float(phase)
        self.center = (float(center[0]), float(center[1]))

    # ---- 求值 ----

    def evaluate(self, t) -> Union[complex, np.ndarray]:
        """
        在时刻 t 计算位置（复数表示）

        R(t) = center + r · e^{i(ωt + φ)}

        参数:
            t: 时间参数，标量或 numpy 数组

        返回:
            复数标量（t 为标量时）或复数数组（t 为数组时）
        """
        angle = self.frequency * t + self.phase
        z = self.radius * np.exp(1j * angle)
        if self.center != (0.0, 0.0):
            z = z + self.center[0] + 1j * self.center[1]
        return z

    def evaluate_xy(self, t) -> Tuple:
        """
        在时刻 t 计算 (x, y) 坐标

        返回:
            (x, y): 标量元组或 numpy 数组元组
        """
        z = self.evaluate(t)
        return z.real, z.imag

    def __call__(self, t) -> Union[complex, np.ndarray]:
        """快捷调用: rotor(t) == rotor.evaluate(t)"""
        return self.evaluate(t)

    # ---- 代数运算 ----

    def __add__(self, other):
        """
        运动叠加: R1 + R2

        几何含义: 两个圆周运动的合成
        数学含义: 复数向量加法
        """
        if isinstance(other, Rotor2D):
            return RotorComposition([self, other])
        if isinstance(other, RotorComposition):
            return RotorComposition([self] + other.rotors, other.center)
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
        return Rotor2D(-self.radius, self.frequency, self.phase, self.center)

    def __mul__(self, scalar):
        """缩放: c · R = Rotor(c*r, ω, φ)"""
        s = float(scalar)
        return Rotor2D(self.radius * s, self.frequency, self.phase, self.center)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    # ---- 比较与哈希 ----

    def __eq__(self, other):
        if not isinstance(other, Rotor2D):
            return False
        return (
            np.isclose(self.radius, other.radius)
            and np.isclose(self.frequency, other.frequency)
            and np.isclose(self.phase, other.phase)
            and np.isclose(self.center[0], other.center[0])
            and np.isclose(self.center[1], other.center[1])
        )

    def __hash__(self):
        return hash((
            round(self.radius, 10),
            round(float(self.frequency), 10),
            round(self.phase % (2 * np.pi), 10),
        ))

    # ---- 变换 ----

    def conjugate(self):
        """
        共轭旋转器: R̄(t) = r · e^{-i(ωt + φ)}

        几何含义: 反转旋转方向
        """
        return Rotor2D(self.radius, -self.frequency, -self.phase, self.center)

    def derivative(self):
        """
        导数旋转器: dR/dt = irω · e^{i(ωt + φ)}

        几何含义: 速度向量（切线方向，超前 π/2）
        数学: R'(t) = R(rω, ω, φ + π/2; t)
        """
        return Rotor2D(
            self.radius * abs(self.frequency),
            self.frequency,
            self.phase + np.pi / 2 * np.sign(self.frequency),
            (0.0, 0.0),
        )

    def reverse(self):
        """反转初相位"""
        return Rotor2D(self.radius, self.frequency, -self.phase, self.center)

    # ---- 表示 ----

    def to_math(self) -> str:
        """LaTeX 数学表达式"""
        r = self.radius
        w = self.frequency
        p = self.phase
        if np.isclose(p, 0):
            return f"{r:.3g} e^{{{w}it}}"
        return f"{r:.3g} e^{{i({w}t + {p:.3g})}}"

    def __repr__(self):
        c = f", center={self.center}" if self.center != (0, 0) else ""
        return f"Rotor2D(r={self.radius}, ω={self.frequency}, φ={self.phase:.4f}{c})"

    def __str__(self):
        return self.to_math()


# ============================================================
# RotorComposition — 旋转器组合
# ============================================================

class RotorComposition:
    """
    多个 Rotor 的叠加组合

    数学定义:
        γ(t) = center + Σ R_k(t)
             = center + Σ r_k · e^{i(ω_k · t + φ_k)}

    几何含义:
        多个圆周运动的合成。每个 Rotor 是一个"本轮"，
        所有本轮的向量叠加形成复杂曲线。

        这正是托勒密的本轮-均轮系统，也是 Fourier 级数的几何表达。

    示例:
        >>> # 外摆线: 两个 Rotor 叠加
        >>> curve = Rotor2D(3, 1) + Rotor2D(1, 7)

        >>> # 三个 Rotor 叠加
        >>> curve = Rotor2D(3, 1) + Rotor2D(2, -3) + Rotor2D(0.5, 7)
    """

    def __init__(
        self,
        rotors: Optional[List[Rotor2D]] = None,
        center: Tuple[float, float] = (0.0, 0.0),
    ):
        self.rotors = list(rotors) if rotors else []
        self.center = (float(center[0]), float(center[1]))

    # ---- 求值 ----

    def evaluate(self, t) -> Union[complex, np.ndarray]:
        """
        在时刻 t 计算合成位置

        γ(t) = center + Σ r_k · e^{i(ω_k · t + φ_k)}
        """
        result = sum(r.evaluate(t) for r in self.rotors)
        if self.center != (0.0, 0.0):
            result = result + self.center[0] + 1j * self.center[1]
        return result

    def evaluate_xy(self, t):
        """在时刻 t 计算 (x, y) 坐标"""
        z = self.evaluate(t)
        return z.real, z.imag

    def derivative(self, t):
        """速度 (复数)"""
        return sum(r.derivative().evaluate(t) for r in self.rotors)

    def __call__(self, t):
        """快捷调用"""
        return self.evaluate(t)

    # ---- 代数运算 ----

    def __add__(self, other):
        if isinstance(other, Rotor2D):
            return RotorComposition(
                self.rotors + [other], self.center
            )
        if isinstance(other, RotorComposition):
            return RotorComposition(
                self.rotors + other.rotors,
                (self.center[0] + other.center[0],
                 self.center[1] + other.center[1]),
            )
        return NotImplemented

    def __radd__(self, other):
        if other == 0:
            return self
        return self.__add__(other)

    def __mul__(self, scalar):
        s = float(scalar)
        new_rotors = [r * s for r in self.rotors]
        new_center = (self.center[0] * s, self.center[1] * s)
        return RotorComposition(new_rotors, new_center)

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

    def __eq__(self, other):
        if not isinstance(other, RotorComposition):
            return False
        return self.rotors == other.rotors and np.allclose(self.center, other.center)

    # ---- 分析 ----

    def simplify(self, tol=1e-10):
        """
        化简：合并同频率 Rotor，移除可忽略项

        数学依据:
            r₁·e^{i(ωt+φ₁)} + r₂·e^{i(ωt+φ₂)}
            = R·e^{i(ωt+Φ)}
        其中 R·e^{iΦ} = r₁·e^{iφ₁} + r₂·e^{iφ₂}（复数加法）
        """
        freq_map = {}
        for r in self.rotors:
            w = round(float(r.frequency), 10)
            z = r.radius * np.exp(1j * r.phase)
            if w in freq_map:
                freq_map[w] = (freq_map[w][0] + z, r.frequency)
            else:
                freq_map[w] = (z, r.frequency)

        new_rotors = []
        for w, (z, w_orig) in sorted(freq_map.items()):
            amp = abs(z)
            if amp > tol:
                phase = np.angle(z)
                new_rotors.append(Rotor2D(amp, w_orig, phase))

        return RotorComposition(new_rotors, self.center)

    def frequencies(self) -> List[float]:
        """所有频率值（去重）"""
        return sorted(set(r.frequency for r in self.rotors))

    def spectrum(self) -> List[Tuple[float, float, float]]:
        """
        频率谱: [(ω, r, φ), ...]

        按频率排序，每项给出 (角频率, 振幅, 相位)
        """
        return [
            (r.frequency, r.radius, r.phase)
            for r in sorted(self.rotors, key=lambda r: r.frequency)
        ]

    def total_radius(self) -> float:
        """总半径（所有 Rotor 半径之和）"""
        return sum(r.radius for r in self.rotors)

    def max_frequency(self) -> float:
        """最大频率"""
        return max((r.frequency for r in self.rotors), default=0)

    def is_closed(self, tol=1e-8) -> bool:
        """
        判断曲线是否闭合

        数学判据:
            所有频率比为有理数 ⟺ 曲线闭合（周期运动）
            存在无理频率比 ⟺ 曲线不闭合（准周期运动）

        这直接对应你文档中的核心定理:
            ω = p/q (有理) → 闭合轨道
            ω = 无理数 → 稠密轨道 (Kronecker)
        """
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
                return False  # 无理比 → 不闭合
            denoms.append(frac.denominator)

        # 检查最小公倍数是否合理
        lcm_val = denoms[0]
        for d in denoms[1:]:
            lcm_val = lcm_val * d // np.gcd(lcm_val, d)
        return lcm_val < 10000

    def period(self) -> Optional[float]:
        """
        最小正周期（仅在曲线闭合时有意义）

        T = 2π / gcd(ω₁, ω₂, ..., ωₙ)
        """
        if not self.is_closed():
            return None
        freqs = [abs(float(f)) for f in self.frequencies() if abs(f) > 1e-10]
        if not freqs:
            return 2 * np.pi

        # 用 Fraction 精确求 gcd
        # gcd(a/b, c/d) = gcd(a,c) / lcm(b,d)
        from math import gcd as int_gcd

        def fraction_gcd(f1: Fraction, f2: Fraction) -> Fraction:
            """两个分数的最大公约数"""
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
        return f"RotorComposition([{terms}])"

    def __str__(self):
        if not self.rotors:
            return "0"
        return " + ".join(str(r) for r in self.rotors)

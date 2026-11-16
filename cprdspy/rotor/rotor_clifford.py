"""
rotor_clifford.py — n 维旋转器 (Clifford 代数)

CPR 理论在任意维度的推广，使用几何代数 (Geometric Algebra)。

数学定义:
    R(r, ω, φ; t) = r · exp(-B·(ωt + φ)/2) · e₁ · exp(B·(ωt + φ)/2)

其中:
    - B = e₁e₂ 是旋转平面的单位二重向量 (bivector)
    - exp(-B·θ/2) 是 rotor (旋转器)
    - 三明治积 (sandwich product): v' = R · v · R̃

与低维的关系:
    - 2D: 复数 e^{iθ} 是 Cl(2) 的 rotor
    - 3D: 四元数是 Cl(3) 的 rotor
    - nD: Clifford rotor 是统一推广

核心公式:
    γ(t) = center + Σ R_k(t)

    其中每个 R_k(t) 是 nD 空间中的圆周运动。

作者: cprdspy team
"""

import numpy as np
from fractions import Fraction
from typing import Union, Tuple, List, Optional

from clifford import Cl


# ============================================================
# RotorClifford — n 维旋转器
# ============================================================

class RotorClifford:
    """
    n 维旋转器 — 使用 Clifford 代数

    数学定义:
        R(r, ω, φ; t) = r · exp(-B·(ωt + φ)/2) · e₁ · exp(B·(ωt + φ)/2)

    其中 B = e₁∧e₂ 是旋转平面的单位二重向量。

    参数:
        radius: 圆周运动的半径
        frequency: 角频率
        phase: 初相位
        e1: 旋转平面的第一个基向量 (nD)
        e2: 旋转平面的第二个基向量 (nD)，必须与 e1 正交
        center: 运动中心偏移 (nD)
        n_dim: 空间维度 (默认 3)

    示例:
        >>> # 3D XY 平面内的圆
        >>> r = RotorClifford(3, 1, 0, [1,0,0], [0,1,0], n_dim=3)
        >>> r.evaluate(0)
        array([3., 0., 0.])

        >>> # 4D 旋转
        >>> r4d = RotorClifford(2, 1, 0, [1,0,0,0], [0,1,0,0], n_dim=4)
    """

    def __init__(
        self,
        radius: float = 1.0,
        frequency: Union[int, float] = 1,
        phase: float = 0.0,
        e1: List[float] = None,
        e2: List[float] = None,
        center: List[float] = None,
        n_dim: int = 3,
    ):
        self.radius = float(radius)
        self.frequency = frequency
        self.phase = float(phase)
        self.n_dim = n_dim

        # 默认基向量
        if e1 is None:
            e1 = [1.0] + [0.0] * (n_dim - 1)
        if e2 is None:
            e2 = [0.0, 1.0] + [0.0] * (n_dim - 2)
        if center is None:
            center = [0.0] * n_dim

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

        # 创建 Clifford 代数
        self._layout, self._blades = Cl(n_dim)

        # 创建基向量的 clifford 表示
        self._e1_cl = sum(
            self.e1[i] * self._blades[f'e{i+1}'] for i in range(n_dim)
        )
        self._e2_cl = sum(
            self.e2[i] * self._blades[f'e{i+1}'] for i in range(n_dim)
        )

        # 存储基向量对象用于后续提取分量
        self._basis_vectors = [self._blades[f'e{i+1}'] for i in range(n_dim)]

        # 旋转平面的二重向量 B = e1 ∧ e2 = e1 * e2 (因为 e1·e2 = 0)
        self._B = self._e1_cl * self._e2_cl

    # ---- 求值 ----

    def evaluate(self, t) -> Union[np.ndarray, np.ndarray]:
        """
        在时刻 t 计算位置 (nD 向量)

        R(t) = center + r · exp(-B·(ωt + φ)/2) · e₁ · exp(B·(ωt + φ)/2)

        参数:
            t: 时间参数，标量或 numpy 数组

        返回:
            nD 向量（t 为标量时）或 nD 向量数组（t 为数组时）
        """
        angle = self.frequency * t + self.phase

        if np.isscalar(t):
            # 标量输入
            # Rotor: R = exp(-B * angle / 2)
            R_rotor = np.exp(-self._B * angle / 2)
            R_rev = ~R_rotor  # reverse

            # 三明治积: v' = R · e1 · R̃
            v_rotated = R_rotor * self._e1_cl * R_rev

            # 提取向量分量
            pos = np.array([
                float(v_rotated[basis_vec]) for basis_vec in self._basis_vectors
            ])

            return self.radius * pos + self.center
        else:
            # 数组输入
            results = []
            for ti in t:
                angle_i = self.frequency * ti + self.phase
                R_rotor = np.exp(-self._B * angle_i / 2)
                R_rev = ~R_rotor
                v_rotated = R_rotor * self._e1_cl * R_rev
                pos = np.array([
                    float(v_rotated[basis_vec]) for basis_vec in self._basis_vectors
                ])
                results.append(self.radius * pos + self.center)
            return np.array(results)

    def evaluate_coords(self, t) -> Tuple:
        """
        在时刻 t 计算各坐标分量

        返回:
            tuple of arrays: (x1, x2, ..., xn)
        """
        pos = self.evaluate(t)
        if np.isscalar(t):
            return tuple(pos)
        else:
            return tuple(pos[:, i] for i in range(self.n_dim))

    def __call__(self, t):
        """快捷调用: rotor(t) == rotor.evaluate(t)"""
        return self.evaluate(t)

    # ---- 代数运算 ----

    def __add__(self, other):
        """运动叠加: R1 + R2"""
        if isinstance(other, RotorClifford):
            return RotorCliffordComposition([self, other])
        if isinstance(other, RotorCliffordComposition):
            return RotorCliffordComposition([self] + other.rotors, other.center)
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
        return RotorClifford(
            -self.radius, self.frequency, self.phase,
            self.e1.tolist(), self.e2.tolist(),
            self.center.tolist(), self.n_dim
        )

    def __mul__(self, scalar):
        """缩放: c · R = Rotor(c*r, ω, φ)"""
        s = float(scalar)
        return RotorClifford(
            self.radius * s, self.frequency, self.phase,
            self.e1.tolist(), self.e2.tolist(),
            (self.center * s).tolist(), self.n_dim
        )

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    # ---- 变换 ----

    def conjugate(self):
        """共轭旋转器: 反转旋转方向"""
        return RotorClifford(
            self.radius, -self.frequency, -self.phase,
            self.e1.tolist(), self.e2.tolist(),
            self.center.tolist(), self.n_dim
        )

    def derivative(self):
        """导数旋转器: 速度向量"""
        return RotorClifford(
            self.radius * abs(self.frequency),
            self.frequency,
            self.phase + np.pi / 2 * np.sign(self.frequency),
            self.e1.tolist(), self.e2.tolist(),
            [0.0] * self.n_dim, self.n_dim
        )

    # ---- 表示 ----

    def to_math(self) -> str:
        """数学表达式"""
        r = self.radius
        w = self.frequency
        p = self.phase
        if np.isclose(p, 0):
            return f"{r:.3g} * [cos({w}t)*e1 + sin({w}t)*e2]"
        return f"{r:.3g} * [cos({w}t+{p:.3g})*e1 + sin({w}t+{p:.3g})*e2]"

    def __repr__(self):
        return (
            f"RotorClifford(r={self.radius}, w={self.frequency}, phi={self.phase:.4f}, "
            f"n_dim={self.n_dim})"
        )

    def __str__(self):
        return self.to_math()


# ============================================================
# RotorCliffordComposition — n 维旋转器组合
# ============================================================

class RotorCliffordComposition:
    """
    多个 RotorClifford 的叠加组合

    数学定义:
        γ(t) = center + Σ R_k(t)

    示例:
        >>> # 3D 外摆线
        >>> r1 = RotorClifford(3, 1, 0, [1,0,0], [0,1,0], n_dim=3)
        >>> r2 = RotorClifford(1, 5, 0, [0,1,0], [0,0,1], n_dim=3)
        >>> curve = r1 + r2
    """

    def __init__(
        self,
        rotors: Optional[List[RotorClifford]] = None,
        center: List[float] = None,
    ):
        self.rotors = list(rotors) if rotors else []
        if center is None:
            n_dim = self.rotors[0].n_dim if self.rotors else 3
            self.center = np.zeros(n_dim)
        else:
            self.center = np.asarray(center, dtype=float)

    # ---- 求值 ----

    def evaluate(self, t) -> Union[np.ndarray, np.ndarray]:
        """在时刻 t 计算合成位置"""
        if np.isscalar(t):
            result = sum(r.evaluate(t) for r in self.rotors)
            return result + self.center
        else:
            result = sum(r.evaluate(t) for r in self.rotors)
            return result + self.center[np.newaxis, :]

    def evaluate_coords(self, t) -> Tuple:
        """在时刻 t 计算各坐标分量"""
        pos = self.evaluate(t)
        if np.isscalar(t):
            return tuple(pos)
        else:
            return tuple(pos[:, i] for i in range(pos.shape[1]))

    def __call__(self, t):
        """快捷调用"""
        return self.evaluate(t)

    # ---- 代数运算 ----

    def __add__(self, other):
        if isinstance(other, RotorClifford):
            return RotorCliffordComposition(self.rotors + [other], self.center)
        if isinstance(other, RotorCliffordComposition):
            return RotorCliffordComposition(
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
        return RotorCliffordComposition(new_rotors, self.center * s)

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
        """数学表达式"""
        terms = [r.to_math() for r in self.rotors]
        return " + ".join(terms) if terms else "0"

    def __repr__(self):
        terms = ", ".join(repr(r) for r in self.rotors)
        return f"RotorCliffordComposition([{terms}])"

    def __str__(self):
        if not self.rotors:
            return "0"
        return " + ".join(str(r) for r in self.rotors)

import numpy as np
import matplotlib.pyplot as plt


def cycloid(r, n):
    t = np.linspace(0, 8 * np.pi, n)
    x = r * (t - np.sin(t) / 2)
    y = r * (1 - np.cos(t) / 2)
    plt.plot(x, y)


def cycliod_ring(R, r, T, points=1000):
    t = np.linspace(0, T * 2 * np.pi, points)
    x = R * np.cos(t) + r * np.cos((R / r) * t)
    y = R * np.sin(t) + r * np.sin((R / r) * t)
    plt.plot(x, y)


def fourier_r(r, T, color="#0f0", points=1000):
    t = np.linspace(0, T * 2 * np.pi, points)
    theta = [t] * len(r)
    x = r[0] * np.cos(t)
    y = r[0] * np.sin(t)
    for i in range(1, len(r)):
        theta = (r[i - 1] / r[i]) * t
        x = x + r[i] * np.cos(theta)
        y = y + r[i] * np.sin(theta)

    plt.plot(x, y, color)


# 公式字符串里可以直接用到的名字
_FORMULA_NAMES = {
    "np": np,
    "pi": np.pi,
    "e": np.e,
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "sqrt": np.sqrt,
    "exp": np.exp,
    "log": np.log,
    "abs": np.abs,
}


def func(i, r, formula="r"):
    """把公式字符串求值成第 i 项的频率系数。

    公式里可用 i（项序号）和 r（该项振幅），例如：
    "r" -> r    "i" -> i    "i + 1" -> 谐波序号    "r**i" -> 幂次增长
    """
    return eval(formula, {"__builtins__": {}}, {"i": i, "r": r, **_FORMULA_NAMES})


def fourier(R, P, T, formula="r", color="#0f0", points=1000):
    t = np.linspace(0, T * 2 * np.pi, points)
    x = R[0] * np.cos(t)
    y = R[0] * np.sin(t)
    for i in range(1, len(R)):
        theta = func(i, R, formula) * t
        phi = P[i]
        x = x + R[i] * np.cos(theta + phi * np.pi)
        y = y + R[i] * np.sin(theta + phi * np.pi)

    plt.plot(x, y, color=color)


def fourier_copilot(R, A, phi, T, color="#0f0", points=1000):
    """按 x=Σrᵢcos(aᵢθ+φᵢ), y=Σrᵢsin(aᵢθ+φᵢ) 绘制曲线。"""
    R = np.asarray(R, dtype=float)
    A = np.asarray(A, dtype=float)
    phi = np.asarray(phi, dtype=float)

    if R.ndim != 1 or A.ndim != 1 or phi.ndim != 1:
        raise ValueError("R、A 和 phi 必须是一维数组")
    if len(R) == 0 or len(R) != len(A) or len(R) != len(phi):
        raise ValueError("R、A 和 phi 必须长度相同且非空")
    if points < 2:
        raise ValueError("points 必须至少为 2")

    theta = np.linspace(0, 2 * np.pi * T, points)
    angles = A[:, None] * theta[None, :] + phi[:, None]

    x = np.sum(R[:, None] * np.cos(angles), axis=0)
    y = np.sum(R[:, None] * np.sin(angles), axis=0)

    plt.plot(x, y, color=color)
    return x, y


def fourier_3d(R, A, delta, T, B=None, gamma=None, color="#0f0", points=1000, ax=None):
    """按球坐标形式绘制三维傅里叶曲线：

        x = Σ rᵢ·cosθᵢ·cosφᵢ
        y = Σ rᵢ·cosθᵢ·sinφᵢ
        z = Σ rᵢ·sinθᵢ

    其中 θᵢ(t) = Aᵢ·t + deltaᵢ，φᵢ(t) = Bᵢ·t + gammaᵢ。
    B 省略时取 A，gamma 省略时取 0（即 φ 与 θ 同频、零相位）。
    每个求和项是半径 rᵢ 的球面上的一个点，求和即得三维空间曲线。
    """
    R = np.asarray(R, dtype=float)
    A = np.asarray(A, dtype=float)
    delta = np.asarray(delta, dtype=float)
    B = A if B is None else np.asarray(B, dtype=float)
    gamma = np.zeros_like(R) if gamma is None else np.asarray(gamma, dtype=float)

    arrays = (R, A, delta, B, gamma)
    if any(a.ndim != 1 for a in arrays):
        raise ValueError("R、A、delta、B 和 gamma 必须是一维数组")
    if len(R) == 0 or len({len(a) for a in arrays}) != 1:
        raise ValueError("R、A、delta、B 和 gamma 必须长度相同且非空")
    if points < 2:
        raise ValueError("points 必须至少为 2")

    t = np.linspace(0, 2 * np.pi * T, points)
    theta = A[:, None] * t[None, :] + delta[:, None]
    phi = B[:, None] * t[None, :] + gamma[:, None]

    x = np.sum(R[:, None] * np.cos(theta) * np.cos(phi), axis=0)
    y = np.sum(R[:, None] * np.cos(theta) * np.sin(phi), axis=0)
    z = np.sum(R[:, None] * np.sin(theta), axis=0)

    if ax is None:
        ax = plt.axes(projection="3d")
    ax.plot(x, y, z, color=color)
    return x, y, z


# 高维fourier函数
def hyper_fourier(R, T, formula="r", formula_phi=None, color="#0f0", points=1000):
    if formula_phi is None:
        formula_phi = formula
    t = np.linspace(0, T * 2 * np.pi, points)
    x = 0
    y = 0
    z = 0
    for i in range(len(R)):
        theta = func(i, R[i], formula) * t
        phi = func(i, R[i], formula_phi) * t
        x = x + R[i] * np.cos(theta) * np.cos(phi)
        y = y + R[i] * np.sin(theta) * np.cos(phi)
        z = z + R[i] * np.sin(phi)

    ax = plt.axes(projection="3d")
    ax.plot(x, y, z, color=color)


# Example usage
# cycloid(1, 100)
# cycliod_ring(12, 5, 12)
# cycliod_ring(12, -5, 12)
# cycliod_ring(11, -24, 24)
# cycliod_ring(11, 24, 24)
# fourier_r([3, 6, 9], 99, 3000)
# a = [5, 2]
# fourier_r(
#     a,
#     9,
#     "#00f",
#     3000,
# )
# fourier(
#     a,
#     [1/2,1/2],
#     100,
#     "r[i-1]/r[i]",
#     "#0f0",
#     10000,
# )
# fourier(
#     [1,4,9],
#     [0,0,0],
#     50,
#     # "(np.sum(r[:i]))/r[i]",
#     "r[i-1]/r[i]",
#     "#0f0",
#     10000,
# )
# fourier(
#     [2, 4, 6],
#     [np.pi / 2] * 3,
#     10,
#     "(np.sum(r[:i]))/r[i-1]",
#     "#0f0",
#     10000,
# )
# hyper_fourier(
#     [3, 6, 9, 12, 15],
#     1,
#     "r",
#     "i + 1",
#     "#f00",
#     10000,
# )
# fourier_copilot_3d(
#     R=[3, 2, 1],
#     A=[1, 2, 3],
#     delta=[0, np.pi / 2, np.pi],
#     T=1,
#     B=[1, 3, 5],
#     gamma=[0, np.pi / 3, np.pi / 2],
#     color="#0ff",
#     points=4000,
# )
# fourier_copilot(
#     R=[1, 4, 9],
#     A=[1, 2, 3],
#     phi=[0, np.pi / 2, np.pi],
#     T=1,
# )

# presets = [
#     # 1) 单球面大圆
#     dict(R=[2], A=[1], delta=[0], T=1, B=[1], gamma=[0], color="#00f"),
#     # 2) 球面 Lissajous（α:β = 3:2）
#     dict(R=[2], A=[3], delta=[0], T=1, B=[2], gamma=[0], color="#f00"),
#     # 3) 三个球面分量叠加成的闭合结
#     dict(R=[3, 2, 1], A=[1, 2, 3], delta=[0, np.pi/2, np.pi], T=1,
#          B=[1, 3, 5], gamma=[0, np.pi/3, np.pi/2], color="#0f0"),
# ]

# fig = plt.figure(figsize=(6, 6))
# ax = fig.add_subplot(projection="3d")
# for p in presets:
#     fourier_3d(points=4000, ax=ax, **p)

# ax.set_box_aspect((1, 1, 1))   # 可选：让三个轴视觉比例一致


plt.axis("equal")
plt.show()

"""3D 椭球花瓣花朵 —— 纯 numpy 移植版（不需要 Blender，几秒出图）。

对应 `blender_ellipsoid.py` 里 `petal()` / 末尾 5 层 demo 的几何，
但把「几何 = 生成元 × 对称群 × 层栈」这一范式提炼成了数据（`layers`）。

花结构（三层抽象，缺一不可）：
    花 = ⋃_层  T_层 · ⋃_i  R_z(i·2π/N) · 花瓣
    花瓣 = 右半椭球冠 ∪ 左半（右半绕竖直线 x=x_d 转 180°）
    椭球冠: x=a·cos u·sin v, y=b·sin u·sin v, z=c·cos v,  u∈[0,π], v∈[0,θ]
    θ = π/2 − π/n            ← n 瓣铺满平面的临界半角（与 2D 圆弧花同源）

快速运行：
    python ellipsoid_flower.py                 # plotly 交互图（自动开浏览器）
    python ellipsoid_flower.py --backend mpl   # matplotlib 窗口
    python ellipsoid_flower.py --save rose.png # 无窗口导出，最省依赖

等价性（本机实测）：本模块的闭式花瓣与 `plotly_ellipsoid.py` 的仿射矩阵路径
逐点误差 4e-16；与 Blender 5.1 实跑（顶点 float32 + 空对象变换）误差 5e-7。
"""

from __future__ import annotations

import math

import numpy as np

# --------------------------------------------------------------------------
# 1) 生成元：一片花瓣（两个沿同一边缘弧“铰接”的椭球冠）
# --------------------------------------------------------------------------


def petal(a=2.0, b=1 / 3, c=2.0, n=4, nu=48, nv=24):
    """返回一片花瓣的 (right, left)，每个是形状 (3, nv, nu) 的坐标数组。

    与 `blender_ellipsoid.petal()` 逐条对应：
      * 取椭球冠 u∈[0,π], v∈[0,θ]（θ = π/2 − π/n）；
      * Rx(−90°) 把北极 (0,0,c) 转到 +y；
      * 平移 (x_d, −y_d, 0) 把冠的边缘弧落到 y=0 平面上，
        其中 x_d = a·sinθ, y_d = c·cosθ；
      * 左半 = 右半绕竖直线 {x=x_d, y=0} 转 180°（等价于原代码的
        diag(−1,−1,1) + 平移，但不再需要 4x4 齐次矩阵）。
    """
    th = math.pi / 2 - math.pi / n
    x_d, y_d = a * math.sin(th), c * math.cos(th)

    u = np.linspace(0.0, math.pi, nu)
    v = np.linspace(0.0, th, nv)
    U, V = np.meshgrid(u, v)

    # 椭球冠 + Rx(-90)： (x, y, z) -> (x, z, -y)，再平移
    px = a * np.cos(U) * np.sin(V) + x_d
    py = c * np.cos(V) - y_d
    pz = -b * np.sin(U) * np.sin(V)

    right = np.stack([px, py, pz])
    left = np.stack([2 * x_d - px, -py, pz])  # 半周旋转
    return right, left


# --------------------------------------------------------------------------
# 2) 对称群 + 层栈：把“一片花瓣”变成“一朵花”
# --------------------------------------------------------------------------


def _rot(tilt_deg):
    """欧拉角(度) -> 3x3 旋转矩阵，顺序 Rx 先、Ry、Rz 后（与原代码一致）。"""
    rx, ry, rz = np.radians(tilt_deg)
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def place(p, tilt=(0, 0, 0), scale=1.0, pos=(0, 0, 0)):
    """world = R(tilt) · (scale ⊙ p) + pos —— 与 Blender 空对象变换同序。"""
    s = np.asarray(scale, dtype=float).reshape(-1, 1, 1)  # 标量或 (3,) 都可
    q = np.einsum("ij,j...->i...", _rot(tilt), s * p)
    return q + np.asarray(pos, dtype=float).reshape(3, 1, 1)


def rose_layers(
    M=5,
    N=12,
    scale_range=(math.sqrt(8), 1.0),
    cup=(15.0, 30.0),
    droop=-15.0,
    phase=None,
):
    """层栈的闭式配方，返回 [(rx_deg, ry_deg, phase_deg, scale), ...]。

    这是把 `blender_ellipsoid.py` 末尾手写的 L0..L4 表格归纳出来的四条规律：
      scale  = 等比插值 scale_range      （外层大、内层小，几何衰减）
      ry     = droop · j                 （线性下倾，形成“卷”）
      rx     = cup 线性“杯角”            （内层更立）
      phase  = (j+1 mod 2) · 180/N       （相邻层错开半瓣 = 叶序错列）
    对照原 demo：ry 与 phase 完全一致；scale 最大偏差 0.18，rx 最大偏差 7.5°
    （作者把内两层手调得比等比略大、杯角取的是 15/30 台阶而非线性）。
    """
    phase = (180.0 / N) if phase is None else phase
    s0, s1 = scale_range
    out = []
    for j in range(M):
        t = j / max(1, M - 1)
        rx = cup[0] + (cup[1] - cup[0]) * t
        s = s0 * (s1 / s0) ** t
        out.append((rx, droop * j, ((j + 1) % 2) * phase, s))
    return out


# demo 里手写的 5 层（L0..L4），原样保留以便逐像素比对
ROSE = [
    (15.0, 0.0, 15.0, math.sqrt(8)),
    (15.0, -15.0, 0.0, 2.0),
    (30.0, -30.0, 15.0, 1.5),
    (30.0, -45.0, 0.0, 1.3),
    (30.0, -60.0, 15.0, 1.0),
]


def atlas(surfs, gap=1):
    """把若干 (3,nv,nu) 曲面拼成一张大网格，用全 NaN 列分隔。

    仅 plotly 能正确把 NaN 列当作空洞；matplotlib 的 plot_surface 会在
    空洞处补出乱三角，所以 matplotlib 后端逐片绘制，不走这里。
    """
    if len(surfs) == 1:
        return surfs[0]
    parts = []
    for i, s in enumerate(surfs):
        if i:
            parts.append(np.full((3, s.shape[1], gap), np.nan))
        parts.append(s)
    return np.concatenate(parts, axis=2)


def flower(
    a=2.0,
    b=1 / 3,
    c=2.0,
    n=4,
    N=12,
    layers=None,
    nu=48,
    nv=24,
    palette=None,
):
    """生成花朵，返回按 (层, 半片) 分组的批次列表，可直接交给任一后端绘制。

    layers: [(rx, ry, phase, scale), ...]，默认 `ROSE`（原 demo 的 L0..L4）。
    返回元素: {"name", "color", "surfs": [(3, nv, nu) × N]}
    """
    layers = ROSE if layers is None else layers
    palette = palette or _PALETTE
    right, left = petal(a, b, c, n, nu, nv)

    batches = []
    for j, (rx, ry, phase, s) in enumerate(layers):
        color = palette[j % len(palette)]
        for side, base in (("R", right), ("L", left)):
            step = 360.0 / N
            surfs = [
                place(base, tilt=(rx, ry, phase + i * step), scale=s)
                for i in range(N)
            ]
            batches.append({"name": f"L{j}{side}", "color": color, "surfs": surfs})
    return batches


_PALETTE = [
    "#ffb3d9",
    "#ff8fc4",
    "#f76fae",
    "#e04f97",
    "#b8327f",
    "#8e1f6b",
]


# --------------------------------------------------------------------------
# 3) 后端：plotly（交互）/ matplotlib（预览）
# --------------------------------------------------------------------------


def draw_plotly(batches, title="Ellipsoid Flower", opacity=0.85, use_atlas=False):
    """use_atlas=True 时把同层同半的 N 片压成 1 个 trace（120→10）。

    依赖 plotly.js 对 NaN 空洞的处理；matplotlib 走不了这条路，所以默认关闭。
    """
    import plotly.graph_objects as go

    fig = go.Figure()
    for b in batches:
        surfs = [atlas(b["surfs"])] if use_atlas else b["surfs"]
        for xyz in surfs:
            x, y, z = xyz
            fig.add_trace(
                go.Surface(
                    x=x,
                    y=y,
                    z=z,
                    name=b["name"],
                    colorscale=[[0, b["color"]], [1, b["color"]]],
                    showscale=False,
                    opacity=opacity,
                    hovertemplate=b["name"] + "<extra></extra>",
                )
            )
    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z (花轴)",
            aspectmode="data",
            camera=dict(eye=dict(x=1.4, y=-1.6, z=0.9)),
        ),
        width=900,
        height=700,
        margin=dict(l=0, r=0, t=40, b=0),
    )
    return fig


def _bounds(batches):
    lo, hi = [], []
    for b in batches:
        for s in b["surfs"]:
            pts = s.reshape(3, -1)
            pts = pts[:, ~np.isnan(pts).any(axis=0)]
            lo.append(pts.min(axis=1))
            hi.append(pts.max(axis=1))
    return np.vstack(lo).min(axis=0), np.vstack(hi).max(axis=0)


def draw_matplotlib(batches, title="Ellipsoid Flower", alpha=0.85, ax=None):
    import matplotlib.pyplot as plt

    if ax is None:
        fig = plt.figure(figsize=(9, 9))
        ax = fig.add_subplot(111, projection="3d")
    else:
        fig = ax.figure

    for b in batches:  # matplotlib 不能用 NaN 拼接，逐片绘制
        for s in b["surfs"]:
            x, y, z = s
            ax.plot_surface(
                x, y, z, color=b["color"], alpha=alpha, linewidth=0, antialiased=False
            )

    lo, hi = _bounds(batches)
    mid, r = (lo + hi) / 2, (hi - lo).max() / 2
    ax.set_xlim(mid[0] - r, mid[0] + r)
    ax.set_ylim(mid[1] - r, mid[1] + r)
    ax.set_zlim(mid[2] - r, mid[2] + r)
    ax.set_box_aspect((1, 1, 1))
    ax.set_axis_off()
    ax.view_init(elev=35, azim=-60)
    ax.set_title(title)
    fig.tight_layout()
    return fig


def render(**kw):
    """一步到位：生成几何 + 出图。返回 (fig, backend)。"""
    backend = kw.pop("backend", "plotly")
    title = kw.pop("title", "Ellipsoid Flower")
    batches = flower(**kw)
    draw = {"plotly": draw_plotly, "mpl": draw_matplotlib, "matplotlib": draw_matplotlib}
    if backend not in draw:
        raise ValueError(f"unknown backend: {backend}")
    return draw[backend](batches, title=title), backend


def main():
    import argparse

    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--backend", default="plotly", choices=["plotly", "mpl"])
    p.add_argument("--petals", type=int, default=12, help="每层花瓣数 N")
    p.add_argument("--layers", type=int, default=5, help="层数 M")
    p.add_argument("--n", type=int, default=4, help="花瓣生成参数 n (θ=π/2−π/n)")
    p.add_argument("--res", type=int, default=48, help="u 方向分辨率 nu")
    p.add_argument("--recipe", action="store_true", help="用 rose_layers() 闭式配方")
    p.add_argument("--save", metavar="FILE", help="导出到 .html/.png 而不弹窗")
    args = p.parse_args()

    nv = max(6, args.res // 2)
    layers = rose_layers(args.layers, args.petals) if args.recipe else None
    batches = flower(n=args.n, N=args.petals, layers=layers, nu=args.res, nv=nv)

    if args.save:
        if args.save.endswith(".html"):
            draw_plotly(batches).write_html(args.save, include_plotlyjs="cdn")
        else:
            draw_matplotlib(batches).savefig(args.save, dpi=150, bbox_inches="tight")
        print("saved:", args.save)
    elif args.backend == "plotly":
        draw_plotly(batches).show()
    else:
        import matplotlib.pyplot as plt

        draw_matplotlib(batches)
        plt.show()


if __name__ == "__main__":
    main()

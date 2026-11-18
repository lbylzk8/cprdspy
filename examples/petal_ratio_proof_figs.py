"""
花瓣长度比 R/r 证明用的"教科书式"配图（初等几何版，图内中文标注）。

生成四张图到 docs/images/：
  petal-anatomy.png      一片花瓣的解剖：rho、圆心距 d_c、半瓣长 a、瓣长 R、张角 theta_p、拱宽 d
  petal-two-petals.png   两瓣相交：内弧心 C1、C2，中点 M，小花瓣 = 圆C1 与 圆C2 的交（r = 2|OM|）
  petal-projection.png   把 |OM| 拆成两段投影：|OM| = a cos(gamma) - (d_c/2) sin(gamma)
  petal-angle-chase.png  角度追逐：theta_s = theta_p - theta 的纯几何来源

约定：一片花瓣 = 两个半径 rho 的圆盘的交（lens）。把花瓣摆平（轴 = +x）时，
  下侧圆心 P=(a,-d_c/2) 生成【上】边界弧，上侧圆心 Q=(a,+d_c/2) 生成【下】边界弧
  ——lens 的边界弧总属于"对面那一侧"的圆心。
运行：python examples/petal_ratio_proof_figs.py
"""

from pathlib import Path

import numpy as np

OUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "images"
DEG = 180.0 / np.pi

BLUE, RED, OCHRE, GREEN = "#1f6fb4", "#c92a2a", "#a06a00", "#2b8a3e"
GREY = "0.35"


def _setup_plt():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["mathtext.fontset"] = "dejavusans"
    return plt


def rot(phi):
    c, s = np.cos(phi), np.sin(phi)
    return np.array([[c, -s], [s, c]])


def arc_points(center, rho, p_from, p_to, n=800):
    """沿圆 center 从 p_from 到 p_to 走短弧。"""
    a0 = np.arctan2(*(p_from - center)[::-1])
    a1 = np.arctan2(*(p_to - center)[::-1])
    t = a0 + ((a1 - a0 + np.pi) % (2 * np.pi) - np.pi) * np.linspace(0, 1, n)
    return np.stack([center[0] + rho * np.cos(t), center[1] + rho * np.sin(t)], axis=1)


def _sweep(vertex, p_from, p_to):
    a0 = np.arctan2(*(p_from - vertex)[::-1])
    a1 = np.arctan2(*(p_to - vertex)[::-1])
    return a0, (a1 - a0 + np.pi) % (2 * np.pi) - np.pi


def wedge(ax, vertex, p_from, p_to, radius, color="k", lw=1.3, n=180):
    a0, d = _sweep(vertex, p_from, p_to)
    t = a0 + d * np.linspace(0, 1, n)
    pts = vertex + radius * np.stack([np.cos(t), np.sin(t)], axis=1)
    ax.plot(pts[:, 0], pts[:, 1], color=color, lw=lw, zorder=7)
    return a0, d


def angle_label(ax, vertex, p_from, p_to, radius, text, pull=0.20, fontsize=12,
                mid_frac=0.5, extra_ang=None, color="k", **kw):
    """画楔形并标角度；extra_ang（弧度）可把标签挪到指定方向。"""
    a0, d = wedge(ax, vertex, p_from, p_to, radius, color=color, **kw)
    ang = a0 + d * mid_frac if extra_ang is None else extra_ang
    r = radius + pull
    ax.text(vertex[0] + r * np.cos(ang), vertex[1] + r * np.sin(ang), text,
            fontsize=fontsize, ha="center", va="center", zorder=8, color=color)


def right_angle(ax, at, u, v, size=0.06, color="0.4"):
    u, v = np.asarray(u, float), np.asarray(v, float)
    p1, p2, p3 = at + size * u, at + size * (u + v), at + size * v
    ax.plot([p1[0], p2[0], p3[0]], [p1[1], p2[1], p3[1]], color=color, lw=1.1, zorder=7)


def dot(ax, p, label=None, off=(0.05, 0.05), ms=5.0, mfc=BLUE, mec=BLUE, fs=13, hollow=False):
    ax.plot([p[0]], [p[1]], "o", ms=ms, mfc="none" if hollow else mfc, mec=mec, zorder=9)
    if label:
        ax.text(*(np.asarray(p, float) + np.asarray(off, float)), label, fontsize=fs, zorder=9)


def seg(ax, p_from, p_to, color=GREY, lw=1.1, ls="-", z=5):
    ax.plot([p_from[0], p_to[0]], [p_from[1], p_to[1]], color=color, lw=lw, ls=ls, zorder=z)


def arrow(ax, p_from, p_to, color=GREY, lw=1.5, ls="-", z=6):
    ax.annotate("", xy=p_to, xytext=p_from,
                arrowprops=dict(arrowstyle="-|>", lw=lw, color=color, linestyle=ls,
                                shrinkA=0, shrinkB=0), zorder=z)


def midlabel(ax, p_from, p_to, text, offset=(0.0, 0.06), color="0.1", fontsize=12.5, ha="center"):
    m = (np.asarray(p_from, float) + np.asarray(p_to, float)) / 2
    ax.text(m[0] + offset[0], m[1] + offset[1], text, fontsize=fontsize, color=color,
            ha=ha, va="center", zorder=8)


def new_ax(fig, rect, title=None):
    ax = fig.add_axes(rect)
    ax.set_aspect("equal")
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=12.5, pad=8)
    return ax


def petal_lens(rho, dc):
    """把一片花瓣摆平（轴 = +x）。下侧圆心 P 生成上边界弧。"""
    a = np.sqrt(rho**2 - dc**2 / 4)
    R = 2 * a
    return dict(a=a, R=R, rho=rho, dc=dc,
                O=np.array([0.0, 0.0]), A=np.array([R, 0.0]),
                P=np.array([a, -dc / 2]), Q=np.array([a, dc / 2]),
                M=np.array([a, 0.0]), W=np.array([a, rho - dc / 2]))


def draw_lens(ax, g, lw=2.4, color=BLUE, circles=True):
    rho, O, A = g["rho"], g["O"], g["A"]
    if circles:
        th = np.linspace(0, 2 * np.pi, 800)
        for c in (g["P"], g["Q"]):
            ax.plot(c[0] + rho * np.cos(th), c[1] + rho * np.sin(th),
                    color="0.87", lw=0.9, ls=":", zorder=0)
    ax.plot(*arc_points(g["P"], rho, O, A).T, lw=lw, color=color, zorder=3)
    ax.plot(*arc_points(g["Q"], rho, O, A).T, lw=lw, color=color, zorder=3)
    seg(ax, O, A, color="0.4", lw=1.0, ls="-.", z=2)


def tips(ax, g):
    dot(ax, g["O"], "$O$", (-0.14, -0.02))
    dot(ax, g["A"], "$A$", (0.05, -0.02))


def tip_tangents(ax, g, length=0.62, color=OCHRE, full=True):
    """尖端 A 的两条切线（full=True 时向两侧延长）。返回朝花瓣【外侧】的单位方向。"""
    A, O = g["A"], g["O"]
    outs = []
    for c in (g["P"], g["Q"]):
        u = (A - c) / np.linalg.norm(A - c)
        t = np.array([-u[1], u[0]])
        if np.dot(t, O - A) > 0:                 # 让 t 背离 O（指向花瓣外）
            t = -t
        p0, p1 = (A - length * t, A + length * t) if full else (A, A + length * t)
        seg(ax, p0, p1, color=color, lw=1.3, ls="--", z=4)
        seg(ax, c, A, color="0.62", lw=0.9, ls=":", z=1)
        outs.append(t)
    return outs


def root_tangents(ax, g, length=1.05, color=OCHRE):
    """根部 O 处两条边界弧的切线（= 花瓣的开口角两边）。返回两条射线的单位方向。"""
    O = g["O"]
    outs = []
    for c in (g["P"], g["Q"]):
        u = (c - O) / np.linalg.norm(c - O)      # 半径方向
        t = np.array([-u[1], u[0]])
        if t[0] < 0:
            t = -t                               # 取指向花瓣那一侧
        arrow(ax, O, O + length * t, color=color, lw=1.4, ls="--", z=6)
        seg(ax, O, c, color="0.45", lw=1.1, ls="--", z=3)
        right_angle(ax, O, u, t, size=0.075)
        outs.append(t)
    return outs


def safe_text(ax, x, y, *lines, **kw):
    """多行文本：先检查每行 $ 成对，避免"半个数学环境"导致的排版事故。"""
    s = "\n".join(lines)
    bad = [ln for ln in s.split("\n") if ln.count("$") % 2]
    assert not bad, "unbalanced $ in: " + repr(bad)
    return ax.text(x, y, s, **kw)


def panel_with_text(fig, x0, title, lines, fs=11.8):
    """上图下文字：文字占独立坐标轴，永远不会压住图形。返回图形轴。"""
    ax = new_ax(fig, [x0, 0.375, 0.30, 0.50], title)
    tx = fig.add_axes([x0, 0.015, 0.30, 0.335])
    tx.axis("off")
    tx.set_xlim(0, 1); tx.set_ylim(0, 1)
    safe_text(tx, 0.015, 0.99, *lines, fontsize=fs, ha="left", va="top",
              linespacing=1.8)
    return ax


# ==================================================== 图 1：一片花瓣的解剖（三栏）
def figure_anatomy(rho=1.0, dc=1.2):
    """示例取 3-4-5 直角三角形：rho=1, d_c/2=0.6 -> a=0.8, R=1.6, d=0.8。
    故意不用 rho=d_c（那时最宽弦刚好等于圆心距、W 与 Q 重合，图上分不清）。"""
    plt = _setup_plt()
    g = petal_lens(rho, dc)
    a, R, O, A, P, Q, M, W = (g[k] for k in ("a", "R", "O", "A", "P", "Q", "M", "W"))
    Wb = np.array([a, -(rho - dc / 2)])
    theta_p = 2 * np.arctan(R / dc)
    d = 2 * rho - dc
    XL, XR = (-0.45, 2.15), (-0.98, 0.92)

    fig = plt.figure(figsize=(15.4, 6.3))

    # ---- (a) 圆心距 d_c 与勾股 -> R = 2a
    ax = panel_with_text(fig, 0.015, "（a）圆心距 $d_c=|PQ|$；勾股给 $a$，$R=2a$", [
        r"直角三角形 $OMP$，直角在 $M$：",
        r"$a^{2}+\left(\dfrac{d_c}{2}\right)^{2}=\rho^{2}"
        r"\quad\Rightarrow\quad a=\sqrt{\rho^{2}-\dfrac{d_c^{2}}{4}}$",
        r"尖 $A$ 与根 $O$ 关于竖线 $PQ$ 对称，故 $R=|OA|=2a$。",
    ])
    draw_lens(ax, g)
    seg(ax, P, Q, color=OCHRE, lw=3.0, z=6)
    seg(ax, O, P, color="0.3", lw=1.2, ls="--", z=3)
    seg(ax, A, P, color="0.3", lw=1.2, ls="--", z=3)
    ax.fill([O[0], M[0], P[0]], [O[1], M[1], P[1]], color="#fff3cd", alpha=0.95, zorder=1)
    right_angle(ax, M, np.array([0.0, -1.0]), np.array([1.0, 0.0]))
    dot(ax, P, "$P$", (0.07, -0.05), mfc=OCHRE, mec=OCHRE)
    dot(ax, Q, "$Q$", (0.07, 0.0), mfc=OCHRE, mec=OCHRE)
    tips(ax, g)
    dot(ax, M, "$M$", (-0.02, -0.15), ms=3.5, mfc="none", mec=GREY)
    midlabel(ax, O, P, r"$\rho$", (-0.13, -0.02))
    midlabel(ax, A, P, r"$\rho$", (0.10, -0.03))
    midlabel(ax, O, M, r"$a$", (0.0, -0.13), color="#7b241c")
    midlabel(ax, M, A, r"$a$", (0.0, -0.13), color="#7b241c")
    midlabel(ax, M, Q, r"$\dfrac{d_c}{2}$", (0.08, 0.02), color=OCHRE, ha="left")
    midlabel(ax, P, M, r"$\dfrac{d_c}{2}$", (0.08, -0.02), color=OCHRE, ha="left")
    ax.set_xlim(*XL); ax.set_ylim(*XR)

    # ---- (b) 拱宽 d：最宽的弦正好落在两圆心连线上
    ax = panel_with_text(fig, 0.355, "（b）拱宽 $d$：竖线 $PQ$ 截出的最长弦", [
        r"竖线过圆心 $P$，故 $|PW|=\rho$、$|PM|=\dfrac{d_c}{2}$，",
        r"$|MW|=\rho-\dfrac{d_c}{2}$，最宽弦 $d=2|MW|=2\rho-d_c$。",
        r"又 $R^{2}=4\rho^{2}-d_c^{2}=(2\rho-d_c)(2\rho+d_c)$，",
        r"代入 $2\rho=d+d_c$ 得 $R^{2}=d^{2}+2d\,d_c$。",
    ])
    draw_lens(ax, g)
    seg(ax, P, Q, color=OCHRE, lw=1.6, z=5)
    seg(ax, W, Wb, color=RED, lw=3.4, z=6)
    right_angle(ax, M, np.array([0.0, 1.0]), np.array([1.0, 0.0]))
    dot(ax, W, "$W$", (0.07, 0.02), mfc=RED, mec=RED)
    dot(ax, Wb, "$W'$", (-0.20, -0.06), mfc=RED, mec=RED)
    dot(ax, P, "$P$", (0.07, -0.05), mfc=OCHRE, mec=OCHRE)
    dot(ax, Q, "$Q$", (0.07, 0.0), mfc=OCHRE, mec=OCHRE)
    tips(ax, g)
    dot(ax, M, "$M$", (-0.02, -0.14), ms=3.5, mfc="none", mec=GREY)
    midlabel(ax, M, W, r"$\dfrac{d}{2}$", (0.09, 0.04), color=RED, ha="left", fontsize=12.5)
    midlabel(ax, P, M, r"$\dfrac{d_c}{2}$", (0.09, -0.04), color=OCHRE, ha="left")
    ax.set_xlim(*XL); ax.set_ylim(*XR)

    # ---- (c) 张角 theta_p：根部两条切线的夹角
    ax = panel_with_text(fig, 0.695,
                         "（c）张角 $\\theta_p$：根部两切线夹角 $=2\\arctan(R/d_c)$", [
        r"半径 $\perp$ 切线，轴夹在中间：$\dfrac{\theta_p}{2}+\angle POM=90^{\circ}$；",
        r"直角三角形 $OMP$：$\angle OPM+\angle POM=90^{\circ}$；相减得",
        r"$\dfrac{\theta_p}{2}=\angle OPM$，$\tan\angle OPM=\dfrac{|OM|}{|MP|}=\dfrac{R}{d_c}$，",
        r"即 $\theta_p=2\arctan\dfrac{R}{d_c}$（尖端两切线夹角也是 $\theta_p$）。",
    ])
    draw_lens(ax, g, circles=False)
    ax.fill([O[0], M[0], P[0]], [O[1], M[1], P[1]], color="#fff3cd", alpha=0.95, zorder=1)
    t1, t2 = root_tangents(ax, g)
    seg(ax, P, Q, color=OCHRE, lw=2.6, z=6)
    right_angle(ax, M, np.array([0.0, 1.0]), np.array([1.0, 0.0]))
    angle_label(ax, P, O, M, 0.30, r"$\dfrac{\theta_p}{2}$", pull=0.15,
                color="#7b241c", fontsize=12.5)
    angle_label(ax, O, P, M, 0.34, r"$\delta$", pull=0.10, color="0.35", fontsize=12)
    wedge(ax, O, t1, t2, 0.55, color=OCHRE, lw=1.6)
    ax.text(0.70, 0.17, r"$\theta_p$", fontsize=13.5, color=OCHRE,
            ha="center", va="center", zorder=8)
    dot(ax, P, "$P$", (0.07, -0.05), mfc=OCHRE, mec=OCHRE)
    dot(ax, Q, "$Q$", (0.07, 0.0), mfc=OCHRE, mec=OCHRE)
    tips(ax, g)
    dot(ax, M, "$M$", (-0.02, -0.15), ms=3.5, mfc="none", mec=GREY)
    ax.set_xlim(*XL); ax.set_ylim(*XR)

    fig.suptitle("图 1　一片对称弧花瓣 $=$ 两个半径 $\\rho$ 的圆盘的交。"
                 "示例 $\\rho=1,\\ d_c=1.2$：$a=0.8,\\ R=1.6,\\ d=0.8,\\ \\theta_p\\approx106.3^{\\circ}$",
                 fontsize=13.5, y=0.975)
    p = OUT_DIR / "petal-anatomy.png"
    fig.savefig(p, dpi=150)
    plt.close("all")
    return p


# ==================================================== 两瓣构造的公共几何
def build_pair(rho, dc, theta):
    a = np.sqrt(rho**2 - dc**2 / 4)
    R = 2 * a
    g = theta / 2
    C1 = rot(-g) @ np.array([a, -dc / 2])   # 花瓣1 内弧心（在轴的外侧）
    C1o = rot(-g) @ np.array([a, dc / 2])   # 花瓣1 外弧心
    C2 = rot(g) @ np.array([a, dc / 2])     # 花瓣2 内弧心
    C2o = rot(g) @ np.array([a, -dc / 2])   # 花瓣2 外弧心

    def far(cA, cB):
        v = cB - cA
        n = np.linalg.norm(v)
        if n < 1e-12 or n > 2 * rho:
            return None
        mid = (cA + cB) / 2
        h = np.sqrt(max(rho**2 - (n / 2) ** 2, 0.0))
        perp = np.array([-v[1], v[0]]) / n
        p1, p2 = mid + h * perp, mid - h * perp
        return p1 if np.linalg.norm(p1) > np.linalg.norm(p2) else p2

    O = np.array([0.0, 0.0])
    k = dict(rho=rho, dc=dc, a=a, R=R, theta=theta, gamma=g, O=O,
             A=rot(-g) @ np.array([R, 0.0]), B=rot(g) @ np.array([R, 0.0]),
             C1=C1, C1o=C1o, C2=C2, C2o=C2o, M=(C1 + C2) / 2,
             N1=rot(-g) @ np.array([a, 0.0]), N2=rot(g) @ np.array([a, 0.0]))
    k["C"] = far(C1, C2)
    k["r"] = float(np.linalg.norm(k["C"]))
    k["theta_p"] = 2 * np.arctan(R / dc)
    k["theta_s"] = 2 * np.arcsin(k["r"] / (2 * rho))
    k["d"] = 2 * rho - dc
    return k


def petal_outline(ax, k, which, lw=1.9, color=BLUE):
    rho, O = k["rho"], k["O"]
    tip, cin, cout = ((k["A"], k["C1"], k["C1o"]) if which == 1
                      else (k["B"], k["C2"], k["C2o"]))
    ax.plot(*arc_points(cout, rho, O, tip).T, lw=lw, color=color, zorder=3)
    ax.plot(*arc_points(cin, rho, O, tip).T, lw=lw, color=color, zorder=3)


def small_petal(ax, k, lw=3.0):
    rho, O, C = k["rho"], k["O"], k["C"]
    up = arc_points(k["C1"], rho, O, C, 500)
    lo = arc_points(k["C2"], rho, O, C, 500)
    ax.fill(np.concatenate([up[:, 0], lo[::-1, 0]]), np.concatenate([up[:, 1], lo[::-1, 1]]),
            color="#f7d0d0", alpha=0.9, zorder=1)
    ax.plot(*up.T, lw=lw, color=RED, zorder=4)
    ax.plot(*lo.T, lw=lw, color=RED, zorder=4)


# ==================================================== 图 2：两瓣相交（标出 C1、C2）
def figure_two_petals(rho=1.0, dc=1.2, theta_deg=60.0):
    plt = _setup_plt()
    k = build_pair(rho, dc, theta_deg / DEG)
    O, A, B, C, M = k["O"], k["A"], k["B"], k["C"], k["M"]
    C1, C2, C1o, C2o, rho_, R, r = k["C1"], k["C2"], k["C1o"], k["C2o"], k["rho"], k["R"], k["r"]

    fig = plt.figure(figsize=(11.0, 8.2))
    ax = new_ax(fig, [0.03, 0.05, 0.94, 0.88])

    th = np.linspace(0, 2 * np.pi, 900)
    for c in (C1, C2):
        ax.plot(c[0] + rho_ * np.cos(th), c[1] + rho_ * np.sin(th),
                color="0.82", lw=0.9, ls=":", zorder=0)
    small_petal(ax, k)
    petal_outline(ax, k, 1); petal_outline(ax, k, 2)

    seg(ax, O, C * 1.14, color="0.25", lw=1.2, ls="-.", z=2)
    for P in (A, B):
        seg(ax, O, P, color="0.55", lw=0.8, ls=":", z=2)
    seg(ax, C1, C2, color=OCHRE, lw=2.8, z=6)
    seg(ax, O, C1, color="0.3", lw=1.2, ls="--", z=3)
    seg(ax, O, C2, color="0.3", lw=1.2, ls="--", z=3)
    right_angle(ax, M, np.array([0.0, 1.0]), np.array([1.0, 0.0]), size=0.055)
    midlabel(ax, O, C1, r"$\rho$", (-0.14, -0.04))
    midlabel(ax, O, C2, r"$\rho$", (-0.14, 0.04))
    midlabel(ax, O, M, r"$|OM|$", (0.0, -0.16), color=OCHRE, fontsize=12)
    midlabel(ax, M, C, r"$|OM|$", (0.0, 0.16), color=OCHRE, fontsize=12)

    for c, lab, off in ((C1, r"$C_1$", (0.04, -0.16)), (C2, r"$C_2$", (0.04, 0.09)),
                        (C1o, r"$C_1'$", (0.06, 0.06)), (C2o, r"$C_2'$", (0.06, -0.16))):
        hollow = "'" in lab
        dot(ax, c, lab, off, ms=7.5 if not hollow else 4.5,
             mfc=OCHRE if not hollow else "none", mec=OCHRE, hollow=hollow)
    dot(ax, O, "$O$", (-0.17, -0.02))
    dot(ax, A, "$A$", (0.04, -0.13))
    dot(ax, B, "$B$", (0.04, 0.05))
    dot(ax, C, "$C$", (0.05, 0.05), mfc=RED, mec=RED)
    dot(ax, M, "$M$", (-0.05, -0.15), ms=4, mfc="none", mec=OCHRE)

    safe_text(ax, -1.30, -0.62,
              f"$\\rho={rho},\\ d_c={dc},\\ \\theta={theta_deg:.0f}^\\circ$",
              f"$R=|OA|={R:.4f},\\quad r=|OC|=2|OM|={r:.4f}$",
              f"$R/r={R / r:.4f}$",
              fontsize=13, ha="left", va="top", linespacing=1.7)
    safe_text(ax, -1.28, 1.02,
              r"小花瓣 $=$ disk$(C_1)\cap$ disk$(C_2)$（两条内弧围成）",
              r"$|OC_1|=|OC_2|=\rho\ \Rightarrow\ O$、$C$ 关于 $C_1C_2$ 对称，$r=2|OM|$",
              fontsize=12.5, ha="left", va="top", linespacing=1.7,
              bbox=dict(fc="#f4f6fb", ec="0.82", boxstyle="round,pad=0.4"))
    ax.set_xlim(-1.45, 1.95); ax.set_ylim(-1.30, 1.12)
    ax.set_title(f"图 2　两瓣共基点 $O$、轴夹角 $\\theta={theta_deg:.0f}^\\circ$："
                 "内弧心 $C_1$、$C_2$ 与它们重叠出的小花瓣", fontsize=13.5, pad=10)
    p = OUT_DIR / "petal-two-petals.png"
    fig.savefig(p, dpi=150)
    plt.close("all")
    return p


# ==================================================== 图 3：|OM| 的两段投影
def figure_projection(rho=1.0, dc=1.2, theta_deg=64.0):
    plt = _setup_plt()
    k = build_pair(rho, dc, theta_deg / DEG)
    O, C, M, N1 = k["O"], k["C"], k["M"], k["N1"]
    C1, a, dc_, R, r, g = k["C1"], k["a"], k["dc"], k["R"], k["r"], k["gamma"]
    H1 = np.array([N1[0], 0.0])

    fig = plt.figure(figsize=(15.4, 6.6))

    # 左：花瓣摆平
    ax = new_ax(fig, [0.015, 0.10, 0.26, 0.80],
                "（a）摆平：轴下方的 $P=\\left(a,\\,-\\dfrac{d_c}{2}\\right)$ 生成【上】边界弧")
    gs = petal_lens(rho, dc)
    draw_lens(ax, gs, circles=False)
    seg(ax, gs["P"], gs["Q"], color=OCHRE, lw=2.2, z=6)
    right_angle(ax, gs["M"], np.array([0.0, 1.0]), np.array([1.0, 0.0]))
    dot(ax, gs["P"], "$P$", (0.06, -0.05), mfc=OCHRE, mec=OCHRE)
    dot(ax, gs["Q"], "$Q$", (0.06, 0.0), mfc=OCHRE, mec=OCHRE)
    tips(ax, gs)
    dot(ax, gs["M"], "$M$", (-0.02, -0.15), ms=3.5, mfc="none", mec=GREY)
    midlabel(ax, gs["O"], gs["M"], r"$a$", (0, -0.13), color="#7b241c")
    midlabel(ax, gs["P"], gs["M"], r"$\dfrac{d_c}{2}$", (-0.08, 0.0), color=OCHRE, ha="right")
    ax.set_xlim(-0.45, 2.15); ax.set_ylim(-1.00, 0.92)

    # 中：绕 O 转 gamma，投影到角平分线
    ax = new_ax(fig, [0.30, 0.10, 0.36, 0.80],
                "（b）绕 $O$ 转 $\\gamma$：把两段位移投到角平分线上")
    petal_outline(ax, k, 1)
    seg(ax, O, k["A"], color="0.4", lw=1.0, ls="-.", z=2)
    seg(ax, O, C * 1.22, color="0.25", lw=1.3, ls="-.", z=2)
    arrow(ax, O, N1, color=BLUE, lw=2.2)
    arrow(ax, N1, C1, color=OCHRE, lw=2.2)
    seg(ax, N1, H1, color="0.5", lw=1.0, ls="--", z=3)
    seg(ax, C1, M, color="0.5", lw=1.0, ls="--", z=3)
    right_angle(ax, H1, np.array([0.0, -1.0]), np.array([-1.0, 0.0]), size=0.05)
    right_angle(ax, M, np.array([0.0, 1.0]), np.array([-1.0, 0.0]), size=0.05)
    x_oh, x_hm = H1[0] / 2, (H1[0] + M[0]) / 2
    for x0, y1 in ((x_oh, 0.13), (x_hm, 0.36)):
        seg(ax, np.array([x0, 0.02]), np.array([x0, y1]), color="0.6", lw=0.8, ls=":", z=3)
    ax.text(x_oh, 0.15, r"$a\cos\gamma$", fontsize=12.5, color="#7b241c",
            ha="center", va="bottom", zorder=8)
    ax.text(x_hm, 0.38, r"$\dfrac{d_c}{2}\sin\gamma$", fontsize=12, color=OCHRE,
            ha="center", va="bottom", zorder=8)
    dot(ax, N1, "$N_1$", (0.03, 0.05), ms=4, mfc="none", mec=BLUE)
    dot(ax, H1, "$H_1$", (0.02, 0.06), ms=4, mfc="none", mec=GREY)
    dot(ax, C1, "$C_1$", (0.03, -0.17), mfc=OCHRE, mec=OCHRE)
    dot(ax, M, "$M$", (-0.05, -0.15), ms=4, mfc="none", mec=OCHRE)
    dot(ax, O, "$O$", (-0.14, 0.02)); dot(ax, C, "$C$", (0.05, -0.03), mfc=RED, mec=RED)
    dot(ax, k["A"], "$A$", (0.04, -0.12))
    midlabel(ax, O, N1, r"$a$", (0.02, 0.07), color=BLUE)
    midlabel(ax, N1, C1, r"$\dfrac{d_c}{2}$", (0.08, -0.02), color=OCHRE, ha="left")
    angle_label(ax, O, C, N1, 0.62, r"$\gamma$", pull=0.10, fontsize=12)
    angle_label(ax, C1, N1, M, 0.32, r"$\gamma$", pull=0.12, color=OCHRE, fontsize=12)
    ax.set_xlim(-0.20, 1.90); ax.set_ylim(-1.20, 0.75)

    # 右栏文字
    ax = fig.add_axes([0.685, 0.04, 0.305, 0.90])
    ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    safe_text(ax, 0.01, 0.99,
              r"只用一次勾股、两次投影：",
              r"$\overrightarrow{OC_1}=\overrightarrow{ON_1}+\overrightarrow{N_1C_1}$",
              "",
              r"沿花瓣轴那段：长 $a$，与角平分线夹角 $\gamma$，",
              r"$|OH_1|=a\cos\gamma$",
              "",
              r"垂直花瓣轴那段：长 $\dfrac{d_c}{2}$，",
              r"它朝角平分线的反方向偏，投影要减掉",
              r"$|H_1M|=\dfrac{d_c}{2}\sin\gamma$",
              "",
              r"$|OM|=a\cos\gamma-\dfrac{d_c}{2}\sin\gamma$",
              "",
              r"两边乘 2（$R=2a$、$r=2|OM|$）：",
              r"$r=R\cos\dfrac{\theta}{2}-d_c\sin\dfrac{\theta}{2}$",
              "",
              rf"$\rho={rho},\ d_c={dc},\ \theta={theta_deg:.0f}^\circ$：",
              rf"$a={a:.4f},\ |OM|={M[0]:.4f}$",
              rf"$r={r:.4f},\ R={R:.4f},\ R/r={R / r:.4f}$",
              fontsize=12, ha="left", va="top", linespacing=1.55)
    fig.suptitle("图 3　小花瓣长 $r$ 的初等推导：$r=2|OM|$，而 $|OM|$ 是两段位移的投影差",
                 fontsize=13.5, y=0.985)
    p = OUT_DIR / "petal-projection.png"
    fig.savefig(p, dpi=150)
    plt.close("all")
    return p


# ==================================================== 图 4：角度追逐 theta_s = theta_p - theta
def figure_angle_chase(rho=1.0, dc=1.2, theta_deg=56.0):
    plt = _setup_plt()
    k = build_pair(rho, dc, theta_deg / DEG)
    O, A, B, C, C1, C2 = k["O"], k["A"], k["B"], k["C"], k["C1"], k["C2"]
    tp, ts = k["theta_p"], k["theta_s"]

    fig = plt.figure(figsize=(11.6, 7.6))
    ax = new_ax(fig, [0.03, 0.05, 0.94, 0.86])
    small_petal(ax, k)
    petal_outline(ax, k, 1); petal_outline(ax, k, 2)

    reach, rc = 1.55, 1.06
    for P, lab, col, off in ((A, "$A$", BLUE, (0.10, 0.02)),
                             (B, "$B$", BLUE, (0.10, 0.02)),
                             (C, "$C$", RED, (0.02, 0.07))):
        u = P / np.linalg.norm(P)
        arrow(ax, O, reach * u, color=col, lw=1.4)
        ax.text(*(np.asarray(P, float) + np.asarray(off, float)), lab,
                fontsize=13, color=col, zorder=9)
    for c, lab, off in ((C1, "$C_1$", (0.07, -0.06)), (C2, "$C_2$", (0.07, 0.01))):
        u = c / np.linalg.norm(c)
        arrow(ax, O, rc * u, color=OCHRE, lw=1.3, ls="--")
        dot(ax, c, None, mfc=OCHRE, mec=OCHRE)
        ax.text(*(np.asarray(c, float) + np.asarray(off, float)), lab,
                fontsize=13, color=OCHRE, zorder=9)
    dot(ax, O, "$O$", (-0.15, -0.02))

    angle_label(ax, O, A, C, 0.48, r"$\gamma$", pull=0.11, fontsize=12)
    angle_label(ax, O, C, B, 0.48, r"$\gamma$", pull=0.11, fontsize=12)
    angle_label(ax, O, A, C1, 0.88, r"$\delta$", pull=0.16, color=OCHRE, fontsize=13)
    angle_label(ax, O, C2, B, 0.88, r"$\delta$", pull=0.16, color=OCHRE, fontsize=13)
    wedge(ax, O, C1, C2, 1.18, color="k", lw=1.6)
    ax.text(1.24, 0.57, r"$\angle C_1OC_2$", fontsize=12, color="0.1", ha="left")

    safe_text(ax, -1.86, 1.22,
              r"$\delta=90^{\circ}-\dfrac{\theta_p}{2}$：花瓣轴 $\to$ 内弧心的方向",
              r"$\angle C_1OC_2=2\delta+\theta=180^{\circ}-\theta_p+\theta$",
              r"$\theta_s=180^{\circ}-\angle C_1OC_2=\theta_p-\theta$",
              r"$R=2\rho\sin\dfrac{\theta_p}{2},\ r=2\rho\sin\dfrac{\theta_s}{2}$",
              r"$\Rightarrow\ \dfrac{R}{r}=\dfrac{\sin(\theta_p/2)}{\sin(\theta_s/2)}$",
              rf"$\theta_p={tp * DEG:.1f}^\circ,\ \theta={theta_deg:.0f}^\circ"
              rf"\ \Rightarrow\ \theta_s={ts * DEG:.1f}^\circ,\ R/r={k['R'] / k['r']:.4f}$",
              fontsize=12.5, ha="left", va="top", linespacing=1.9,
              bbox=dict(fc="#f4f6fb", ec="0.82", boxstyle="round,pad=0.5"))
    ax.set_xlim(-1.95, 1.95); ax.set_ylim(-1.35, 1.25)
    ax.set_title("图 4　角度追逐：$\\theta_s=\\theta_p-\\theta$（只用切线 $\\perp$ 半径、对称性与圆周角定理）",
                 fontsize=13.5, pad=10)
    p = OUT_DIR / "petal-angle-chase.png"
    fig.savefig(p, dpi=150)
    plt.close("all")
    return p


if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for fn in (figure_anatomy, figure_two_petals, figure_projection, figure_angle_chase):
        print(fn())

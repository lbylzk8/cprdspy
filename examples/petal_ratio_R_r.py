"""
大花瓣 / 小花瓣 长度比 R/r 的几何构造与验证。

模型（与 cprdspy 的 n 花瓣 / docs/一般对称中心花的数学及算法.md 一致）：
    花瓣 = 两个半径 rho 的圆盘的交（lens），两圆心关于花瓣轴对称、间距 dc，两圆都过根部 O。
    半长  a   = sqrt(rho^2 - dc^2/4)
    瓣长  L   = 2a
    张角  theta_p = 2*arctan(2a/dc) = 2*arctan(L/dc)
    最大拱宽 w = 2*rho - dc            （"对称弧最大距离"）

两片全等花瓣共基点 O，轴夹角 theta。相交形成的小花瓣仍以 O 为一个顶点，
另一个顶点 C 是两条"内侧弧"所在圆的第二个交点。

结论（本文件用数值验证）：
    r = |OC| = L*cos(theta/2) - dc*sin(theta/2)
    R/r = L / (L*cos(theta/2) - dc*sin(theta/2))
        = sin(theta_p/2) / sin((theta_p - theta)/2)
        = 1 / (cos(theta/2) - ((L**2 - w**2)/(2*L*w))*sin(theta/2))     # 用拱宽 w
    n 花瓣（rho = Rc，花瓣都从花心出发）：
        = cos(pi/n) / cos(pi/n + theta/2)
    相邻花瓣（theta = 2*pi/n）：
        = cos(pi/n) / cos(2*pi/n) = cos(theta/2)/cos(theta)

运行：  python examples/petal_ratio_R_r.py [--save]
"""

import numpy as np

DEG = 180.0 / np.pi


def rot(phi):
    c, s = np.cos(phi), np.sin(phi)
    return np.array([[c, -s], [s, c]])


def build(rho, dc, theta):
    """返回构造中的所有关键点与圆心。"""
    a = np.sqrt(rho**2 - dc**2 / 4)
    L = 2 * a
    # 花瓣 1：轴在 -theta/2 ；花瓣 2：轴在 +theta/2
    # 规范坐标（轴=+x）：上边界弧 <- 圆心 (a,-dc/2)；下边界弧 <- 圆心 (a,+dc/2)
    c1_in = rot(-theta / 2) @ np.array([a, -dc / 2])   # 花瓣1 内侧弧（上边界）
    c1_out = rot(-theta / 2) @ np.array([a, dc / 2])   # 花瓣1 外侧弧（下边界）
    c2_in = rot(theta / 2) @ np.array([a, dc / 2])     # 花瓣2 内侧弧（下边界）
    c2_out = rot(theta / 2) @ np.array([a, -dc / 2])   # 花瓣2 外侧弧（上边界）
    O = np.array([0.0, 0.0])

    def other(cA, cB):
        """两个等半径圆的交点中，取不是 O 的那个。"""
        d = cB - cA
        n = np.linalg.norm(d)
        if n < 1e-12 or n > 2 * rho:
            return None
        mid = (cA + cB) / 2
        h = np.sqrt(max(rho**2 - (n / 2) ** 2, 0.0))
        perp = np.array([-d[1], d[0]]) / n
        p1, p2 = mid + h * perp, mid - h * perp
        return p1 if np.linalg.norm(p1) > np.linalg.norm(p2) else p2

    return dict(
        a=a, L=L, rho=rho, dc=dc, theta=theta, O=O,
        A=rot(-theta / 2) @ np.array([L, 0.0]),      # 花瓣1 尖
        B=rot(theta / 2) @ np.array([L, 0.0]),       # 花瓣2 尖
        C=other(c1_in, c2_in),                       # 小花瓣尖
        D=other(c2_in, c1_out),                      # 花瓣2内弧 x 花瓣1外弧
        E=other(c1_in, c2_out),                      # 花瓣1内弧 x 花瓣2外弧
        c1_in=c1_in, c1_out=c1_out, c2_in=c2_in, c2_out=c2_out,
    )


def formulas(k):
    L, dc, theta = k["L"], k["dc"], k["theta"]
    rho = k["rho"]
    a = k["a"]
    theta_p = 2 * np.arctan(2 * a / dc)
    w = 2 * rho - dc
    r_direct = L * np.cos(theta / 2) - dc * np.sin(theta / 2)
    r_apex = L * np.sin((theta_p - theta) / 2) / np.sin(theta_p / 2)
    r_width = L / (1 / (np.cos(theta / 2) - ((L**2 - w**2) / (2 * L * w)) * np.sin(theta / 2)))
    return dict(R=L, r=r_direct, r_apex=r_apex, r_width=r_width,
                ratio=L / r_direct, theta_p=theta_p, w=w)


def verify_row(rho, dc, theta):
    k = build(rho, dc, theta)
    f = formulas(k)
    r_num = np.linalg.norm(k["C"])
    ok = abs(r_num - f["r"])
    return k, f, r_num, ok


def petal_arc_points(k, center_key, tip_key, n=800):
    """边界弧采样：从 O 到 tip，沿 center_key 所指圆心的圆。"""
    rho, O = k["rho"], k["O"]
    tip = k[tip_key]
    c = k[center_key]
    ang0 = np.arctan2(O[1] - c[1], O[0] - c[0])
    ang1 = np.arctan2(tip[1] - c[1], tip[0] - c[0])
    d = (ang1 - ang0 + np.pi) % (2 * np.pi) - np.pi
    t = ang0 + d * np.linspace(0, 1, n)
    return np.stack([c[0] + rho * np.cos(t), c[1] + rho * np.sin(t)], axis=1)


def _arc_mid(pts):
    return pts[len(pts) // 2]


def plot(k, path, title):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7.6, 6.4))
    ax.set_aspect("equal")
    ax.axis("off")

    rho = k["rho"]
    th = np.linspace(0, 2 * np.pi, 600)
    ax.plot(rho * np.cos(th), rho * np.sin(th), color="0.8", lw=0.8, ls="--", zorder=0)

    big = {
        "1in": petal_arc_points(k, "c1_in", "A"),
        "1out": petal_arc_points(k, "c1_out", "A"),
        "2in": petal_arc_points(k, "c2_in", "B"),
        "2out": petal_arc_points(k, "c2_out", "B"),
    }
    small = {
        "up": petal_arc_points(k, "c1_in", "C", n=600),
        "lo": petal_arc_points(k, "c2_in", "C", n=600),
    }
    for pts in big.values():
        ax.plot(pts[:, 0], pts[:, 1], lw=1.5, color="#1f6fb4", zorder=2)
    for pts in small.values():
        ax.plot(pts[:, 0], pts[:, 1], lw=3.0, color="#c92a2a", alpha=0.9, zorder=3)

    for P in [k["A"], k["B"], k["C"]]:
        ax.plot([0, P[0]], [0, P[1]], lw=0.7, color="0.45", zorder=1)

    # 角 theta
    r_ang = 0.30
    t = np.linspace(-k["theta"] / 2, k["theta"] / 2, 100)
    ax.plot(r_ang * np.cos(t), r_ang * np.sin(t), color="k", lw=1.1)
    th_lab = k["theta"] / 4
    ax.text(r_ang * 1.55 * np.cos(th_lab), r_ang * 1.55 * np.sin(th_lab),
            r"$\theta$", fontsize=14, ha="center")

    for c in ["c1_in", "c1_out", "c2_in", "c2_out"]:
        ax.plot(k[c][0], k[c][1], "o", ms=3, mfc="none", mec="0.4", zorder=4)

    lab = {
        "O": (k["O"], (-0.10, -0.03)),
        "A": (k["A"], (0.05, -0.10)),
        "B": (k["B"], (0.05, 0.05)),
        "C": (k["C"], (0.06, -0.02)),
        "D": (_arc_mid(small["lo"]), (-0.02, -0.13)),
        "E": (_arc_mid(small["up"]), (-0.02, 0.09)),
        "F": (_arc_mid(big["2out"]), (0.02, 0.09)),
        "G": (_arc_mid(big["1out"]), (0.02, -0.13)),
    }
    for nm, (P, (dx, dy)) in lab.items():
        ax.plot(P[0], P[1], "ko", ms=3.5, zorder=5)
        ax.text(P[0] + dx, P[1] + dy, nm, fontsize=13, zorder=6)

    # R / r 标注
    midA = k["A"] / 2
    ax.text(midA[0] + 0.06, midA[1] - 0.16, "R", fontsize=12, color="#1f6fb4")
    midC = k["C"] / 2
    ax.text(midC[0], midC[1] + 0.06, "r", fontsize=12, color="#c92a2a")

    ax.set_title(title, fontsize=12)
    ax.set_xlim(min(-1.15 * rho, -0.2), 1.15 * k["L"] + 0.2)
    ax.set_ylim(-1.15 * k["L"] * np.sin(k["theta"] / 2) - 0.6,
                1.15 * k["L"] * np.sin(k["theta"] / 2) + 0.6)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_flower(n, path):
    """n 花瓣（rho = Rc = 1）整朵花 + 相邻两瓣的重叠小瓣。"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    Rc = 1.0
    dc = 2 * Rc * np.sin(np.pi / n)
    theta = 2 * np.pi / n
    fig, ax = plt.subplots(figsize=(6.6, 6.6))
    ax.set_aspect("equal")
    ax.axis("off")
    a = np.sqrt(Rc**2 - dc**2 / 4)
    L = 2 * a

    th = np.linspace(0, 2 * np.pi, 600)
    ax.plot(Rc * np.cos(th), Rc * np.sin(th), color="0.8", lw=0.8, ls="--")

    for i in range(n):
        k = build(Rc, dc, theta)
        phi = theta * i + theta / 2
        Rm = rot(phi)
        for key in ["c1_in", "c1_out", "c2_in", "c2_out"]:
            c = Rm @ k[key]
            tip_key = "A" if key.startswith("c1") else "B"
            pts = Rm @ petal_arc_points(k, key, tip_key).T
            ax.plot(pts[0], pts[1], lw=1.2, color="#1f6fb4", alpha=0.85)
        for key, tip in [("c1_in", "C"), ("c2_in", "C")]:
            pts = Rm @ petal_arc_points(k, key, tip, n=400).T
            ax.plot(pts[0], pts[1], lw=2.2, color="#c92a2a", alpha=0.75)

    k = build(Rc, dc, theta)
    ax.text(0, 0, " O", fontsize=11)
    ax.set_title(f"n={n} petals (blue), overlap petals (red):  R/r = cos(pi/n)/cos(2pi/n) = "
                 f"{np.cos(np.pi/n)/np.cos(2*np.pi/n):.6f}", fontsize=11)
    lim = L * 1.12
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main(save=False):
    Rc = 1.0
    print("=" * 100)
    print("1) 一般花瓣：数值交点 vs 闭式公式")
    print("=" * 100)
    hdr = f"{'rho':>6}{'dc':>7}{'theta':>8}{'theta_p':>9}{'R':>10}{'r(num)':>11}{'r(form)':>11}{'R/r':>10}{'max|err|':>11}"
    print(hdr)
    worst = 0.0
    skipped = 0
    for rho in [0.7, 1.0, 1.3]:
        for dc in [0.4, 0.9, 1.5, 1.9]:
            for td in [10, 25, 40, 60]:
                theta = np.radians(td)
                a2 = rho**2 - dc**2 / 4
                if a2 <= 0:
                    continue
                k, f, r_num, err = verify_row(rho, dc, theta)
                if f["r"] <= 1e-12:                      # theta >= theta_p：无重叠
                    skipped += 1
                    print(f"{rho:6.2f}{dc:7.2f}{td:8.0f}{DEG*f['theta_p']:9.2f}"
                          f"{f['R']:10.6f}{'--':>11}{'--':>11}{'inf':>10}   (theta>=theta_p, 无小花瓣)")
                    continue
                worst = max(worst, err)
                print(f"{rho:6.2f}{dc:7.2f}{td:8.0f}{DEG*f['theta_p']:9.2f}"
                      f"{f['R']:10.6f}{r_num:11.6f}{f['r']:11.6f}{f['ratio']:10.6f}{err:11.2e}")
    print(f"\n有效行最大误差 = {worst:.3e}   （另有 {skipped} 行 theta>=theta_p，小花瓣不存在）\n")

    print("=" * 100)
    print("2) 三种等价写法互检（张角式 / 拱宽式）")
    print("=" * 100)
    for rho, dc, td in [(1.0, 0.6, 35), (1.0, 1.2, 35), (0.8, 0.9, 50), (1.3, 1.5, 25)]:
        k, f, r_num, _ = verify_row(rho, dc, np.radians(td))
        print(f"rho={rho:4.2f} dc={dc:4.2f} theta={td:3d}  r_direct={f['r']:.10f} "
              f"r_apex={f['r_apex']:.10f} r_width={f['r_width']:.10f} "
              f"err={max(abs(f['r']-f['r_apex']), abs(f['r']-f['r_width'])):.2e}")

    print("\n" + "=" * 100)
    print("3) cprdspy 的 n 花瓣（rho = Rc = 1，花瓣都从花心 O 出发）")
    print("   相邻花瓣 theta = 2pi/n -> R/r = cos(pi/n)/cos(2pi/n) = cos(theta/2)/cos(theta)")
    print("=" * 100)
    print(f"{'n':>4}{'theta=2pi/n':>13}{'theta_p':>10}{'R':>10}{'r':>10}{'R/r':>10}{'cos(th/2)/cos(th)':>20}{'err':>10}")
    for n in [5, 6, 7, 8, 9, 10, 12]:
        dc = 2 * Rc * np.sin(np.pi / n)
        theta = 2 * np.pi / n
        k, f, r_num, _ = verify_row(Rc, dc, theta)
        pred = np.cos(theta / 2) / np.cos(theta)
        print(f"{n:4d}{DEG*theta:13.3f}{DEG*f['theta_p']:10.3f}{f['R']:10.6f}{r_num:10.6f}"
              f"{f['ratio']:10.6f}{pred:20.10f}{abs(f['ratio']-pred):10.2e}")

    print("\n   同一 n 花瓣、theta 任意 -> R/r = cos(pi/n)/cos(pi/n + theta/2)")
    for n in [6, 8, 12]:
        dc = 2 * Rc * np.sin(np.pi / n)
        row = []
        for td in [15, 20, 30, 40, 50]:
            theta = np.radians(td)
            k, f, r_num, _ = verify_row(Rc, dc, theta)
            pred = np.cos(np.pi / n) / np.cos(np.pi / n + theta / 2)
            assert abs(f["ratio"] - pred) < 1e-9, (n, td)
            row.append(f"theta={td:2d} -> {f['ratio']:.6f}")
        print(f"   n={n:2d}: " + " | ".join(row))

    print("\n" + "=" * 100)
    print("4) 张角定理：小花瓣张角 theta_small = theta_p - theta；第 k 邻瓣重叠瓣 = theta_p - k*theta")
    print("   等价地  R/r = sin(theta_p/2)/sin(theta_small/2)")
    print("=" * 100)
    for rho, dc, td in [(1.0, 0.6, 35), (1.0, 1.2, 35), (0.8, 0.9, 50), (1.0, 1.0, 60), (1.3, 1.9, 25)]:
        theta = np.radians(td)
        k = build(rho, dc, theta)
        f = formulas(k)
        if f["r"] <= 1e-12:
            continue
        dc_small = k["L"] * np.sin(theta / 2) + k["dc"] * np.cos(theta / 2)
        th_small = 2 * np.arctan(f["r"] / dc_small)
        via_sine = np.sin(f["theta_p"] / 2) / np.sin(th_small / 2)
        print(f"   rho={rho}, dc={dc}, theta={td:2d}: theta_p={DEG*f['theta_p']:7.3f}  "
              f"theta_small={DEG*th_small:7.3f}  (theta_p-theta)={DEG*(f['theta_p']-theta):7.3f}  "
              f"err={abs(th_small-(f['theta_p']-theta)):.2e}   R/r={f['ratio']:.8f} 正弦式={via_sine:.8f}")

    print("\n   第 k 个邻居（轴夹角 k*theta）的重叠瓣长度 r_k = R cos(k*theta/2) - dc sin(k*theta/2)")
    for rho, dc, td in [(1.0, 1.0, 20), (1.0, 0.8, 15)]:
        k1 = build(rho, dc, np.radians(td))
        out = []
        for kk in [1, 2, 3]:
            theta = np.radians(td) * kk
            k = build(rho, dc, theta)
            f = formulas(k)
            if f["r"] <= 1e-12:
                out.append(f"k={kk}: 无重叠瓣")
                continue
            dc_s = k["L"] * np.sin(theta / 2) + k["dc"] * np.cos(theta / 2)
            th_s = 2 * np.arctan(f["r"] / dc_s)
            out.append(f"k={kk}: r={f['r']:.6f} R/r={f['ratio']:.6f} 张角={DEG*th_s:.3f}")
        print(f"   rho={rho}, dc={dc}, theta={td}: " + " | ".join(out))

    print("\n" + "=" * 100)
    print("5) 网格积分：小花瓣(两内弧 lens) 是否恰好等于两花瓣的真实交集")
    print("=" * 100)
    for rho, dc, td in [(1.0, 0.6, 35), (1.0, 1.2, 35), (1.0, 1.0, 60), (0.8, 0.9, 50),
                        (1.0, 0.4, 10), (1.3, 1.9, 25), (1.0, 1.8, 30)]:
        theta = np.radians(td)
        k = build(rho, dc, theta)
        L = k["L"]
        M = 1200
        xs = np.linspace(-0.15 * L, 1.15 * L, M)
        ys = np.linspace(-1.1 * L, 1.1 * L, M)
        X, Y = np.meshgrid(xs, ys)
        cell = (xs[1] - xs[0]) * (ys[1] - ys[0])

        def inside(c):
            return (X - c[0]) ** 2 + (Y - c[1]) ** 2 <= rho**2

        p1 = inside(k["c1_in"]) & inside(k["c1_out"])
        p2 = inside(k["c2_in"]) & inside(k["c2_out"])
        small = inside(k["c1_in"]) & inside(k["c2_in"])
        inter = p1 & p2
        a_inter = inter.sum() * cell
        a_small = small.sum() * cell
        symdiff = (inter ^ small).sum() * cell
        print(f"   rho={rho}, dc={dc}, theta={td:3d}: 交集={a_inter:.6f} 小花瓣={a_small:.6f} "
              f"对称差={symdiff:.3e} 相对对称差={symdiff/a_inter:.2e}")

    if save:
        import os
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "docs", "images")
        os.makedirs(out, exist_ok=True)
        for name, (rho, dc, td) in {
            "petal-ratio-general.png": (1.0, 0.8, 40),
            "petal-ratio-n6-adjacent.png": (1.0, 2 * np.sin(np.pi / 6), 60),
            "petal-ratio-n8-adjacent.png": (1.0, 2 * np.sin(np.pi / 8), 45),
        }.items():
            k = build(rho, dc, np.radians(td))
            f = formulas(k)
            plot(k, os.path.join(out, name),
                 f"R/r = {f['ratio']:.6f}   (theta={td}deg, theta_p={DEG*f['theta_p']:.2f}deg)")
        for n in [6, 8]:
            plot_flower(n, os.path.join(out, f"petal-ratio-flower-n{n}.png"))
        print(f"\n图片已保存到 {out}")


if __name__ == "__main__":
    import sys
    main(save="--save" in sys.argv)

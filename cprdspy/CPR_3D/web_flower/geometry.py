"""numpy 参考几何实现：花瓣网格 + 实例矩阵。

约定（与 js/geometry.js 完全一致，由 tests/test_parity_js.py 逐点锁定）：
  * 列向量约定：p' = M @ p，平移在 M 的第 4 列；
  * 花轴 = Z；欧拉角顺序 R = Rz(rz) @ Ry(ry) @ Rx(rx)（已对 Blender 5.1 实测等价）；
  * 只生成「右半」网格，左半由一个半周旋转实例矩阵 H 得到 —— 1 个几何体 + K 个矩阵。

曲面公式（θ = π/2 − π/n，v = θ·t^curl）：
    P(u,t) = ( a·cos u·sin v + x_d,  c·(cos v − cos θ),  −b·sin u·sin v )
    x_d = a·sin θ,  y_d = c·cos θ
即「椭球冠 → Rx(−90°) → 平移使边缘弧落在 y=0」。curl=1 时与 blender_ellipsoid.petal
逐点一致（实测误差 5e-7，即 float32 精度）。
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

try:  # 作为包导入时
    from .flower_spec import FlowerSpec, Generator
except ImportError:  # 直接在 web_flower/ 里当脚本跑时（CPR_3D 不是包）
    from flower_spec import FlowerSpec, Generator

# --------------------------------------------------------------------------
# 4×4 矩阵小工具（列向量约定）
# --------------------------------------------------------------------------


def mat_t(x: float, y: float, z: float) -> np.ndarray:
    m = np.eye(4)
    m[:3, 3] = (x, y, z)
    return m


def mat_s(s: float) -> np.ndarray:
    return np.diag((s, s, s, 1.0))


def mat_rz(deg: float) -> np.ndarray:
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])


def mat_ry(deg: float) -> np.ndarray:
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]])


def mat_rx(deg: float) -> np.ndarray:
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]])


def euler_rz_ry_rx(rx: float, ry: float, rz: float) -> np.ndarray:
    return mat_rz(rz) @ mat_ry(ry) @ mat_rx(rx)


def half_turn(g: Generator) -> np.ndarray:
    """左半 = 右半绕竖直线 {x=x_d, y=0} 转 180°：(x,y,z) → (2x_d−x, −y, z)。"""
    m = np.eye(4)
    m[0, 0] = m[1, 1] = -1.0
    m[0, 3] = 2.0 * g.x_d
    return m


# --------------------------------------------------------------------------
# 生成元：一片花瓣的右半
# --------------------------------------------------------------------------


def build_petal(g: Generator) -> dict[str, np.ndarray]:
    """返回 {"positions": (nv*nu,3), "normals": (nv*nu,3), "indices": (T,3)}。

    indices 已跳过北极行的零面积三角形：T = 2(nv−1)(nu−1) − (nu−1)。
    三角形绕序满足 three.js 的正面约定：n = (v1−v0)×(v2−v0) 指向花瓣外侧。
    """
    th, x_d, y_d = g.theta, g.x_d, g.y_d
    nu, nv, curl = int(g.nu), int(g.nv), float(g.curl)
    if nu < 2 or nv < 2:
        raise ValueError("nu/nv must be >= 2")

    u = np.linspace(0.0, math.pi, nu)
    t = np.linspace(0.0, 1.0, nv)
    U, T = np.meshgrid(u, t)

    v = th * np.power(T, curl)
    sv, cv = np.sin(v), np.cos(v)
    cu, su = np.cos(U), np.sin(U)

    positions = np.stack(
        [g.a * cu * sv + x_d, g.c * (cv - math.cos(th)), -g.b * su * sv], axis=-1
    )

    # 切向量（t=0 行退化，用解析极限 (0,1,0)）
    vprime = np.where(T > 0, th * curl * np.power(np.maximum(T, 1e-12), curl - 1.0), 0.0)
    rho_p = cv * vprime
    h_p = -sv * vprime
    pu = np.stack([-g.a * su * sv, np.zeros_like(sv), -g.b * cu * sv], axis=-1)
    pt = np.stack(
        [g.a * cu * rho_p, g.c * h_p, -g.b * su * rho_p], axis=-1
    )
    nrm = np.cross(pt, pu)  # 与三角形绕序 (a,c,b)/(a,d,c) 同向 = 外侧
    # 数组形状是 (nv, nu, 3)，t=0 是「第 0 行」（北极，所有 u 重合为一点）。
    # 该点切平面水平，外法向的解析极限 = (0, +1, 0)（与 curl 无关）。
    nrm[0, :, :] = (0.0, 1.0, 0.0)
    length = np.linalg.norm(nrm, axis=-1, keepdims=True)
    normals = np.divide(nrm, length, out=np.zeros_like(nrm), where=length > 1e-12)
    normals[0, :, :] = (0.0, 1.0, 0.0)

    # 网格索引：四边形 a=(i,j) b=(i,j+1) c=(i+1,j+1) d=(i+1,j)
    # → 三角形 (a,c,b) 与 (a,d,c)（绕序与外法向同向）。
    # t=0 一整行都收缩到北极点，故首行只保留 (a,d,c)，去掉零面积三角形。
    idx = lambda i, j: i * nu + j  # noqa: E731
    a = np.array([idx(i, j) for i in range(nv - 1) for j in range(nu - 1)], dtype=np.int64)
    row = np.repeat(np.arange(nv - 1), nu - 1)  # 每个四边形的 i
    b, c, d = a + 1, a + nu + 1, a + nu
    tri = np.stack([np.stack([a, c, b], -1), np.stack([a, d, c], -1)], 1).reshape(-1, 3)
    keep = np.stack([row > 0, np.ones_like(row, dtype=bool)], 1).reshape(-1)
    indices = tri[keep]

    return {
        "positions": positions.reshape(-1, 3).astype(np.float64),
        "normals": normals.reshape(-1, 3).astype(np.float64),
        "indices": indices.astype(np.int64),
    }


# --------------------------------------------------------------------------
# 对称群 + 层栈 → 实例矩阵
# --------------------------------------------------------------------------


def build_instances(spec: FlowerSpec) -> np.ndarray:
    """返回 (K, 4, 4)，K = 2·N·层数；顺序为 层 j → 瓣 i → 半片(R,L)。

    乘法顺序（关键，别改回去）：
        m = T(lift) · Rz(phase + i·step) · Ry(ry) · Rx(rx) · S(scale)
    阵列旋转 Rz(phase + i·step) 必须在**最外层**，即与 Blender 里
    `rotation_euler_deg=(rx, ry, i*30+phase)` 完全等价（R = Rz@Ry@Rx）。

    如果把 i·step 写到最内层（m = Rz(phase)·Ry·Rx·S·Rz(i·step)），杯角/下垂角就变成
    「先摆好整圈、再整体掰一次」，整层会变成一个**歪掉的斜环** —— 内层 droop 大，
    歪得最明显，看起来就是「最上面那层花是斜的」。
    """
    g, sym = spec.generator, spec.symmetry
    h = half_turn(g)
    out = []
    for rx, ry, phase, scale, lift in spec.layer_table():
        for i in range(sym.N):
            m = (
                mat_t(0.0, 0.0, lift)
                @ euler_rz_ry_rx(rx, ry, phase + i * sym.step)
                @ mat_s(scale)
            )
            out.append(m.copy())          # 右半
            out.append(m @ h)             # 左半
    return np.stack(out, 0)


def column_major(matrices: np.ndarray) -> np.ndarray:
    """展平成 three.js InstancedMesh 需要的 Float32Array 顺序（列主序）。"""
    return np.ascontiguousarray(matrices.transpose(0, 2, 1)).reshape(-1).astype(np.float32)


def flower_points(spec: FlowerSpec, stride: int = 7) -> np.ndarray:
    """把整朵花展成点云（采样），用于快速比对/导出。"""
    petal = build_petal(spec.generator)["positions"]
    sel = np.arange(0, len(petal), stride)
    mats = build_instances(spec)
    pts = petal[sel]
    homo = np.hstack([pts, np.ones((len(pts), 1))])
    return np.concatenate([homo @ m.T for m in mats], 0)[:, :3]


# --------------------------------------------------------------------------
# 资产序列化（给前端用）
# --------------------------------------------------------------------------


def petal_to_asset(petal: dict[str, np.ndarray], ndigits: int = 6) -> dict[str, Any]:
    """紧凑 JSON 友好结构（列表，四舍五入到 ndigits 位）。"""
    r = lambda a: np.round(a, ndigits).tolist()  # noqa: E731
    return {
        "positions": r(petal["positions"]),
        "normals": r(petal["normals"]),
        "indices": petal["indices"].tolist(),
    }


def to_obj(spec: FlowerSpec, path: str) -> int:
    """把整朵花烘焙成 .obj（顶点已变换），可直接拖进 Blender 对照。返回三角形数。"""
    petal = build_petal(spec.generator)
    pts, nrm, tri = petal["positions"], petal["normals"], petal["indices"]
    mats = build_instances(spec)
    nv, faces_total = len(pts), 0
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("# cprdspy web_flower export\n")
        for m in mats:
            p = (m[:3, :3] @ pts.T).T + m[:3, 3]
            n = m[:3, :3] @ nrm.T
            n = n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
            for row in p:
                f.write("v %.6f %.6f %.6f\n" % tuple(row))
            for row in n:
                f.write("vn %.6f %.6f %.6f\n" % tuple(row))
        for k in range(len(mats)):
            off_v, off_n = k * nv, k * nv
            for t in tri:
                # 与 indices 同序写出：OBJ 正面法向 (v1−v0)×(v2−v0) 与 vn 一致
                f.write(
                    "f %d//%d %d//%d %d//%d\n"
                    % (
                        t[0] + 1 + off_v,
                        t[0] + 1 + off_n,
                        t[1] + 1 + off_v,
                        t[1] + 1 + off_n,
                        t[2] + 1 + off_v,
                        t[2] + 1 + off_n,
                    )
                )
                faces_total += 1
    return faces_total

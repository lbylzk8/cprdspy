"""Python 侧几何/规范的性质测试（纯 assert，不需要 pytest）。

跑法：
    python tests/test_python.py            # 直接跑
    python run_tests.py                    # 连 JS 一致性一起跑
    pytest cprdspy/CPR_3D/web_flower/tests # 装了 pytest 也能跑
"""

from __future__ import annotations

import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

import flower_spec as fs  # noqa: E402
import geometry as G  # noqa: E402

ALL = list(fs.PRESET_NAMES)


# ---------------------------------------------------------------- 生成元

def test_rim_lies_on_y0():
    """t=1（边缘弧）必须精确落在 y=0 平面上 —— 这是花瓣能拼成一圈的几何前提。"""
    for name in ALL:
        g = fs.preset(name).generator
        p = G.build_petal(g)["positions"].reshape(g.nv, g.nu, 3)
        assert np.abs(p[-1, :, 1]).max() < 1e-12, f"{name}: 边缘弧不在 y=0"


def test_pole_collapses_to_one_point():
    """t=0 一整行必须收缩成同一点（北极），否则顶点法向退化。"""
    for name in ALL:
        g = fs.preset(name).generator
        p = G.build_petal(g)["positions"].reshape(g.nv, g.nu, 3)
        assert np.abs(p[0] - p[0, 0]).max() < 1e-15, f"{name}: 北极没收缩"
        assert abs(p[0, 0, 0] - g.x_d) < 1e-12
        assert abs(p[0, 0, 1] - (g.c * (1 - math.cos(g.theta)))) < 1e-12
        assert abs(p[0, 0, 2]) < 1e-12


def test_tiling_angle():
    """θ = π/2 − π/n：n=4→45°，n=6→60°；且 x_d=a·sinθ, y_d=c·cosθ。"""
    assert math.isclose(fs.Generator(n=4).theta, math.pi / 4)
    assert math.isclose(fs.Generator(n=6).theta, math.pi / 3)
    g = fs.Generator(a=2.0, c=3.0, n=5)
    assert math.isclose(g.x_d, 2.0 * math.sin(g.theta))
    assert math.isclose(g.y_d, 3.0 * math.cos(g.theta))


def test_normals_unit_and_outward():
    """法向必须全是单位向量，且与三角形绕序 (v1−v0)×(v2−v0) 同向。"""
    for name in ALL:
        g = fs.preset(name).generator
        petal = G.build_petal(g)
        P, N, I = petal["positions"], petal["normals"], petal["indices"]
        length = np.linalg.norm(N, axis=1)
        assert np.abs(length - 1).max() < 1e-9, f"{name}: 法向不是单位长 ({length.min()}..{length.max()})"

        a, b, c = P[I[:, 0]], P[I[:, 1]], P[I[:, 2]]
        gn = np.cross(b - a, c - a)
        area = np.linalg.norm(gn, axis=1)
        assert area.min() > 1e-12, f"{name}: 存在零面积三角形"
        gn /= area[:, None]
        vn = (N[I[:, 0]] + N[I[:, 1]] + N[I[:, 2]]) / 3.0
        dot = np.einsum("ij,ij->i", gn, vn)
        assert dot.min() > 0.5, f"{name}: 绕序与法向反了 (min={dot.min():.4f})"
        assert len(I) == 2 * (g.nv - 1) * (g.nu - 1) - (g.nu - 1)


def test_indices_in_range():
    for name in ALL:
        g = fs.preset(name).generator
        petal = G.build_petal(g)
        assert petal["indices"].min() >= 0
        assert petal["indices"].max() == g.nv * g.nu - 1


def test_curl_changes_shape_but_keeps_endpoints():
    """curl 是子午线重参数化：改形状，但 ρ(0)=0、ρ(1)=sinθ、h(0)=1、h(1)=cosθ 不变。"""
    g1 = fs.Generator(curl=1.0, nu=32, nv=17)
    g2 = fs.Generator(curl=2.0, nu=32, nv=17)
    p1 = G.build_petal(g1)["positions"]
    p2 = G.build_petal(g2)["positions"]
    # 端点行一致
    assert np.abs(p1.reshape(17, 32, 3)[-1] - p2.reshape(17, 32, 3)[-1]).max() < 1e-12
    assert np.abs(p1.reshape(17, 32, 3)[0] - p2.reshape(17, 32, 3)[0]).max() < 1e-12
    # 中间行不一样
    assert np.abs(p1.reshape(17, 32, 3)[8] - p2.reshape(17, 32, 3)[8]).max() > 1e-3


def test_matches_ellipsoid_flower_reference():
    """与已经对过 Blender 的 ellipsoid_flower.petal 逐点一致（右半 + 左半）。"""
    sys.path.insert(0, os.path.dirname(ROOT))
    import ellipsoid_flower as ref  # noqa: E402

    g = fs.Generator(a=2.0, b=1 / 3, c=2.0, n=4, nu=48, nv=24, curl=1.0)
    right, left = ref.petal(a=g.a, b=g.b, c=g.c, n=g.n, nu=g.nu, nv=g.nv)
    right = np.ascontiguousarray(right.transpose(1, 2, 0)).reshape(-1, 3)
    left = np.ascontiguousarray(left.transpose(1, 2, 0)).reshape(-1, 3)

    petal = G.build_petal(g)
    assert np.abs(petal["positions"] - right).max() < 1e-12

    h = G.half_turn(g)
    left_from_matrix = (h[:3, :3] @ petal["positions"].T).T + h[:3, 3]
    assert np.abs(left_from_matrix - left).max() < 1e-12, "左半实例矩阵 ≠ 参考实现的左半"


# ---------------------------------------------------------------- 实例矩阵

def test_half_turn_is_proper_rotation():
    g = fs.Generator()
    h = G.half_turn(g)
    assert math.isclose(np.linalg.det(h[:3, :3]), 1.0, abs_tol=1e-12)
    assert np.abs(h[:3, :3] @ h[:3, :3].T - np.eye(3)).max() < 1e-12
    assert np.abs(h @ h - np.eye(4)).max() < 1e-12, "半周旋转做两次必须回到原位"


def test_instances_count_det_and_ordering():
    for name in ALL:
        spec = fs.preset(name)
        mats = G.build_instances(spec)
        k = spec.instance_count()
        assert len(mats) == k, f"{name}: {len(mats)} != 2*N*M={k}"
        det = np.linalg.det(mats[:, :3, :3])
        assert (det > 0).all(), f"{name}: 出现反射（det<0），会翻面"
        # 同一层的右半/左半行列式相同（都是纯旋转 × 各向同性缩放），且只差一个半周旋转
        r, l = mats[0], mats[1]
        assert math.isclose(det[0], det[1], rel_tol=1e-12)
        assert np.abs(r @ G.half_turn(spec.generator) - l).max() < 1e-12
        # 第 1 瓣（下标 2，顺序是 层→瓣→半片，每瓣占 2 个）= 第 0 瓣**左乘** Rz(step)。
        # 左乘而不是右乘：阵列旋转是最外层（Rz(phase+i·step)·Ry·Rx），
        # 右乘会让整层变成一个歪掉的斜环（见 build_instances 的注释）。
        step = spec.symmetry.step
        if spec.symmetry.N >= 2:
            assert np.abs(G.mat_rz(step) @ r - mats[2]).max() < 1e-12


def test_each_layer_is_a_centered_ring():
    """每一层必须是「同一片花瓣绕花轴等分旋转」得到的正环。

    这条测试专治「上层歪着」：如果阵列旋转被写到最内层（base·Rz(i·step)），
    整层会变成倾斜的斜环，各瓣的极点高度不再一致 —— 内层 droop 最大，歪得最凶。
    """
    for name in ALL:
        spec = fs.preset(name)
        g = spec.generator
        per = 2 * spec.symmetry.N
        step = spec.symmetry.step
        pole = G.build_petal(g)["positions"][0]   # v=0 的极点（花瓣最高点）
        mats = G.build_instances(spec)
        for j in range(len(spec.layer_table())):
            layer = mats[j * per:(j + 1) * per]
            right = layer[::2]
            poles = np.array([m[:3, :3] @ pole + m[:3, 3] for m in right])
            radius = np.hypot(poles[:, 0], poles[:, 1])
            # 同层所有瓣必须同高同半径 —— 这就是「这一层没有整体歪掉」的判据
            assert np.abs(poles[:, 2] - poles[:, 2].mean()).max() < 1e-9, (
                f"{name}: 第 {j} 层各瓣高度不一致（层被整体掰歪了）"
            )
            assert np.abs(radius - radius.mean()).max() < 1e-9, (
                f"{name}: 第 {j} 层各瓣半径不一致"
            )
            # 相邻两瓣严格差一个 Rz(step)（含 twist 时也成立）
            for k in range(0, per - 2, 2):
                assert np.abs(G.mat_rz(step) @ layer[k] - layer[k + 2]).max() < 1e-9, (
                    f"{name}: 第 {j} 层的瓣不是等角阵列"
                )


def test_instances_match_ellipsoid_flower_place():
    """整朵花的实例矩阵必须等于参考实现的 place(tilt=(rx, ry, phase + i·step))。

    ellipsoid_flower.py 已经逐点对过 Blender，是这棵树里唯一「外部真值」。
    """
    sys.path.insert(0, os.path.dirname(ROOT))
    import ellipsoid_flower as ref  # noqa: E402

    spec = fs.preset("ROSE_TABLE")
    mats = G.build_instances(spec)
    idx = 0
    for rx, ry, phase, scale, _lift in spec.layer_table():
        for i in range(spec.symmetry.N):
            expect = np.eye(4)
            expect[:3, :3] = ref._rot((rx, ry, phase + i * 360.0 / spec.symmetry.N)) * scale
            assert np.abs(mats[idx] - expect).max() < 1e-12, (
                f"第 {idx} 个实例与参考 place() 不一致 —— 乘法顺序漂了"
            )
            idx += 2



def test_column_major_matches_three_convention():
    """three.js 的 Matrix4.elements 是列主序：m.elements[c*4+r] == M[r,c]。"""
    spec = fs.preset("ROSE")
    mats = G.build_instances(spec)
    flat = G.column_major(mats)
    assert flat.dtype == np.float32
    assert flat.size == len(mats) * 16
    k = 3
    for r in range(4):
        for c in range(4):
            assert math.isclose(flat[k * 16 + c * 4 + r], mats[k][r, c], abs_tol=1e-6)


def test_euler_order_matches_blender_xyz():
    """R = Rz@Ry@Rx 与 Blender rotation_euler 的 'XYZ' 顺序等价（已实测）。"""
    rx, ry, rz = 18.0, -33.0, 51.0
    m = G.euler_rz_ry_rx(rx, ry, rz)
    # 独立再算一遍：先 Rx 把 +Z 拉向 +Y，再 Ry，再 Rz
    v = np.array([1.0, 2.0, 3.0, 0.0])
    step1 = G.mat_rx(rx) @ v
    step2 = G.mat_ry(ry) @ step1
    step3 = G.mat_rz(rz) @ step2
    assert np.abs(m @ v - step3).max() < 1e-12
    assert np.abs(m[:3, 3]).max() < 1e-15, "纯旋转矩阵不该带平移"


# ---------------------------------------------------------------- 层栈

def test_recipe_reproduces_blender_demo():
    """闭式配方应当复现 blender_ellipsoid.py 末尾手写的 L0..L4。

    ry / phase 必须逐点精确相等；scale（几何衰减 vs 手调）与 rx（线性 vs 分段常数）
    允许手调残差 —— 这两条容差就是「配方够不够好」的量化答案。
    """
    rows = fs.preset("ROSE").layer_table()
    for (rx, ry, ph, sc, _), (erx, ery, eph, esc) in zip(rows, fs.ROSE_TABLE):
        assert math.isclose(ry, ery, abs_tol=1e-12), "下垂角必须完全一致"
        assert math.isclose(ph, eph, abs_tol=1e-12), "错列角必须完全一致"
        assert math.isclose(sc, esc, abs_tol=0.2), f"缩放偏差过大 {sc} vs {esc}"
        assert abs(rx - erx) <= 8.0, f"杯角偏差过大 {rx} vs {erx}"


def test_explicit_table_overrides_recipe_and_locks():
    spec = fs.preset("ROSE_TABLE")
    rows = spec.layer_table()
    assert len(rows) == len(fs.ROSE_TABLE)
    assert [r[:4] for r in rows] == [tuple(x) for x in fs.ROSE_TABLE]
    # 显式表给了 4 元组 → lift 补 0
    assert all(r[4] == 0.0 for r in rows)


def test_symmetry_step():
    assert math.isclose(fs.Symmetry(N=12).step, 30.0)
    assert math.isclose(fs.Symmetry(N=12, twist=6.0).step, 36.0)


# ---------------------------------------------------------------- 序列化

def test_spec_json_roundtrip():
    for name in ALL:
        spec = fs.preset(name)
        back = fs.FlowerSpec.from_json(spec.to_json())
        assert back.to_dict() == spec.to_dict(), f"{name}: JSON 往返丢字段"
        assert np.abs(G.build_instances(back) - G.build_instances(spec)).max() < 1e-12


def test_presets_are_serializable_and_bounded():
    data = fs.all_presets()
    assert set(data) == set(fs.PRESET_NAMES)
    for name, spec in data.items():
        assert 3 <= spec.generator.n <= 12, name
        assert spec.generator.nu >= 6 and spec.generator.nv >= 3, name
        assert spec.instance_count() <= 4096, f"{name}: 超过前端实例上限"


def main() -> int:
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"  ok    {fn.__name__}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"  FAIL  {fn.__name__}: {type(exc).__name__}: {exc}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed  (test_python.py)")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

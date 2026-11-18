"""Python ↔ JS 数值一致性测试。

跑 `node tests/js_dump.mjs` 拿 JS 侧输出，和 geometry.py 逐点比。
这条测试是「一个真源、两份实现」这套架构唯一的护栏：谁单独改了某一边的公式，
这里立刻红。容差分三档，写清楚为什么：

  * 实例矩阵 float64      → 1e-12（求和顺序/FMA 造成的最后一位抖动）
  * 顶点/法向 float32     → 2e-6 （GPU 格式本身只有 24 位尾数）
  * 索引 / 层表           → 精确相等（离散量，不允许抖）
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

import flower_spec as fs  # noqa: E402
import geometry as G  # noqa: E402

SKIP_REASON = ""
if shutil.which("node") is None:
    SKIP_REASON = "没找到 node，跳过 JS 一致性测试"
elif not os.path.exists(os.path.join(ROOT, "assets", "presets.json")):
    SKIP_REASON = "缺 assets/presets.json，先跑 python build_assets.py"


def _dump() -> dict:
    proc = subprocess.run(
        ["node", os.path.join(HERE, "js_dump.mjs")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=ROOT,
    )
    if proc.returncode != 0:
        raise AssertionError(f"node js_dump.mjs 失败 (exit {proc.returncode}):\n{proc.stderr}")
    return json.loads(proc.stdout)


def _flat(a: np.ndarray) -> np.ndarray:
    return np.asarray(a, dtype=float).reshape(-1)


def check(name: str, js: dict) -> dict:
    spec = fs.preset(name)
    g = spec.generator
    py = G.build_petal(g)
    mats = G.build_instances(spec)

    report = {}

    # --- 派生标量 ---
    report["theta"] = abs(js["theta"] - g.theta)
    report["step"] = abs(js["step"] - spec.symmetry.step)

    # --- 层表：离散+连续混合，要求精确 ---
    assert len(js["layers"]) == len(spec.layer_table()), f"{name}: 层数不一致"
    for a, b in zip(js["layers"], spec.layer_table()):
        assert len(a) == len(b), f"{name}: 层字段数不一致 {a} vs {b}"
        assert max(abs(x - y) for x, y in zip(a, b)) < 1e-12, f"{name}: 层表不一致 {a} vs {b}"

    # --- 顶点：JS 存的是 Float32Array，所以两边都降到 float32 再比 ---
    for key in ("positions", "normals"):
        a = np.asarray(js[key], dtype=np.float32)
        b = py[key].astype(np.float32).reshape(-1)
        assert a.shape == b.shape, f"{name}/{key}: 形状 {a.shape} vs {b.shape}"
        report[key] = float(np.abs(a - b).max())

    # --- 索引：整数，必须逐元素相等（顺序也相等，否则绕序就漂了）---
    ji = np.asarray(js["indices"], dtype=np.int64).reshape(-1, 3)
    assert ji.shape == py["indices"].shape, f"{name}: 三角形数 {ji.shape} vs {py['indices'].shape}"
    assert np.array_equal(ji, py["indices"]), f"{name}: 索引不逐点相等"
    report["indices"] = 0.0

    # --- 实例矩阵 float64 ---
    jm = np.asarray(js["matrices"], dtype=float).reshape(-1, 4, 4)
    assert jm.shape == mats.shape, f"{name}: 矩阵数 {jm.shape} vs {mats.shape}"
    report["matrices"] = float(np.abs(jm - mats).max())

    # --- 交给 GPU 的那份列主序 float32 ---
    jc = np.asarray(js["colMajor"], dtype=np.float32)
    pc = G.column_major(mats)
    assert jc.shape == pc.shape, f"{name}: 列主序长度 {jc.shape} vs {pc.shape}"
    report["colMajor"] = float(np.abs(jc.astype(float) - pc.astype(float)).max())

    # --- 规模统计 ---
    assert js["counts"]["vertices"] == g.nv * g.nu, f"{name}: 顶点数"
    assert js["counts"]["instances"] == spec.instance_count(), f"{name}: 实例数"
    assert js["counts"]["triangles"] == len(py["indices"]), f"{name}: 三角形数"
    return report


LIMITS = {"theta": 1e-12, "step": 1e-12, "positions": 2e-6, "normals": 2e-6,
          "indices": 0.0, "matrices": 1e-12, "colMajor": 1e-5}


def test_js_matches_python():
    if SKIP_REASON:
        print(f"  SKIP  {SKIP_REASON}")
        return
    data = _dump()
    assert set(data) == set(fs.PRESET_NAMES), f"JS 只输出了 {sorted(data)}"
    worst = {}
    for name in fs.PRESET_NAMES:
        for key, dev in check(name, data[name]).items():
            assert dev <= LIMITS[key] + 1e-15, (
                f"{name}/{key}: 偏差 {dev:g} 超过容差 {LIMITS[key]:g} —— 两端公式漂了"
            )
            worst[key] = max(worst.get(key, 0.0), dev)
    line = "  ".join(f"{k}≤{v:.1e}" for k, v in sorted(worst.items()))
    print(f"        {line}")


def test_assets_presets_match_python_presets():
    """浏览器拿到的 presets.json 必须就是 flower_spec.preset() 的输出。"""
    if SKIP_REASON:
        print("  SKIP  无 assets/presets.json")
        return
    with open(os.path.join(ROOT, "assets", "presets.json"), encoding="utf-8") as f:
        data = json.load(f)
    assert data["order"] == list(fs.PRESET_NAMES), "预设顺序变了，记得重跑 build_assets.py"
    for name in fs.PRESET_NAMES:
        assert data["presets"][name] == fs.preset(name).to_dict(), (
            f"{name}: presets.json 过期，跑 python build_assets.py"
        )


def test_ref_assets_match_python():
    """build_assets.py --ref 烘出来的参考几何必须还能被 geometry.py 复现。

    （ref 里的浮点数被 round 到 9 位，所以这里用 1e-8 而不是 1e-12。）
    """
    path = os.path.join(ROOT, "assets", "ref", "ROSE.json")
    if not os.path.exists(path):
        print("  SKIP  没有 assets/ref/ROSE.json（跑 python build_assets.py --ref 生成）")
        return
    with open(path, encoding="utf-8") as f:
        ref = json.load(f)
    spec = fs.FlowerSpec.from_dict(ref["spec"])
    py = G.build_petal(spec.generator)
    mats = G.build_instances(spec)

    assert np.abs(_flat(ref["petal"]["positions"]) - _flat(py["positions"])).max() < 1e-8
    assert np.abs(_flat(ref["petal"]["normals"]) - _flat(py["normals"])).max() < 1e-8
    assert np.array_equal(np.asarray(ref["petal"]["indices"]), py["indices"])
    assert np.abs(np.asarray(ref["instances"], dtype=float) - mats).max() < 1e-8
    assert np.abs(
        np.asarray(ref["halfTurn"], dtype=float) - G.half_turn(spec.generator)
    ).max() < 1e-8
    col = np.asarray(ref["instancesColMajor"], dtype=np.float32).astype(float)
    # 这份已经是 float32，只能要求「同一 ulp 量级」；顺序错了会直接爆到 O(1)
    assert np.abs(col - G.column_major(mats).astype(float)).max() <= 2e-6, "列主序字节序漂了"


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
    print(f"\n{len(fns) - failed}/{len(fns)} passed  (test_parity_js.py)")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

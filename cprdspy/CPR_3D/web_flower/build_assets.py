"""离线打包：把 Python 侧的花型规范 + 参考几何导出成前端能直接 fetch 的 JSON。

用法（在 web_flower/ 目录里）：
    python build_assets.py                 # 只出 assets/presets.json
    python build_assets.py --ref           # 追加 assets/ref/<NAME>.json（给 JS 一致性测试用）
    python build_assets.py --obj           # 追加 assets/obj/<NAME>.obj（可拖进 Blender 对照）
    python build_assets.py --list          # 打印每个预设的规模，不写文件

前端不需要 numpy、也不需要在浏览器里跑 Python：
  * `presets.json` 是纯数据 —— JS 用同一套公式实时生成几何，所以滑条能立刻响应；
  * `ref/*.json` 是 Python 烘好的顶点/矩阵 —— 只用于 tests/test_parity_js.py 逐点比对，
    防止 Python 和 JS 两边公式漂移。
"""

from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

try:
    from . import geometry, flower_spec as fs
except ImportError:
    import geometry
    import flower_spec as fs

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")


def _dump(obj, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
    print(f"  wrote {os.path.relpath(path, HERE)}  ({os.path.getsize(path) / 1024:.1f} KB)")


def write_presets(names: list[str]) -> None:
    """所有预设的规范（纯数据，体积只有几十 KB）。"""
    payload = {
        "meta": {
            "generator": "cprdspy web_flower build_assets.py",
            "axis": "z",
            "euler": "R = Rz @ Ry @ Rx  (degrees)",
            "units": "degrees / model units",
        },
        "order": names,
        "presets": {n: fs.preset(n).to_dict() for n in names},
    }
    _dump(payload, os.path.join(ASSETS, "presets.json"))


def write_ref(name: str) -> None:
    """Python 烘好的参考几何：右半网格 + K 个实例矩阵 + 层表。"""
    spec = fs.preset(name)
    petal = geometry.build_petal(spec.generator)
    mats = geometry.build_instances(spec)
    r = lambda a, n=6: np.round(np.asarray(a, dtype=float), n).tolist()  # noqa: E731
    payload = {
        "name": name,
        "spec": spec.to_dict(),
        "petal": {
            "positions": r(petal["positions"], 9),
            "normals": r(petal["normals"], 9),
            "indices": petal["indices"].tolist(),
        },
        "instances": r(mats, 9),          # (K,4,4) 行主序
        "instancesColMajor": geometry.column_major(mats).tolist(),
        "layers": [list(map(float, row)) for row in spec.layer_table()],
        "halfTurn": r(geometry.half_turn(spec.generator), 9),
        "counts": {
            "vertices": int(len(petal["positions"])),
            "triangles": int(len(petal["indices"])),
            "instances": int(len(mats)),
        },
    }
    _dump(payload, os.path.join(ASSETS, "ref", f"{name}.json"))


def write_obj(name: str) -> None:
    spec = fs.preset(name)
    path = os.path.join(ASSETS, "obj", f"{name}.obj")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    n = geometry.to_obj(spec, path)
    print(f"  wrote {os.path.relpath(path, HERE)}  ({n} triangles)")


def summarize(names: list[str]) -> None:
    print(f"{'preset':11s} {'n':>2s} {'N':>3s} {'M':>2s} {'nu x nv':>8s} "
          f"{'verts':>7s} {'tris':>7s} {'inst':>5s}")
    for name in names:
        spec = fs.preset(name)
        g = spec.generator
        petal = geometry.build_petal(g)
        k = geometry.build_instances(spec)
        assert len(k) == spec.instance_count(), "instance_count 与 build_instances 不一致"
        det = np.linalg.det(k[:, :3, :3])
        assert (det > 0).all(), f"{name}: 出现反射矩阵 (det<0)"
        print(
            f"{name:11s} {g.n:2d} {spec.symmetry.N:3d} {len(spec.layer_table()):2d} "
            f"{g.nu:4d}x{g.nv:<3d} {len(petal['positions']):7d} {len(petal['indices']):7d} "
            f"{len(k):5d}"
        )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="导出 web_flower 前端资产")
    ap.add_argument("--presets", default=",".join(fs.PRESET_NAMES), help="逗号分隔的预设名")
    ap.add_argument("--ref", action="store_true", help="导出 Python 参考几何（一致性测试用）")
    ap.add_argument("--obj", action="store_true", help="导出烘焙后的 .obj")
    ap.add_argument("--list", action="store_true", help="只打印规模统计")
    args = ap.parse_args(argv)

    names = [p.strip().upper() for p in args.presets.split(",") if p.strip()]
    unknown = [n for n in names if n not in fs.PRESET_NAMES]
    if unknown:
        ap.error(f"未知预设 {unknown}，可选 {list(fs.PRESET_NAMES)}")

    summarize(names)
    if args.list:
        return 0
    write_presets(names)
    for n in names:
        if args.ref:
            write_ref(n)
        if args.obj:
            write_obj(n)
    return 0


if __name__ == "__main__":
    sys.exit(main())

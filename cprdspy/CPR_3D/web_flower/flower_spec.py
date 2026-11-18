"""花型规范 —— 把「生成元 × 对称群 × 层栈」这一范式写成纯数据。

本模块是 web_flower 的唯一真源（single source of truth）：
  * Python 侧 `geometry.py` 与 JS 侧 `js/geometry.js` 都只消费这里定义的字段；
  * `tests/test_parity_js.py` 逐点比对两端输出，公式漂移会立刻失败。

三层抽象（换任何一层都只改数据，不改代码）：
    生成元 generator  —— 一片花瓣的曲面公式（ellipsoid_cap + curl 重参数化）
    对称群 symmetry   —— 绕花轴 Z 的 N 等分阵列，twist 可拧成旋涡
    层栈 stack        —— M 层 (杯角 rx, 下倾 ry, 错列 phase, 缩放 scale, 抬升 lift)

角度单位：本模块内部一律用「度」描述层栈，用「弧度」做三角运算（在 geometry 里转换）。
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field, replace
from typing import Any

SQRT8 = math.sqrt(8.0)


# --------------------------------------------------------------------------
# 数据结构
# --------------------------------------------------------------------------


@dataclass
class Generator:
    """花瓣生成元：椭球冠 u∈[0,π], v∈[0,θ]，θ = π/2 − π/n。"""

    kind: str = "ellipsoid_cap"
    a: float = 2.0          # 花轴径向半轴（瓣长）
    b: float = 1 / 3         # 侧向半轴（瓣宽/薄）
    c: float = 2.0          # 冠高半轴（瓣的鼓起）
    n: int = 4              # 铺满条件参数：θ = π/2 − π/n
    curl: float = 1.0       # 子午线重参数化 v = θ·t^curl；1=标准椭球冠
    nu: int = 64            # u 方向网格（沿边缘弧）
    nv: int = 32            # v 方向网格（沿脊线）

    @property
    def theta(self) -> float:
        return math.pi / 2 - math.pi / self.n

    @property
    def x_d(self) -> float:
        return self.a * math.sin(self.theta)

    @property
    def y_d(self) -> float:
        return self.c * math.cos(self.theta)


@dataclass
class Symmetry:
    N: int = 12             # 每层花瓣数
    twist: float = 0.0      # 额外步进角（度）：step = 360/N + twist，>0 成旋涡

    @property
    def step(self) -> float:
        return 360.0 / self.N + self.twist


@dataclass
class Stack:
    """层栈。给了 table 就用表；否则用配方由 M 生成。"""

    M: int = 5
    cup: tuple[float, float] = (15.0, 30.0)   # rx 由外层到内层线性（度）
    droop: float = -15.0                      # ry = droop·j（度/层）
    phase: float | None = None                # 相邻层错列角；None → 180/N
    scale_range: tuple[float, float] = (SQRT8, 1.0)
    lift: float = 0.0                         # 最内层沿花轴的抬升总量
    table: list | None = None                 # 显式 [(rx, ry, phase, scale), ...]

    def resolve(self, N: int) -> list[tuple[float, float, float, float, float]]:
        """返回 [(rx_deg, ry_deg, phase_deg, scale, lift), ...]，长度 = 层数。"""
        if self.table:
            rows = [tuple(r) for r in self.table]
            if all(len(r) == 4 for r in rows):
                rows = [r + (0.0,) for r in rows]
            return [tuple(r) for r in rows]

        phase = 180.0 / N if self.phase is None else self.phase
        s0, s1 = self.scale_range
        m = max(1, self.M - 1)
        rows = []
        for j in range(self.M):
            t = j / m
            rx = self.cup[0] + (self.cup[1] - self.cup[0]) * t
            scale = s0 * (s1 / s0) ** t
            rows.append((rx, self.droop * j, ((j + 1) % 2) * phase, scale, self.lift * t))
        return rows


@dataclass
class Style:
    color_outer: list[str] = field(
        default_factory=lambda: ["#ffd1e8", "#ffb3d9", "#ff8fc4", "#f76fae", "#e04f97"]
    )
    color_inner: list[str] = field(
        default_factory=lambda: ["#ffc2b3", "#ff9f87", "#f77f68", "#e0644f", "#c4493a"]
    )
    opacity: float = 0.92
    wireframe: bool = False


@dataclass
class FlowerSpec:
    name: str = "ROSE"
    generator: Generator = field(default_factory=Generator)
    symmetry: Symmetry = field(default_factory=Symmetry)
    stack: Stack = field(default_factory=Stack)
    style: Style = field(default_factory=Style)

    # ---- 层表（含 lift）----
    def layer_table(self) -> list[tuple[float, float, float, float, float]]:
        return self.stack.resolve(self.symmetry.N)

    def instance_count(self) -> int:
        return 2 * self.symmetry.N * len(self.layer_table())

    # ---- 序列化 ----
    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["stack"]["cup"] = list(self.stack.cup)
        d["stack"]["scale_range"] = list(self.stack.scale_range)
        if self.stack.table is not None:
            d["stack"]["table"] = [list(r) for r in self.stack.table]
        return d

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "FlowerSpec":
        g = Generator(**d.get("generator", {}))
        s = Symmetry(**d.get("symmetry", {}))
        st = d.get("stack", {})
        st = {**st, "cup": tuple(st["cup"])} if "cup" in st else st
        st = {**st, "scale_range": tuple(st["scale_range"])} if "scale_range" in st else st
        k = Stack(**st)
        y = Style(**d.get("style", {}))
        return cls(name=d.get("name", "CUSTOM"), generator=g, symmetry=s, stack=k, style=y)

    @classmethod
    def from_json(cls, text: str) -> "FlowerSpec":
        return cls.from_dict(json.loads(text))

    def replace(self, **kw) -> "FlowerSpec":
        return replace(self, **kw)


# --------------------------------------------------------------------------
# 预设：每个预设就是一段数据
# --------------------------------------------------------------------------

# Blender demo 末尾手写的 L0..L4（用于回归对齐 blender_ellipsoid.py）
ROSE_TABLE = [
    (15.0, 0.0, 15.0, SQRT8),
    (15.0, -15.0, 0.0, 2.0),
    (30.0, -30.0, 15.0, 1.5),
    (30.0, -45.0, 0.0, 1.3),
    (30.0, -60.0, 15.0, 1.0),
]


def preset(name: str) -> FlowerSpec:
    name = name.upper()
    if name == "ROSE":
        return FlowerSpec(name="ROSE")
    if name == "ROSE_TABLE":
        return FlowerSpec(
            name="ROSE_TABLE", stack=Stack(M=5, table=[tuple(r) for r in ROSE_TABLE])
        )
    if name == "LOTUS":  # 平铺宽瓣：小 droop、大 N、圆脊
        return FlowerSpec(
            name="LOTUS",
            generator=Generator(a=2.4, b=0.9, c=1.1, n=6, curl=0.75, nu=72, nv=28),
            symmetry=Symmetry(N=16),
            stack=Stack(M=4, cup=(6.0, 22.0), droop=-6.0, scale_range=(2.2, 1.0)),
            style=Style(
                color_outer=["#cfefff", "#a8e0ff", "#7fcdf2", "#59b6e3"],
                color_inner=["#eafcff", "#c2f2ff", "#9ae8ff", "#6fdcf5"],
            ),
        )
    if name == "TULIP":  # 少瓣高杯：内层立起来
        return FlowerSpec(
            name="TULIP",
            generator=Generator(a=1.8, b=1.1, c=2.2, n=5, curl=1.35, nu=64, nv=32),
            symmetry=Symmetry(N=6),
            stack=Stack(M=3, cup=(38.0, 58.0), droop=-4.0, scale_range=(1.9, 1.0), lift=0.35),
            style=Style(
                color_outer=["#ffe0ec", "#ffc0dd", "#ff9ecb"],
                color_inner=["#f6c8ff", "#e6a2f5", "#d07be0"],
            ),
        )
    if name == "AGAVE":  # 硬直尖瓣：宽 n、大 droop
        return FlowerSpec(
            name="AGAVE",
            generator=Generator(a=2.0, b=0.22, c=2.6, n=8, curl=1.0, nu=48, nv=36),
            symmetry=Symmetry(N=12, twist=6.0),
            stack=Stack(M=6, cup=(12.0, 34.0), droop=-18.0, scale_range=(2.6, 0.85)),
            style=Style(
                color_outer=["#d8f5c8", "#b7e8a4", "#93d981", "#6fc763", "#4fb048", "#33963a"],
                color_inner=["#eef7c9", "#dcef9f", "#cbe276", "#b5d252", "#9bbf36", "#7da826"],
            ),
        )
    if name == "SPIRAL":  # 旋涡：靠 twist 拧
        return FlowerSpec(
            name="SPIRAL",
            generator=Generator(a=2.2, b=0.55, c=1.8, n=5, curl=1.1, nu=80, nv=30),
            symmetry=Symmetry(N=13, twist=11.0),
            stack=Stack(M=5, cup=(18.0, 40.0), droop=-12.0, scale_range=(2.4, 0.8)),
            style=Style(
                color_outer=["#fff2b8", "#ffe08a", "#ffc861", "#f7a94f", "#e0863c"],
                color_inner=["#ffd9e6", "#ffb8d1", "#ff92bb", "#e86ba1", "#c44a86"],
            ),
        )
    raise KeyError(f"unknown preset {name!r}; choose from {list(PRESET_NAMES)}")


PRESET_NAMES = ("ROSE", "ROSE_TABLE", "LOTUS", "TULIP", "AGAVE", "SPIRAL")


def all_presets() -> dict[str, FlowerSpec]:
    return {k: preset(k) for k in PRESET_NAMES}


if __name__ == "__main__":
    for k in PRESET_NAMES:
        s = preset(k)
        rows = s.layer_table()
        print(
            f"{k:11s} n={s.generator.n} N={s.symmetry.N:2d} M={len(rows)} "
            f"instances={s.instance_count():3d}  layer0={tuple(round(v, 3) for v in rows[0])}"
        )

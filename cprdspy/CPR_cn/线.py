"""
线模块 — 线段生成与绘制

提供点连线、全连接、多层多边形、万字符等中文接口。
"""

import warnings
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

from .点 import 点集, n_点s, 点阵, draw_点s


class 线集:
    """线段容器，支持 + 运算符拼接，以及 draw_线 绘制。

    用法:
        线s = 连接(点s对象, 闭合=True)
        线s = 线s + 连接(其他点s, 闭合=False)
        draw_线(线s)

    属性:
        线段列表: list of (x_array, y_array)
    """

    def __init__(self, 线段列表=None):
        self._线段列表 = []
        if 线段列表 is not None:
            for seg in 线段列表:
                self.添加线段(seg[0], seg[1])

    def 添加线段(self, x, y):
        """添加一段线。x, y 为至少2个点的坐标数组。"""
        self._线段列表.append(
            (np.atleast_1d(np.asarray(x, dtype=float)),
             np.atleast_1d(np.asarray(y, dtype=float)))
        )
        return self

    def __add__(self, other):
        if isinstance(other, 线集):
            result = 线集()
            result._线段列表 = self._线段列表 + other._线段列表
            return result
        return NotImplemented

    def __radd__(self, other):
        if other == 0:
            return self
        return NotImplemented

    def __len__(self):
        return len(self._线段列表)

    def __getitem__(self, idx):
        return self._线段列表[idx]

    def __repr__(self):
        return f"线集(n={len(self._线段列表)})"

    @property
    def 线段列表(self):
        return self._线段列表


# ======================== 内部辅助 ========================

def _解析线颜色映射(by):
    """将颜色映射缩写解析为全名。"""
    if not isinstance(by, str):
        raise TypeError(f"color_by 必须是字符串")
    s = by.lower().strip()
    if not s:
        raise ValueError("color_by 不能为空字符串")
    if "index".startswith(s) or "索引".startswith(s):
        return "索引"
    if "angle".startswith(s) or "角度".startswith(s):
        return "角度"
    if "length".startswith(s) or "长度".startswith(s):
        return "长度"
    if "x".startswith(s):
        return "x"
    if "y".startswith(s):
        return "y"
    raise ValueError(f"不支持的 color_by: {by!r}")


def _线颜色值(线段列表, 颜色映射):
    """根据线段列表和颜色映射计算每段线的颜色值数组。"""
    by = _解析线颜色映射(颜色映射)
    values = []
    for x, y in 线段列表:
        if by == '索引':
            values.append(len(values))
        elif by == '角度':
            dx = x[-1] - x[0]
            dy = y[-1] - y[0]
            values.append(np.arctan2(dy, dx))
        elif by == '长度':
            dx = x[-1] - x[0]
            dy = y[-1] - y[0]
            values.append(np.sqrt(dx**2 + dy**2))
        elif by == 'x':
            values.append((x[0] + x[-1]) / 2)
        elif by == 'y':
            values.append((y[0] + y[-1]) / 2)
    return np.array(values)


def _是统一颜色线(颜色):
    """判断颜色是否表示统一颜色。"""
    if isinstance(颜色, str):
        return True
    if isinstance(颜色, bytes):
        return True
    if hasattr(颜色, "ndim") and 颜色.ndim == 0:
        return True
    return False


def _是颜色名列表(颜色):
    """判断颜色是否是颜色名/色码字符串的列表。"""
    if not isinstance(颜色, (list, np.ndarray)):
        return False
    first = 颜色[0]
    if isinstance(first, str):
        return True
    if hasattr(first, "ndim") and first.ndim == 0 and np.issubdtype(first, np.str_):
        return True
    return False


# ======================== 核心生成函数 ========================

def 连接(点s, 闭合=True):
    """按顺序连接点，生成折线（或闭合多边形）。

    参数:
        点s (点集 | array-like): 形状为 (N, 2) 的点坐标。
        闭合 (bool): 是否闭合（首尾相连）。

    返回:
        线集: 线段容器。
    """
    if isinstance(点s, 点集):
        pts = 点s.点坐标
    else:
        pts = np.asarray(点s)
    n = len(pts)
    线s = 线集()
    for i in range(n - 1):
        线s.添加线段([pts[i, 0], pts[i + 1, 0]], [pts[i, 1], pts[i + 1, 1]])
    if 闭合 and n > 1:
        线s.添加线段([pts[-1, 0], pts[0, 0]], [pts[-1, 1], pts[0, 1]])
    return 线s


def 连接_全部(点s):
    """两两连接所有点（全连接图）。

    参数:
        点s (点集 | array-like): 形状为 (N, 2) 的点坐标。

    返回:
        线集: 包含 C(N,2) 段线的线段容器。
    """
    if isinstance(点s, 点集):
        pts = 点s.点坐标
    else:
        pts = np.asarray(点s)
    n = len(pts)
    线s = 线集()
    for i in range(n):
        for j in range(i + 1, n):
            线s.添加线段([pts[i, 0], pts[j, 0]], [pts[i, 1], pts[j, 1]])
    return 线s


def 多重多边形(
    n=6, m=3, 主半径=1, a=1, b=1, p=2, q=2,
    旋转=0, 层旋转=0, 形状='圆', 方向='双向', 圆心=(0, 0),
):
    """生成多层正n边形连线（每层为闭合多边形）。

    参数与点阵一致。

    返回:
        线集
    """
    点s = 点阵(
        n=n, m=m, 主半径=主半径, a=a, b=b, p=p, q=q,
        旋转=旋转, 层旋转=层旋转, 形状=形状, 方向=方向, 圆心=圆心,
    )
    pts = 点s.点坐标
    线s = 线集()
    for start in range(0, len(pts), n):
        chunk = 点集(pts[start:start + n])
        线s = 线s + 连接(chunk, 闭合=True)
    return 线s


def 梅塔特隆立方体(n=6, m=3, 旋转=0, 圆心=(0, 0)):
    """生成类梅塔特隆立方体连线（多层圆上n等分点之间全连接）。

    参数:
        n (int): 每层点数。
        m (int): 层数，半径为1,2,...,m。
        旋转 (float): 初始旋转（弧度）。

    返回:
        线集
    """
    点s = 点集(np.empty((0, 2)))
    for i in range(m):
        点s = 点s + n_点s(n=n, 主半径=i + 1, 旋转=旋转, 圆心=圆心)
    return 连接_全部(点s)


def 水晶立方体(
    n=6, m=3, 主半径=1, a=1, b=1, p=2, q=2,
    旋转=0, 层旋转=None, 形状='圆', 方向='双向', 圆心=(0, 0),
):
    """生成水晶立方体连线（点阵全连接图）。

    内部调用点阵生成点集，然后对所有点做两两全连接。
    """
    if 层旋转 is None:
        层旋转 = 180 / n
    点s = 点阵(
        n=n, m=m, 主半径=主半径, a=a, b=b, p=p, q=q,
        旋转=旋转, 层旋转=层旋转, 形状=形状, 方向=方向, 圆心=圆心,
    )
    return 连接_全部(点s)


def 万字符(n=3, 主半径=1, 旋转=0):
    """生成卍字螺旋点。

    点位于螺旋线上：r_i = R·(√2)^i, θ_i = i·π/4 + 旋转。

    返回:
        点集
    """
    角度s = np.arange(n) * np.pi / 4 + 旋转
    半径s = 主半径 * np.sqrt(2) ** np.arange(n)
    x = 半径s * np.cos(角度s)
    y = 半径s * np.sin(角度s)
    return 点集(np.column_stack([x, y]))


def 万字符线(n=3, 主半径=1, 旋转=0):
    """生成卍字图案连线（中心辐射线 + 螺旋连线）。

    返回:
        线集
    """
    线s = 线集()

    if n == 2:
        r1 = 主半径 * np.sqrt(2) ** (n - 2)
        for i in range(4):
            a = i * 2 * np.pi / 4 + 旋转
            线s.添加线段([r1 * np.cos(a), 0], [r1 * np.sin(a), 0])
    elif n % 2 == 1:
        r1 = 主半径 * np.sqrt(2) ** (n - 3)
        r2 = 主半径 * np.sqrt(2) ** (n - 2)
        for i in range(4):
            a1 = i * 2 * np.pi / 4 + 旋转
            a2 = i * 2 * np.pi / 4 + np.pi / 4 + 旋转
            线s.添加线段([r1 * np.cos(a1), 0], [r1 * np.sin(a1), 0])
            线s.添加线段([r2 * np.cos(a2), 0], [r2 * np.sin(a2), 0])
    else:
        r1 = 主半径 * np.sqrt(2) ** (n - 2)
        r2 = 主半径 * np.sqrt(2) ** (n - 3)
        for i in range(4):
            a1 = i * 2 * np.pi / 4 + 旋转
            a2 = i * 2 * np.pi / 4 + np.pi / 4 + 旋转
            线s.添加线段([r1 * np.cos(a1), 0], [r1 * np.sin(a1), 0])
            线s.添加线段([r2 * np.cos(a2), 0], [r2 * np.sin(a2), 0])

    for i in range(4):
        点s = 万字符(n, 主半径, i * np.pi / 2 + 旋转)
        线s = 线s + 连接(点s, 闭合=False)

    return 线s


# ======================== 绘制函数 ========================

def draw_线(
    线s,
    颜色='g',
    透明度=1,
    线宽=1,
    线型='-',
    标签=None,
    颜色映射=None,
    cmap=None,
    ax=None,
    显示=True,
    **kwargs,
):
    """绘制线段集合，支持统一颜色、颜色列表和渐变色。

    参数:
        线s (线集): 线集对象。
        颜色: 统一颜色(str) / 颜色名列表 / 数值列表。
        颜色映射 (str | None): 自动生成渐变色——
            '索引' '角度' '长度' 'x' 'y'（支持缩写）。
        cmap (str | None): colormap名称，默认"plasma"。

    返回:
        matplotlib.lines.Line2D | LineCollection
    """
    if ax is None:
        ax = plt.gca()

    线段列表 = 线s.线段列表
    use_gradient = 颜色映射 is not None or not _是统一颜色线(颜色)

    if use_gradient:
        segs = [np.column_stack([x, y]) for x, y in 线段列表]

        if 颜色映射 is not None:
            c_values = _线颜色值(线段列表, 颜色映射)
            if cmap is None:
                cmap = "plasma"
            lc = LineCollection(segs, cmap=cmap, alpha=透明度, linewidths=线宽, linestyles=线型, label=标签, **kwargs)
            lc.set_array(c_values)
        elif _是颜色名列表(颜色):
            lc = LineCollection(segs, colors=颜色, alpha=透明度, linewidths=线宽, linestyles=线型, label=标签, **kwargs)
        else:
            c_values = np.asarray(颜色)
            if cmap is None:
                cmap = "plasma"
            lc = LineCollection(segs, cmap=cmap, alpha=透明度, linewidths=线宽, linestyles=线型, label=标签, **kwargs)
            lc.set_array(c_values)

        ax.add_collection(lc)
        ax.autoscale_view()
        ax.set_aspect("equal", adjustable="box")
        if 标签:
            ax.legend()
        if 显示:
            plt.show()
        return lc
    else:
        line_objs = []
        first_label = 标签
        for x, y in 线段列表:
            obj = ax.plot(x, y, color=颜色, alpha=透明度, linewidth=线宽, linestyle=线型, label=first_label, **kwargs)
            line_objs.append(obj[0])
            first_label = None
        ax.set_aspect("equal", adjustable="box")
        if 标签:
            ax.legend()
        if 显示:
            plt.show()
        return line_objs


def draw_多重多边形(
    n=6, m=3, 主半径=1, a=1, b=1, p=2, q=2,
    旋转=0, 层旋转=0, 形状='圆', 方向='双向', 圆心=(0, 0),
    颜色='g', 透明度=1, 线宽=1, 线型='-', 标签=None,
    颜色映射=None, cmap=None, 显示=True, ax=None, **kwargs,
):
    """绘制多层多边形。参数与多重多边形一致。"""
    线s = 多重多边形(n=n, m=m, 主半径=主半径, a=a, b=b, p=p, q=q,
                   旋转=旋转, 层旋转=层旋转, 形状=形状, 方向=方向, 圆心=圆心)
    return draw_线(线s, 颜色=颜色, 透明度=透明度, 线宽=线宽, 线型=线型, 标签=标签,
                   颜色映射=颜色映射, cmap=cmap, 显示=显示, ax=ax, **kwargs)


def draw_梅塔特隆立方体(
    n=6, m=3, 旋转=0, 圆心=(0, 0),
    颜色='g', 透明度=1, 线宽=1, 线型='-', 标签=None,
    颜色映射=None, cmap=None, 显示=True, ax=None, **kwargs,
):
    """绘制类梅塔特隆立方体。"""
    线s = 梅塔特隆立方体(n=n, m=m, 旋转=旋转, 圆心=圆心)
    return draw_线(线s, 颜色=颜色, 透明度=透明度, 线宽=线宽, 线型=线型, 标签=标签,
                   颜色映射=颜色映射, cmap=cmap, 显示=显示, ax=ax, **kwargs)


def draw_水晶立方体(
    n=6, m=3, 旋转=0, 方向='双向', 圆心=(0, 0),
    颜色='#0f0', 透明度=1, 线宽=1, 线型='-', 标签=None,
    颜色映射=None, cmap=None, 显示=True, ax=None, **kwargs,
):
    """绘制水晶立方体。"""
    线s = 水晶立方体(n=n, m=m, 旋转=旋转, 方向=方向, 圆心=圆心)
    return draw_线(线s, 颜色=颜色, 透明度=透明度, 线宽=线宽, 线型=线型, 标签=标签,
                   颜色映射=颜色映射, cmap=cmap, 显示=显示, ax=ax, **kwargs)


def draw_万字符(
    n=3, 主半径=1, 旋转=0,
    颜色='b', 透明度=1, 线宽=1, 线型='-', 标签=None,
    颜色映射=None, cmap=None, 显示=True, ax=None, **kwargs,
):
    """绘制单个卍字图案。"""
    线s = 万字符线(n=n, 主半径=主半径, 旋转=旋转)
    return draw_线(线s, 颜色=颜色, 透明度=透明度, 线宽=线宽, 线型=线型, 标签=标签,
                   颜色映射=颜色映射, cmap=cmap, 显示=显示, ax=ax, **kwargs)


def draw_万字符s(
    n=3, 主半径=1, m=4, 旋转=0,
    颜色='b', 透明度=1, 线宽=1, 线型='-', 标签=None,
    颜色映射=None, cmap=None, 显示=True, ax=None, **kwargs,
):
    """绘制多个旋转卍字图案。

    参数:
        m (int): 卍字个数，均匀分布在2π范围内。
    """
    all_线s = 线集()
    for i in range(m):
        all_线s = all_线s + 万字符线(n=n, 主半径=主半径, 旋转=i * np.pi / m + 旋转)
    return draw_线(all_线s, 颜色=颜色, 透明度=透明度, 线宽=线宽, 线型=线型, 标签=标签,
                   颜色映射=颜色映射, cmap=cmap, 显示=显示, ax=ax, **kwargs)


__all__ = [
    "线集", "连接", "连接_全部", "多重多边形",
    "梅塔特隆立方体", "水晶立方体", "万字符", "万字符线",
    "draw_线", "draw_多重多边形", "draw_梅塔特隆立方体",
    "draw_水晶立方体", "draw_万字符", "draw_万字符s",
]

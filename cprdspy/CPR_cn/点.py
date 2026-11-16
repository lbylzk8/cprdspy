"""
点模块 — 点集生成与绘制

提供n等分点、点阵生成、散点绘制等中文接口。
"""

import warnings
import numpy as np
import matplotlib.pyplot as plt


class 点集:
    """点集容器，支持 + 运算符拼接，以及 draw_点s 绘制。

    用法:
        点s = n_点s(3, 1) + n_点s(5, 1) + n_点s(8, 1)
        draw_点s(点s)

    属性:
        点坐标: 底层 numpy 数组，形状 (N, 2)
        x: 所有点的 x 坐标数组
        y: 所有点的 y 坐标数组
    """

    def __init__(self, 点坐标):
        self._点坐标 = np.atleast_2d(np.asarray(点坐标, dtype=float))

    def __array__(self, dtype=None):
        return np.asarray(self._点坐标, dtype=dtype)

    def __add__(self, other):
        if isinstance(other, 点集):
            return 点集(np.vstack([self._点坐标, other._点坐标]))
        return NotImplemented

    def __radd__(self, other):
        if other == 0:
            return self
        return NotImplemented

    def __len__(self):
        return len(self._点坐标)

    def __getitem__(self, idx):
        return self._点坐标[idx]

    def __repr__(self):
        return f"点集(n={len(self._点坐标)})"

    @property
    def 点坐标(self):
        return self._点坐标

    @property
    def x(self):
        return self._点坐标[:, 0]

    @property
    def y(self):
        return self._点坐标[:, 1]

    def 旋转(self, 角度):
        """绕原点旋转（弧度），原地修改。返回self支持链式调用。"""
        cos_a, sin_a = np.cos(角度), np.sin(角度)
        x, y = self._点坐标[:, 0], self._点坐标[:, 1]
        self._点坐标[:, 0] = x * cos_a - y * sin_a
        self._点坐标[:, 1] = x * sin_a + y * cos_a
        return self

    def 缩放(self, sx, sy=None):
        """缩放坐标，原地修改。返回self支持链式调用。"""
        if sy is None:
            sy = sx
        self._点坐标[:, 0] *= sx
        self._点坐标[:, 1] *= sy
        return self

    def 平移(self, dx, dy):
        """平移坐标，原地修改。返回self支持链式调用。"""
        self._点坐标[:, 0] += dx
        self._点坐标[:, 1] += dy
        return self

    def __eq__(self, other):
        if isinstance(other, 点集):
            return np.allclose(self._点坐标, other._点坐标)
        return NotImplemented


# ======================== 内部辅助 ========================

def _解析形状(形状):
    """将形状缩写解析为全名。"""
    if not isinstance(形状, str):
        raise TypeError(f"形状必须是字符串，收到 {type(形状).__name__}: {形状!r}")
    s = 形状.lower().strip()
    if not s:
        raise ValueError("形状不能为空字符串")
    if "circle".startswith(s) or "圆".startswith(s):
        return "圆"
    if "ellipse".startswith(s) or "椭圆".startswith(s):
        return "椭圆"
    if "superellipse".startswith(s) or "超椭圆".startswith(s):
        return "超椭圆"
    raise ValueError(f"不支持的形状: {形状!r}")


def _解析方向(方向):
    """将方向缩写解析为全名。"""
    if not isinstance(方向, str):
        raise TypeError(f"方向必须是字符串，收到 {type(方向).__name__}: {方向!r}")
    d = 方向.lower().strip()
    if not d:
        raise ValueError("方向不能为空字符串")
    if "in".startswith(d) or "向内".startswith(d) or "内".startswith(d):
        return "向内"
    if "out".startswith(d) or "向外".startswith(d) or "外".startswith(d):
        return "向外"
    if "both".startswith(d) or "双向".startswith(d) or "双".startswith(d):
        return "双向"
    raise ValueError(f"不支持的方向: {方向!r}，可选 '向内' '向外' '双向'")


def _解析颜色映射(by):
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
    if "radius".startswith(s) or "半径".startswith(s):
        return "半径"
    if "x".startswith(s):
        return "x"
    if "y".startswith(s):
        return "y"
    raise ValueError(f"不支持的 color_by: {by!r}")


# ======================== 核心生成函数 ========================

def n_点s(n=12, 主半径=1, a=1, b=1, p=2, q=2, 旋转=0, 使用角度制=True, 形状='圆', 圆心=(0, 0)):
    """生成n等分点集。

    参数:
        n (int): 等分点数。
        主半径 (float): 基准大小（圆的半径，椭圆的缩放因子）。
        a (float): x半轴系数。
        b (float): y半轴系数。
        p (float): 超椭圆x指数。
        q (float): 超椭圆y指数。
        旋转 (float): 初始旋转角度。
        使用角度制 (bool): 旋转是否使用角度制。
        形状 (str): '圆' | '椭圆' | '超椭圆'（支持缩写）。
        圆心 (tuple): 中心坐标。

    返回:
        点集: 包含 (n, 2) 点坐标的点集对象。
    """
    形状 = _解析形状(形状)
    旋转弧度 = np.deg2rad(旋转) if 使用角度制 else 旋转
    角度s = np.arange(n) * 2 * np.pi / n + np.pi / 2 + 旋转弧度

    if 形状 == '圆':
        x = 圆心[0] + 主半径 * np.cos(角度s)
        y = 圆心[1] + 主半径 * np.sin(角度s)
    elif 形状 == '椭圆':
        x = 圆心[0] + 主半径 * a * np.cos(角度s)
        y = 圆心[1] + 主半径 * b * np.sin(角度s)
    elif 形状 == '超椭圆':
        cos_sign = np.sign(np.cos(角度s))
        sin_sign = np.sign(np.sin(角度s))
        cos_abs = np.abs(np.cos(角度s))
        sin_abs = np.abs(np.sin(角度s))
        cos_pow = np.where(cos_abs > 0, cos_abs ** (2.0 / p), 0.0)
        sin_pow = np.where(sin_abs > 0, sin_abs ** (2.0 / q), 0.0)
        x = 圆心[0] + 主半径 * a * cos_sign * cos_pow
        y = 圆心[1] + 主半径 * b * sin_sign * sin_pow

    return 点集(np.column_stack([x, y]))


def draw_点s(
    点s, 颜色='b', 大小=100, 透明度=1,
    颜色映射=None, cmap=None, 显示=True, ax=None,
    **kwargs,
):
    """绘制点集，支持统一颜色、逐点颜色和渐变色。

    参数:
        点s (点集 | array-like): 形状为 (N, 2) 的点坐标。
        颜色 (str | array-like): 统一颜色或逐点颜色。
        大小 (int | array-like): 点的大小。
        透明度 (float): 透明度。
        颜色映射 (str | None): 自动生成渐变色——
            '索引' '角度' '半径' 'x' 'y'（支持缩写）。
        cmap (str | None): colormap名称。
        ax (matplotlib.axes.Axes): 目标坐标轴。
    """
    if isinstance(点s, 点集):
        pts = 点s.点坐标
    else:
        pts = np.asarray(点s)

    if ax is None:
        ax = plt.gca()

    c_values = _解析颜色s(pts, 颜色, 颜色映射)
    use_c = 颜色映射 is not None or not _是统一颜色(颜色)

    if use_c:
        sc = ax.scatter(pts[:, 0], pts[:, 1], c=c_values, s=大小, alpha=透明度, cmap=cmap, **kwargs)
    else:
        sc = ax.scatter(pts[:, 0], pts[:, 1], color=颜色, s=大小, alpha=透明度, **kwargs)

    ax.set_aspect("equal", adjustable="box")
    if 显示:
        plt.show()
    return sc


def _是统一颜色(颜色):
    """判断颜色是否表示统一颜色。"""
    if isinstance(颜色, str):
        return True
    if hasattr(颜色, "ndim") and 颜色.ndim == 0:
        return True
    return False


def _解析颜色s(pts, 颜色, 颜色映射):
    """根据颜色和颜色映射参数解析用于scatter c=的颜色数组。"""
    N = len(pts)

    if 颜色映射 is not None:
        if not _是统一颜色(颜色):
            warnings.warn(f"颜色映射={颜色映射!r}和颜色数组同时指定，颜色数组将被忽略")
        by = _解析颜色映射(颜色映射)
        if by == '索引':
            return np.arange(N)
        elif by == '角度':
            return np.arctan2(pts[:, 1], pts[:, 0])
        elif by == '半径':
            return np.sqrt(pts[:, 0] ** 2 + pts[:, 1] ** 2)
        elif by == 'x':
            return pts[:, 0]
        else:
            return pts[:, 1]

    if not _是统一颜色(颜色):
        return np.asarray(颜色)

    return None


# ======================== 点阵生成 ========================

def 点阵(
    n=12,
    m=3,
    主半径=1,
    a=1, b=1, p=2, q=2,
    旋转=0,
    层旋转=0,
    使用角度制=True,
    形状='圆',
    方向='双向',
    圆心=(0, 0),
):
    """生成多层正n边形点阵（半径逐层缩放）。

    第i层（i从0开始）：
        向内: 半径 = 主半径 * (cos(pi/n))^i
        向外: 半径 = 主半径 * (cos(pi/n))^(-i)
        双向: 内侧 + 外侧

    参数:
        n (int): 每层点数。
        m (int): 层数。
        主半径 (float): 基准半径。
        旋转 (float): 初始旋转。
        层旋转 (float): 每层附加旋转步长。
        方向 (str): '双向'|'向外'|'向内'。
        形状 (str): '圆' | '椭圆' | '超椭圆'。

    返回:
        点集
    """
    旋转弧度 = np.deg2rad(旋转) if 使用角度制 else 旋转
    层旋转弧度 = np.deg2rad(层旋转) if 使用角度制 else 层旋转
    方向 = _解析方向(方向)

    点s列表 = []

    if 方向 == '向内':
        for i in range(m):
            r_i = 主半径 * (np.cos(np.pi / n)) ** i
            rot_i = 旋转弧度 + i * (np.pi / n + 层旋转弧度)
            点s列表.append(n_点s(n=n, 主半径=r_i, a=a, b=b, p=p, q=q, 旋转=rot_i, 使用角度制=False, 形状=形状, 圆心=圆心))
    elif 方向 == '向外':
        for i in range(m):
            r_i = 主半径 * (np.cos(np.pi / n)) ** (-i)
            rot_i = 旋转弧度 + i * (np.pi / n + 层旋转弧度)
            点s列表.append(n_点s(n=n, 主半径=r_i, a=a, b=b, p=p, q=q, 旋转=rot_i, 使用角度制=False, 形状=形状, 圆心=圆心))
    elif 方向 == '双向':
        for i in range(m):
            r_in = 主半径 * (np.cos(np.pi / n)) ** i
            r_out = 主半径 * (np.cos(np.pi / n)) ** (-i)
            rot_in = 旋转弧度 + i * (np.pi / n + 层旋转弧度)
            rot_out = 旋转弧度 + i * (np.pi / n - 层旋转弧度)
            点s列表.append(n_点s(n=n, 主半径=r_in, a=a, b=b, p=p, q=q, 旋转=rot_in, 使用角度制=False, 形状=形状, 圆心=圆心))
            点s列表.append(n_点s(n=n, 主半径=r_out, a=a, b=b, p=p, q=q, 旋转=rot_out, 使用角度制=False, 形状=形状, 圆心=圆心))

    if not 点s列表:
        return 点集(np.empty((0, 2)))
    return 点集(np.vstack([d._点坐标 for d in 点s列表]))


def draw_点阵(
    n=12, m=3, 主半径=1, a=1, b=1, p=2, q=2,
    旋转=0, 层旋转=0, 使用角度制=True, 形状='圆', 方向='双向',
    圆心=(0, 0),
    颜色='b', 大小=100, 透明度=1,
    颜色映射=None, cmap=None,
    ax=None,
    **kwargs,
):
    """绘制多层正n边形点阵。参数与点阵一致。"""
    点s = 点阵(
        n=n, m=m, 主半径=主半径, a=a, b=b, p=p, q=q,
        旋转=旋转, 层旋转=层旋转, 使用角度制=使用角度制,
        形状=形状, 方向=方向, 圆心=圆心,
    )
    return draw_点s(点s, 颜色=颜色, 大小=大小, 透明度=透明度, 颜色映射=颜色映射, cmap=cmap, ax=ax, **kwargs)


__all__ = ["点集", "n_点s", "draw_点s", "点阵", "draw_点阵"]

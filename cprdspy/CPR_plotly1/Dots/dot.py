import warnings
import numpy as np
import plotly.graph_objects as go


class Dots:
    """点集容器，支持 + 运算符拼接，以及 draw_dots 绘制。

    用法:
        dots = n_dots(3, 1) + n_dots(5, 1) + n_dots(8, 1)
        draw_dots(dots)

    属性:
        points: 底层 numpy 数组，形状 (N, 2)
        x: 所有点的 x 坐标数组
        y: 所有点的 y 坐标数组
    """

    def __init__(self, points):
        self._points = np.atleast_2d(np.asarray(points, dtype=float))

    # ---- 使 Dots 可参与 numpy 操作 ----
    def __array__(self, dtype=None):
        """支持 numpy 自动转换（如 np.vstack([dots1, dots2])）。"""
        return np.asarray(self._points, dtype=dtype)

    # ---- 拼接运算符 ----
    def __add__(self, other):
        """拼接两个 Dots 对象：dots_a + dots_b。"""
        if isinstance(other, Dots):
            return Dots(np.vstack([self._points, other._points]))
        return NotImplemented

    def __radd__(self, other):
        """支持 sum([dots1, dots2, ...])。"""
        if other == 0:
            return self
        return NotImplemented

    # ---- 容器协议 ----
    def __len__(self):
        return len(self._points)

    def __getitem__(self, idx):
        return self._points[idx]

    def __repr__(self):
        return f"Dots(n={len(self._points)})"

    # ---- 便捷属性 ----
    @property
    def points(self):
        """底层 numpy 数组，形状 (N, 2)。"""
        return self._points

    @property
    def x(self):
        """所有点的 x 坐标。"""
        return self._points[:, 0]

    @property
    def y(self):
        """所有点的 y 坐标。"""
        return self._points[:, 1]

    # ---- 变换操作（原地修改，返回 self 支持链式调用） ----

    def rotate(self, angle):
        """绕原点旋转 angle 弧度，原地修改。

        返回 self，支持链式调用。
        """
        cos_a, sin_a = np.cos(angle), np.sin(angle)
        x, y = self._points[:, 0], self._points[:, 1]
        self._points[:, 0] = x * cos_a - y * sin_a
        self._points[:, 1] = x * sin_a + y * cos_a
        return self

    def scale(self, sx, sy=None):
        """按 (sx, sy) 缩放坐标，原地修改。sy 为 None 时与 sx 相同（等比缩放）。

        返回 self，支持链式调用。
        """
        if sy is None:
            sy = sx
        self._points[:, 0] *= sx
        self._points[:, 1] *= sy
        return self

    def translate(self, dx, dy):
        """平移 (dx, dy)，原地修改。

        返回 self，支持链式调用。
        """
        self._points[:, 0] += dx
        self._points[:, 1] += dy
        return self

    # ---- 比较 ----

    def __eq__(self, other):
        """逐元素比较点坐标是否相等。"""
        if isinstance(other, Dots):
            return np.allclose(self._points, other._points)
        return NotImplemented


# ======================== 核心生成函数 ========================


def n_dots(n=12, R=1, a=1, b=1, p=2, q=2, rotation=0, use_degree=True, shape="circle", center=(0, 0)):
    """生成点集。

    参数:
        n (int): 等分点数。
        R (float): 基准大小 ——
            shape="circle"      圆的半径
            shape="ellipse"     椭圆整体缩放因子（半轴 = R*a, R*b）
            shape="superellipse" 超椭圆整体缩放因子（半轴 = R*a, R*b）
        a (float): x 半轴系数（ellipse / superellipse 时与 R 相乘得到实际半轴）。
        b (float): y 半轴系数（ellipse / superellipse 时与 R 相乘得到实际半轴）。
        p (float): 超椭圆公式 |x/a|^p + |y/b|^q = 1 中的 x 指数，仅 shape="superellipse"。
        q (float): 超椭圆公式 |x/a|^q + |y/b|^q = 1 中的 y 指数，仅 shape="superellipse"。
        rotation (float): 初始旋转角度（度或弧度取决于 use_degree），默认为 0。
        use_degree (bool): rotation 是否使用角度制，默认 True（度）。
        shape (str): 形状类型 ——
            "circle"       正圆:     x = R·cos(θ),         y = R·sin(θ)
            "ellipse"      椭圆:     x = R·a·cos(θ),      y = R·b·sin(θ)
            "superellipse" 超椭圆:   |x/(R·a)|^p + |y/(R·b)|^q = 1
        center (tuple): 中心坐标，默认为 (0, 0)。

    返回:
        Dots: 包含 (n, 2) 点坐标的点集对象，支持 + 拼接。
    """
    shape = _resolve_shape(shape)
    rotation_rad = np.deg2rad(rotation) if use_degree else rotation
    angles = np.arange(n) * 2 * np.pi / n + np.pi / 2 + rotation_rad

    if shape == "circle":
        x = center[0] + R * np.cos(angles)
        y = center[1] + R * np.sin(angles)

    elif shape == "ellipse":
        x = center[0] + R * a * np.cos(angles)
        y = center[1] + R * b * np.sin(angles)

    elif shape == "superellipse":
        cos_sign = np.sign(np.cos(angles))
        sin_sign = np.sign(np.sin(angles))
        cos_abs = np.abs(np.cos(angles))
        sin_abs = np.abs(np.sin(angles))
        cos_pow = np.where(cos_abs > 0, cos_abs ** (2.0 / p), 0.0)
        sin_pow = np.where(sin_abs > 0, sin_abs ** (2.0 / q), 0.0)
        x = center[0] + R * a * cos_sign * cos_pow
        y = center[1] + R * b * sin_sign * sin_pow

    return Dots(np.column_stack([x, y]))


# ======================== 内部辅助 ========================


def _resolve_shape(shape):
    """将 shape 缩写解析为全名，支持前缀匹配。"""
    if not isinstance(shape, str):
        raise TypeError(f"shape 必须是字符串，收到 {type(shape).__name__}: {shape!r}")
    s = shape.lower().strip()
    if not s:
        raise ValueError("shape 不能为空字符串")
    if "circle".startswith(s):
        return "circle"
    if "ellipse".startswith(s):
        return "ellipse"
    if "superellipse".startswith(s):
        return "superellipse"
    raise ValueError(
        f"不支持的 shape: {shape!r}，输入任意前缀即可，如 'c'→circle 'e'→ellipse 's'→superellipse"
    )


def _resolve_direction(direction):
    """将 direction 缩写解析为全名，支持前缀匹配。"""
    if not isinstance(direction, str):
        raise TypeError(
            f"direction 必须是字符串，收到 {type(direction).__name__}: {direction!r}"
        )
    d = direction.lower().strip()
    if not d:
        raise ValueError("direction 不能为空字符串")
    if "in".startswith(d):
        return "in"
    if "out".startswith(d):
        return "out"
    if "both".startswith(d):
        return "both"
    raise ValueError(
        f"不支持的 direction: {direction!r}，可选 'in' 'out' 'both'（或缩写 'i' 'o' 'b'）"
    )


def draw_dots(
    dots, color="blue", size=6, alpha=1, color_by=None, cmap=None, name=None, showlegend=None, **kwargs
):
    """绘制点集，支持统一颜色、逐点颜色和渐变色。

    参数:
        dots (Dots | array-like): 形状为 (N, 2) 的点坐标。
        color (str | array-like): 统一颜色或逐点颜色。
        size (int | array-like): 点的大小，默认为 6。
        alpha (float): 透明度，默认为 1。
        color_by (str | None): 自动生成渐变色，按指定维度映射 ——
            "index"  按点的顺序
            "angle"  按点相对于原点的极角
            "radius" 按点相对于原点的极径
            "x"      按 x 坐标
            "y"      按 y 坐标
        cmap (str | None): colormap 名称（plotly 支持有限）。
        name (str): 轨迹名称。
        showlegend (bool): 是否显示图例。
        **kwargs: 其他传递给 go.Scatter 的参数。

    返回:
        plotly.graph_objs.Scatter: 散点图轨迹。
    """
    if isinstance(dots, Dots):
        pts = dots.points
    else:
        pts = np.asarray(dots)

    c_values = _resolve_colors(pts, color, color_by)
    use_c = color_by is not None or not _is_uniform_color(color)

    if use_c:
        trace = go.Scatter(
            x=pts[:, 0],
            y=pts[:, 1],
            mode="markers",
            marker=dict(
                size=size,
                color=c_values,
                colorscale=cmap if cmap else "Viridis",
                opacity=alpha,
            ),
            name=name,
            showlegend=showlegend if showlegend is not None else (name is not None),
            **kwargs,
        )
    else:
        trace = go.Scatter(
            x=pts[:, 0],
            y=pts[:, 1],
            mode="markers",
            marker=dict(
                size=size,
                color=color,
                opacity=alpha,
            ),
            name=name,
            showlegend=showlegend if showlegend is not None else (name is not None),
            **kwargs,
        )

    return [trace]


def _is_uniform_color(color):
    """判断 color 是否表示统一颜色。"""
    if isinstance(color, str):
        return True
    if hasattr(color, "ndim") and color.ndim == 0:
        return True
    return False


def _color_by_alias(by):
    """将 color_by 缩写解析为全名，支持前缀匹配。"""
    if not isinstance(by, str):
        raise TypeError(f"color_by 必须是字符串，收到 {type(by).__name__}: {by!r}")
    s = by.lower().strip()
    if not s:
        raise ValueError("color_by 不能为空字符串")
    if "index".startswith(s):
        return "index"
    if "angle".startswith(s):
        return "angle"
    if "radius".startswith(s):
        return "radius"
    if "x".startswith(s):
        return "x"
    if "y".startswith(s):
        return "y"
    raise ValueError(
        f"不支持的 color_by: {by!r}，可选 'index' 'angle' 'radius' 'x' 'y'（或缩写 'i' 'a' 'r'）"
    )


def _resolve_colors(pts, color, color_by):
    """根据 color 和 color_by 参数解析颜色数组。"""
    N = len(pts)

    if color_by is not None:
        if not _is_uniform_color(color):
            warnings.warn(
                f"color_by={color_by!r} 和 color 数组同时指定，color 数组将被忽略"
            )
        by = _color_by_alias(color_by)
        if by == "index":
            return np.arange(N)
        elif by == "angle":
            return np.arctan2(pts[:, 1], pts[:, 0])
        elif by == "radius":
            return np.sqrt(pts[:, 0] ** 2 + pts[:, 1] ** 2)
        elif by == "x":
            return pts[:, 0]
        else:  # y
            return pts[:, 1]

    if not _is_uniform_color(color):
        return np.asarray(color)

    return None


# ======================== 点阵生成 ========================


def n_dots_array(
    n=12,
    m=3,
    R=1,
    a=1,
    b=1,
    p=2,
    q=2,
    rotation=0,
    d_rotation=0,
    use_degree=True,
    shape="circle",
    direction="both",
    center=(0, 0),
):
    """生成多层正 n 边形点阵（半径逐层缩放），支持 n_dots 所有形状。"""
    rotation_rad = np.deg2rad(rotation) if use_degree else rotation
    dr_rad = np.deg2rad(d_rotation) if use_degree else d_rotation
    direction = _resolve_direction(direction)

    dots_list = []

    if direction == "in":
        for i in range(m):
            r_i = R * (np.cos(np.pi / n)) ** i
            rot_i = rotation_rad + i * (np.pi / n + dr_rad)
            dots_list.append(
                n_dots(n=n, R=r_i, a=a, b=b, p=p, q=q, rotation=rot_i, use_degree=False, shape=shape, center=center)
            )

    elif direction == "out":
        for i in range(m):
            r_i = R * (np.cos(np.pi / n)) ** (-i)
            rot_i = rotation_rad + i * (np.pi / n + dr_rad)
            dots_list.append(
                n_dots(n=n, R=r_i, a=a, b=b, p=p, q=q, rotation=rot_i, use_degree=False, shape=shape, center=center)
            )

    elif direction == "both":
        for i in range(m):
            r_in = R * (np.cos(np.pi / n)) ** i
            r_out = R * (np.cos(np.pi / n)) ** (-i)
            rot_in = rotation_rad + i * (np.pi / n + dr_rad)
            rot_out = rotation_rad + i * (np.pi / n - dr_rad)
            dots_list.append(
                n_dots(n=n, R=r_in, a=a, b=b, p=p, q=q, rotation=rot_in, use_degree=False, shape=shape, center=center)
            )
            dots_list.append(
                n_dots(n=n, R=r_out, a=a, b=b, p=p, q=q, rotation=rot_out, use_degree=False, shape=shape, center=center)
            )

    if not dots_list:
        return Dots(np.empty((0, 2)))
    return Dots(np.vstack([d._points for d in dots_list]))


# ======================== 绘制函数 ========================


def draw_n_dots_array(
    n=12,
    m=3,
    R=1,
    a=1,
    b=1,
    p=2,
    q=2,
    rotation=0,
    d_rotation=0,
    use_degree=True,
    shape="circle",
    direction="both",
    center=(0, 0),
    color="blue",
    size=6,
    alpha=1,
    color_by=None,
    cmap=None,
    name=None,
    **kwargs,
):
    """绘制多层正 n 边形点阵。

    返回:
        plotly.graph_objs.Scatter
    """
    dots = n_dots_array(
        n=n, m=m, R=R, a=a, b=b, p=p, q=q,
        rotation=rotation, d_rotation=d_rotation, use_degree=use_degree,
        shape=shape, direction=direction, center=center,
    )
    return draw_dots(
        dots, color=color, size=size, alpha=alpha,
        color_by=color_by, cmap=cmap, name=name, **kwargs,
    )


__all__ = [
    "Dots",
    "n_dots",
    "draw_dots",
    "n_dots_array",
    "draw_n_dots_array",
]

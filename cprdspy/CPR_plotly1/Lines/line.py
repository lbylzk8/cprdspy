import warnings
import numpy as np
import plotly.graph_objects as go
import matplotlib.cm as cm
import matplotlib.colors as mcolors

from ..Dots.dot import Dots, n_dots, n_dots_array, draw_dots

# ======================== 线段容器 ========================


class Lines:
    """线段容器，支持 + 运算符拼接，以及 draw_lines 绘制。

    用法:
        lines = connect(dots_obj, closed=True)
        lines = lines + connect(other_dots, closed=False)
        draw_lines(lines)

    属性:
        segments: list of (x_array, y_array) — 每个元素是一段线的 (x, y) 坐标数组。
    """

    def __init__(self, segments=None):
        self._segments = []
        if segments is not None:
            for seg in segments:
                self.add_segment(seg[0], seg[1])

    def add_segment(self, x, y):
        """添加一段线。x, y 为至少 2 个点的坐标数组。"""
        self._segments.append(
            (
                np.atleast_1d(np.asarray(x, dtype=float)),
                np.atleast_1d(np.asarray(y, dtype=float)),
            )
        )
        return self

    # ---- 拼接运算符 ----
    def __add__(self, other):
        """拼接两个 Lines 对象：lines_a + lines_b。"""
        if isinstance(other, Lines):
            result = Lines()
            result._segments = self._segments + other._segments
            return result
        return NotImplemented

    def __radd__(self, other):
        """支持 sum([lines1, lines2, ...])。"""
        if other == 0:
            return self
        return NotImplemented

    # ---- 容器协议 ----
    def __len__(self):
        return len(self._segments)

    def __getitem__(self, idx):
        return self._segments[idx]

    def __repr__(self):
        return f"Lines(n={len(self._segments)})"

    # ---- 便捷属性 ----
    @property
    def segments(self):
        """线段列表，每个元素为 (x_array, y_array)。"""
        return self._segments


# ======================== 核心生成函数 ========================


def connect(dots, closed=True):
    """按顺序连接点，生成折线（或闭合多边形）。

    参数:
        dots (Dots | array-like): 形状为 (N, 2) 的点坐标。
        closed (bool): 是否闭合（首尾相连），默认为 True。

    返回:
        Lines: 包含 N-1（不闭合）或 N（闭合）段线的线段容器。
    """
    if isinstance(dots, Dots):
        pts = dots.points
    else:
        pts = np.asarray(dots)
    n = len(pts)
    lines = Lines()
    for i in range(n - 1):
        lines.add_segment(
            [pts[i, 0], pts[i + 1, 0]],
            [pts[i, 1], pts[i + 1, 1]],
        )
    if closed and n > 1:
        lines.add_segment(
            [pts[-1, 0], pts[0, 0]],
            [pts[-1, 1], pts[0, 1]],
        )
    return lines


def connect_all(dots):
    """两两连接所有点（全连接图）。

    参数:
        dots (Dots | array-like): 形状为 (N, 2) 的点坐标。

    返回:
        Lines: 包含 C(N, 2) = N*(N-1)/2 段线的线段容器。
    """
    if isinstance(dots, Dots):
        pts = dots.points
    else:
        pts = np.asarray(dots)
    n = len(pts)
    lines = Lines()
    for i in range(n):
        for j in range(i + 1, n):
            lines.add_segment(
                [pts[i, 0], pts[j, 0]],
                [pts[i, 1], pts[j, 1]],
            )
    return lines


def multi_polygon(
    n=6,
    m=3,
    R=1,
    a=1,
    b=1,
    p=2,
    q=2,
    rotation=0,
    d_rotation=0,
    shape="circle",
    direction="both",
    center=(0, 0),
):
    """生成多层正 n 边形连线（每层为闭合多边形）。

    返回:
        Lines: 包含所有层多边形的线段容器。
    """
    dots = n_dots_array(
        n=n, m=m, R=R, a=a, b=b, p=p, q=q,
        rotation=rotation, d_rotation=d_rotation,
        shape=shape, direction=direction, center=center,
    )
    pts = dots.points
    lines = Lines()
    for start in range(0, len(pts), n):
        chunk = Dots(pts[start : start + n])
        lines = lines + connect(chunk, closed=True)
    return lines


def metatron_cube(n=6, m=3, rotation=0, center=(0, 0)):
    """生成类梅塔特隆立方体连线（多层圆上 n 等分点之间全连接）。

    返回:
        Lines: 包含所有点对之间连线的线段容器。
    """
    dots = Dots(np.empty((0, 2)))
    for i in range(m):
        dots = dots + n_dots(n=n, R=i + 1, rotation=rotation, center=center)
    return connect_all(dots)


def krystal_cube(
    n=6,
    m=3,
    R=1,
    a=1,
    b=1,
    p=2,
    q=2,
    rotation=0,
    d_rotation=None,
    shape="circle",
    direction="both",
    center=(0, 0),
):
    """生成水晶立方体连线（点阵全连接图）。

    返回:
        Lines: 包含所有点对之间连线的线段容器。
    """
    if d_rotation is None:
        d_rotation = 180 / n
    dots = n_dots_array(
        n=n, m=m, R=R, a=a, b=b, p=p, q=q,
        rotation=rotation, d_rotation=d_rotation,
        shape=shape, direction=direction, center=center,
    )
    return connect_all(dots)


def swastika(n=3, R=1, rotation=0):
    """生成卍字螺旋点。

    返回:
        Dots: 卍字螺旋点。
    """
    angles = np.arange(n) * np.pi / 4 + rotation
    radii = R * np.sqrt(2) ** np.arange(n)
    x = radii * np.cos(angles)
    y = radii * np.sin(angles)
    return Dots(np.column_stack([x, y]))


def swastika_lines(n=3, R=1, rotation=0):
    """生成卍字图案连线（中心辐射线 + 螺旋连线）。

    返回:
        Lines: 卍字图案的所有线段。
    """
    lines = Lines()

    if n == 2:
        r1 = R * np.sqrt(2) ** (n - 2)
        for i in range(4):
            a = i * 2 * np.pi / 4 + rotation
            lines.add_segment([r1 * np.cos(a), 0], [r1 * np.sin(a), 0])

    elif n % 2 == 1:
        r1 = R * np.sqrt(2) ** (n - 3)
        r2 = R * np.sqrt(2) ** (n - 2)
        for i in range(4):
            a1 = i * 2 * np.pi / 4 + rotation
            a2 = i * 2 * np.pi / 4 + np.pi / 4 + rotation
            lines.add_segment([r1 * np.cos(a1), 0], [r1 * np.sin(a1), 0])
            lines.add_segment([r2 * np.cos(a2), 0], [r2 * np.sin(a2), 0])

    else:
        r1 = R * np.sqrt(2) ** (n - 2)
        r2 = R * np.sqrt(2) ** (n - 3)
        for i in range(4):
            a1 = i * 2 * np.pi / 4 + rotation
            a2 = i * 2 * np.pi / 4 + np.pi / 4 + rotation
            lines.add_segment([r1 * np.cos(a1), 0], [r1 * np.sin(a1), 0])
            lines.add_segment([r2 * np.cos(a2), 0], [r2 * np.sin(a2), 0])

    # 4 条螺旋臂（每条旋转 90°），各 n 个点
    for i in range(4):
        dots = swastika(n, R, i * np.pi / 2 + rotation)
        lines = lines + connect(dots, closed=False)

    return lines


# ======================== 绘制函数 ========================


def _line_color_alias(by):
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
    if "length".startswith(s):
        return "length"
    if "x".startswith(s):
        return "x"
    if "y".startswith(s):
        return "y"
    raise ValueError(
        f"不支持的 color_by: {by!r}，可选 'index' 'angle' 'length' 'x' 'y'（或缩写 'i' 'a' 'l'）"
    )


def _line_color_values(segments, color_by):
    """根据 segments 和 color_by 计算每段线的颜色值数组。"""
    by = _line_color_alias(color_by)
    values = []
    for x, y in segments:
        if by == "index":
            values.append(len(values))
        elif by == "angle":
            dx = x[-1] - x[0]
            dy = y[-1] - y[0]
            values.append(np.arctan2(dy, dx))
        elif by == "length":
            dx = x[-1] - x[0]
            dy = y[-1] - y[0]
            values.append(np.sqrt(dx**2 + dy**2))
        elif by == "x":
            values.append((x[0] + x[-1]) / 2)
        elif by == "y":
            values.append((y[0] + y[-1]) / 2)
    return np.array(values)


def _is_uniform_color_line(color):
    """判断 color 是否表示统一颜色。"""
    if isinstance(color, str):
        return True
    if isinstance(color, bytes):
        return True
    if hasattr(color, "ndim") and color.ndim == 0:
        return True
    return False


def _is_color_name_list(color):
    """判断 color 是否是颜色名/色码字符串的列表。"""
    if not isinstance(color, (list, np.ndarray)):
        return False
    first = color[0] if hasattr(color, '__iter__') and len(color) > 0 else None
    if first is None:
        return False
    if isinstance(first, str):
        return True
    if hasattr(first, "ndim") and first.ndim == 0 and np.issubdtype(first, np.str_):
        return True
    return False


def _map_colorscale(values, cmap_name="Plasma"):
    """Map numeric values to hex color strings using a matplotlib colormap.

    参数:
        values (array-like): 每段线的数值。
        cmap_name (str): matplotlib colormap 名称（不区分大小写）。

    返回:
        list[str]: 每段线对应的十六进制颜色字符串。
    """
    if len(values) == 0:
        return []
    vmin, vmax = np.min(values), np.max(values)
    if np.isclose(vmin, vmax):
        # 所有值相同，取中间色
        vmin, vmax = vmin - 1, vmax + 1
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    # matplotlib colormap 名称是大小写敏感的，尝试多种方式
    try:
        colormap = cm.get_cmap(cmap_name)
    except (ValueError, KeyError):
        try:
            colormap = cm.get_cmap(cmap_name.lower())
        except (ValueError, KeyError):
            colormap = cm.get_cmap("plasma")
    return [mcolors.to_hex(colormap(norm(v))) for v in values]


def draw_lines(
    lines,
    color="green",
    alpha=1,
    line_width=1,
    label=None,
    name=None,
    showlegend=None,
    color_by=None,
    cmap=None,
    **kwargs,
):
    """绘制线段集合，支持统一颜色和渐变色。

    参数:
        lines (Lines): Lines 对象。
        color: 颜色模式 ——
            - str:             统一颜色
            - str 列表:         逐段指定颜色
            - 数值列表:          逐段数值，通过 colorscale 映射
        alpha (float): 透明度。
        line_width (float | array): 线宽。
        label (str): 图例标签。
        name (str): 轨迹名称。
        showlegend (bool): 是否显示图例。
        color_by (str | None): 自动生成渐变色 ——
            "index" "angle" "length" "x" "y"
        cmap (str | None): colorscale 名称。默认 "Plasma"。
        **kwargs: 其他传递给 go.Scatter 的参数。

    返回:
        list: 包含所有 go.Scatter 轨迹的列表。
    """
    segments = lines.segments
    use_gradient = color_by is not None or not _is_uniform_color_line(color)
    traces = []

    if use_gradient:
        if color_by is not None:
            c_values = _line_color_values(segments, color_by)
            if cmap is None:
                cmap = "Plasma"
            colors = _map_colorscale(c_values, cmap)
            for i, (x, y) in enumerate(segments):
                trace = go.Scatter(
                    x=x,
                    y=y,
                    mode="lines",
                    line=dict(
                        color=colors[i],
                        width=line_width,
                    ),
                    opacity=alpha,
                    name=name if name else label,
                    showlegend=showlegend if showlegend is not None else (i == 0 and (label is not None)),
                    **kwargs,
                )
                traces.append(trace)
        elif _is_color_name_list(color):
            for i, (x, y) in enumerate(segments):
                c = color[i % len(color)]
                trace = go.Scatter(
                    x=x,
                    y=y,
                    mode="lines",
                    line=dict(color=c, width=line_width),
                    opacity=alpha,
                    name=name if name else label,
                    showlegend=showlegend if showlegend is not None else (i == 0 and (label is not None)),
                    **kwargs,
                )
                traces.append(trace)
        else:
            c_values = np.asarray(color)
            if cmap is None:
                cmap = "Plasma"
            colors = _map_colorscale(c_values, cmap)
            for i, (x, y) in enumerate(segments):
                trace = go.Scatter(
                    x=x,
                    y=y,
                    mode="lines",
                    line=dict(
                        color=colors[i],
                        width=line_width,
                    ),
                    opacity=alpha,
                    name=name if name else label,
                    showlegend=showlegend if showlegend is not None else (i == 0 and (label is not None)),
                    **kwargs,
                )
                traces.append(trace)
    else:
        # 统一颜色
        for i, (x, y) in enumerate(segments):
            trace = go.Scatter(
                x=x,
                y=y,
                mode="lines",
                line=dict(color=color, width=line_width),
                opacity=alpha,
                name=name if name else label,
                showlegend=showlegend if showlegend is not None else (i == 0 and (label is not None)),
                **kwargs,
            )
            traces.append(trace)

    return traces


def draw_multi_polygon(
    n=6,
    m=3,
    R=1,
    a=1,
    b=1,
    p=2,
    q=2,
    rotation=0,
    d_rotation=0,
    shape="circle",
    direction="both",
    center=(0, 0),
    color="green",
    alpha=1,
    line_width=1,
    label=None,
    name=None,
    showlegend=None,
    color_by=None,
    cmap=None,
    **kwargs,
):
    """绘制多层多边形。"""
    lines = multi_polygon(
        n=n, m=m, R=R, a=a, b=b, p=p, q=q,
        rotation=rotation, d_rotation=d_rotation,
        shape=shape, direction=direction, center=center,
    )
    return draw_lines(
        lines, color=color, alpha=alpha, line_width=line_width,
        label=label, name=name, showlegend=showlegend,
        color_by=color_by, cmap=cmap, **kwargs,
    )


def draw_metatron_cube(
    n=6,
    m=3,
    rotation=0,
    center=(0, 0),
    color="green",
    alpha=1,
    line_width=1,
    label=None,
    name=None,
    showlegend=None,
    color_by=None,
    cmap=None,
    **kwargs,
):
    """绘制类梅塔特隆立方体。"""
    lines = metatron_cube(n=n, m=m, rotation=rotation, center=center)
    return draw_lines(
        lines, color=color, alpha=alpha, line_width=line_width,
        label=label, name=name, showlegend=showlegend,
        color_by=color_by, cmap=cmap, **kwargs,
    )


def draw_krystal_cube(
    n=6,
    m=3,
    rotation=0,
    direction="both",
    center=(0, 0),
    color="#0f0",
    alpha=1,
    line_width=1,
    label=None,
    name=None,
    showlegend=None,
    color_by=None,
    cmap=None,
    **kwargs,
):
    """绘制水晶立方体。"""
    lines = krystal_cube(
        n=n, m=m, rotation=rotation, direction=direction, center=center
    )
    return draw_lines(
        lines, color=color, alpha=alpha, line_width=line_width,
        label=label, name=name, showlegend=showlegend,
        color_by=color_by, cmap=cmap, **kwargs,
    )


def draw_swastika(
    n=3,
    R=1,
    rotation=0,
    color="blue",
    alpha=1,
    line_width=1,
    label=None,
    name=None,
    showlegend=None,
    color_by=None,
    cmap=None,
    **kwargs,
):
    """绘制单个卍字图案。"""
    lines = swastika_lines(n=n, R=R, rotation=rotation)
    return draw_lines(
        lines, color=color, alpha=alpha, line_width=line_width,
        label=label, name=name, showlegend=showlegend,
        color_by=color_by, cmap=cmap, **kwargs,
    )


def draw_swastikas(
    n=3,
    R=1,
    m=4,
    rotation=0,
    color="blue",
    alpha=1,
    line_width=1,
    label=None,
    name=None,
    showlegend=None,
    color_by=None,
    cmap=None,
    **kwargs,
):
    """绘制多个旋转卍字图案。"""
    all_lines = Lines()
    for i in range(m):
        all_lines = all_lines + swastika_lines(
            n=n, R=R, rotation=i * np.pi / m + rotation
        )
    return draw_lines(
        all_lines, color=color, alpha=alpha, line_width=line_width,
        label=label, name=name, showlegend=showlegend,
        color_by=color_by, cmap=cmap, **kwargs,
    )


__all__ = [
    "Lines",
    "connect",
    "connect_all",
    "multi_polygon",
    "metatron_cube",
    "krystal_cube",
    "swastika",
    "swastika_lines",
    "draw_lines",
    "draw_multi_polygon",
    "draw_metatron_cube",
    "draw_krystal_cube",
    "draw_swastika",
    "draw_swastikas",
]

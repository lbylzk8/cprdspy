import warnings
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

from cprdspy.CPR_matplotlib.Dots.dot import Dots, n_dots, n_dots_array, draw_dots

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

    示例:
        # 闭合六边形
        hex_lines = connect(n_dots(6, R=1), closed=True)

        # 不闭合折线
        polyline = connect(n_dots(10, R=2), closed=False)
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

    注意:
        线段数量为 O(N²)，N 较大时可能非常密集。
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

    内部调用 n_dots_array 生成点阵，然后将每一层的点首尾相连。

    参数:
        与 n_dots_array 完全一致，透传所有形状参数。

    返回:
        Lines: 包含所有层多边形的线段容器。

    示例:
        # 双向 3 层六边形
        draw_lines(multi_polygon(6, m=3))

        # 向外椭圆多边形
        draw_lines(multi_polygon(8, m=4, a=2, shape="el", direction="o"))
    """
    dots = n_dots_array(
        n=n,
        m=m,
        R=R,
        a=a,
        b=b,
        p=p,
        q=q,
        rotation=rotation,
        d_rotation=d_rotation,
        shape=shape,
        direction=direction,
        center=center,
    )
    pts = dots.points
    lines = Lines()
    for start in range(0, len(pts), n):
        chunk = Dots(pts[start : start + n])
        lines = lines + connect(chunk, closed=True)
    return lines


def metatron_cube(n=6, m=3, rotation=0, center=(0, 0)):
    """生成类梅塔特隆立方体连线（多层圆上 n 等分点之间全连接）。

    生成 m 层半径分别为 1, 2, ..., m 的圆上 n 等分点，
    然后对所有点做两两全连接。

    参数:
        n (int): 每层点数。
        m (int): 层数，半径为 1, 2, ..., m。
        rotation (float): 初始旋转（弧度），默认为 0。
        center (tuple): 中心坐标，默认为 (0, 0)。

    返回:
        Lines: 包含所有点对之间连线的线段容器。

    注意:
        总点数为 n*m，线段数为 C(n*m, 2)，m 较大时可能非常密集。
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

    内部调用 n_dots_array 生成点阵，然后对所有点做两两全连接。
    类似于 metatron_cube，但使用点阵的缩放半径而非等差半径。

    参数:
        n (int): 每层点数。
        m (int): 层数（direction="both" 时每侧 m 层，共 2*m 层）。
        R (float): 基准半径/大小，逐层按比例缩放。
        a (float): x 半轴系数，透传 n_dots。
        b (float): y 半轴系数，透传 n_dots。
        p (float): 超椭圆 x 指数，透传 n_dots。
        q (float): 超椭圆 y 指数，透传 n_dots。
        rotation (float): 初始旋转（弧度），默认为 0。
        d_rotation (float): 每层附加旋转步长（弧度）。默认 None 时自动使用 π/n。
        shape (str): 形状类型，透传 n_dots_array。支持缩写。
        direction (str): 扩展方向，透传 n_dots_array。
        center (tuple): 中心坐标，默认为 (0, 0)。

    返回:
        Lines: 包含所有点对之间连线的线段容器。

    注意:
        总点数为 n * (direction="both" 时 2*m 否则 m)，线段数为 C(N, 2)。
        m 较大时点数和连线数可能非常密集。

    示例:
        # 基础水晶立方体
        draw_krystal_cube(6, m=3)

        # 椭圆形状
        draw_krystal_cube(8, m=4, a=2, b=1, shape="el", direction="o")
    """
    if d_rotation is None:
        d_rotation = 180 / n
    dots = n_dots_array(
        n=n,
        m=m,
        R=R,
        a=a,
        b=b,
        p=p,
        q=q,
        rotation=rotation,
        d_rotation=d_rotation,
        shape=shape,
        direction=direction,
        center=center,
    )
    return connect_all(dots)


def swastika(n=3, R=1, rotation=0):
    """生成卍字螺旋点。

    点位于螺旋线上：r_i = R·(√2)^i, θ_i = i·π/4 + rotation, i = 0..n-1。

    参数:
        n (int): 点数。
        R (float): 基准半径。
        rotation (float): 初始旋转（弧度），默认为 0。

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

    参数:
        n (int): 螺旋点数。
        R (float): 基准半径。
        rotation (float): 初始旋转（弧度），默认为 0。

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
    """将 color_by 缩写解析为全名，支持前缀匹配。

    示例:
        'i' 'ind' 'index' → 'index'
        'a' 'ang' 'angle' → 'angle'
        'l' 'len' 'length' → 'length'
        'x' → 'x'
        'y' → 'y'
    """
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
    """判断 color 是否是颜色名/色码字符串的列表。

    例如 ['r', '#ff0', 'blue'] → True
         [0.1, 0.5, 0.9]     → False
    """
    if not isinstance(color, (list, np.ndarray)):
        return False
    # 检查第一个元素是否是字符串（如果是数字 0 维 ndarray 的列表，元素可能是标量 ndarray）
    first = color[0]
    if isinstance(first, str):
        return True
    if hasattr(first, "ndim") and first.ndim == 0 and np.issubdtype(first, np.str_):
        return True
    return False


def draw_lines(
    lines,
    color="g",
    alpha=1,
    linewidth=1,
    linestyle="-",
    label=None,
    color_by=None,
    cmap=None,
    ax=None,
    show=True,
    **kwargs,
):
    """绘制线段集合，支持统一颜色、颜色列表和渐变色。

    参数:
        lines (Lines): Lines 对象。
        color: 颜色模式 ——
            - str:             统一颜色，如 "g", "#ff6600"
            - str 列表:         逐段指定颜色，如 ["r","g","b","#ff0"...]
            - 数值列表:          逐段数值，通过 cmap 映射为颜色，如 [0,1,2,3]
        alpha (float): 透明度，默认为 1。
        linewidth (float | array): 线宽，默认为 1。ListCollection 时可为数组。
        linestyle (str): 线型，默认为 "-"。
        label (str): 图例标签。
        color_by (str | None): 自动生成渐变色，按指定维度映射 ——
            "index" "i"    按线段顺序
            "angle" "a"    按线段朝向极角
            "length" "l"   按线段长度
            "x"            按线段中点的 x
            "y"            按线段中点的 y
            设为 None 时不启用（默认）。
        cmap (str | None): colormap 名称，color_by 或数值 color 时生效。默认 "plasma"。
            常用: "viridis" "plasma" "coolwarm" "hsv" "rainbow" "turbo" 等。
        show (bool): 是否调用 plt.show() 直接显示图像，默认为 True。
            Jupyter 中设为 True 可直接输出图而非对象编号。
        ax (matplotlib.axes.Axes): 目标坐标轴，默认为 None。
        **kwargs: 透明传递给 LineCollection 或 ax.plot。

    返回:
        matplotlib.lines.Line2D | LineCollection

    示例:
        # 统一颜色
        draw_lines(connect(dots), color="cyan")

        # 逐段颜色名列表
        draw_lines(multi_polygon(6, m=3), color=["r","g","b","c","m","y"])

        # 按角度渐变
        draw_lines(connect_all(dots), color_by="a", cmap="hsv")

        # 按数值渐变
        draw_lines(lines, color=[0.1, 0.5, 0.9], cmap="coolwarm")
    """
    if ax is None:
        ax = plt.gca()

    segments = lines.segments
    use_gradient = color_by is not None or not _is_uniform_color_line(color)

    if use_gradient:
        segs = [np.column_stack([x, y]) for x, y in segments]

        if color_by is not None:
            # --- color_by 路径：自动计算渐变值 ---
            c_values = _line_color_values(segments, color_by)
            if cmap is None:
                cmap = "plasma"
            lc = LineCollection(
                segs,
                cmap=cmap,
                alpha=alpha,
                linewidths=linewidth,
                linestyles=linestyle,
                label=label,
                **kwargs,
            )
            lc.set_array(c_values)

        elif _is_color_name_list(color):
            # --- 颜色名列表路径：直接指定每段颜色 ---
            lc = LineCollection(
                segs,
                colors=color,
                alpha=alpha,
                linewidths=linewidth,
                linestyles=linestyle,
                label=label,
                **kwargs,
            )

        else:
            # --- 数值列表路径：cmap 映射 ---
            c_values = np.asarray(color)
            if cmap is None:
                cmap = "plasma"
            lc = LineCollection(
                segs,
                cmap=cmap,
                alpha=alpha,
                linewidths=linewidth,
                linestyles=linestyle,
                label=label,
                **kwargs,
            )
            lc.set_array(c_values)

        ax.add_collection(lc)
        ax.autoscale_view()
        ax.set_aspect("equal", adjustable="box")
        if label:
            ax.legend()
        if show:
            plt.show()
        return lc

    else:
        # --- ax.plot 路径（统一颜色） ---
        line_objs = []
        first_label = label
        for x, y in segments:
            obj = ax.plot(
                x,
                y,
                color=color,
                alpha=alpha,
                linewidth=linewidth,
                linestyle=linestyle,
                label=first_label,
                **kwargs,
            )
            line_objs.append(obj[0])
            first_label = None

        ax.set_aspect("equal", adjustable="box")
        if label:
            ax.legend()
        if show:
            plt.show()
        return line_objs


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
    color="g",
    alpha=1,
    linewidth=1,
    linestyle="-",
    label=None,
    color_by=None,
    cmap=None,
    show=True,
    ax=None,
    **kwargs,
):
    """绘制多层多边形，参数与 multi_polygon 一致（额外支持 draw_lines 的样式参数）。"""
    lines = multi_polygon(
        n=n,
        m=m,
        R=R,
        a=a,
        b=b,
        p=p,
        q=q,
        rotation=rotation,
        d_rotation=d_rotation,
        shape=shape,
        direction=direction,
        center=center,
    )
    return draw_lines(
        lines,
        color=color,
        alpha=alpha,
        linewidth=linewidth,
        linestyle=linestyle,
        label=label,
        color_by=color_by,
        cmap=cmap,
        show=show,
        ax=ax,
        **kwargs,
    )


def draw_metatron_cube(
    n=6,
    m=3,
    rotation=0,
    center=(0, 0),
    color="g",
    alpha=1,
    linewidth=1,
    linestyle="-",
    label=None,
    color_by=None,
    cmap=None,
    show=True,
    ax=None,
    **kwargs,
):
    """绘制类梅塔特隆立方体，参数与 metatron_cube 一致（额外支持样式参数）。"""
    lines = metatron_cube(n=n, m=m, rotation=rotation, center=center)
    return draw_lines(
        lines,
        color=color,
        alpha=alpha,
        linewidth=linewidth,
        linestyle=linestyle,
        label=label,
        color_by=color_by,
        cmap=cmap,
        show=show,
        ax=ax,
        **kwargs,
    )


def draw_krystal_cube(
    n=6,
    m=3,
    rotation=0,
    direction="both",
    center=(0, 0),
    color="#0f0",
    alpha=1,
    linewidth=1,
    linestyle="-",
    label=None,
    color_by=None,
    cmap=None,
    show=True,
    ax=None,
    **kwargs,
):
    """绘制水晶立方体，参数与 krystal_cube 一致（额外支持样式参数）。"""
    lines = krystal_cube(
        n=n, m=m, rotation=rotation, direction=direction, center=center
    )
    return draw_lines(
        lines,
        color=color,
        alpha=alpha,
        linewidth=linewidth,
        linestyle=linestyle,
        label=label,
        color_by=color_by,
        cmap=cmap,
        show=show,
        ax=ax,
        **kwargs,
    )


def draw_swastika(
    n=3,
    R=1,
    rotation=0,
    color="b",
    alpha=1,
    linewidth=1,
    linestyle="-",
    label=None,
    color_by=None,
    cmap=None,
    show=True,
    ax=None,
    **kwargs,
):
    """绘制单个卍字图案。

    参数:
        n (int): 螺旋点数。
        R (float): 基准半径。
        rotation (float): 初始旋转（弧度），默认为 0。
        color (str): 线段颜色，默认为 "b"。
        color_by (str | None): 渐变色维度，透传 draw_lines。
        cmap (str | None): colormap，透传 draw_lines。
        其他样式参数同 draw_lines。
    """
    lines = swastika_lines(n=n, R=R, rotation=rotation)
    return draw_lines(
        lines,
        color=color,
        alpha=alpha,
        linewidth=linewidth,
        linestyle=linestyle,
        label=label,
        color_by=color_by,
        cmap=cmap,
        show=show,
        ax=ax,
        **kwargs,
    )


def draw_swastikas(
    n=3,
    R=1,
    m=4,
    rotation=0,
    color="b",
    alpha=1,
    linewidth=1,
    linestyle="-",
    label=None,
    color_by=None,
    cmap=None,
    show=True,
    ax=None,
    **kwargs,
):
    """绘制多个旋转卍字图案。

    参数:
        n (int): 每个卍字的螺旋点数。
        R (float): 基准半径。
        m (int): 卍字个数，均匀分布在 2π 范围内。
        rotation (float): 基准旋转（弧度），默认为 0。
        color_by (str | None): 渐变色维度，透传 draw_lines。
        cmap (str | None): colormap，透传 draw_lines。
        其他样式参数同 draw_swastika。
    """
    all_lines = Lines()
    for i in range(m):
        all_lines = all_lines + swastika_lines(
            n=n, R=R, rotation=i * np.pi / m + rotation
        )
    return draw_lines(
        all_lines,
        color=color,
        alpha=alpha,
        linewidth=linewidth,
        linestyle=linestyle,
        label=label,
        color_by=color_by,
        cmap=cmap,
        show=show,
        ax=ax,
        **kwargs,
    )


# ======================== 向后兼容别名 ========================


def n_points(N, R, theta=0):
    """[已废弃] 请改用 cprdspy.CPR_matplotlib.Dots.dot.n_dots(n=N, R=R, rotation=theta)。

    返回:
        numpy.ndarray
    """
    warnings.warn("n_points 已废弃，请改用 n_dots", DeprecationWarning, stacklevel=2)
    return n_dots(n=N, R=R, rotation=theta).points


def connect_in_order(points, color="g"):
    """[已废弃] 请改用 draw_lines(connect(dots, closed=False), color=color)。"""
    warnings.warn(
        "connect_in_order 已废弃，请改用 connect(dots, closed=False) + draw_lines",
        DeprecationWarning,
        stacklevel=2,
    )
    dots = Dots(np.asarray(points))
    lines = connect(dots, closed=False)
    return draw_lines(lines, color=color)


def connect_with_points(points, colorp="b", colorl="g"):
    """[已废弃] 请分别调用 draw_dots 和 draw_lines。"""
    warnings.warn("connect_with_points 已废弃", DeprecationWarning, stacklevel=2)
    dots = Dots(np.asarray(points))
    draw_dots(dots, color=colorp)
    lines = connect(dots, closed=True)
    return draw_lines(lines, color=colorl)


def connect_all_with_points(points, colorp="b", colorl="g"):
    """[已废弃] 请分别调用 draw_dots 和 draw_lines。"""
    warnings.warn("connect_all_with_points 已废弃", DeprecationWarning, stacklevel=2)
    dots = Dots(np.asarray(points))
    draw_dots(dots, color=colorp)
    lines = connect_all(dots)
    return draw_lines(lines, color=colorl)


def connect_like_metatron(n, m, color="b", theta=0):
    """[已废弃] 请改用 draw_metatron_cube(n=n, m=m, rotation=theta, color=color)。"""
    warnings.warn(
        "connect_like_metatron 已废弃，请改用 draw_metatron_cube",
        DeprecationWarning,
        stacklevel=2,
    )
    return draw_metatron_cube(n=n, m=m, rotation=theta, color=color)


def _old_multi_polygon(n, m, color="b", alpha=0, theta=0):
    """[已废弃] 请改用 draw_multi_polygon(n=n, m=m, rotation=alpha, d_rotation=theta, color=color)。

    注意: 旧版 alpha 参数在旧版中表示初始旋转偏移，新版的 rotation 替代它。
    旧版 theta 在旧版中表示每层旋转步长，新版的 d_rotation 替代它。
    """
    warnings.warn(
        "旧版 multi_polygon 已废弃，请改用 draw_multi_polygon",
        DeprecationWarning,
        stacklevel=2,
    )
    return draw_multi_polygon(n=n, m=m, rotation=alpha, d_rotation=theta, color=color)

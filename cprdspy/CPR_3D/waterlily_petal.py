import numpy as np
import plotly.graph_objects as go

# 全局图对象，用于连续添加椭球
_current_fig = None


def ellipsoid(
    a=1,
    b=1,
    c=1,
    center=(0, 0, 0),
    rotation=None,
    u_res=30,
    v_res=30,
    u_range=(0, 2 * np.pi),
    v_range=(0, np.pi),
    color="rgba(100,150,255,0.7)",
    wireframe=False,
    name="Ellipsoid",
    show_axes=False,
    fig=None,
    auto_add=True,
    **kwargs,
):
    """
    绘制椭球。

    参数：
        a, b, c: 椭球三个方向的半轴长度（默认 1 为球体）
        center: 椭球中心 (x, y, z)
        rotation: 旋转角度 (rx, ry, rz)（欧拉角，度数），None 表示无旋转
        u_res, v_res: 网格分辨率（越大越精细，默认 30）
        u_range: u 参数范围 (u_min, u_max)，默认 (0, 2π) 为完整圆周
        v_range: v 参数范围 (v_min, v_max)，默认 (0, π) 为完整球面
        color: 椭球颜色（支持 rgba、hex、named color）
        wireframe: True 时绘制网格线而非实心
        name: 图例名称
        show_axes: True 时显示坐标轴
        fig: 指定 Figure 对象，None 时使用全局图或创建新的
        auto_add: 如果 True 且 fig=None，自动使用全局图（连续添加）；
                 如果 False，创建新图（默认 True）
        **kwargs: 其他 go.Surface 参数（如 hovertemplate）

    返回：
        fig (go.Figure)

    常用范围示例：
        半球: v_range=(0, np.pi/2)
        四分之一球: u_range=(0, np.pi/2), v_range=(0, np.pi/2)
        球顶部: v_range=(0, np.pi/4)
        半周圆: u_range=(0, np.pi), v_range=(0, np.pi)

    使用示例（连续添加到同一图）:
        fig = start_figure()  # 启动新图
        ellipsoid(a=1, b=1, c=1, color='red', name='Sphere 1')
        ellipsoid(a=2, b=1.5, c=1, center=(3,0,0), color='blue', name='Sphere 2')
        show_figure(fig)  # 显示组合图
    """
    global _current_fig

    # 参数化椭球面
    u = np.linspace(u_range[0], u_range[1], u_res)
    v = np.linspace(v_range[0], v_range[1], v_res)
    u_grid, v_grid = np.meshgrid(u, v)

    # 基础椭球坐标
    x = a * np.cos(u_grid) * np.sin(v_grid)
    y = b * np.sin(u_grid) * np.sin(v_grid)
    z = c * np.cos(v_grid)

    # 旋转处理（欧拉角 Z-Y-X 约定）
    if rotation:
        rx, ry, rz = (
            np.radians(rotation[0]),
            np.radians(rotation[1]),
            np.radians(rotation[2]),
        )
        # 绕 X 轴旋转
        Rx = np.array(
            [[1, 0, 0], [0, np.cos(rx), -np.sin(rx)], [0, np.sin(rx), np.cos(rx)]]
        )
        # 绕 Y 轴旋转
        Ry = np.array(
            [[np.cos(ry), 0, np.sin(ry)], [0, 1, 0], [-np.sin(ry), 0, np.cos(ry)]]
        )
        # 绕 Z 轴旋转
        Rz = np.array(
            [[np.cos(rz), -np.sin(rz), 0], [np.sin(rz), np.cos(rz), 0], [0, 0, 1]]
        )
        R = Rz @ Ry @ Rx  # 组合旋转矩阵

        # 应用旋转（需要展平、旋转、再reshape）
        pts = np.stack([x, y, z], axis=-1)
        shape = pts.shape
        pts_flat = pts.reshape(-1, 3)
        pts_rot = pts_flat @ R.T
        pts_rotated = pts_rot.reshape(shape)
        x, y, z = pts_rotated[..., 0], pts_rotated[..., 1], pts_rotated[..., 2]

    # 平移到中心
    x = x + center[0]
    y = y + center[1]
    z = z + center[2]

    # 确定要使用的 Figure
    if fig is None:
        if auto_add and _current_fig is not None:
            fig = _current_fig  # 使用全局图
        else:
            fig = go.Figure()  # 创建新图

    # 添加 Surface
    if wireframe:
        # 网格模式：只显示线条
        for i in range(v_res):
            fig.add_trace(
                go.Scatter3d(
                    x=x[i],
                    y=y[i],
                    z=z[i],
                    mode="lines",
                    line=dict(color=color, width=1),
                    showlegend=(i == 0),
                    name=name,
                    hoverinfo="skip",
                )
            )
        for j in range(u_res):
            fig.add_trace(
                go.Scatter3d(
                    x=x[:, j],
                    y=y[:, j],
                    z=z[:, j],
                    mode="lines",
                    line=dict(color=color, width=1),
                    showlegend=False,
                    hoverinfo="skip",
                )
            )
    else:
        # 实心模式：使用 color 参数创建均匀颜色
        surface_kwargs = {
            k: v for k, v in kwargs.items() if k not in ["u_range", "v_range"]
        }

        # 创建均匀的 surfacecolor（所有点使用相同颜色）
        surfacecolor = np.ones_like(z)

        fig.add_trace(
            go.Surface(
                x=x,
                y=y,
                z=z,
                surfacecolor=surfacecolor,
                colorscale=[[0, color], [1, color]],
                showscale=False,
                name=name,
                **surface_kwargs,
            )
        )

    # 设置坐标轴
    axis_dict = dict(showgrid=True, zeroline=show_axes)
    fig.update_layout(
        scene=dict(
            xaxis=axis_dict, yaxis=axis_dict, zaxis=axis_dict, aspectmode="data"
        ),
        hovermode="closest",
    )

    return fig


def start_figure(title="Ellipsoids", width=900, height=700):
    """
    启动一个新的全局图，用于连续添加椭球。

    参数：
        title: 图表标题
        width: 图表宽度
        height: 图表高度

    返回：
        fig (go.Figure)

    使用示例：
        fig = start_figure("My Ellipsoids")
        ellipsoid(a=1, name='Red')
        ellipsoid(a=2, center=(3,0,0), name='Blue')
        show_figure(fig)
    """
    global _current_fig
    _current_fig = go.Figure()
    _current_fig.update_layout(
        title=title,
        width=width,
        height=height,
        showlegend=True,
        scene=dict(aspectmode="data"),
    )
    return _current_fig


def show_figure(fig=None):
    """
    显示当前图或指定的图。

    参数：
        fig: 要显示的 Figure，None 时显示全局图
    """
    global _current_fig
    if fig is None:
        fig = _current_fig
    if fig is not None:
        fig.show()
    else:
        print("No figure to show. Use start_figure() first.")


def clear_figure():
    """清空全局图。"""
    global _current_fig
    _current_fig = None


def ellipsoids(*ellipsoid_args, title="Ellipsoids", figsize=(900, 700)):
    """
    一次性绘制多个椭球。

    参数：
        *ellipsoid_args: 可变数量的椭球参数字典，每个字典传给 ellipsoid()
        title: 图标题
        figsize: (width, height)

    示例：
        fig = ellipsoids(
            {'a': 1, 'b': 2, 'c': 0.5, 'color': 'red'},
            {'a': 1.5, 'b': 1, 'c': 2, 'center': (2, 0, 0), 'color': 'blue'}
        )
    """
    fig = go.Figure()
    for args in ellipsoid_args:
        ellipsoid(**args, fig=fig)

    fig.update_layout(title=title, width=figsize[0], height=figsize[1], showlegend=True)
    return fig


# ========== 精确楔形区域（解析边界，光滑区域） ==========
def plane_ellipsoid_intersection(a, b, c, center, plane_normal, plane_d, n_points=800):
    """
    解析求平面与椭球的交线（若存在），返回 (x,y,z) arrays 或 None。
    平面形式： n·(p - center) = plane_d
    """
    n = np.array(plane_normal, dtype=float)
    n = n / np.linalg.norm(n)
    p0 = np.array(center, dtype=float) + n * plane_d

    # basis on plane
    arbitrary = np.array([1.0, 0.0, 0.0])
    if abs(np.dot(arbitrary, n)) > 0.9:
        arbitrary = np.array([0.0, 1.0, 0.0])
    e1 = np.cross(n, arbitrary)
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(n, e1)
    e2 /= np.linalg.norm(e2)

    S = np.diag([1.0 / a**2, 1.0 / b**2, 1.0 / c**2])
    E = np.column_stack([e1, e2])
    M = E.T.dot(S).dot(E)
    l = E.T.dot(S).dot(p0)
    s = p0.dot(S).dot(p0) - 1.0

    # invert M
    try:
        Minv = np.linalg.inv(M)
    except np.linalg.LinAlgError:
        return None

    u0 = -Minv.dot(l)
    cprime = u0.dot(M).dot(u0) - s
    if cprime <= 0:
        return None

    vals, vecs = np.linalg.eigh(M)
    if np.any(vals <= 0):
        return None
    axes_lengths = np.sqrt(cprime / vals)

    t = np.linspace(0, 2 * np.pi, n_points)
    circle = np.vstack([np.cos(t), np.sin(t)])
    uv_local = (vecs @ (axes_lengths[:, None] * circle)) + u0[:, None]
    pts3 = p0[:, None] + E.dot(uv_local)
    x, y, z = pts3[0, :], pts3[1, :], pts3[2, :]
    return x, y, z


def _intervals_for_plane_at_u(a, b, c, center, plane_normal, plane_d, u):
    """
    给定 u，解析求解使得 S*sin v + C*cos v <= D 的 v 区间（v ∈ [0, π])
    返回 list of (v_min, v_max)
    """
    nx, ny, nz = plane_normal
    # compute coefficients
    Scoef = nx * (a * np.cos(u)) + ny * (b * np.sin(u))
    Ccoef = nz * (c)
    D = plane_d

    R = np.hypot(Scoef, Ccoef)
    if R == 0:
        # expression is constant 0; inequality is 0 <= D
        if 0 <= D:
            return [(0.0, np.pi)]
        else:
            return []
    # represent S sin v + C cos v = R * sin(v + phi)
    phi = np.arctan2(Ccoef, Scoef)  # note order
    val = D / R
    if val <= -1.0:
        # sin(...) >= -1 so inequality sin(...) <= val -> always or none
        # if val < -1 then impossible, but due to numerical, handle
        # Check value at mid: v=pi/2 -> sin(pi/2+phi)
        # Simpler: if val < -1 treat as no solution
        return []
    if val >= 1.0:
        # sin(...) <= val where val>=1 -> always true
        return [(0.0, np.pi)]

    # find principal roots r = arcsin(val)
    r = np.arcsin(val)
    # general solutions: v + phi = r + 2kπ or v + phi = π - r + 2kπ
    # find roots within [0, π]
    roots = []
    candidates = [r - phi, (np.pi - r) - phi]
    # normalize into [0, 2π) then pick those in [0, π]
    for cand in candidates:
        t0 = cand
        # bring to principal range
        t0 = (t0 + 2 * np.pi) % (2 * np.pi)
        if 0 <= t0 <= np.pi:
            roots.append(t0)
        # also check subtract 2π
        t1 = t0 - 2 * np.pi
        if 0 <= t1 <= np.pi:
            roots.append(t1)
    roots = np.array(sorted(set(roots)))

    # if no roots inside [0,π], evaluate inequality at a sample to decide if whole domain
    if len(roots) == 0:
        # check mid
        vm = np.pi / 2.0
        if Scoef * np.sin(vm) + Ccoef * np.cos(vm) <= D:
            return [(0.0, np.pi)]
        else:
            return []

    # roots split [0,π] into intervals; determine where inequality holds
    points = np.concatenate(([0.0], roots, [np.pi]))
    intervals = []
    for i in range(len(points) - 1):
        a0, a1 = points[i], points[i + 1]
        vm = 0.5 * (a0 + a1)
        if Scoef * np.sin(vm) + Ccoef * np.cos(vm) <= D:
            intervals.append((a0, a1))
    return intervals


def ellipsoid_wedge_exact(
    a=1,
    b=1,
    c=1,
    center=(0, 0, 0),
    rotation=None,
    plane1_normal=(1, 0, 0),
    plane1_d=0,
    plane2_normal=(0, 1, 0),
    plane2_d=0,
    u_res=200,
    v_samples=60,
    below_xy=False,
    color="rgba(100,150,255,0.8)",
    name="WedgeExact",
    fig=None,
):
    """
    用解析边界构建楔形区域的窄带拼接，保证边界平滑。
    当 below_xy=True 时只保留 z < 0 的部分（XY 平面下）。
    """
    global _current_fig
    if fig is None:
        if _current_fig is not None:
            fig = _current_fig
        else:
            fig = go.Figure()

    # normalize normals
    n1 = np.array(plane1_normal, dtype=float)
    n1 /= np.linalg.norm(n1)
    n2 = np.array(plane2_normal, dtype=float)
    n2 /= np.linalg.norm(n2)

    # sample u
    us = np.linspace(0.0, 2 * np.pi, u_res)

    strips_added = 0
    for i in range(len(us) - 1):
        u0 = us[i]
        u1 = us[i + 1]
        int1_0 = _intervals_for_plane_at_u(a, b, c, center, n1, plane1_d, u0)
        int2_0 = _intervals_for_plane_at_u(a, b, c, center, n2, plane2_d, u0)
        int1_1 = _intervals_for_plane_at_u(a, b, c, center, n1, plane1_d, u1)
        int2_1 = _intervals_for_plane_at_u(a, b, c, center, n2, plane2_d, u1)

        # take intersection of unions; for simplicity, we will sample candidate intervals by
        # taking union of boundary points from both u0 and u1
        cand_vs = []
        for seg in int1_0 + int1_1 + int2_0 + int2_1:
            cand_vs.extend(seg)
        if not cand_vs:
            continue
        cand_vs = np.unique(np.clip(cand_vs, 0.0, np.pi))
        cand_vs = np.concatenate(([0.0], cand_vs, [np.pi]))

        # examine each small v-interval between consecutive candidate points and test if
        # both planes inequalities hold for mid u between u0,u1 and mid v
        for j in range(len(cand_vs) - 1):
            v0, v1 = cand_vs[j], cand_vs[j + 1]
            vm = 0.5 * (v0 + v1)
            um = 0.5 * (u0 + u1)
            # check if mid point satisfies both inequalities
            x_m = a * np.cos(um) * np.sin(vm)
            y_m = b * np.sin(um) * np.sin(vm)
            z_m = c * np.cos(vm)
            px = x_m + center[0]
            py = y_m + center[1]
            pz = z_m + center[2]
            cond1 = (
                np.dot(n1, [px - center[0], py - center[1], pz - center[2]])
                <= plane1_d + 1e-9
            )
            cond2 = (
                np.dot(n2, [px - center[0], py - center[1], pz - center[2]])
                <= plane2_d + 1e-9
            )
            cond3 = (pz < 0) if below_xy else True
            if not (cond1 and cond2 and cond3):
                continue
            # build strip between u0 and u1 for v in [v0,v1]
            v_vals = np.linspace(v0, v1, max(3, v_samples))
            # compute columns
            x_col0 = a * np.cos(u0) * np.sin(v_vals) + center[0]
            y_col0 = b * np.sin(u0) * np.sin(v_vals) + center[1]
            z_col0 = c * np.cos(v_vals) + center[2]
            x_col1 = a * np.cos(u1) * np.sin(v_vals) + center[0]
            y_col1 = b * np.sin(u1) * np.sin(v_vals) + center[1]
            z_col1 = c * np.cos(v_vals) + center[2]

            X = np.column_stack([x_col0, x_col1])
            Y = np.column_stack([y_col0, y_col1])
            Z = np.column_stack([z_col0, z_col1])

            fig.add_trace(
                go.Surface(
                    x=X,
                    y=Y,
                    z=Z,
                    surfacecolor=np.ones_like(Z),
                    colorscale=[[0, color], [1, color]],
                    showscale=False,
                    name=name,
                    hoverinfo="skip",
                    cmin=0,
                    cmax=1,
                )
            )
            strips_added += 1

    # 补画两条边界曲线（高分辨率）以增强平滑感
    xb1, yb1, zb1 = plane_ellipsoid_intersection(
        a, b, c, center, n1, plane1_d, n_points=1200
    ) or (None, None, None)
    xb2, yb2, zb2 = plane_ellipsoid_intersection(
        a, b, c, center, n2, plane2_d, n_points=1200
    ) or (None, None, None)
    if xb1 is not None:
        # 只保留满足另一个平面限制和 below_xy 条件的点
        mask = (
            np.dot(np.vstack([xb1 - center[0], yb1 - center[1], zb1 - center[2]]).T, n2)
            <= plane2_d + 1e-9
        )
        if below_xy:
            mask &= zb1 < 0
        fig.add_trace(
            go.Scatter3d(
                x=xb1[mask],
                y=yb1[mask],
                z=zb1[mask],
                mode="lines",
                line=dict(
                    color=(
                        color.replace("0.8", "1.0") if isinstance(color, str) else color
                    ),
                    width=6,
                ),
                name=name + "_edge1",
            )
        )
    if xb2 is not None:
        mask = (
            np.dot(np.vstack([xb2 - center[0], yb2 - center[1], zb2 - center[2]]).T, n1)
            <= plane1_d + 1e-9
        )
        if below_xy:
            mask &= zb2 < 0
        fig.add_trace(
            go.Scatter3d(
                x=xb2[mask],
                y=yb2[mask],
                z=zb2[mask],
                mode="lines",
                line=dict(
                    color=(
                        color.replace("0.8", "1.0") if isinstance(color, str) else color
                    ),
                    width=6,
                ),
                name=name + "_edge2",
            )
        )

    fig.update_layout(scene=dict(aspectmode="data"))
    return fig


# ========== 在当前 notebook 中演示（针对用户参数） ==========
print("绘制解析楔形区域（z<0）示例： a=4,b=1,c=1，过焦点，和 Y 轴向下夹角30°的两平面")

# 参数
A, B, C = 4, 1, 1
c_dist = np.sqrt(A**2 - B**2)
focal_pt = (c_dist, 0, 0)
angle = np.radians(30)
plane_ny = np.cos(angle)
plane_nz = np.sin(angle)
plane1_n = (0, plane_ny, -plane_nz)
plane2_n = (0, plane_ny, plane_nz)

fig_exact = start_figure("Exact Focal Wedge (z<0)", width=1000, height=800)
# 参考半透明椭球
ellipsoid(
    a=A,
    b=B,
    c=C,
    center=(0, 0, 0),
    color="rgba(200,200,200,0.07)",
    u_res=80,
    v_res=80,
    fig=fig_exact,
)
# 精确楔形（仅 z<0）
ellipsoid_wedge_exact(
    a=A,
    b=B,
    c=C,
    center=(0, 0, 0),
    plane1_normal=plane1_n,
    plane1_d=0,
    plane2_normal=plane2_n,
    plane2_d=0,
    u_res=300,
    v_samples=80,
    below_xy=True,
    color="rgba(255,100,100,0.8)",
    name="ExactWedge",
    fig=fig_exact,
)
# 标注焦点
fig_exact.add_trace(
    go.Scatter3d(
        x=[focal_pt[0]],
        y=[0],
        z=[0],
        mode="markers+text",
        marker=dict(size=6, color="red"),
        text=["F"],
        textposition="top center",
    )
)
show_figure(fig_exact)
print("完成：已在 notebook 中绘制解析楔形区域（z<0）。")

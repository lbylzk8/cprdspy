"""
Ellipsoid plotting using Plotly.
支持完全可定制的椭球绘制（3 种半轴、旋转、位置、颜色、透明度、网格密度等）。
"""

import numpy as np
import plotly.graph_objects as go


def ellipsoid(
    a=1,
    b=1,
    c=1,
    center=(0, 0, 0),
    rotation=None,
    u_res=30,
    v_res=30,
    color="rgba(100,150,255,0.7)",
    wireframe=False,
    name="Ellipsoid",
    show_axes=False,
    fig=None,
    **kwargs,
):
    """
    绘制椭球。

    参数：
        a, b, c: 椭球三个方向的半轴长度（默认 1 为球体）
        center: 椭球中心 (x, y, z)
        rotation: 旋转角度 (rx, ry, rz)（欧拉角，度数），None 表示无旋转
        u_res, v_res: 网格分辨率（越大越精细，默认 30）
        color: 椭球颜色（支持 rgba、hex、named color）
        wireframe: True 时绘制网格线而非实心
        name: 图例名称
        show_axes: True 时显示坐标轴
        fig: 已有的 Plotly Figure，None 时创建新的
        **kwargs: 其他 go.Surface 参数（如 hovertemplate）

    返回：
        fig (go.Figure)
    """
    # 参数化椭球面
    u = np.linspace(0, 2 * np.pi, u_res)
    v = np.linspace(0, np.pi, v_res)
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

    # 创建或获取 Figure
    if fig is None:
        fig = go.Figure()

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
        # 实心模式
        fig.add_trace(
            go.Surface(
                x=x,
                y=y,
                z=z,
                surfacecolor=z,
                colorscale="Viridis",
                showscale=False,
                name=name,
                **kwargs,
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


if __name__ == "__main__":
    # 示例 1：基础球体
    fig1 = ellipsoid(name="Sphere")
    fig1.show()

    # 示例 2：椭球
    fig2 = ellipsoid(a=2, b=1.5, c=0.8, name="Ellipsoid")
    fig2.show()

    # 示例 3：多个椭球
    fig3 = ellipsoids(
        {"a": 1, "b": 1, "c": 1, "color": "rgba(255,0,0,0.6)"},
        {"a": 1.5, "b": 1, "c": 2, "center": (3, 0, 0), "color": "rgba(0,255,0,0.6)"},
        {
            "a": 0.8,
            "b": 0.8,
            "c": 1.2,
            "rotation": (45, 30, 60),
            "center": (1.5, 1.5, 0),
            "color": "rgba(0,0,255,0.6)",
        },
    )
    fig3.show()

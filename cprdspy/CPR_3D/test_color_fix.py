# 颜色修复测试 - 可以直接在新的 Jupyter 单元格中运行

import numpy as np
import plotly.graph_objects as go


# 复制修复后的 ellipsoid 函数
def ellipsoid_fixed(
    a=1,
    b=1,
    c=1,
    center=(0, 0, 0),
    rotation=None,
    affine_matrix=None,
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
    # 参数化椭球面
    u = np.linspace(u_range[0], u_range[1], u_res)
    v = np.linspace(v_range[0], v_range[1], v_res)
    u_grid, v_grid = np.meshgrid(u, v)

    # 基础椭球坐标
    x = a * np.cos(u_grid) * np.sin(v_grid)
    y = b * np.sin(u_grid) * np.sin(v_grid)
    z = c * np.cos(v_grid)

    # 旋转/仿射处理
    pts = np.stack([x, y, z], axis=-1)
    shape = pts.shape
    pts_flat = pts.reshape(-1, 3)

    if affine_matrix is not None:
        A = np.asarray(affine_matrix)
        if A.shape == (3, 3):
            A4 = np.eye(4)
            A4[:3, :3] = A
            A = A4
        if A.shape == (3, 4):
            A4 = np.eye(4)
            A4[:3, :4] = A
            A = A4
        if A.shape != (4, 4):
            raise ValueError("affine_matrix must be shape (4,4), (3,3) or (3,4)")

        ones = np.ones((pts_flat.shape[0], 1))
        pts_h = np.concatenate([pts_flat, ones], axis=1)
        pts_trans = pts_h @ A.T
        pts_trans_reshaped = pts_trans[:, :3].reshape(shape)
        x, y, z = (
            pts_trans_reshaped[..., 0],
            pts_trans_reshaped[..., 1],
            pts_trans_reshaped[..., 2],
        )
    else:
        if rotation:
            rx, ry, rz = (
                np.radians(rotation[0]),
                np.radians(rotation[1]),
                np.radians(rotation[2]),
            )
            Rx = np.array(
                [[1, 0, 0], [0, np.cos(rx), -np.sin(rx)], [0, np.sin(rx), np.cos(rx)]]
            )
            Ry = np.array(
                [[np.cos(ry), 0, np.sin(ry)], [0, 1, 0], [-np.sin(ry), 0, np.cos(ry)]]
            )
            Rz = np.array(
                [[np.cos(rz), -np.sin(rz), 0], [np.sin(rz), np.cos(rz), 0], [0, 0, 1]]
            )
            R = Rz @ Ry @ Rx
            pts_rot = pts_flat @ R.T
            pts_rotated = pts_rot.reshape(shape)
            x, y, z = pts_rotated[..., 0], pts_rotated[..., 1], pts_rotated[..., 2]

        x = x + center[0]
        y = y + center[1]
        z = z + center[2]

    if fig is None:
        fig = go.Figure()

    if wireframe:
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
        # 修复颜色显示问题 - 关键修改在这里
        surface_kwargs = {
            k: v for k, v in kwargs.items() if k not in ["u_range", "v_range"]
        }

        fig.add_trace(
            go.Surface(
                x=x,
                y=y,
                z=z,
                colorscale=[[0, color], [1, color]],  # 使用单一颜色
                showscale=False,
                name=name,
                cmin=0,  # 设置颜色范围
                cmax=1,  # 设置颜色范围
                **surface_kwargs,
            )
        )

    axis_dict = dict(showgrid=True, zeroline=show_axes)
    fig.update_layout(
        scene=dict(
            xaxis=axis_dict, yaxis=axis_dict, zaxis=axis_dict, aspectmode="data"
        ),
        hovermode="closest",
    )
    return fig


# 测试1：你原来的红色椭球
print("测试1：红色椭球（你原来的参数）")
fig1 = ellipsoid_fixed(
    a=4,
    b=1,
    c=1,
    u_range=(0, np.pi),
    v_range=(0, np.pi / 2),
    affine_matrix=np.diag([-1.0, 1.0, -1.0, 1.0]),
    color="rgba(255,0,0,0.7)",
    name="红色椭球",
)
fig1.show()

# 测试2：多个不同颜色的椭球
print("测试2：多个不同颜色的椭球")
fig2 = go.Figure()

ellipsoid_fixed(
    a=2, b=2, c=2, center=(0, 0, 0), color="rgba(255,0,0,0.7)", name="红色", fig=fig2
)
ellipsoid_fixed(
    a=2, b=2, c=2, center=(5, 0, 0), color="rgba(0,255,0,0.7)", name="绿色", fig=fig2
)
ellipsoid_fixed(
    a=2, b=2, c=2, center=(10, 0, 0), color="rgba(0,0,255,0.7)", name="蓝色", fig=fig2
)

fig2.update_layout(title="颜色测试", width=900, height=700, showlegend=True)
fig2.show()

print("测试完成！现在颜色应该正确显示了。")

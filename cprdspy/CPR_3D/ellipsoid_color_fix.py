import numpy as np
import plotly.graph_objects as go

# 全局图对象，用于连续添加椭球
_current_fig = None


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
    """
    绘制椭球（修复颜色版本）。

    参数：
        a, b, c: 椭球三个方向的半轴长度（默认 1 为球体）
        center: 椭球中心 (x, y, z)
        rotation: 旋转角度 (rx, ry, rz)（欧拉角，度数），None 表示无旋转
        affine_matrix: 可选 4x4 齐次仿射矩阵，优先于 rotation/center
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

    # 旋转/仿射处理
    pts = np.stack([x, y, z], axis=-1)
    shape = pts.shape
    pts_flat = pts.reshape(-1, 3)

    if affine_matrix is not None:
        # 期望 affine_matrix 为 4x4 齐次矩阵
        A = np.asarray(affine_matrix)
        if A.shape == (3, 3):
            # 仅线性部分 -> 转为 4x4（无平移）
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
        pts_h = np.concatenate([pts_flat, ones], axis=1)  # (N,4)
        pts_trans = pts_h @ A.T
        pts_trans_reshaped = pts_trans[:, :3].reshape(shape)
        x, y, z = (
            pts_trans_reshaped[..., 0],
            pts_trans_reshaped[..., 1],
            pts_trans_reshaped[..., 2],
        )
    else:
        # 仍然支持按欧拉角旋转并平移到 center（原行为）
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
        # 实心模式：修复颜色显示问题
        surface_kwargs = {
            k: v for k, v in kwargs.items() if k not in ["u_range", "v_range"]
        }

        # 方法1：直接使用 colorscale（推荐）
        fig.add_trace(
            go.Surface(
                x=x,
                y=y,
                z=z,
                colorscale=[[0, color], [1, color]],  # 使用单一颜色
                showscale=False,
                name=name,
                cmin=0,
                cmax=1,
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


# 测试颜色修复
def test_colors():
    """测试不同颜色的椭球"""
    fig = start_figure("颜色测试")
    
    # 测试红色
    ellipsoid_fixed(
        a=2, b=2, c=2, 
        center=(0, 0, 0), 
        color="rgba(255,0,0,0.7)", 
        name="红色"
    )
    
    # 测试绿色
    ellipsoid_fixed(
        a=2, b=2, c=2, 
        center=(5, 0, 0), 
        color="rgba(0,255,0,0.7)", 
        name="绿色"
    )
    
    # 测试蓝色
    ellipsoid_fixed(
        a=2, b=2, c=2, 
        center=(10, 0, 0), 
        color="rgba(0,0,255,0.7)", 
        name="蓝色"
    )
    
    # 测试黄色
    ellipsoid_fixed(
        a=2, b=2, c=2, 
        center=(15, 0, 0), 
        color="rgba(255,255,0,0.7)", 
        name="黄色"
    )
    
    show_figure(fig)


# 单独测试一个红色椭球（使用你原来的参数）
def test_red_ellipsoid():
    """测试红色椭球（使用你原来的参数）"""
    fig = ellipsoid_fixed(
        a=4,
        b=1,
        c=1,
        u_range=(0, np.pi),
        v_range=(0, np.pi / 2),
        affine_matrix=np.diag([-1.0, 1.0, -1.0, 1.0]),
        auto_add=True,
        color="rgba(255,0,0,0.7)",
    )
    fig.show()


if __name__ == "__main__":
    # 运行测试
    print("测试颜色修复...")
    test_colors()
    print("红色椭球测试...")
    test_red_ellipsoid()
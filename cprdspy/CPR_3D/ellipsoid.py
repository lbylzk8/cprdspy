import numpy as np
import plotly.graph_objects as go
from typing import Optional, Tuple, Dict

# 全局图对象，用于连续添加椭球（交互式会话中可复用）
_current_fig: Optional[go.Figure] = None

# 简单网格缓存，避免在短时间内多次生成相同参数的网格
_grid_cache: Dict[
    Tuple[int, int, float, float, float, float], Tuple[np.ndarray, np.ndarray]
] = {}


def _ensure_affine4(A: np.ndarray) -> np.ndarray:
    """
    确保并返回一个 4x4 的齐次仿射矩阵。
    支持输入形状 (3,3)、(3,4) 或 (4,4)。返回 dtype=float 的 4x4 矩阵。
    """
    A = np.asarray(A, dtype=float)
    if A.shape == (3, 3):
        A4 = np.eye(4, dtype=float)
        A4[:3, :3] = A
        return A4
    if A.shape == (3, 4):
        A4 = np.eye(4, dtype=float)
        A4[:3, :4] = A
        return A4
    if A.shape == (4, 4):
        return A
    raise ValueError("affine_matrix must be shape (4,4), (3,3) or (3,4)")


def _euler_to_rotation(rx: float, ry: float, rz: float) -> np.ndarray:
    """
    将欧拉角（度）转换为 3x3 旋转矩阵，顺序为 Rx->Ry->Rz（先绕 X 再 Y 再 Z）。
    返回 3x3 numpy 矩阵。
    """
    rx, ry, rz = np.radians([rx, ry, rz])
    Rx = np.array(
        [[1, 0, 0], [0, np.cos(rx), -np.sin(rx)], [0, np.sin(rx), np.cos(rx)]],
        dtype=float,
    )
    Ry = np.array(
        [[np.cos(ry), 0, np.sin(ry)], [0, 1, 0], [-np.sin(ry), 0, np.cos(ry)]],
        dtype=float,
    )
    Rz = np.array(
        [[np.cos(rz), -np.sin(rz), 0], [np.sin(rz), np.cos(rz), 0], [0, 0, 1]],
        dtype=float,
    )
    return Rz @ Ry @ Rx


def _get_uv_grid(
    u_res: int, v_res: int, u_range: Tuple[float, float], v_range: Tuple[float, float]
):
    """
    从缓存中获取或创建 u, v 网格（用于减少重复生成）。
    key 使用分辨率与范围保证唯一性。
    返回 (u_grid, v_grid)
    """
    key = (
        u_res,
        v_res,
        float(u_range[0]),
        float(u_range[1]),
        float(v_range[0]),
        float(v_range[1]),
    )
    if key in _grid_cache:
        return _grid_cache[key]
    u = np.linspace(u_range[0], u_range[1], u_res)
    v = np.linspace(v_range[0], v_range[1], v_res)
    u_grid, v_grid = np.meshgrid(u, v)
    _grid_cache[key] = (u_grid, v_grid)
    return u_grid, v_grid


def ellipsoid(
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
    绘制椭球。

    参数：
        a, b, c: 椭球三个方向的半轴长度（默认 1 为球体）
        center: 椭球中心 (x, y, z)
        rotation: 旋转角度 (rx, ry, rz)（欧拉角，度数），None 表示无旋转
        affine_matrix: 可选 4x4 齐次仿射矩阵，优先于 rotation/center
        u_res, v_res: 网格分辨率（越大越精细，默认 30）
        u_range: u 参数范围 (u_min, u_max)，默认 (0, 2π) 为完整圆周
        v_range: v 参数范围 (v_min, v_max)，默认 (0, π) 为完整球面
        color: 椭球颜色（支持 rgba、hex、named color）
        wireframe: False 时绘制网格线而非实心
        name: 图例名称
        show_axes: False 时显示坐标轴
        fig: 指定 Figure 对象，None 时使用全局图或创建新的
        auto_add: 如果 True 且 fig=None，自动使用全局图（连续添加）；
                 如果 False，创建新图（默认 True）
        **kwargs: 其他 go.Surface 参数（如 hovertemplate）

    返回：
        fig (go.Figure)
    """
    global _current_fig

    # ---- 输入校验（早报错） ----
    try:
        a = float(a)
        b = float(b)
        c = float(c)
    except Exception:
        raise TypeError("a,b,c must be numbers")
    if a <= 0 or b <= 0 or c <= 0:
        raise ValueError("a, b, c must be positive")
    if u_res < 2 or v_res < 2:
        raise ValueError("u_res and v_res must be >= 2")

    # 使用缓存的网格生成函数，避免重复分配
    u_grid, v_grid = _get_uv_grid(u_res, v_res, u_range, v_range)

    # 计算基础椭球坐标（dtype float）
    x = (a * np.cos(u_grid) * np.sin(v_grid)).astype(float)
    y = (b * np.sin(u_grid) * np.sin(v_grid)).astype(float)
    z = (c * np.cos(v_grid)).astype(float)

    # 旋转或仿射变换处理：优先使用 affine_matrix
    if affine_matrix is not None:
        A4 = _ensure_affine4(affine_matrix)
        # 使用 ravel + column_stack 减少中间大数组分配
        pts_h = np.column_stack(
            [x.ravel(), y.ravel(), z.ravel(), np.ones(x.size, dtype=float)]
        )
        pts_trans = pts_h @ A4.T
        x = pts_trans[:, 0].reshape(x.shape)
        y = pts_trans[:, 1].reshape(x.shape)
        z = pts_trans[:, 2].reshape(x.shape)
    else:
        # 使用欧拉角旋转（如果提供），并且最后再平移 center
        if rotation is not None:
            R = _euler_to_rotation(rotation[0], rotation[1], rotation[2])
            pts_flat = np.column_stack([x.ravel(), y.ravel(), z.ravel()])
            pts_rot = pts_flat @ R.T
            x = pts_rot[:, 0].reshape(x.shape)
            y = pts_rot[:, 1].reshape(x.shape)
            z = pts_rot[:, 2].reshape(x.shape)

        # 平移到中心（保留原来行为）
        x = x + float(center[0])
        y = y + float(center[1])
        z = z + float(center[2])

    # 确定要使用的 Figure
    if fig is None:
        if auto_add and _current_fig is not None:
            fig = _current_fig  # 使用全局图
        else:
            fig = go.Figure()  # 创建新图

    # 添加 Surface 或线框
    # Plotly 渲染：对于实心面使用 colorscale 或 surfacecolor，确保 cmin/cmax 明确
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
        # 实心模式：将用户 kwargs 传递给 Surface，使用 colorscale 或 surfacecolor
        surface_kwargs = {
            k: v for k, v in kwargs.items() if k not in ["u_range", "v_range"]
        }

        # 如果用户传入 surfacecolor，就直接使用；否则用统一 colorscale 保持单色外观
        if "surfacecolor" in surface_kwargs:
            sc = surface_kwargs.pop("surfacecolor")
            fig.add_trace(
                go.Surface(
                    x=x,
                    y=y,
                    z=z,
                    surfacecolor=sc,
                    showscale=False,
                    name=name,
                    cmin=0,
                    cmax=1,
                    **surface_kwargs,
                )
            )
        else:
            fig.add_trace(
                go.Surface(
                    x=x,
                    y=y,
                    z=z,
                    colorscale=[[0, color], [1, color]],  # 固定单色显示
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

    # # 测试颜色修复
    # def test_colors():
    #     """测试不同颜色的椭球"""
    #     fig = start_figure("颜色测试", 1200, 900)
    #     matrix1 = np.eye(4)
    #     matrix1[2, 3] = -2
    #     matrix2 = np.eye(4)
    #     matrix2[0, 0] = -1.0
    #     matrix2[2, 2] = -1.0
    #     matrix2[2, 3] = -0.6
    #     # 测试红色
    #     ellipsoid(
    #         a=4,
    #         b=1,
    #         c=1,
    #         center=(0, 0, 0),
    #         u_range=(0, np.pi),
    #         v_range=(0, np.pi / 2 / 2),
    #         color="rgba(255,0,0,0.7)",
    #         affine_matrix=matrix1,
    #         name="红色",
    #     )

    #     # 测试绿色
    #     ellipsoid(
    #         a=4,
    #         b=1,
    #         c=1,
    #         center=(0, 0, 0),
    #         u_range=(0, np.pi),
    #         v_range=(0, np.pi / 2 / 2),
    #         affine_matrix=matrix2,
    #         color="rgba(0,255,0,0.7)",
    #         name="绿色",
    #     )

    #     # 测试蓝色
    #     # ellipsoid(
    #     #     a=2, b=2, c=2, center=(10, 0, 0), color="rgba(0,0,255,0.7)", name="蓝色"
    #     # )

    #     # # 测试黄色
    #     # ellipsoid(
    #     #     a=2, b=2, c=2, center=(15, 0, 0), color="rgba(255,255,0,0.7)", name="黄色"
    #     # )

    #     show_figure(fig)

    # # 单独测试一个红色椭球（使用你原来的参数）
    # def test_red_ellipsoid():
    #     """测试红色椭球（使用你原来的参数）"""
    #     fig = ellipsoid(
    #         a=4,
    #         b=1,
    #         c=1,
    #         u_range=(0, np.pi),
    #         v_range=(0, np.pi / 2),
    #         affine_matrix=np.diag([-1.0, 1.0, -1.0, 1.0]),
    #         auto_add=True,
    #         color="rgba(255,0,0,0.7)",
    #     )
    #     fig.show()

    # if __name__ == "__main__":
    # 示例：直接运行此文件会展示几个示例图（在浏览器中打开以保证可视化）


if __name__ == "__main__":
    try:
        # 简单默认椭球
        print("示例1：默认椭球")
        fig = ellipsoid(
            a=3,
            b=1.5,
            c=1.0,
            u_res=40,
            v_res=40,
            color="rgba(100,150,255,0.7)",
            auto_add=False,
        )
        try:
            fig.show(renderer="browser")
        except Exception:
            fig.show()

        # 仿射平移与镜像示例
        print("示例2：仿射平移与镜像")
        A = np.diag([-1.0, 1.0, 1.0, 1.0])
        A[:3, 3] = np.array([3.0, 0.0, 0.0])
        fig2 = ellipsoid(
            a=1.2,
            b=0.8,
            c=1.0,
            affine_matrix=A,
            color="rgba(200,120,180,0.7)",
            auto_add=False,
        )
        try:
            fig2.show(renderer="browser")
        except Exception:
            fig2.show()

        # 旋转 + 部分曲面示例（只显示上半球）
        print("示例3：旋转 + 部分曲面")
        fig3 = ellipsoid(
            a=2.0,
            b=1.0,
            c=1.0,
            rotation=(30, 45, 0),
            u_range=(0, np.pi),
            v_range=(0, np.pi / 2),
            color="rgba(255,100,100,0.7)",
            auto_add=False,
        )
        try:
            fig3.show(renderer="browser")
        except Exception:
            fig3.show()

        print("示例运行完毕，请在浏览器中查看生成的图形窗口。")
    except Exception as exc:
        print("运行示例时出错：", exc)

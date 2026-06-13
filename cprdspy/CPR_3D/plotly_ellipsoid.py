# Plotly 脚本：基于参数化生成椭球并支持仿射变换
# 使用方法：在支持 Python 环境中运行（需要 plotly 和 numpy）
# 功能：创建椭球（可部分），应用仿射矩阵 / 欧拉角旋转 / 平移，显示 3D 图形

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math

# 缓存 u/v 网格以复用，键为 (u_res,v_res,u0,u1,v0,v1)
_UV_GRID_CACHE = {}


def _get_uv_grid(u_res, v_res, u_range, v_range, cache_uv=True):
    """返回 (u_grid, v_grid)。返回 numpy arrays。"""
    try:
        u_res = int(u_res)
    except Exception:
        u_res = int(float(u_res))
    try:
        v_res = int(v_res)
    except Exception:
        v_res = int(float(v_res))
    if u_res < 2 or v_res < 2:
        raise ValueError("u_res and v_res must be >= 2")
    
    u0, u1 = float(u_range[0]), float(u_range[1])
    v0, v1 = float(v_range[0]), float(v_range[1])
    key = (u_res, v_res, u0, u1, v0, v1)
    if cache_uv and key in _UV_GRID_CACHE:
        return _UV_GRID_CACHE[key]
    
    u = np.linspace(u0, u1, u_res)
    v = np.linspace(v0, v1, v_res)
    u_grid, v_grid = np.meshgrid(u, v)
    
    if cache_uv:
        _UV_GRID_CACHE[key] = (u_grid, v_grid)
    return u_grid, v_grid


def _euler_to_rotation_matrix(rotation_euler_deg):
    """
    将欧拉角转换为旋转矩阵
    参数: rotation_euler_deg = (rx, ry, rz) - 欧拉角 (度)
    返回: 3x3 rotation Matrix
    """
    rx, ry, rz = np.radians(rotation_euler_deg)
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(rx), -np.sin(rx)],
        [0, np.sin(rx), np.cos(rx)]
    ], dtype=float)
    Ry = np.array([
        [np.cos(ry), 0, np.sin(ry)],
        [0, 1, 0],
        [-np.sin(ry), 0, np.cos(ry)]
    ], dtype=float)
    Rz = np.array([
        [np.cos(rz), -np.sin(rz), 0],
        [np.sin(rz), np.cos(rz), 0],
        [0, 0, 1]
    ], dtype=float)
    return Rz @ Ry @ Rx


def _quaternion_to_rotation_matrix(q):
    """
    将四元数转换为3x3旋转矩阵
    参数: q = [w, x, y, z] - 四元数 (w是标量部分, [x, y, z]是向量部分)
    返回: 3x3 rotation Matrix
    """
    w, x, y, z = q
    # 标准化四元数
    norm = math.sqrt(w * w + x * x + y * y + z * z)
    if norm == 0:
        return np.eye(3)
    w, x, y, z = w / norm, x / norm, y / norm, z / norm

    # 计算旋转矩阵
    R = np.zeros((3, 3))
    R[0][0] = 1 - 2 * (y * y + z * z)
    R[0][1] = 2 * (x * y - w * z)
    R[0][2] = 2 * (x * z + w * y)
    R[1][0] = 2 * (x * y + w * z)
    R[1][1] = 1 - 2 * (x * x + z * z)
    R[1][2] = 2 * (y * z - w * x)
    R[2][0] = 2 * (x * z - w * y)
    R[2][1] = 2 * (y * z + w * x)
    R[2][2] = 1 - 2 * (x * x + y * y)
    return R


def _axis_angle_to_quaternion(axis, angle):
    """
    将轴角表示转换为四元数
    参数: axis - 旋转轴向量
          angle - 旋转角度（弧度）
    返回: [w, x, y, z] 四元数
    """
    axis = np.array(axis)
    axis = axis / np.linalg.norm(axis)
    half_angle = angle / 2
    sin_half = math.sin(half_angle)
    cos_half = math.cos(half_angle)
    return [cos_half, axis[0] * sin_half, axis[1] * sin_half, axis[2] * sin_half]


def create_parametric_ellipsoid_plotly(
    a=1.0,
    b=1.0,
    c=1.0,
    u_res=32,
    v_res=32,
    u_range=(0.0, 2 * math.pi),
    v_range=(0.0, math.pi),
    color='lightblue',
    opacity=0.8,
    affine_matrix=None,  # 4x4 numpy array or nested list
    rotation_euler_deg=None,  # tuple (rx, ry, rz) degrees, used if affine_matrix is None
    quaternion=None,  # list [w, x, y, z], used if affine_matrix and rotation_euler_deg are None
    axis_angle=None,  # tuple (axis, angle_deg), used if higher priority params are None
    location=(0.0, 0.0, 0.0),
    keep_y_positive=False,  # 如果 True，仅保留变换后 y >= 0 的顶点/面
    name="Ellipsoid",
    show_wireframe=False,
    wireframe_color='black'
):
    """
    使用 Plotly 创建一个参数化椭球网格可视化.

    参数说明：
      a,b,c: 椭球在 x,y,z 方向的半轴长度
      u_res,v_res: 网格分辨率（u 列数, v 行数）
      u_range,v_range: 参数范围
      color: 表面颜色
      opacity: 透明度
      affine_matrix: 若提供，会作为 4x4 齐次矩阵直接应用到顶点上（优先级最高）
      rotation_euler_deg: 如果未提供仿射矩阵，可通过欧拉角旋转（度），随后平移 location
      quaternion: 如果未提供仿射矩阵和欧拉角，可通过四元数旋转（[w, x, y, z]），随后平移 location
      axis_angle: 如果未提供仿射矩阵、欧拉角和四元数，可通过轴角旋转（(axis, angle_deg)），随后平移 location
      location: 平移向量（仅在未提供 affine_matrix 时生效）
      keep_y_positive: True 则剔除变换后 y < 0 的顶点/面（适合取 Y 正半部分）
      name: 轨迹名称
      show_wireframe: 是否显示线框
      wireframe_color: 线框颜色
    """

    # 生成 u/v 网格（可能从缓存中读取）
    u_grid, v_grid = _get_uv_grid(u_res, v_res, u_range, v_range)
    
    sv = np.sin(v_grid)
    cv = np.cos(v_grid)
    cu = np.cos(u_grid)
    su = np.sin(u_grid)
    
    x = a * cu * sv
    y = b * su * sv
    z = c * cv
    
    # 将网格展平为 (N,3) 便于仿射矩阵或旋转统一处理
    pts = np.column_stack([x.ravel(), y.ravel(), z.ravel()])  # shape (N,3)
    
    # 处理仿射矩阵或欧拉旋转 + 平移
    if affine_matrix is not None:
        # 支持 numpy 数组或可被转换为 numpy 的嵌套列表
        A = np.asarray(affine_matrix, dtype=float)
        if A.shape == (3, 3):
            A4 = np.eye(4, dtype=float)
            A4[:3, :3] = A
        elif A.shape == (3, 4):
            A4 = np.eye(4, dtype=float)
            A4[:3, :4] = A
        elif A.shape == (4, 4):
            A4 = A
        else:
            raise ValueError("affine_matrix must be shape (4,4), (3,3) or (3,4)")

        # 如果提供了旋转参数，先应用旋转
        if rotation_euler_deg is not None:
            R = _euler_to_rotation_matrix(rotation_euler_deg)
            pts = pts @ R.T
        # 如果提供四元数，转换为旋转矩阵并应用
        elif quaternion is not None:
            R = _quaternion_to_rotation_matrix(quaternion)
            pts = pts @ R.T
        # 如果提供轴角，先转换为四元数，再转换为旋转矩阵并应用
        elif axis_angle is not None:
            axis, angle_deg = axis_angle
            q = _axis_angle_to_quaternion(axis, math.radians(angle_deg))
            R = _quaternion_to_rotation_matrix(q)
            pts = pts @ R.T

        # 然后应用仿射变换
        pts_h = np.hstack([pts, np.ones((pts.shape[0], 1), dtype=float)])  # (N,4)
        pts_t = (pts_h @ A4.T)[:, :3]
    else:
        pts_t = pts.copy()
        # 如果提供旋转角度（度），用 numpy 构建旋转矩阵并作用于所有点
        if rotation_euler_deg is not None:
            R = _euler_to_rotation_matrix(rotation_euler_deg)
            pts_t = pts_t @ R.T
        # 如果提供四元数，转换为旋转矩阵并应用
        elif quaternion is not None:
            R = _quaternion_to_rotation_matrix(quaternion)
            pts_t = pts_t @ R.T
        # 如果提供轴角，先转换为四元数，再转换为旋转矩阵并应用
        elif axis_angle is not None:
            axis, angle_deg = axis_angle
            q = _axis_angle_to_quaternion(axis, math.radians(angle_deg))
            R = _quaternion_to_rotation_matrix(q)
            pts_t = pts_t @ R.T

        # 平移
        loc = np.asarray(location, dtype=float)
        pts_t = pts_t + loc.reshape(1, 3)

    # 重塑回网格形状
    x_t = pts_t[:, 0].reshape(v_res, u_res)
    y_t = pts_t[:, 1].reshape(v_res, u_res)
    z_t = pts_t[:, 2].reshape(v_res, u_res)
    
    # 如果需要只保留 y >= 0 的部分
    if keep_y_positive:
        y_mask = y_t >= 0
        x_t = np.where(y_mask, x_t, np.nan)
        y_t = np.where(y_mask, y_t, np.nan)
        z_t = np.where(y_mask, z_t, np.nan)
    
    # 创建 3D 表面图
    surface = go.Surface(
        x=x_t,
        y=y_t,
        z=z_t,
        name=name,
        colorscale=[[0, color], [1, color]],  # 单色
        showscale=False,
        opacity=opacity
    )
    
    # 添加线框（如果需要）
    if show_wireframe:
        wireframe_traces = []
        # 添加垂直线（沿 u 方向）
        for j in range(u_res):
            wire_x = x_t[:, j]
            wire_y = y_t[:, j]
            wire_z = z_t[:, j]
            # 移除 NaN 值
            mask = ~(np.isnan(wire_x) | np.isnan(wire_y) | np.isnan(wire_z))
            if np.any(mask):
                trace = go.Scatter3d(
                    x=wire_x[mask],
                    y=wire_y[mask],
                    z=wire_z[mask],
                    mode='lines',
                    line=dict(color=wireframe_color, width=1),
                    showlegend=False,
                    hoverinfo='skip'
                )
                wireframe_traces.append(trace)
        
        # 添加水平线（沿 v 方向）
        for i in range(v_res):
            wire_x = x_t[i, :]
            wire_y = y_t[i, :]
            wire_z = z_t[i, :]
            # 移除 NaN 值
            mask = ~(np.isnan(wire_x) | np.isnan(wire_y) | np.isnan(wire_z))
            if np.any(mask):
                trace = go.Scatter3d(
                    x=wire_x[mask],
                    y=wire_y[mask],
                    z=wire_z[mask],
                    mode='lines',
                    line=dict(color=wireframe_color, width=1),
                    showlegend=False,
                    hoverinfo='skip'
                )
                wireframe_traces.append(trace)
                
        return [surface] + wireframe_traces
    
    return [surface]


def visualize_ellipsoids(ellipsoid_traces, title="Parametric Ellipsoids"):
    """
    可视化多个椭球体轨迹
    参数:
      ellipsoid_traces: 包含多个椭球体轨迹的列表
      title: 图表标题
    """
    fig = go.Figure()
    
    for trace in ellipsoid_traces:
        fig.add_trace(trace)
    
    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.0)
            )
        ),
        width=800,
        height=600
    )
    
    fig.show()
    return fig


def petal_plotly(
    a=2,
    b=1/3,
    c=2,
    n=4,
    u_res=100,
    v_res=100,
    color1='lightcoral',
    color2='lightgreen',
    affine_matrix=None,
    name="Petal",
    rotation_euler_deg=None,  # 绕原点的欧拉角旋转（度）
    quaternion=None,  # 绕原点的四元数旋转
    axis_angle=None,  # 绕原点的轴角旋转
    location=(0.0, 0.0, 0.0),  # 绕原点的平移
    scale=(1.0, 1.0, 1.0),  # 绕原点的缩放
    opacity=0.7
):
    theta = np.pi / 2 - np.pi / n
    y_dist = c * np.cos(theta)
    x_dist = a * np.sin(theta)
    
    # 为右半部分创建矩阵
    if affine_matrix is not None:
        A = affine_matrix.copy()
    else:
        A = np.eye(4)
    A[0][3] += x_dist
    A[1][3] += -y_dist
    
    # 创建右半部分
    right_traces = create_parametric_ellipsoid_plotly(
        a, b, c,
        u_res, v_res,
        u_range=(0, np.pi),
        v_range=(0, theta),
        name=name + "_right",
        color=color1,
        affine_matrix=A,
        rotation_euler_deg=(-90, 0, 0),
        opacity=opacity
    )
    
    # 为左半部分创建矩阵
    if affine_matrix is not None:
        B = affine_matrix.copy()
    else:
        B = np.eye(4)
    B[0][0] = -B[0][0]
    B[1][1] = -B[1][1]
    B[0][3] += x_dist
    B[1][3] += y_dist
    
    # 创建左半部分
    left_traces = create_parametric_ellipsoid_plotly(
        a, b, c,
        u_res, v_res,
        u_range=(0, np.pi),
        v_range=(0, theta),
        name=name + "_left",
        color=color2,
        affine_matrix=B,
        rotation_euler_deg=(-90, 0, 0),
        opacity=opacity
    )
    
    # 合并轨迹
    all_traces = right_traces + left_traces
    
    # 应用整体变换（旋转、平移、缩放）
    if rotation_euler_deg is not None or quaternion is not None or axis_angle is not None or location != (0, 0, 0) or scale != (1, 1, 1):
        R = np.eye(3)
        if rotation_euler_deg is not None:
            R = _euler_to_rotation_matrix(rotation_euler_deg)
        elif quaternion is not None:
            R = _quaternion_to_rotation_matrix(quaternion)
        elif axis_angle is not None:
            axis, angle_deg = axis_angle
            q = _axis_angle_to_quaternion(axis, math.radians(angle_deg))
            R = _quaternion_to_rotation_matrix(q)
            
        t = np.array(location)
        s = np.array(scale)
        
        for trace in all_traces:
            # 对于所有轨迹类型（Surface 和 Scatter3d）应用缩放、旋转和平移
            if hasattr(trace, 'x') and hasattr(trace, 'y') and hasattr(trace, 'z'):
                original_x = np.asarray(trace.x).copy()
                original_y = np.asarray(trace.y).copy()
                original_z = np.asarray(trace.z).copy()
                # 应用缩放
                scaled_x = original_x * s[0]
                scaled_y = original_y * s[1]
                scaled_z = original_z * s[2]
                
                # 应用旋转
                points_rotated = np.dot(np.column_stack([scaled_x.ravel(), scaled_y.ravel(), scaled_z.ravel()]), R.T)
                rotated_x = points_rotated[:, 0].reshape(original_x.shape)
                rotated_y = points_rotated[:, 1].reshape(original_y.shape)
                rotated_z = points_rotated[:, 2].reshape(original_z.shape)
                
                # 应用平移
                trace.x = rotated_x + t[0]
                trace.y = rotated_y + t[1]
                trace.z = rotated_z + t[2]
    
    return all_traces


def flower_plotly(
    a=2,
    b=1/3,
    c=2,
    n=4,
    u_res=100,
    v_res=100,
    color1='lightgreen',
    color2='lightblue',
    affine_matrix=None,
    name="Petal",
    rotation_euler_deg=(0, 0, 0),
    quaternion=None,
    axis_angle=None,
    location=(0.0, 0.0, 0.0),
    scale=(1.0, 1.0, 1.0),
    opacity=0.7
):
    """
    创建一朵由 12 个花瓣组成的花（flower pattern）。

    通过将 12 个 petal 绕 Z 轴均匀旋转排列（每次旋转 30°），
    形成一个完整的花朵形状。

    参数说明：
      a,b,c: 椭球在 x,y,z 方向的半轴长度
      n: 花瓣形状参数（控制花瓣角度范围）
      u_res,v_res: 网格分辨率
      color1: 右半花瓣颜色（Plotly 颜色字符串）
      color2: 左半花瓣颜色（Plotly 颜色字符串）
      affine_matrix: 基础仿射变换矩阵（4x4）
      name: 花瓣名称前缀
      rotation_euler_deg: 绕原点的欧拉角基础旋转（度）
      quaternion: 绕原点的四元数基础旋转
      axis_angle: 绕原点的轴角基础旋转
      location: 绕原点的平移
      scale: 绕原点的缩放
      opacity: 花瓣透明度

    返回：
      包含所有花瓣轨迹的列表（可直接传入 visualize_ellipsoids）
    """
    all_traces = []
    for i in range(12):
        petal_traces = petal_plotly(
            a, b, c, n,
            u_res, v_res,
            color1, color2,
            affine_matrix=affine_matrix,
            name=name + str(i + 1),
            rotation_euler_deg=(
                30 + rotation_euler_deg[0],
                -60 + rotation_euler_deg[1],
                i * 30 + 15 + rotation_euler_deg[2],
            ),
            quaternion=quaternion,
            axis_angle=axis_angle,
            location=location,
            scale=scale,
            opacity=opacity
        )
        all_traces.extend(petal_traces)
    return all_traces


def flowers_plotly(
    a=2,
    b=1/3,
    c=2,
    n=4,
    M=3,
    u_res=100,
    v_res=100,
    color1='lightgreen',
    color2='lightblue',
    affine_matrix=None,
    name="Petal",
    opacity=0.7
):
    """
    创建 M 朵花（flowers pattern）。

    每朵花以略微不同的 Z 轴旋转角度排列，形成多层次的
    花朵组合效果。

    参数说明：
      a,b,c: 椭球在 x,y,z 方向的半轴长度
      n: 花瓣形状参数
      M: 花朵数量
      u_res,v_res: 网格分辨率
      color1: 右半花瓣颜色
      color2: 左半花瓣颜色
      affine_matrix: 基础仿射变换矩阵（4x4）
      name: 花朵名称前缀
      opacity: 花瓣透明度

    返回：
      包含所有花朵轨迹的列表
    """
    all_traces = []
    for i in range(M):
        flower_traces = flower_plotly(
            a, b, c, n,
            u_res, v_res,
            color1, color2,
            affine_matrix=affine_matrix,
            name=name + "_" + str(i + 1),
            rotation_euler_deg=(30, -60, i * 30 + 15),
            opacity=opacity
        )
        all_traces.extend(flower_traces)
    return all_traces


# 示例使用
if __name__ == "__main__":
    # 创建基本椭球体
    ellipsoid1 = create_parametric_ellipsoid_plotly(a=2, b=1, c=1.5, name="Ellipsoid 1", color='lightblue')

    # 创建旋转后的椭球体
    ellipsoid2 = create_parametric_ellipsoid_plotly(
        a=1, b=1.5, c=2,
        rotation_euler_deg=(30, 45, 60),
        location=(3, 0, 0),
        name="Rotated Ellipsoid",
        color='lightgreen'
    )

    # 创建一个花瓣形状
    petal_traces = petal_plotly(
        a=2, b=1/3, c=2, n=4, u_res=50, v_res=50,
        color1='pink', color2='yellow',
        name="Petal", opacity=0.8
    )

    # 创建一朵花（12个花瓣）
    flower_traces = flower_plotly(
        a=2, b=1/3, c=2, n=4,
        u_res=50, v_res=50,
        color1='lightcoral', color2='lightblue',
        name="Flower_Petal",
        location=(5, 0, 0),
        scale=(1.5, 1.5, 1.5),
        opacity=0.7
    )

    # 可视化所有形状
    all_traces = ellipsoid1 + ellipsoid2 + petal_traces + flower_traces
    visualize_ellipsoids(all_traces, title="Plotly Ellipsoids, Petal and Flower")

import matplotlib.pyplot as plt
import numpy as np
import math
import matplotlib.cm as cm
from cprdspy.CPR_matplotlib.Arcs.arc import *

# from cprdspy.CPR_matplotlib.Arcs.oval_arc import *


# ===================== 基础工具函数 =====================
def rotate_point(point, theta):
    """将点绕原点旋转 theta 角度（弧度）"""
    x, y = point
    x_new = x * np.cos(theta) - y * np.sin(theta)
    y_new = x * np.sin(theta) + y * np.cos(theta)
    return (x_new, y_new)


def get_hex_grid_centers(radius=8, spacing=4):
    """生成正六边形网格中心点（用于组合图案）"""
    centers = [(0, 0)]  # 中心位置
    angles = [math.pi / 6 + i * math.pi / 3 for i in range(6)]  # 正六边形6个方向
    for angle in angles:
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        centers.append((x, y))
    return centers


# ===================== 核心绘制函数 =====================
class CPRFlowerDrawer:
    """圈点圆CPR花型绘制器（统一管理圆/椭圆花瓣）"""

    def __init__(self, figsize=(8, 8), dpi=120, bg_color="#10101a"):
        """初始化画布"""
        self.fig, self.ax = plt.subplots(figsize=figsize, dpi=dpi)
        self.ax.set_aspect("equal")  # 等比例显示
        self.ax.axis("off")  # 隐藏坐标轴
        self.fig.patch.set_facecolor(bg_color)  # 背景色

    def draw_circle_petal_flower(
        self,
        center=(0, 0),
        R=1,
        r=1,
        n=4,
        N=12,  # 圆花瓣核心参数
        rotation=0,
        color="#66d9ff",
        alpha=0.8,
        gradient=True,  # 是否开启渐变配色
        # 中心圆参数
        center_circle_r=0.1,
        center_circle_color="#ff4d94",
        # 花瓣点参数
        peak_size=6,
        peak_color="#ffff00",
        peak_edge="#fff",
        peak_edgewidth=0.5,
    ):
        """绘制圆花瓣花（圈+点+圆）"""
        # 1. 绘制中心实心圆
        circle = plt.Circle(
            center,
            center_circle_r,
            facecolor=center_circle_color,
            edgecolor="#fff",
            linewidth=0.5,
            alpha=alpha,
            zorder=5,
        )
        self.ax.add_patch(circle)

        # 2. 生成渐变配色（如果开启）
        if gradient:
            colors = cm.Blues(np.linspace(0.4, 0.9, N))  # N个花瓣对应N种深浅
        else:
            colors = [color] * N

        # 3. 循环绘制圆花瓣+顶点散点
        angle = 2 * np.pi / n
        a = R * np.sin(np.pi / n)
        for i in range(N):
            petal_rot = rotation + i * 2 * np.pi / N
            petal_color = colors[i] if gradient else color

            # 圆花瓣参数计算
            if r > 0:
                beta = np.arccos(min(1, max(-1, a / r)))
            else:
                beta = 0
            theta_arc = np.pi / 2 - np.pi / n + np.arccos(min(1, max(-1, a / r)))

            # 圆弧中心点
            center1_theta = petal_rot + angle / 2
            center2_theta = petal_rot - angle / 2
            center1 = (
                np.cos(center1_theta) * R + center[0],
                np.sin(center1_theta) * R + center[1],
            )
            center2 = (
                np.cos(center2_theta) * R + center[0],
                np.sin(center2_theta) * R + center[1],
            )

            # 圆弧角度
            if abs(r - a) < 1e-12:
                theta1 = np.pi + angle / 2
                theta2 = np.pi + angle / 2 + theta_arc
                theta3 = np.pi / 2
                theta4 = np.pi / 2 + theta_arc
            elif r > a:
                theta1 = np.pi + angle / 2
                theta2 = np.pi + angle / 2 + theta_arc
                theta3 = np.pi / 2 - beta
                theta4 = np.pi / 2 - beta + theta_arc
            else:
                print(f"警告：r={r} < a={a}，无法绘制花瓣")
                continue

            # 绘制圆弧（圈）
            arc(
                r,
                theta1,
                theta2,
                petal_rot,
                color=petal_color,
                alpha=alpha,
                center=center1,
                points=1000,
                use_degree=False,
                ax=self.ax,
            )
            arc(
                r,
                theta3,
                theta4,
                petal_rot,
                color=petal_color,
                alpha=alpha,
                center=center2,
                points=1000,
                use_degree=False,
                ax=self.ax,
            )

            # 绘制花瓣顶点散点（点）
            peak_x = center[0] + R * np.cos(petal_rot)
            peak_y = center[1] + R * np.sin(petal_rot)
            self.ax.scatter(
                peak_x,
                peak_y,
                s=peak_size,
                c=peak_color,
                edgecolor=peak_edge,
                linewidth=peak_edgewidth,
                alpha=alpha,
                zorder=10,
            )

    def draw_oval_petal_flower(
        self,
        center=(0, 0),
        a=3,
        b=1.5,
        d=0.3,
        n=8,  # 椭圆花瓣核心参数
        rotation=0,
        color="#66d9ff",
        alpha=0.8,
        gradient=True,  # 是否开启渐变配色
        # 中心圆参数
        center_circle_r=0.2,
        center_circle_color="#ff4d94",
        # 花瓣点参数
        peak_size=8,
        peak_color="#ffff00",
        peak_edge="#000",
        peak_edgewidth=0.5,
    ):
        """绘制椭圆花瓣花（圈+点+圆）"""
        # 1. 绘制中心实心圆
        circle = plt.Circle(
            center,
            center_circle_r,
            facecolor=center_circle_color,
            edgecolor="#fff",
            linewidth=0.5,
            alpha=alpha,
            zorder=5,
        )
        self.ax.add_patch(circle)

        # 2. 生成渐变配色（如果开启）
        if gradient:
            colors = cm.Blues(np.linspace(0.4, 0.9, n))
        else:
            colors = [color] * n

        # 3. 循环绘制椭圆花瓣+顶点散点
        for i in range(n):
            petal_rot = rotation + i * 2 * np.pi / n
            petal_color = colors[i] if gradient else color

            # 椭圆花瓣参数计算
            x0 = b / (2 * a) * np.sqrt(4 * a**2 - d**2) / (d / 2)
            beta = np.arctan(x0)
            beta_b1 = np.pi / 2 - beta
            beta_e1 = np.pi / 2 + beta
            beta_b2 = 3 * np.pi / 2 - beta
            beta_e2 = 3 * np.pi / 2 + beta

            # 椭圆弧中心点
            center1 = (center[0], center[1] - d / 2)
            center2 = (center[0], center[1] + d / 2)
            center1_rot = rotate_point(center1, petal_rot)
            center2_rot = rotate_point(center2, petal_rot)

            # 绘制椭圆弧（圈）
            oval_arc(
                a,
                b,
                beta_b1,
                beta_e1,
                petal_rot,
                color=petal_color,
                alpha=alpha,
                center=center1_rot,
                points=1000,
                use_degree=False,
                ax=self.ax,
            )
            oval_arc(
                a,
                b,
                beta_b2,
                beta_e2,
                petal_rot,
                color=petal_color,
                alpha=alpha,
                center=center2_rot,
                points=1000,
                use_degree=False,
                ax=self.ax,
            )

            # 绘制花瓣顶点散点（点）
            peak_x = center[0] + a * np.cos(petal_rot)
            peak_y = center[1] + a * np.sin(petal_rot)
            self.ax.scatter(
                peak_x,
                peak_y,
                s=peak_size,
                c=peak_color,
                edgecolor=peak_edge,
                linewidth=peak_edgewidth,
                alpha=alpha,
                zorder=10,
            )

    def draw_combination_pattern(
        self,
        flower_type="oval",  # "circle" 或 "oval"
        grid_radius=8,
        # 统一参数
        alpha=0.7,
        gradient=True,
        center_circle_color="#ff4d94",
        peak_color="#ffff00",
        peak_edge="#000",
    ):
        """绘制组合图案（正六边形网格排列）"""
        # 获取网格中心点
        centers = get_hex_grid_centers(radius=grid_radius)

        # 不同位置的花参数（中心花更大、花瓣更多）
        if flower_type == "circle":
            params_list = [
                # 中心花
                {
                    "R": 2.5,
                    "r": 2.5,
                    "n": 4,
                    "N": 8,
                    "rotation": 0,
                    "center_circle_r": 0.25,
                    "peak_size": 6,
                },
                # 周围6朵花
                {
                    "R": 1.8,
                    "r": 1.8,
                    "n": 4,
                    "N": 6,
                    "rotation": math.pi / 12,
                    "center_circle_r": 0.18,
                    "peak_size": 4,
                },
                {
                    "R": 1.8,
                    "r": 1.8,
                    "n": 4,
                    "N": 6,
                    "rotation": math.pi / 6,
                    "center_circle_r": 0.18,
                    "peak_size": 4,
                },
                {
                    "R": 1.8,
                    "r": 1.8,
                    "n": 4,
                    "N": 6,
                    "rotation": math.pi / 4,
                    "center_circle_r": 0.18,
                    "peak_size": 4,
                },
                {
                    "R": 1.8,
                    "r": 1.8,
                    "n": 4,
                    "N": 6,
                    "rotation": math.pi / 3,
                    "center_circle_r": 0.18,
                    "peak_size": 4,
                },
                {
                    "R": 1.8,
                    "r": 1.8,
                    "n": 4,
                    "N": 6,
                    "rotation": 5 * math.pi / 12,
                    "center_circle_r": 0.18,
                    "peak_size": 4,
                },
                {
                    "R": 1.8,
                    "r": 1.8,
                    "n": 4,
                    "N": 6,
                    "rotation": math.pi / 2,
                    "center_circle_r": 0.18,
                    "peak_size": 4,
                },
            ]
        else:  # oval
            params_list = [
                # 中心花
                {
                    "a": 2.5,
                    "b": 1.25,
                    "d": 0.3,
                    "n": 8,
                    "rotation": 0,
                    "center_circle_r": 0.25,
                    "peak_size": 6,
                },
                # 周围6朵花
                {
                    "a": 1.8,
                    "b": 0.9,
                    "d": 0.2,
                    "n": 6,
                    "rotation": math.pi / 12,
                    "center_circle_r": 0.18,
                    "peak_size": 4,
                },
                {
                    "a": 1.8,
                    "b": 0.9,
                    "d": 0.2,
                    "n": 6,
                    "rotation": math.pi / 6,
                    "center_circle_r": 0.18,
                    "peak_size": 4,
                },
                {
                    "a": 1.8,
                    "b": 0.9,
                    "d": 0.2,
                    "n": 6,
                    "rotation": math.pi / 4,
                    "center_circle_r": 0.18,
                    "peak_size": 4,
                },
                {
                    "a": 1.8,
                    "b": 0.9,
                    "d": 0.2,
                    "n": 6,
                    "rotation": math.pi / 3,
                    "center_circle_r": 0.18,
                    "peak_size": 4,
                },
                {
                    "a": 1.8,
                    "b": 0.9,
                    "d": 0.2,
                    "n": 6,
                    "rotation": 5 * math.pi / 12,
                    "center_circle_r": 0.18,
                    "peak_size": 4,
                },
                {
                    "a": 1.8,
                    "b": 0.9,
                    "d": 0.2,
                    "n": 6,
                    "rotation": math.pi / 2,
                    "center_circle_r": 0.18,
                    "peak_size": 4,
                },
            ]

        # 批量绘制
        for i, center in enumerate(centers):
            params = params_list[i]
            params["center"] = center
            params["alpha"] = alpha
            params["gradient"] = gradient
            params["center_circle_color"] = center_circle_color
            params["peak_color"] = peak_color
            params["peak_edge"] = peak_edge

            if flower_type == "circle":
                self.draw_circle_petal_flower(**params)
            else:
                self.draw_oval_petal_flower(**params)

    def save_figure(self, filename="圈点圆CPR图案.png", dpi=300):
        """保存高清图片（无白边）"""
        self.fig.savefig(
            filename,
            dpi=dpi,
            bbox_inches="tight",
            facecolor=self.fig.get_facecolor(),
            edgecolor="none",
        )

    def show(self):
        """显示图案"""
        plt.tight_layout()
        plt.show()


# ===================== 调用示例（按需选择） =====================
if __name__ == "__main__":
    # 1. 绘制单朵渐变椭圆花（基础款）
    drawer = CPRFlowerDrawer(figsize=(8, 8), dpi=120, bg_color="#10101a")
    drawer.draw_oval_petal_flower(
        a=3,
        b=1.5,
        d=0.3,
        n=8,
        color="#66d9ff",
        alpha=0.8,
        gradient=True,  # 开启渐变
        center_circle_r=0.2,
        center_circle_color="#ff4d94",
        peak_size=8,
        peak_color="#ffff00",
        peak_edge="#000",
    )
    # drawer.save_figure("单朵椭圆花.png")
    # drawer.show()

    # 2. 绘制单朵渐变圆花瓣花
    # drawer = CPRFlowerDrawer(figsize=(8,8), dpi=120, bg_color="#10101a")
    # drawer.draw_circle_petal_flower(
    #     R=2, r=2, n=4, N=8,
    #     color="#66d9ff", alpha=0.8,
    #     gradient=True,
    #     center_circle_r=0.15, center_circle_color="#ff4d94",
    #     peak_size=6, peak_color="#ffff00", peak_edge="#fff"
    # )
    # drawer.save_figure("单朵圆花瓣花.png")
    # drawer.show()

    # 3. 绘制椭圆花组合图案（推荐！）
    # drawer = CPRFlowerDrawer(figsize=(12,12), dpi=150, bg_color="#10101a")
    # drawer.draw_combination_pattern(
    #     flower_type="oval", grid_radius=8,
    #     alpha=0.7, gradient=True,
    #     center_circle_color="#ff4d94",
    #     peak_color="#ffff00", peak_edge="#000"
    # )
    # drawer.save_figure("椭圆花组合图案.png", dpi=300)
    # drawer.show()

"""Circles 模块 — 圆与椭圆的生成与绘制。

公开 API:
    - circle                   绘制圆（含 ax 参数，返回 Line2D）
    - circle_fill              绘制圆（带填充）
    - draw_circle              简单绘制圆（无 ax 参数）
    - circle_p                 通过圆心和圆上一点绘制圆
    - ellipse                  绘制椭圆
    - ellipse_fill             绘制椭圆（带填充）
    - concentric_circles       同心圆（等差/等比）
    - concentric_circles_fill  同心圆（带填充）
    - concentric_ellipse       同心椭圆（等差/等比）
    - concentric_ellipse_fill  同心椭圆（带填充）
"""

from .circle import (
    circle,
    circle_fill,
    draw_circle,
    circle_p,
    ellipse,
    ellipse_fill,
    concentric_circles,
    concentric_circles_fill,
    concentric_ellipse,
    concentric_ellipse_fill,
)

__all__ = [
    "circle",
    "circle_fill",
    "draw_circle",
    "circle_p",
    "ellipse",
    "ellipse_fill",
    "concentric_circles",
    "concentric_circles_fill",
    "concentric_ellipse",
    "concentric_ellipse_fill",
]

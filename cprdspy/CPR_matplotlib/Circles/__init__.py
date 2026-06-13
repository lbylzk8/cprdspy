"""Circles 模块 — 圆与椭圆的生成与绘制。

公开 API:
    - circle             绘制圆（含 ax 参数，返回 Line2D）
    - draw_circle        简单绘制圆（无 ax 参数）
    - circle_p           通过圆心和圆上一点绘制圆
    - ellipse            绘制椭圆
    - concentric_circles 同心圆（等差/等比）
    - concentric_ellipse 同心椭圆（等差/等比）
"""

from .circle import (
    circle,
    draw_circle,
    circle_p,
    ellipse,
    concentric_circles,
    concentric_ellipse,
)

__all__ = [
    "circle",
    "draw_circle",
    "circle_p",
    "ellipse",
    "concentric_circles",
    "concentric_ellipse",
]

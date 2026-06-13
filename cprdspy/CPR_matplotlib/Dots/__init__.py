"""Dots 模块 — 点集生成与绘制。

公开 API:
    - Dots                 点集容器类，支持 + 拼接
    - n_dots              生成圆/椭圆/超椭圆上的 n 等分点
    - draw_dots           绘制点集，支持统一颜色、逐点颜色和渐变色
    - n_dots_array        生成多层正 n 边形点阵
    - draw_n_dots_array   绘制多层点阵
"""

from .dot import (
    Dots,
    n_dots,
    draw_dots,
    n_dots_array,
    draw_n_dots_array,
)

__all__ = [
    "Dots",
    "n_dots",
    "draw_dots",
    "n_dots_array",
    "draw_n_dots_array",
]

"""Dots 模块 — 5 函数"""

from cprdspy.CPR_plotly1 import (
    Dots_plotly, n_dots_plotly, draw_dots_plotly,
    n_dots_array_plotly, draw_n_dots_array_plotly,
)
import numpy as np

MODULE_ID = "dots"
MODULE_LABEL = "Dots"
MODULE_ICON = "∙"

COLOR_BY_OPTIONS = [
    {"label": "无 (统一色)", "value": "none"},
    {"label": "序号 (index)", "value": "index"},
    {"label": "角度 (angle)", "value": "angle"},
    {"label": "半径 (radius)", "value": "radius"},
    {"label": "X 坐标", "value": "x"},
    {"label": "Y 坐标", "value": "y"},
]

SHAPE_OPTIONS = [
    {"label": "圆 (circle)", "value": "c"},
    {"label": "椭圆 (ellipse)", "value": "e"},
    {"label": "超椭圆 (superellipse)", "value": "s"},
]

DIR_OPTIONS = [
    {"label": "双向", "value": "both"},
    {"label": "向外", "value": "out"},
    {"label": "向内", "value": "in"},
]

CMAP_OPTIONS = [
    {"label": "Viridis", "value": "viridis"},
    {"label": "Plasma", "value": "plasma"},
    {"label": "Inferno", "value": "inferno"},
    {"label": "Magma", "value": "magma"},
    {"label": "Turbo", "value": "turbo"},
    {"label": "Coolwarm", "value": "coolwarm"},
    {"label": "Spectral", "value": "Spectral"},
]

FUNCTIONS = {
    "n_dots": {
        "label": "N 等分点 (n_dots)",
        "params": [
            {"name": "n", "label": "点数", "type": "slider", "min": 3, "max": 60, "step": 1, "default": 12},
            {"name": "R", "label": "半径 R", "type": "slider", "min": 0.1, "max": 5, "step": 0.1, "default": 1},
            {"name": "a", "label": "半轴系数 a", "type": "slider", "min": 0.5, "max": 3, "step": 0.1, "default": 1},
            {"name": "b", "label": "半轴系数 b", "type": "slider", "min": 0.5, "max": 3, "step": 0.1, "default": 1},
            {"name": "p", "label": "超椭圆指数 p", "type": "slider", "min": 1, "max": 8, "step": 0.5, "default": 2},
            {"name": "q", "label": "超椭圆指数 q", "type": "slider", "min": 1, "max": 8, "step": 0.5, "default": 2},
            {"name": "rotation", "label": "旋转°", "type": "slider", "min": 0, "max": 360, "default": 0},
            {"name": "shape", "label": "形状", "type": "dropdown", "options": SHAPE_OPTIONS, "default": "c"},
            {"name": "color", "label": "颜色", "type": "color", "default": "#e74c3c"},
            {"name": "size", "label": "点大小", "type": "slider", "min": 2, "max": 20, "step": 1, "default": 8},
            {"name": "color_by", "label": "按...着色", "type": "dropdown", "options": COLOR_BY_OPTIONS, "default": "none"},
            {"name": "cmap", "label": "色板", "type": "dropdown", "options": CMAP_OPTIONS, "default": "viridis"},
        ],
        "func": lambda n, R, a, b, p, q, rotation, shape, color, size, color_by, cmap, **kw:
            draw_dots_plotly(n_dots_plotly(n=n, R=R, a=a, b=b, p=p, q=q, rotation=rotation, shape=shape),
                           color=color, size=size, color_by=None if color_by == "none" else color_by, cmap=cmap),
    },
    "n_dots_array": {
        "label": "多层点阵 (n_dots_array)",
        "params": [
            {"name": "n", "label": "每层点数", "type": "slider", "min": 3, "max": 30, "step": 1, "default": 6},
            {"name": "m", "label": "层数", "type": "slider", "min": 1, "max": 10, "step": 1, "default": 3},
            {"name": "R", "label": "基准半径", "type": "slider", "min": 0.1, "max": 5, "step": 0.1, "default": 1},
            {"name": "d_rotation", "label": "层旋转°", "type": "slider", "min": 0, "max": 90, "default": 10},
            {"name": "direction", "label": "方向", "type": "dropdown", "options": DIR_OPTIONS, "default": "both"},
            {"name": "shape", "label": "形状", "type": "dropdown", "options": SHAPE_OPTIONS, "default": "c"},
            {"name": "color", "label": "颜色", "type": "color", "default": "#f1c40f"},
            {"name": "size", "label": "点大小", "type": "slider", "min": 2, "max": 20, "step": 1, "default": 8},
            {"name": "color_by", "label": "着色", "type": "dropdown", "options": COLOR_BY_OPTIONS, "default": "radius"},
            {"name": "cmap", "label": "色板", "type": "dropdown", "options": CMAP_OPTIONS, "default": "viridis"},
        ],
        "func": draw_n_dots_array_plotly,
    },
    "n_dots_multi": {
        "label": "多点集叠加 (Dots +)",
        "params": [
            {"name": "n1", "label": "第一组点数", "type": "slider", "min": 3, "max": 30, "step": 1, "default": 6},
            {"name": "R1", "label": "第一组半径", "type": "slider", "min": 0.1, "max": 5, "step": 0.1, "default": 0.8},
            {"name": "n2", "label": "第二组点数", "type": "slider", "min": 3, "max": 30, "step": 1, "default": 6},
            {"name": "R2", "label": "第二组半径", "type": "slider", "min": 0.1, "max": 5, "step": 0.1, "default": 0.4},
            {"name": "rot2", "label": "第二组旋转°", "type": "slider", "min": 0, "max": 360, "default": 30},
            {"name": "n3", "label": "第三组点数", "type": "slider", "min": 3, "max": 30, "step": 1, "default": 6},
            {"name": "R3", "label": "第三组半径", "type": "slider", "min": 0.1, "max": 5, "step": 0.1, "default": 0.2},
            {"name": "rot3", "label": "第三组旋转°", "type": "slider", "min": 0, "max": 360, "default": 60},
            {"name": "color", "label": "颜色", "type": "color", "default": "#1abc9c"},
            {"name": "size", "label": "点大小", "type": "slider", "min": 2, "max": 20, "step": 1, "default": 8},
            {"name": "color_by", "label": "着色", "type": "dropdown", "options": COLOR_BY_OPTIONS, "default": "radius"},
            {"name": "cmap", "label": "色板", "type": "dropdown", "options": CMAP_OPTIONS, "default": "viridis"},
        ],
        "func": lambda n1, R1, n2, R2, rot2, n3, R3, rot3, color, size, color_by, cmap, **kw:
            draw_dots_plotly(
                n_dots_plotly(n1, R=R1) +
                n_dots_plotly(n2, R=R2, rotation=rot2) +
                n_dots_plotly(n3, R=R3, rotation=rot3),
                color=color, size=size, color_by=None if color_by == "none" else color_by, cmap=cmap,
            ),
    },
    "n_dots_superellipse": {
        "label": "超椭圆点 (superellipse)",
        "params": [
            {"name": "n", "label": "点数", "type": "slider", "min": 3, "max": 60, "step": 1, "default": 12},
            {"name": "R", "label": "半径", "type": "slider", "min": 0.1, "max": 5, "step": 0.1, "default": 1},
            {"name": "a", "label": "半轴 a", "type": "slider", "min": 0.5, "max": 3, "step": 0.1, "default": 1},
            {"name": "b", "label": "半轴 b", "type": "slider", "min": 0.5, "max": 3, "step": 0.1, "default": 1},
            {"name": "p", "label": "指数 p", "type": "slider", "min": 2, "max": 10, "step": 1, "default": 4},
            {"name": "q", "label": "指数 q", "type": "slider", "min": 2, "max": 10, "step": 1, "default": 2},
            {"name": "rotation", "label": "旋转°", "type": "slider", "min": 0, "max": 360, "default": 0},
            {"name": "color", "label": "颜色", "type": "color", "default": "#9b59b6"},
            {"name": "size", "label": "点大小", "type": "slider", "min": 2, "max": 20, "step": 1, "default": 8},
            {"name": "color_by", "label": "着色", "type": "dropdown", "options": COLOR_BY_OPTIONS, "default": "angle"},
            {"name": "cmap", "label": "色板", "type": "dropdown", "options": CMAP_OPTIONS, "default": "plasma"},
        ],
        "func": lambda n, R, a, b, p, q, rotation, color, size, color_by, cmap, **kw:
            draw_dots_plotly(n_dots_plotly(n=n, R=R, a=a, b=b, p=p, q=q, rotation=rotation, shape="s"),
                           color=color, size=size, color_by=None if color_by == "none" else color_by, cmap=cmap),
    },
    "n_dots_ellipse": {
        "label": "椭圆点阵 (ellipse dots)",
        "params": [
            {"name": "n", "label": "点数", "type": "slider", "min": 3, "max": 60, "step": 1, "default": 8},
            {"name": "R", "label": "半径", "type": "slider", "min": 0.1, "max": 5, "step": 0.1, "default": 1},
            {"name": "a", "label": "半轴 a", "type": "slider", "min": 0.5, "max": 3, "step": 0.1, "default": 1.5},
            {"name": "b", "label": "半轴 b", "type": "slider", "min": 0.5, "max": 3, "step": 0.1, "default": 0.8},
            {"name": "rotation", "label": "旋转°", "type": "slider", "min": 0, "max": 360, "default": 30},
            {"name": "color", "label": "颜色", "type": "color", "default": "#2ecc71"},
            {"name": "size", "label": "点大小", "type": "slider", "min": 2, "max": 20, "step": 1, "default": 8},
            {"name": "color_by", "label": "着色", "type": "dropdown", "options": COLOR_BY_OPTIONS, "default": "angle"},
            {"name": "cmap", "label": "色板", "type": "dropdown", "options": CMAP_OPTIONS, "default": "viridis"},
        ],
        "func": lambda n, R, a, b, rotation, color, size, color_by, cmap, **kw:
            draw_dots_plotly(n_dots_plotly(n=n, R=R, a=a, b=b, rotation=rotation, shape="e"),
                           color=color, size=size, color_by=None if color_by == "none" else color_by, cmap=cmap),
    },
}

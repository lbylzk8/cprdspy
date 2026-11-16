"""Circles 模块 — 10 函数"""

from cprdspy.CPR_plotly1 import (
    circle_plotly, circle_fill_plotly, draw_circle_plotly, circle_p_plotly,
    ellipse_plotly, ellipse_fill_plotly, concentric_circles_plotly,
    concentric_circles_fill_plotly, concentric_ellipse_plotly, concentric_ellipse_fill_plotly,
)

MODULE_ID = "circles"
MODULE_LABEL = "Circles"
MODULE_ICON = "○"

COMMON = [
    {"name": "color", "label": "颜色", "type": "color", "default": "#3498db"},
    {"name": "line_width", "label": "线宽", "type": "slider", "min": 0.5, "max": 10, "step": 0.5, "default": 2},
    {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
    {"name": "points", "label": "点数", "type": "slider", "min": 50, "max": 1000, "step": 50, "default": 200},
]

DIR_OPTIONS = [
    {"label": "双向 (both)", "value": "both"},
    {"label": "向外 (out)", "value": "out"},
    {"label": "向内 (in)", "value": "in"},
]

FUNCTIONS = {
    "circle": {
        "label": "圆 (circle)",
        "params": [
            {"name": "radius", "label": "半径", "type": "slider", "min": 0.1, "max": 10, "step": 0.1, "default": 2},
            *COMMON,
        ],
        "func": circle_plotly,
    },
    "circle_fill": {
        "label": "填充圆 (circle_fill)",
        "params": [
            {"name": "radius", "label": "半径", "type": "slider", "min": 0.1, "max": 10, "step": 0.1, "default": 1},
            {"name": "color", "label": "边线颜色", "type": "color", "default": "#3498db"},
            {"name": "fill_color", "label": "填充颜色", "type": "color", "default": "#aed6f1"},
            {"name": "fill_alpha", "label": "填充透明度", "type": "slider", "min": 0.05, "max": 1, "step": 0.05, "default": 0.3},
            {"name": "edge_width", "label": "边线宽", "type": "slider", "min": 0.5, "max": 10, "step": 0.5, "default": 2},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
            {"name": "points", "label": "点数", "type": "slider", "min": 50, "max": 1000, "step": 50, "default": 200},
        ],
        "func": circle_fill_plotly,
    },
    "draw_circle": {
        "label": "独立圆图 (draw_circle)",
        "params": [
            {"name": "radius", "label": "半径", "type": "slider", "min": 0.1, "max": 10, "step": 0.1, "default": 1},
            *COMMON,
        ],
        "func": lambda radius, color, line_width, alpha, points, **kw:
            list(draw_circle_plotly(radius=radius, color=color, line_width=line_width, alpha=alpha, points=points).data),
    },
    "circle_p": {
        "label": "点定圆 (circle_p)",
        "params": [
            {"name": "point_x", "label": "Point X", "type": "slider", "min": -5, "max": 5, "step": 0.1, "default": 1},
            {"name": "point_y", "label": "Point Y", "type": "slider", "min": -5, "max": 5, "step": 0.1, "default": 0},
            {"name": "color", "label": "颜色", "type": "color", "default": "#2ecc71"},
            {"name": "line_width", "label": "线宽", "type": "slider", "min": 0.5, "max": 10, "step": 0.5, "default": 2},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
            {"name": "points", "label": "点数", "type": "slider", "min": 50, "max": 1000, "step": 50, "default": 200},
        ],
        "func": lambda point_x, point_y, color, line_width, alpha, points, **kw:
            circle_p_plotly(center=(0, 0), point=(point_x, point_y), color=color),
    },
    "ellipse": {
        "label": "椭圆 (ellipse)",
        "params": [
            {"name": "a", "label": "长轴 a", "type": "slider", "min": 0.5, "max": 10, "step": 0.1, "default": 3},
            {"name": "b", "label": "短轴 b", "type": "slider", "min": 0.5, "max": 10, "step": 0.1, "default": 1.5},
            {"name": "rotation", "label": "旋转°", "type": "slider", "min": 0, "max": 360, "default": 30},
            *COMMON,
        ],
        "func": ellipse_plotly,
    },
    "ellipse_fill": {
        "label": "填充椭圆 (ellipse_fill)",
        "params": [
            {"name": "a", "label": "长轴 a", "type": "slider", "min": 0.5, "max": 10, "step": 0.1, "default": 3},
            {"name": "b", "label": "短轴 b", "type": "slider", "min": 0.5, "max": 10, "step": 0.1, "default": 1.5},
            {"name": "rotation", "label": "旋转°", "type": "slider", "min": 0, "max": 360, "default": 30},
            {"name": "color", "label": "边线颜色", "type": "color", "default": "#e67e22"},
            {"name": "fill_color", "label": "填充颜色", "type": "color", "default": "#f9e79f"},
            {"name": "fill_alpha", "label": "填充透明度", "type": "slider", "min": 0.05, "max": 1, "step": 0.05, "default": 0.3},
            {"name": "edge_width", "label": "边线宽", "type": "slider", "min": 0.5, "max": 10, "step": 0.5, "default": 2},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
            {"name": "points", "label": "点数", "type": "slider", "min": 50, "max": 2000, "step": 50, "default": 1000},
        ],
        "func": ellipse_fill_plotly,
    },
    "concentric_circles": {
        "label": "同心圆 (concentric_circles)",
        "params": [
            {"name": "n", "label": "圈数", "type": "slider", "min": 1, "max": 10, "step": 1, "default": 3},
            {"name": "radius", "label": "基准半径", "type": "slider", "min": 0.1, "max": 5, "step": 0.1, "default": 1},
            {"name": "param", "label": "间距参数", "type": "slider", "min": 0.1, "max": 3, "step": 0.05, "default": 0.5},
            {"name": "mode", "label": "模式", "type": "dropdown", "options": [
                {"label": "等差 (arithmetic)", "value": "arithmetic"},
                {"label": "等比 (geometric)", "value": "geometric"},
            ], "default": "arithmetic"},
            {"name": "direction", "label": "方向", "type": "dropdown", "options": DIR_OPTIONS, "default": "both"},
            {"name": "color", "label": "颜色", "type": "color", "default": "#9b59b6"},
            {"name": "line_width", "label": "线宽", "type": "slider", "min": 0.5, "max": 10, "step": 0.5, "default": 1.5},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
            {"name": "points", "label": "点数", "type": "slider", "min": 50, "max": 1000, "step": 50, "default": 200},
        ],
        "func": concentric_circles_plotly,
    },
    "concentric_circles_fill": {
        "label": "填充同心圆 (concentric_circles_fill)",
        "params": [
            {"name": "n", "label": "圈数", "type": "slider", "min": 1, "max": 10, "step": 1, "default": 3},
            {"name": "radius", "label": "基准半径", "type": "slider", "min": 0.1, "max": 5, "step": 0.1, "default": 0.2},
            {"name": "param", "label": "间距参数", "type": "slider", "min": 0.1, "max": 3, "step": 0.05, "default": 0.25},
            {"name": "mode", "label": "模式", "type": "dropdown", "options": [
                {"label": "等差 (arithmetic)", "value": "arithmetic"},
                {"label": "等比 (geometric)", "value": "geometric"},
            ], "default": "arithmetic"},
            {"name": "direction", "label": "方向", "type": "dropdown", "options": DIR_OPTIONS, "default": "both"},
            {"name": "color", "label": "边线颜色", "type": "color", "default": "#3498db"},
            {"name": "fill_color", "label": "填充颜色", "type": "color", "default": "#aed6f1"},
            {"name": "fill_alpha", "label": "填充透明度", "type": "slider", "min": 0.05, "max": 1, "step": 0.05, "default": 0.3},
            {"name": "edge_width", "label": "边线宽", "type": "slider", "min": 0.5, "max": 10, "step": 0.5, "default": 2},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
            {"name": "points", "label": "点数", "type": "slider", "min": 50, "max": 1000, "step": 50, "default": 200},
        ],
        "func": concentric_circles_fill_plotly,
    },
    "concentric_ellipse": {
        "label": "同心椭圆 (concentric_ellipse)",
        "params": [
            {"name": "n", "label": "圈数", "type": "slider", "min": 1, "max": 10, "step": 1, "default": 2},
            {"name": "a", "label": "长轴 a", "type": "slider", "min": 0.5, "max": 10, "step": 0.1, "default": 1},
            {"name": "b", "label": "短轴 b", "type": "slider", "min": 0.5, "max": 10, "step": 0.1, "default": 0.6},
            {"name": "param", "label": "间距参数", "type": "slider", "min": 0.1, "max": 3, "step": 0.05, "default": 0.4},
            {"name": "mode", "label": "模式", "type": "dropdown", "options": [
                {"label": "等差", "value": "arithmetic"}, {"label": "等比", "value": "geometric"},
            ], "default": "arithmetic"},
            {"name": "direction", "label": "方向", "type": "dropdown", "options": DIR_OPTIONS, "default": "both"},
            {"name": "rotation", "label": "椭圆旋转°", "type": "slider", "min": 0, "max": 360, "default": 30},
            {"name": "color", "label": "颜色", "type": "color", "default": "#e91e90"},
            {"name": "line_width", "label": "线宽", "type": "slider", "min": 0.5, "max": 10, "step": 0.5, "default": 1.5},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
            {"name": "points", "label": "点数", "type": "slider", "min": 50, "max": 1000, "step": 50, "default": 200},
        ],
        "func": concentric_ellipse_plotly,
    },
    "concentric_ellipse_fill": {
        "label": "填充同心椭圆 (concentric_ellipse_fill)",
        "params": [
            {"name": "n", "label": "圈数", "type": "slider", "min": 1, "max": 10, "step": 1, "default": 2},
            {"name": "a", "label": "长轴 a", "type": "slider", "min": 0.5, "max": 10, "step": 0.1, "default": 0.8},
            {"name": "b", "label": "短轴 b", "type": "slider", "min": 0.5, "max": 10, "step": 0.1, "default": 0.4},
            {"name": "param", "label": "间距", "type": "slider", "min": 0.1, "max": 3, "step": 0.05, "default": 0.3},
            {"name": "mode", "label": "模式", "type": "dropdown", "options": [
                {"label": "等差", "value": "arithmetic"}, {"label": "等比", "value": "geometric"},
            ], "default": "arithmetic"},
            {"name": "direction", "label": "方向", "type": "dropdown", "options": DIR_OPTIONS, "default": "both"},
            {"name": "rotation", "label": "椭圆旋转°", "type": "slider", "min": 0, "max": 360, "default": 30},
            {"name": "color", "label": "边线", "type": "color", "default": "#2ecc71"},
            {"name": "fill_color", "label": "填充色", "type": "color", "default": "#a9dfbf"},
            {"name": "fill_alpha", "label": "填充透明度", "type": "slider", "min": 0.05, "max": 1, "step": 0.05, "default": 0.3},
            {"name": "edge_width", "label": "边线宽", "type": "slider", "min": 0.5, "max": 10, "step": 0.5, "default": 2},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
            {"name": "points", "label": "点数", "type": "slider", "min": 50, "max": 1000, "step": 50, "default": 200},
        ],
        "func": concentric_ellipse_fill_plotly,
    },
}

"""Arcs 模块 — 8 函数"""

from cprdspy.CPR_plotly1 import (
    arc_plotly, arc_inverse_plotly, arc_point_plotly, arc_point_inverse_plotly,
    arc_dot_plotly, arc_dot_inverse_plotly, oval_arc_plotly, arc_rotate_plotly,
)

MODULE_ID = "arcs"
MODULE_LABEL = "Arcs"
MODULE_ICON = "⌒"

FUNCTIONS = {
    "arc": {
        "label": "圆弧 (arc)",
        "params": [
            {"name": "r", "label": "半径", "type": "slider", "min": 0.1, "max": 10, "step": 0.1, "default": 1},
            {"name": "angle1", "label": "起始角", "type": "slider", "min": 0, "max": 360, "default": 45},
            {"name": "angle2", "label": "终止角", "type": "slider", "min": 0, "max": 360, "default": 135},
            {"name": "rotation", "label": "旋转", "type": "slider", "min": 0, "max": 360, "default": 0},
            {"name": "color", "label": "颜色", "type": "color", "default": "#e74c3c"},
            {"name": "line_width", "label": "线宽", "type": "slider", "min": 0.5, "max": 10, "step": 0.5, "default": 2},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
            {"name": "points", "label": "点数", "type": "slider", "min": 50, "max": 2000, "step": 50, "default": 1000},
        ],
        "func": arc_plotly,
    },
    "arc_inverse": {
        "label": "反向圆弧 (arc_inverse)",
        "params": [
            {"name": "r", "label": "半径", "type": "slider", "min": 0.1, "max": 10, "step": 0.1, "default": 1},
            {"name": "angle1", "label": "起始角", "type": "slider", "min": 0, "max": 360, "default": 30},
            {"name": "angle2", "label": "终止角", "type": "slider", "min": 0, "max": 360, "default": 200},
            {"name": "rotation", "label": "旋转", "type": "slider", "min": 0, "max": 360, "default": 0},
            {"name": "color", "label": "颜色", "type": "color", "default": "#2ecc71"},
            {"name": "line_width", "label": "线宽", "type": "slider", "min": 0.5, "max": 10, "step": 0.5, "default": 2},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
            {"name": "points", "label": "点数", "type": "slider", "min": 50, "max": 2000, "step": 50, "default": 1000},
        ],
        "func": arc_inverse_plotly,
    },
    "arc_point": {
        "label": "端点弧 (arc_point)",
        "params": [
            {"name": "point1_x", "label": "Point1 X", "type": "slider", "min": -5, "max": 5, "step": 0.1, "default": 1},
            {"name": "point1_y", "label": "Point1 Y", "type": "slider", "min": -5, "max": 5, "step": 0.1, "default": 0.5},
            {"name": "point2_x", "label": "Point2 X", "type": "slider", "min": -5, "max": 5, "step": 0.1, "default": -0.5},
            {"name": "point2_y", "label": "Point2 Y", "type": "slider", "min": -5, "max": 5, "step": 0.1, "default": 1},
            {"name": "color", "label": "颜色", "type": "color", "default": "#9b59b6"},
            {"name": "line_width", "label": "线宽", "type": "slider", "min": 0.5, "max": 10, "step": 0.5, "default": 2},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
            {"name": "points", "label": "点数", "type": "slider", "min": 50, "max": 2000, "step": 50, "default": 1000},
        ],
        "func": lambda point1_x, point1_y, point2_x, point2_y, color, line_width, alpha, points, **kw:
            arc_point_plotly(point1=(point1_x, point1_y), point2=(point2_x, point2_y),
                             color=color, line_width=line_width, alpha=alpha, points=points),
    },
    "arc_point_inverse": {
        "label": "反向端点弧 (arc_point_inverse)",
        "params": [
            {"name": "point1_x", "label": "Point1 X", "type": "slider", "min": -5, "max": 5, "step": 0.1, "default": 1},
            {"name": "point1_y", "label": "Point1 Y", "type": "slider", "min": -5, "max": 5, "step": 0.1, "default": 0.5},
            {"name": "point2_x", "label": "Point2 X", "type": "slider", "min": -5, "max": 5, "step": 0.1, "default": -0.5},
            {"name": "point2_y", "label": "Point2 Y", "type": "slider", "min": -5, "max": 5, "step": 0.1, "default": 1},
            {"name": "color", "label": "颜色", "type": "color", "default": "#e67e22"},
            {"name": "line_width", "label": "线宽", "type": "slider", "min": 0.5, "max": 10, "step": 0.5, "default": 2},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
            {"name": "points", "label": "点数", "type": "slider", "min": 50, "max": 2000, "step": 50, "default": 1000},
        ],
        "func": lambda point1_x, point1_y, point2_x, point2_y, color, line_width, alpha, points, **kw:
            arc_point_inverse_plotly(point1=(point1_x, point1_y), point2=(point2_x, point2_y),
                                     color=color, line_width=line_width, alpha=alpha, points=points),
    },
    "arc_dot": {
        "label": "弧点阵 (arc_dot)",
        "params": [
            {"name": "r", "label": "半径", "type": "slider", "min": 0.1, "max": 10, "step": 0.1, "default": 1},
            {"name": "angle1", "label": "起始角", "type": "slider", "min": 0, "max": 360, "default": 45},
            {"name": "angle2", "label": "终止角", "type": "slider", "min": 0, "max": 360, "default": 180},
            {"name": "rotation", "label": "旋转", "type": "slider", "min": 0, "max": 360, "default": 0},
            {"name": "color", "label": "颜色", "type": "color", "default": "#1abc9c"},
            {"name": "points", "label": "点数", "type": "slider", "min": 10, "max": 500, "step": 10, "default": 100},
        ],
        "func": lambda r, angle1, angle2, rotation, color, points, **kw:
            [__import__("plotly.graph_objects", fromlist=["Scatter"]).Scatter(
                x=arc_dot_plotly(r=r, angle1=angle1, angle2=angle2, rotation=rotation, points=points)[0],
                y=arc_dot_plotly(r=r, angle1=angle1, angle2=angle2, rotation=rotation, points=points)[1],
                mode="markers", marker=dict(color=color, size=4),
            )],
    },
    "arc_dot_inverse": {
        "label": "反向弧点阵 (arc_dot_inverse)",
        "params": [
            {"name": "r", "label": "半径", "type": "slider", "min": 0.1, "max": 10, "step": 0.1, "default": 1},
            {"name": "angle1", "label": "起始角", "type": "slider", "min": 0, "max": 360, "default": 30},
            {"name": "angle2", "label": "终止角", "type": "slider", "min": 0, "max": 360, "default": 200},
            {"name": "rotation", "label": "旋转", "type": "slider", "min": 0, "max": 360, "default": 0},
            {"name": "color", "label": "颜色", "type": "color", "default": "#e91e90"},
            {"name": "points", "label": "点数", "type": "slider", "min": 10, "max": 500, "step": 10, "default": 100},
        ],
        "func": lambda r, angle1, angle2, rotation, color, points, **kw:
            [__import__("plotly.graph_objects", fromlist=["Scatter"]).Scatter(
                x=arc_dot_inverse_plotly(r=r, angle1=angle1, angle2=angle2, rotation=rotation, points=points)[0],
                y=arc_dot_inverse_plotly(r=r, angle1=angle1, angle2=angle2, rotation=rotation, points=points)[1],
                mode="markers", marker=dict(color=color, size=4),
            )],
    },
    "oval_arc": {
        "label": "椭圆弧 (oval_arc)",
        "params": [
            {"name": "a", "label": "长轴 a", "type": "slider", "min": 0.5, "max": 10, "step": 0.1, "default": 2},
            {"name": "b", "label": "短轴 b", "type": "slider", "min": 0.5, "max": 10, "step": 0.1, "default": 1},
            {"name": "angle1", "label": "起始角", "type": "slider", "min": 0, "max": 360, "default": 30},
            {"name": "angle2", "label": "终止角", "type": "slider", "min": 0, "max": 360, "default": 200},
            {"name": "angle", "label": "椭圆旋转", "type": "slider", "min": 0, "max": 360, "default": 30},
            {"name": "color", "label": "颜色", "type": "color", "default": "#c2185b"},
            {"name": "line_width", "label": "线宽", "type": "slider", "min": 0.5, "max": 10, "step": 0.5, "default": 2},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
            {"name": "points", "label": "点数", "type": "slider", "min": 50, "max": 2000, "step": 50, "default": 1000},
        ],
        "func": oval_arc_plotly,
    },
    "arc_rotate": {
        "label": "旋转弧 (arc_rotate)",
        "params": [
            {"name": "r", "label": "半径", "type": "slider", "min": 0.1, "max": 10, "step": 0.1, "default": 1},
            {"name": "angle1", "label": "起始角", "type": "slider", "min": 0, "max": 360, "default": 30},
            {"name": "angle2", "label": "终止角", "type": "slider", "min": 0, "max": 360, "default": 150},
            {"name": "rotation", "label": "旋转", "type": "slider", "min": 0, "max": 360, "default": 60},
            {"name": "color", "label": "颜色", "type": "color", "default": "#1565c0"},
            {"name": "line_width", "label": "线宽", "type": "slider", "min": 0.5, "max": 10, "step": 0.5, "default": 2},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
            {"name": "points", "label": "点数", "type": "slider", "min": 50, "max": 2000, "step": 50, "default": 1000},
        ],
        "func": arc_rotate_plotly,
    },
}

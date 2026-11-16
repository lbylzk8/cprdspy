"""Stars 模块 — 2 函数"""

from cprdspy.CPR_plotly1 import star_plotly, stars_plotly

MODULE_ID = "stars"
MODULE_LABEL = "Stars"
MODULE_ICON = "★"

FUNCTIONS = {
    "star": {
        "label": "单层星 (star)",
        "params": [
            {"name": "R", "label": "内圆半径 R", "type": "slider", "min": 0.1, "max": 5, "step": 0.1, "default": 1},
            {"name": "r", "label": "弧半径 r", "type": "slider", "min": 0.1, "max": 5, "step": 0.1, "default": 1},
            {"name": "n", "label": "弧数 n", "type": "slider", "min": 2, "max": 12, "step": 1, "default": 4},
            {"name": "N", "label": "星角数 N", "type": "slider", "min": 2, "max": 24, "step": 1, "default": 12},
            {"name": "rotation", "label": "旋转°", "type": "slider", "min": 0, "max": 360, "default": 0},
            {"name": "color", "label": "颜色", "type": "color", "default": "#f1c40f"},
            {"name": "line_width", "label": "线宽", "type": "slider", "min": 0.5, "max": 8, "step": 0.5, "default": 2},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
            {"name": "points", "label": "点数", "type": "slider", "min": 50, "max": 2000, "step": 50, "default": 500},
        ],
        "func": star_plotly,
    },
    "stars": {
        "label": "多层星 (stars)",
        "params": [
            {"name": "R", "label": "内圆半径 R", "type": "slider", "min": 0.1, "max": 5, "step": 0.1, "default": 1},
            {"name": "r", "label": "弧半径 r", "type": "slider", "min": 0.1, "max": 5, "step": 0.1, "default": 1.2},
            {"name": "n", "label": "弧数 n", "type": "slider", "min": 2, "max": 12, "step": 1, "default": 4},
            {"name": "ratio", "label": "层缩放比", "type": "slider", "min": 1, "max": 3, "step": 0.1, "default": 1.5},
            {"name": "M", "label": "层数 M", "type": "slider", "min": 1, "max": 8, "step": 1, "default": 3},
            {"name": "N", "label": "每层角数 N", "type": "slider", "min": 2, "max": 24, "step": 1, "default": 12},
            {"name": "rotation", "label": "旋转°", "type": "slider", "min": 0, "max": 360, "default": 0},
            {"name": "color", "label": "颜色", "type": "color", "default": "#e67e22"},
            {"name": "line_width", "label": "线宽", "type": "slider", "min": 0.5, "max": 8, "step": 0.5, "default": 1.5},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
            {"name": "points", "label": "点数", "type": "slider", "min": 50, "max": 2000, "step": 50, "default": 500},
        ],
        "func": stars_plotly,
    },
}

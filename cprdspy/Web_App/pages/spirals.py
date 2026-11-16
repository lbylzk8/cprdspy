"""Spirals 模块 — 5 函数"""

from cprdspy.CPR_plotly1 import (
    logSpiral_plotly, nSpiral_plotly, nSpirals_plotly,
    calla_petal_plotly, calla_plotly,
)

MODULE_ID = "spirals"
MODULE_LABEL = "Spirals"
MODULE_ICON = "◎"

DIR_OPTIONS = [
    {"label": "双向 (both)", "value": "both"},
    {"label": "向外 (out)", "value": "out"},
    {"label": "向内 (in)", "value": "in"},
]

FUNCTIONS = {
    "logSpiral": {
        "label": "对数螺线 (logSpiral)",
        "params": [
            {"name": "n", "label": "花瓣数 n", "type": "slider", "min": 2, "max": 12, "step": 1, "default": 4},
            {"name": "a", "label": "X 缩放 a", "type": "slider", "min": 0.5, "max": 5, "step": 0.1, "default": 1},
            {"name": "b", "label": "Y 缩放 b", "type": "slider", "min": 0.5, "max": 5, "step": 0.1, "default": 1},
            {"name": "cyc", "label": "周期数", "type": "slider", "min": 0.25, "max": 5, "step": 0.25, "default": 2},
            {"name": "theta", "label": "相位 θ°", "type": "slider", "min": 0, "max": 360, "default": 0},
            {"name": "rotation", "label": "旋转°", "type": "slider", "min": 0, "max": 360, "default": 0},
            {"name": "direction", "label": "方向", "type": "dropdown", "options": DIR_OPTIONS, "default": "both"},
            {"name": "color", "label": "颜色", "type": "color", "default": "#3498db"},
            {"name": "line_width", "label": "线宽", "type": "slider", "min": 0.5, "max": 8, "step": 0.5, "default": 1.5},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
        ],
        "func": logSpiral_plotly,
    },
    "nSpiral": {
        "label": "N 边形螺旋 (nSpiral)",
        "params": [
            {"name": "n", "label": "边数 n", "type": "slider", "min": 2, "max": 12, "step": 1, "default": 4},
            {"name": "a", "label": "缩放 a", "type": "slider", "min": 0.5, "max": 5, "step": 0.1, "default": 1},
            {"name": "N", "label": "螺旋数 N", "type": "slider", "min": 2, "max": 12, "step": 1, "default": 4},
            {"name": "cyc", "label": "周期数", "type": "slider", "min": 0.25, "max": 3, "step": 0.25, "default": 1.5},
            {"name": "theta", "label": "相位 θ°", "type": "slider", "min": 0, "max": 90, "default": 15},
            {"name": "rotation", "label": "旋转°", "type": "slider", "min": 0, "max": 360, "default": 0},
            {"name": "direction", "label": "方向", "type": "dropdown", "options": DIR_OPTIONS, "default": "both"},
            {"name": "color", "label": "颜色", "type": "color", "default": "#e74c3c"},
            {"name": "line_width", "label": "线宽", "type": "slider", "min": 0.5, "max": 8, "step": 0.5, "default": 1},
        ],
        "func": nSpiral_plotly,
    },
    "nSpirals": {
        "label": "多头螺线 (nSpirals)",
        "params": [
            {"name": "n", "label": "边数 n", "type": "slider", "min": 2, "max": 12, "step": 1, "default": 4},
            {"name": "N", "label": "头数 N", "type": "slider", "min": 2, "max": 12, "step": 1, "default": 5},
            {"name": "cyc", "label": "周期数", "type": "slider", "min": 0.25, "max": 3, "step": 0.25, "default": 1},
            {"name": "theta", "label": "相位 θ°", "type": "slider", "min": 0, "max": 90, "default": 0},
            {"name": "rotation", "label": "旋转°", "type": "slider", "min": 0, "max": 360, "default": 0},
            {"name": "direction", "label": "方向", "type": "dropdown", "options": DIR_OPTIONS, "default": "both"},
            {"name": "color", "label": "颜色", "type": "color", "default": "#2ecc71"},
            {"name": "line_width", "label": "线宽", "type": "slider", "min": 0.5, "max": 8, "step": 0.5, "default": 1},
        ],
        "func": nSpirals_plotly,
    },
    "calla_petal": {
        "label": "马蹄莲花瓣 (calla_petal)",
        "params": [
            {"name": "n", "label": "边数 n", "type": "slider", "min": 2, "max": 12, "step": 1, "default": 4},
            {"name": "a", "label": "缩放 a", "type": "slider", "min": 0.5, "max": 5, "step": 0.1, "default": 1},
            {"name": "cyc", "label": "周期数", "type": "slider", "min": 0.5, "max": 3, "step": 0.25, "default": 1.25},
            {"name": "theta", "label": "相位 θ°", "type": "slider", "min": 0, "max": 360, "default": 0},
            {"name": "rotation", "label": "旋转°", "type": "slider", "min": 0, "max": 360, "default": 0},
            {"name": "direction", "label": "方向", "type": "dropdown", "options": DIR_OPTIONS, "default": "both"},
            {"name": "color", "label": "颜色", "type": "color", "default": "#9b59b6"},
            {"name": "line_width", "label": "线宽", "type": "slider", "min": 0.5, "max": 8, "step": 0.5, "default": 1.5},
        ],
        "func": calla_petal_plotly,
    },
    "calla": {
        "label": "完整马蹄莲 (calla)",
        "params": [
            {"name": "n", "label": "边数 n", "type": "slider", "min": 2, "max": 12, "step": 1, "default": 4},
            {"name": "a", "label": "缩放 a", "type": "slider", "min": 0.5, "max": 5, "step": 0.1, "default": 1},
            {"name": "cyc", "label": "周期数", "type": "slider", "min": 0.5, "max": 3, "step": 0.25, "default": 1.25},
            {"name": "N", "label": "花瓣数 N", "type": "slider", "min": 2, "max": 24, "step": 1, "default": 12},
            {"name": "theta", "label": "相位 θ°", "type": "slider", "min": 0, "max": 360, "default": 0},
            {"name": "rotation", "label": "旋转°", "type": "slider", "min": 0, "max": 360, "default": 0},
            {"name": "direction", "label": "方向", "type": "dropdown", "options": DIR_OPTIONS, "default": "both"},
            {"name": "line_width", "label": "线宽", "type": "slider", "min": 0.5, "max": 8, "step": 0.5, "default": 1},
        ],
        "func": calla_plotly,
    },
}

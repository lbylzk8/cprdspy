"""Waves 模块 — 8 函数"""

from cprdspy.CPR_plotly1 import (
    wave_plotly, wave_fill_plotly, wave_wave_plotly, wave_wave_fill_plotly,
    wave_ari_plotly, wave_ari_fill_plotly, wave_geo_plotly, wave_geo_fill_plotly,
)

MODULE_ID = "waves"
MODULE_LABEL = "Waves"
MODULE_ICON = "≈"

DIR_OPTIONS = [
    {"label": "双向", "value": "both"},
    {"label": "向外", "value": "out"},
    {"label": "向内", "value": "in"},
]

MODE_OPTIONS = [
    {"label": "等差 (arithmetic)", "value": "arithmetic"},
    {"label": "等比 (geometric)", "value": "geometric"},
]

FUNCTIONS = {
    "wave": {
        "label": "统一波 (wave)",
        "params": [
            {"name": "A", "label": "振幅 A", "type": "slider", "min": 0.05, "max": 3, "step": 0.05, "default": 0.3},
            {"name": "F", "label": "频率 F", "type": "slider", "min": 1, "max": 8, "step": 1, "default": 2},
            {"name": "P", "label": "周期 P", "type": "slider", "min": 3, "max": 24, "step": 1, "default": 8},
            {"name": "mode", "label": "模式", "type": "dropdown", "options": MODE_OPTIONS, "default": "geometric"},
            {"name": "rotation", "label": "旋转°", "type": "slider", "min": 0, "max": 360, "default": 0},
            {"name": "direction", "label": "方向", "type": "dropdown", "options": DIR_OPTIONS, "default": "both"},
            {"name": "R", "label": "基准半径", "type": "slider", "min": 0.1, "max": 5, "step": 0.1, "default": 1},
            {"name": "color", "label": "颜色", "type": "color", "default": "#3498db"},
            {"name": "line_width", "label": "线宽", "type": "slider", "min": 0.5, "max": 5, "step": 0.5, "default": 1},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
            {"name": "points", "label": "点数", "type": "slider", "min": 100, "max": 2000, "step": 100, "default": 1000},
        ],
        "func": wave_plotly,
    },
    "wave_fill": {
        "label": "填充波 (wave_fill)",
        "params": [
            {"name": "A", "label": "振幅 A", "type": "slider", "min": 0.05, "max": 3, "step": 0.05, "default": 0.3},
            {"name": "F", "label": "频率 F", "type": "slider", "min": 1, "max": 8, "step": 1, "default": 3},
            {"name": "P", "label": "周期 P", "type": "slider", "min": 3, "max": 24, "step": 1, "default": 12},
            {"name": "mode", "label": "模式", "type": "dropdown", "options": MODE_OPTIONS, "default": "arithmetic"},
            {"name": "rotation", "label": "旋转°", "type": "slider", "min": 0, "max": 360, "default": 0},
            {"name": "direction", "label": "方向", "type": "dropdown", "options": DIR_OPTIONS, "default": "both"},
            {"name": "R", "label": "基准半径", "type": "slider", "min": 0.1, "max": 5, "step": 0.1, "default": 1},
            {"name": "color", "label": "边线色", "type": "color", "default": "#1abc9c"},
            {"name": "fill_color", "label": "填充色", "type": "color", "default": "#d1f2eb"},
            {"name": "fill_alpha", "label": "填充透明度", "type": "slider", "min": 0.05, "max": 1, "step": 0.05, "default": 0.3},
            {"name": "edge_width", "label": "边线宽", "type": "slider", "min": 0.5, "max": 5, "step": 0.5, "default": 1},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
            {"name": "points", "label": "点数", "type": "slider", "min": 100, "max": 2000, "step": 100, "default": 1000},
        ],
        "func": wave_fill_plotly,
    },
    "wave_ari": {
        "label": "等差波 (wave_ari)",
        "params": [
            {"name": "A", "label": "振幅 A", "type": "slider", "min": 0.05, "max": 3, "step": 0.05, "default": 0.2},
            {"name": "F", "label": "频率 F", "type": "slider", "min": 1, "max": 8, "step": 1, "default": 3},
            {"name": "P", "label": "周期 P", "type": "slider", "min": 3, "max": 24, "step": 1, "default": 12},
            {"name": "rotation", "label": "旋转°", "type": "slider", "min": 0, "max": 360, "default": 0},
            {"name": "direction", "label": "方向", "type": "dropdown", "options": DIR_OPTIONS, "default": "both"},
            {"name": "R", "label": "基准半径", "type": "slider", "min": 0.1, "max": 5, "step": 0.1, "default": 1},
            {"name": "color", "label": "颜色", "type": "color", "default": "#e67e22"},
            {"name": "line_width", "label": "线宽", "type": "slider", "min": 0.5, "max": 5, "step": 0.5, "default": 1},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
            {"name": "points", "label": "点数", "type": "slider", "min": 100, "max": 2000, "step": 100, "default": 1000},
        ],
        "func": wave_ari_plotly,
    },
    "wave_ari_fill": {
        "label": "填充等差波 (wave_ari_fill)",
        "params": [
            {"name": "A", "label": "振幅 A", "type": "slider", "min": 0.05, "max": 3, "step": 0.05, "default": 0.3},
            {"name": "F", "label": "频率 F", "type": "slider", "min": 1, "max": 8, "step": 1, "default": 3},
            {"name": "P", "label": "周期 P", "type": "slider", "min": 3, "max": 24, "step": 1, "default": 12},
            {"name": "rotation", "label": "旋转°", "type": "slider", "min": 0, "max": 360, "default": 0},
            {"name": "direction", "label": "方向", "type": "dropdown", "options": DIR_OPTIONS, "default": "both"},
            {"name": "R", "label": "基准半径", "type": "slider", "min": 0.1, "max": 5, "step": 0.1, "default": 1},
            {"name": "color", "label": "边线色", "type": "color", "default": "#c2185b"},
            {"name": "fill_color", "label": "填充色", "type": "color", "default": "#f8bbd0"},
            {"name": "fill_alpha", "label": "填充透明度", "type": "slider", "min": 0.05, "max": 1, "step": 0.05, "default": 0.3},
            {"name": "edge_width", "label": "边线宽", "type": "slider", "min": 0.5, "max": 5, "step": 0.5, "default": 1},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
            {"name": "points", "label": "点数", "type": "slider", "min": 100, "max": 2000, "step": 100, "default": 1000},
        ],
        "func": wave_ari_fill_plotly,
    },
    "wave_geo": {
        "label": "等比波 (wave_geo)",
        "params": [
            {"name": "A", "label": "振幅 A", "type": "slider", "min": 0.05, "max": 3, "step": 0.05, "default": 0.2},
            {"name": "F", "label": "频率 F", "type": "slider", "min": 1, "max": 8, "step": 1, "default": 2},
            {"name": "P", "label": "周期 P", "type": "slider", "min": 3, "max": 24, "step": 1, "default": 10},
            {"name": "rotation", "label": "旋转°", "type": "slider", "min": 0, "max": 360, "default": 0},
            {"name": "direction", "label": "方向", "type": "dropdown", "options": DIR_OPTIONS, "default": "both"},
            {"name": "R", "label": "基准半径", "type": "slider", "min": 0.1, "max": 5, "step": 0.1, "default": 1},
            {"name": "color", "label": "颜色", "type": "color", "default": "#9b59b6"},
            {"name": "line_width", "label": "线宽", "type": "slider", "min": 0.5, "max": 5, "step": 0.5, "default": 1},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
            {"name": "points", "label": "点数", "type": "slider", "min": 100, "max": 2000, "step": 100, "default": 1000},
        ],
        "func": wave_geo_plotly,
    },
    "wave_geo_fill": {
        "label": "填充等比波 (wave_geo_fill)",
        "params": [
            {"name": "A", "label": "振幅 A", "type": "slider", "min": 0.05, "max": 3, "step": 0.05, "default": 0.2},
            {"name": "F", "label": "频率 F", "type": "slider", "min": 1, "max": 8, "step": 1, "default": 3},
            {"name": "P", "label": "周期 P", "type": "slider", "min": 3, "max": 24, "step": 1, "default": 12},
            {"name": "rotation", "label": "旋转°", "type": "slider", "min": 0, "max": 360, "default": 0},
            {"name": "direction", "label": "方向", "type": "dropdown", "options": DIR_OPTIONS, "default": "both"},
            {"name": "R", "label": "基准半径", "type": "slider", "min": 0.1, "max": 5, "step": 0.1, "default": 1},
            {"name": "color", "label": "边线色", "type": "color", "default": "#8d6e63"},
            {"name": "fill_color", "label": "填充色", "type": "color", "default": "#d7ccc8"},
            {"name": "fill_alpha", "label": "填充透明度", "type": "slider", "min": 0.05, "max": 1, "step": 0.05, "default": 0.3},
            {"name": "edge_width", "label": "边线宽", "type": "slider", "min": 0.5, "max": 5, "step": 0.5, "default": 1},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
            {"name": "points", "label": "点数", "type": "slider", "min": 100, "max": 2000, "step": 100, "default": 1000},
        ],
        "func": wave_geo_fill_plotly,
    },
    "wave_wave": {
        "label": "波中波 (wave_wave)",
        "params": [
            {"name": "A", "label": "振幅 A", "type": "slider", "min": 0.05, "max": 2, "step": 0.05, "default": 0.15},
            {"name": "F", "label": "频率 F", "type": "slider", "min": 1, "max": 6, "step": 1, "default": 2},
            {"name": "P", "label": "周期 P", "type": "slider", "min": 3, "max": 16, "step": 1, "default": 8},
            {"name": "mode", "label": "模式", "type": "dropdown", "options": MODE_OPTIONS, "default": "geometric"},
            {"name": "rotation", "label": "旋转°", "type": "slider", "min": 0, "max": 360, "default": 0},
            {"name": "direction", "label": "方向", "type": "dropdown", "options": DIR_OPTIONS, "default": "both"},
            {"name": "R", "label": "基准半径", "type": "slider", "min": 0.1, "max": 5, "step": 0.1, "default": 1},
            {"name": "color", "label": "颜色", "type": "color", "default": "#e67e22"},
            {"name": "line_width", "label": "线宽", "type": "slider", "min": 0.5, "max": 5, "step": 0.5, "default": 0.8},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
            {"name": "points", "label": "点数", "type": "slider", "min": 100, "max": 2000, "step": 100, "default": 1000},
        ],
        "func": wave_wave_plotly,
    },
    "wave_wave_fill": {
        "label": "填充波中波 (wave_wave_fill)",
        "params": [
            {"name": "A", "label": "振幅 A", "type": "slider", "min": 0.05, "max": 2, "step": 0.05, "default": 0.15},
            {"name": "F", "label": "频率 F", "type": "slider", "min": 1, "max": 6, "step": 1, "default": 2},
            {"name": "P", "label": "周期 P", "type": "slider", "min": 3, "max": 16, "step": 1, "default": 8},
            {"name": "mode", "label": "模式", "type": "dropdown", "options": MODE_OPTIONS, "default": "geometric"},
            {"name": "rotation", "label": "旋转°", "type": "slider", "min": 0, "max": 360, "default": 0},
            {"name": "direction", "label": "方向", "type": "dropdown", "options": DIR_OPTIONS, "default": "both"},
            {"name": "R", "label": "基准半径", "type": "slider", "min": 0.1, "max": 5, "step": 0.1, "default": 1},
            {"name": "color", "label": "边线色", "type": "color", "default": "#2ecc71"},
            {"name": "fill_color", "label": "填充色", "type": "color", "default": "#a9dfbf"},
            {"name": "fill_alpha", "label": "填充透明度", "type": "slider", "min": 0.05, "max": 1, "step": 0.05, "default": 0.3},
            {"name": "edge_width", "label": "边线宽", "type": "slider", "min": 0.5, "max": 5, "step": 0.5, "default": 0.8},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
            {"name": "points", "label": "点数", "type": "slider", "min": 100, "max": 2000, "step": 100, "default": 1000},
        ],
        "func": wave_wave_fill_plotly,
    },
}

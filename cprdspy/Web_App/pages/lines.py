"""Lines 模块 — 14 函数"""

from cprdspy.CPR_plotly1 import (
    Lines_plotly, connect_plotly, connect_all_plotly, multi_polygon_plotly,
    metatron_cube_plotly, krystal_cube_plotly, swastika_plotly, swastika_lines_plotly,
    draw_lines_plotly, draw_multi_polygon_plotly, draw_metatron_cube_plotly,
    draw_krystal_cube_plotly, draw_swastika_plotly, draw_swastikas_plotly,
)
from cprdspy.CPR_plotly1.Dots.dot import Dots as Dots_plotly, n_dots

MODULE_ID = "lines"
MODULE_LABEL = "Lines"
MODULE_ICON = "╱"

COLOR_BY_OPTIONS = [
    {"label": "无 (统一色)", "value": "none"},
    {"label": "序号 (index)", "value": "index"},
    {"label": "角度 (angle)", "value": "angle"},
    {"label": "长度 (length)", "value": "length"},
]

CMAP_OPTIONS = [
    {"label": "Plasma", "value": "plasma"},
    {"label": "Viridis", "value": "viridis"},
    {"label": "Inferno", "value": "inferno"},
    {"label": "Magma", "value": "magma"},
    {"label": "Turbo", "value": "turbo"},
    {"label": "Coolwarm", "value": "coolwarm"},
]

DIR_OPTIONS = [
    {"label": "双向", "value": "both"},
    {"label": "向外", "value": "out"},
    {"label": "向内", "value": "in"},
]

FUNCTIONS = {
    "connect": {
        "label": "顺序连线 (connect)",
        "params": [
            {"name": "n", "label": "点数", "type": "slider", "min": 3, "max": 30, "step": 1, "default": 8},
            {"name": "R", "label": "半径", "type": "slider", "min": 0.1, "max": 5, "step": 0.1, "default": 1},
            {"name": "closed", "label": "闭合", "type": "toggle", "options": [
                {"label": "是", "value": "yes"}, {"label": "否", "value": "no"},
            ], "default": "yes"},
            {"name": "color", "label": "颜色", "type": "color", "default": "#e74c3c"},
            {"name": "line_width", "label": "线宽", "type": "slider", "min": 0.5, "max": 8, "step": 0.5, "default": 2},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
        ],
        "func": lambda n, R, closed, color, line_width, alpha, **kw:
            draw_lines_plotly(connect_plotly(n_dots(n=n, R=R), closed=(closed == "yes")),
                            color=color, line_width=line_width, alpha=alpha),
    },
    "connect_all": {
        "label": "全连接 (connect_all)",
        "params": [
            {"name": "n", "label": "点数", "type": "slider", "min": 3, "max": 12, "step": 1, "default": 5},
            {"name": "R", "label": "半径", "type": "slider", "min": 0.1, "max": 5, "step": 0.1, "default": 1},
            {"name": "color", "label": "颜色", "type": "color", "default": "#3498db"},
            {"name": "line_width", "label": "线宽", "type": "slider", "min": 0.5, "max": 8, "step": 0.5, "default": 1},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 0.4},
        ],
        "func": lambda n, R, color, line_width, alpha, **kw:
            draw_lines_plotly(connect_all_plotly(n_dots(n=n, R=R)),
                            color=color, line_width=line_width, alpha=alpha),
    },
    "multi_polygon": {
        "label": "多层多边形 (multi_polygon)",
        "params": [
            {"name": "n", "label": "每层边数", "type": "slider", "min": 3, "max": 20, "step": 1, "default": 6},
            {"name": "m", "label": "层数", "type": "slider", "min": 1, "max": 10, "step": 1, "default": 3},
            {"name": "R", "label": "基准半径", "type": "slider", "min": 0.1, "max": 5, "step": 0.1, "default": 1},
            {"name": "direction", "label": "方向", "type": "dropdown", "options": DIR_OPTIONS, "default": "both"},
            {"name": "color", "label": "颜色", "type": "color", "default": "#2ecc71"},
            {"name": "line_width", "label": "线宽", "type": "slider", "min": 0.5, "max": 8, "step": 0.5, "default": 1.5},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
            {"name": "color_by", "label": "着色", "type": "dropdown", "options": COLOR_BY_OPTIONS, "default": "none"},
            {"name": "cmap", "label": "色板", "type": "dropdown", "options": CMAP_OPTIONS, "default": "plasma"},
        ],
        "func": lambda n, m, R, direction, color, line_width, alpha, color_by, cmap, **kw:
            draw_multi_polygon_plotly(n=n, m=m, R=R, direction=direction,
                                      color=color, line_width=line_width, alpha=alpha,
                                      color_by=None if color_by == "none" else color_by, cmap=cmap),
    },
    "metatron_cube": {
        "label": "梅塔特隆立方体 (metatron_cube)",
        "params": [
            {"name": "n", "label": "每层点数", "type": "slider", "min": 3, "max": 12, "step": 1, "default": 6},
            {"name": "m", "label": "层数", "type": "slider", "min": 1, "max": 5, "step": 1, "default": 3},
            {"name": "rotation", "label": "旋转°", "type": "slider", "min": 0, "max": 360, "default": 0},
            {"name": "color", "label": "颜色", "type": "color", "default": "#9b59b6"},
            {"name": "line_width", "label": "线宽", "type": "slider", "min": 0.5, "max": 5, "step": 0.5, "default": 0.8},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 0.5},
            {"name": "color_by", "label": "着色", "type": "dropdown", "options": COLOR_BY_OPTIONS, "default": "none"},
            {"name": "cmap", "label": "色板", "type": "dropdown", "options": CMAP_OPTIONS, "default": "plasma"},
        ],
        "func": lambda n, m, rotation, color, line_width, alpha, color_by, cmap, **kw:
            draw_metatron_cube_plotly(n=n, m=m, rotation=rotation,
                                      color=color, line_width=line_width, alpha=alpha,
                                      color_by=None if color_by == "none" else color_by, cmap=cmap),
    },
    "krystal_cube": {
        "label": "水晶立方体 (krystal_cube)",
        "params": [
            {"name": "n", "label": "每层点数", "type": "slider", "min": 3, "max": 10, "step": 1, "default": 6},
            {"name": "m", "label": "层数", "type": "slider", "min": 1, "max": 5, "step": 1, "default": 3},
            {"name": "rotation", "label": "旋转°", "type": "slider", "min": 0, "max": 360, "default": 0},
            {"name": "direction", "label": "方向", "type": "dropdown", "options": DIR_OPTIONS, "default": "both"},
            {"name": "color", "label": "颜色", "type": "color", "default": "#e67e22"},
            {"name": "line_width", "label": "线宽", "type": "slider", "min": 0.5, "max": 5, "step": 0.5, "default": 0.8},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 0.5},
            {"name": "color_by", "label": "着色", "type": "dropdown", "options": COLOR_BY_OPTIONS, "default": "none"},
            {"name": "cmap", "label": "色板", "type": "dropdown", "options": CMAP_OPTIONS, "default": "plasma"},
        ],
        "func": lambda n, m, rotation, direction, color, line_width, alpha, color_by, cmap, **kw:
            draw_krystal_cube_plotly(n=n, m=m, rotation=rotation, direction=direction,
                                     color=color, line_width=line_width, alpha=alpha,
                                     color_by=None if color_by == "none" else color_by, cmap=cmap),
    },
    "draw_swastika": {
        "label": "卍字 (draw_swastika)",
        "params": [
            {"name": "n", "label": "阶数", "type": "slider", "min": 2, "max": 8, "step": 1, "default": 4},
            {"name": "R", "label": "基准大小", "type": "slider", "min": 0.1, "max": 5, "step": 0.1, "default": 1},
            {"name": "rotation", "label": "旋转°", "type": "slider", "min": 0, "max": 360, "default": 0},
            {"name": "color", "label": "颜色", "type": "color", "default": "#1abc9c"},
            {"name": "line_width", "label": "线宽", "type": "slider", "min": 0.5, "max": 8, "step": 0.5, "default": 2},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
        ],
        "func": draw_swastika_plotly,
    },
    "draw_swastikas": {
        "label": "多重卍字 (draw_swastikas)",
        "params": [
            {"name": "n", "label": "阶数", "type": "slider", "min": 2, "max": 6, "step": 1, "default": 3},
            {"name": "R", "label": "基准大小", "type": "slider", "min": 0.1, "max": 5, "step": 0.1, "default": 1},
            {"name": "m", "label": "旋转数", "type": "slider", "min": 2, "max": 16, "step": 1, "default": 8},
            {"name": "rotation", "label": "旋转°", "type": "slider", "min": 0, "max": 360, "default": 12},
            {"name": "color", "label": "颜色", "type": "color", "default": "#e74c3c"},
            {"name": "line_width", "label": "线宽", "type": "slider", "min": 0.5, "max": 8, "step": 0.5, "default": 1.5},
            {"name": "alpha", "label": "透明度", "type": "slider", "min": 0.1, "max": 1, "step": 0.05, "default": 1},
        ],
        "func": draw_swastikas_plotly,
    },
}

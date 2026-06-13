"""
cprdspy.CPR_matplotlib — Matplotlib 绘图模块

提供使用 Matplotlib 绘制各种几何图形的功能：
  - 圆形 (Circles)    · 弧线 (Arcs)      · 螺旋线 (Spirals)
  - 花朵 (Flowers)    · 点阵 (Dots)       · 线条 (Lines)
  - 波形 (Waves)      · 星形 (Stars)
"""

from .Dots.dot import Dots, n_dots, draw_dots, n_dots_array, draw_n_dots_array
from .Lines.line import (
    Lines,
    connect,
    connect_all,
    multi_polygon,
    metatron_cube,
    krystal_cube,
    swastika,
    swastika_lines,
    draw_lines,
    draw_multi_polygon,
    draw_metatron_cube,
    draw_krystal_cube,
    draw_swastika,
    draw_swastikas,
)
from .Circles.circle import (
    circle,
    draw_circle,
    circle_p,
    ellipse,
    concentric_circles,
    concentric_ellipse,
)
from .Arcs.arc import (
    arc_point,
    arc_point_inverse,
    arc,
    arc_inverse,
    arc_dot,
    arc_dot_inverse,
    oval_arc,
    arc_rotate,
)
from .Flowers.flower import (
    flower_petal,
    flower,
    flowers,
    rotate_point,
    oval_petal_a,
    oval_petal,
    oval_flower,
    oval_flower_a,
)
from .Spirals.spiral import logSpiral, nSpiral, nSpirals, calla_petal, calla
from .Waves.waves import wave, wave_wave, wave_ari, wave_geo
from .Stars.star import star, stars

__all__ = [
    # Dots
    "Dots",
    "n_dots",
    "draw_dots",
    "n_dots_array",
    "draw_n_dots_array",
    # Lines
    "Lines",
    "connect",
    "connect_all",
    "multi_polygon",
    "metatron_cube",
    "krystal_cube",
    "swastika",
    "swastika_lines",
    "draw_lines",
    "draw_multi_polygon",
    "draw_metatron_cube",
    "draw_krystal_cube",
    "draw_swastika",
    "draw_swastikas",
    # Circles
    "circle",
    "draw_circle",
    "circle_p",
    "ellipse",
    "concentric_circles",
    "concentric_ellipse",
    # Arcs
    "arc_point",
    "arc_point_inverse",
    "arc",
    "arc_inverse",
    "arc_dot",
    "arc_dot_inverse",
    "oval_arc",
    "arc_rotate",
    # Flowers
    "flower_petal",
    "flower",
    "flowers",
    "rotate_point",
    "oval_petal_a",
    "oval_petal",
    "oval_flower",
    "oval_flower_a",
    # Spirals
    "logSpiral",
    "nSpiral",
    "nSpirals",
    "calla_petal",
    "calla",
    # Waves
    "wave",
    "wave_wave",
    "wave_ari",
    "wave_geo",
    # Stars
    "star",
    "stars",
]

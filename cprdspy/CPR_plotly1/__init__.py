"""
cprdspy.CPR_plotly1 — Plotly 绘图模块

提供使用 Plotly 绘制各种几何图形的功能：
  - 圆形 (Circles)    · 弧线 (Arcs)      · 螺旋线 (Spirals)
  - 花朵 (Flowers)    · 点阵 (Dots)       · 线条 (Lines)
  - 波形 (Waves)      · 星形 (Stars)

所有函数都以 `_plotly` 后缀结尾，以区分于 Matplotlib 版本。
"""

from .Dots.dot import Dots as Dots_plotly
from .Dots.dot import n_dots as n_dots_plotly
from .Dots.dot import draw_dots as draw_dots_plotly
from .Dots.dot import n_dots_array as n_dots_array_plotly
from .Dots.dot import draw_n_dots_array as draw_n_dots_array_plotly

from .Lines.line import Lines as Lines_plotly
from .Lines.line import connect as connect_plotly
from .Lines.line import connect_all as connect_all_plotly
from .Lines.line import multi_polygon as multi_polygon_plotly
from .Lines.line import metatron_cube as metatron_cube_plotly
from .Lines.line import krystal_cube as krystal_cube_plotly
from .Lines.line import swastika as swastika_plotly
from .Lines.line import swastika_lines as swastika_lines_plotly
from .Lines.line import draw_lines as draw_lines_plotly
from .Lines.line import draw_multi_polygon as draw_multi_polygon_plotly
from .Lines.line import draw_metatron_cube as draw_metatron_cube_plotly
from .Lines.line import draw_krystal_cube as draw_krystal_cube_plotly
from .Lines.line import draw_swastika as draw_swastika_plotly
from .Lines.line import draw_swastikas as draw_swastikas_plotly

from .Circles.circle import circle as circle_plotly
from .Circles.circle import circle_fill as circle_fill_plotly
from .Circles.circle import draw_circle as draw_circle_plotly
from .Circles.circle import circle_p as circle_p_plotly
from .Circles.circle import ellipse as ellipse_plotly
from .Circles.circle import ellipse_fill as ellipse_fill_plotly
from .Circles.circle import concentric_circles as concentric_circles_plotly
from .Circles.circle import concentric_circles_fill as concentric_circles_fill_plotly
from .Circles.circle import concentric_ellipse as concentric_ellipse_plotly
from .Circles.circle import concentric_ellipse_fill as concentric_ellipse_fill_plotly

from .Arcs.arc import arc_point as arc_point_plotly
from .Arcs.arc import arc_point_inverse as arc_point_inverse_plotly
from .Arcs.arc import arc as arc_plotly
from .Arcs.arc import arc_inverse as arc_inverse_plotly
from .Arcs.arc import arc_dot as arc_dot_plotly
from .Arcs.arc import arc_dot_inverse as arc_dot_inverse_plotly
from .Arcs.arc import oval_arc as oval_arc_plotly
from .Arcs.arc import arc_rotate as arc_rotate_plotly

from .Flowers.flower import flower_petal as flower_petal_plotly
from .Flowers.flower import flower_petal_fill as flower_petal_fill_plotly
from .Flowers.flower import flower as flower_plotly
from .Flowers.flower import flower_fill as flower_fill_plotly
from .Flowers.flower import flowers as flowers_plotly
from .Flowers.flower import rotate_point as rotate_point_plotly
from .Flowers.flower import oval_petal_a as oval_petal_a_plotly
from .Flowers.flower import oval_petal as oval_petal_plotly
from .Flowers.flower import oval_petal_fill as oval_petal_fill_plotly
from .Flowers.flower import oval_flower as oval_flower_plotly
from .Flowers.flower import oval_flower_fill as oval_flower_fill_plotly
from .Flowers.flower import oval_flower_a as oval_flower_a_plotly
from .Flowers.flower import oval_flower_a_fill as oval_flower_a_fill_plotly

from .Spirals.spiral import logSpiral as logSpiral_plotly
from .Spirals.spiral import nSpiral as nSpiral_plotly
from .Spirals.spiral import nSpirals as nSpirals_plotly
from .Spirals.spiral import calla_petal as calla_petal_plotly
from .Spirals.spiral import calla as calla_plotly

from .Waves.waves import wave as wave_plotly
from .Waves.waves import wave_fill as wave_fill_plotly
from .Waves.waves import wave_wave as wave_wave_plotly
from .Waves.waves import wave_wave_fill as wave_wave_fill_plotly
from .Waves.waves import wave_ari as wave_ari_plotly
from .Waves.waves import wave_ari_fill as wave_ari_fill_plotly
from .Waves.waves import wave_geo as wave_geo_plotly
from .Waves.waves import wave_geo_fill as wave_geo_fill_plotly

from .Stars.star import star as star_plotly
from .Stars.star import stars as stars_plotly

__all__ = [
    # Dots
    "Dots_plotly",
    "n_dots_plotly",
    "draw_dots_plotly",
    "n_dots_array_plotly",
    "draw_n_dots_array_plotly",
    # Lines
    "Lines_plotly",
    "connect_plotly",
    "connect_all_plotly",
    "multi_polygon_plotly",
    "metatron_cube_plotly",
    "krystal_cube_plotly",
    "swastika_plotly",
    "swastika_lines_plotly",
    "draw_lines_plotly",
    "draw_multi_polygon_plotly",
    "draw_metatron_cube_plotly",
    "draw_krystal_cube_plotly",
    "draw_swastika_plotly",
    "draw_swastikas_plotly",
    # Circles
    "circle_plotly",
    "circle_fill_plotly",
    "draw_circle_plotly",
    "circle_p_plotly",
    "ellipse_plotly",
    "ellipse_fill_plotly",
    "concentric_circles_plotly",
    "concentric_circles_fill_plotly",
    "concentric_ellipse_plotly",
    "concentric_ellipse_fill_plotly",
    # Arcs
    "arc_point_plotly",
    "arc_point_inverse_plotly",
    "arc_plotly",
    "arc_inverse_plotly",
    "arc_dot_plotly",
    "arc_dot_inverse_plotly",
    "oval_arc_plotly",
    "arc_rotate_plotly",
    # Flowers
    "flower_petal_plotly",
    "flower_petal_fill_plotly",
    "flower_plotly",
    "flower_fill_plotly",
    "flowers_plotly",
    "rotate_point_plotly",
    "oval_petal_a_plotly",
    "oval_petal_plotly",
    "oval_petal_fill_plotly",
    "oval_flower_plotly",
    "oval_flower_fill_plotly",
    "oval_flower_a_plotly",
    "oval_flower_a_fill_plotly",
    # Spirals
    "logSpiral_plotly",
    "nSpiral_plotly",
    "nSpirals_plotly",
    "calla_petal_plotly",
    "calla_plotly",
    # Waves
    "wave_plotly",
    "wave_fill_plotly",
    "wave_wave_plotly",
    "wave_wave_fill_plotly",
    "wave_ari_plotly",
    "wave_ari_fill_plotly",
    "wave_geo_plotly",
    "wave_geo_fill_plotly",
    # Stars
    "star_plotly",
    "stars_plotly",
]

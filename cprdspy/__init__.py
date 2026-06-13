"""
cprdspy - 一个用于绘制各种几何图形的Python库

这个库提供了绘制圆形、弧线、点阵、线条、螺旋线和花朵等几何图形的功能。
所有图形都使用Plotly绘制，支持交互式显示和自定义样式。

全局配置系统支持多种预定义主题和自定义样式，让你的图形更具个性化。
"""

# 导入全局配置
from .config import (
    Config,
    ConfigError,
    config,
    set_theme,
    get_available_themes,
    apply_config,
    reset_config,
)

# 导入各个模块的公开API
from .CPR_plotly.Circles.circle_config import (
    CircleConfig,
    CircleError,
    config as circle_config,
    circle,
    circle_from_point,
    concentric_circles,
    concentric_circles_geometric,
)

from .CPR_plotly.Arcs.arc_config import (
    ArcConfig,
    ArcError,
    config as arc_config,
    arc,
    arc_inverse,
    arc_degree,
    arc_degree_inverse,
)

from .CPR_plotly.Dots.dot_config import (
    DotConfig,
    DotError,
    config as dot_config,
    n_points,
    draw_points,
    n_points_array,
    n_points_array_inner,
    n_points_array_outer,
    n_points_array_rotate,
    n_points_array_inner_rotate,
    n_points_array_outer_rotate,
    draw_n_points_array,
    draw_n_points_array_inner,
    draw_n_points_array_outer,
    colorful_dots,
)

from .CPR_plotly.Lines.line_config import (
    LineConfig,
    LineError,
    config as line_config,
    n_points as line_n_points,
    draw_points as line_draw_points,
    connect_points,
    multi_polygon,
    metatron_cube,
    swastika,
    multi_swastika,
)

from .CPR_plotly.Spirals.spiral_config import (
    SpiralConfig,
    SpiralError,
    config as spiral_config,
    logSpiral,
    logSpiral_out,
    logSpiral_in,
    n_spiral,
    n_spiral_rotate,
    n_spiral_rotate_out,
    n_spiral_rotate_in,
    chrysanthemum_petal,
    chrysanthemum_by_petal,
    rodincoil,
    rodincoil_colorful,
)

from .CPR_plotly.Flowers.flower_config import (
    FlowerConfig,
    FlowerError,
    config as flower_config,
    n_flower_petal,
    n_flower_arc,
    n_flowers_flower_arc_with_field,
    one_flower_petal,
    one_flower_arc,
    one_flower_flower_arc_with_field,
    flowers_flower_by_petal,
    flowers_flower_by_arc,
    flowers_flower_by_flower_arc_with_field,
    flowers_flower_by_petal_multi,
    flower_by_petal_fill,
    n_lily_petal_fill,
)

from .CPR_plotly.Waves.wave_config import (
    WaveConfig,
    WaveError,
    config as wave_config,
    wave_circle_arithmetic,
    wave_circle_geometric,
    wave_circle_ari_o,
    wave_circle_ari_i,
    wave_circle_ari,
    wave_circle_pro_o,
    wave_circle_pro_i,
    wave_circle_pro,
)

from .CPR_matplotlib.Flowers.flower import (
    flower as flower_mpl,
    flowers as flowers_mpl,
    flower_petal as flower_petal_mpl,
    oval_petal as oval_petal_mpl,
    oval_petal_a as oval_petal_a_mpl,
    oval_flower as oval_flower_mpl,
    oval_flower_a as oval_flower_a_mpl,
)
from .CPR_matplotlib.Waves.waves import (
    wave as wave_mpl,
    wave_wave as wave_wave_mpl,
    wave_ari as wave_ari_mpl,
    wave_geo as wave_geo_mpl,
)

from .CPR_matplotlib.Circles.circle import (
    circle as circle_mpl,
    draw_circle as draw_circle_mpl,
    circle_p as circle_p_mpl,
    ellipse as ellipse_mpl,
    concentric_circles as concentric_circles_mpl,
    concentric_ellipse as concentric_ellipse_mpl,
)

from .CPR_matplotlib.Arcs.arc import (
    arc_point as arc_point_mpl,
    arc_point_inverse as arc_point_inverse_mpl,
    arc as arc_mpl,
    arc_inverse as arc_inverse_mpl,
    arc_dot as arc_dot_mpl,
    arc_dot_inverse as arc_dot_inverse_mpl,
    oval_arc as oval_arc_mpl,
    arc_rotate as arc_rotate_mpl,
)

from .CPR_matplotlib.Spirals.spiral import (
    logSpiral as logSpiral_mpl,
    nSpiral as nSpiral_mpl,
    nSpirals as nSpirals_mpl,
    calla_petal as calla_petal_mpl,
    calla as calla_mpl,
)

from .CPR_matplotlib.Dots.dot import (
    Dots as Dots_mpl,
    n_dots as n_dots_mpl,
    draw_dots as draw_dots_mpl,
    n_dots_array as n_dots_array_mpl,
    draw_n_dots_array as draw_n_dots_array_mpl,
)

from .CPR_matplotlib.Lines.line import (
    Lines as Lines_mpl,
    connect as connect_mpl,
    connect_all as connect_all_mpl,
    multi_polygon as multi_polygon_mpl,
    metatron_cube as metatron_cube_mpl,
    krystal_cube as krystal_cube_mpl,
    swastika as swastika_mpl,
    swastika_lines as swastika_lines_mpl,
    draw_lines as draw_lines_mpl,
    draw_multi_polygon as draw_multi_polygon_mpl,
    draw_metatron_cube as draw_metatron_cube_mpl,
    draw_krystal_cube as draw_krystal_cube_mpl,
    draw_swastika as draw_swastika_mpl,
    draw_swastikas as draw_swastikas_mpl,
)

from .CPR_matplotlib.Stars.star import star as star_mpl, stars as stars_mpl

# 导出所有公开API
__all__ = [
    # 全局配置
    "Config",
    "ConfigError",
    "config",
    "set_theme",
    "get_available_themes",
    "apply_config",
    "reset_config",
    # 圆形模块
    "CircleConfig",
    "CircleError",
    "circle_config",
    "circle",
    "circle_from_point",
    "concentric_circles",
    "concentric_circles_geometric",
    # 弧线模块
    "ArcConfig",
    "ArcError",
    "arc_config",
    "arc",
    "arc_inverse",
    "arc_degree",
    "arc_degree_inverse",
    # 点阵模块
    "DotConfig",
    "DotError",
    "dot_config",
    "n_points",
    "draw_points",
    "n_points_array",
    "n_points_array_inner",
    "n_points_array_outer",
    "n_points_array_rotate",
    "n_points_array_inner_rotate",
    "n_points_array_outer_rotate",
    "draw_n_points_array",
    "draw_n_points_array_inner",
    "draw_n_points_array_outer",
    "colorful_dots",
    # 线条模块
    "LineConfig",
    "LineError",
    "line_config",
    "line_n_points",
    "line_draw_points",
    "connect_points",
    "multi_polygon",
    "metatron_cube",
    "swastika",
    "multi_swastika",
    # 螺旋线模块
    "SpiralConfig",
    "SpiralError",
    "spiral_config",
    "logSpiral",
    "logSpiral_out",
    "logSpiral_in",
    "n_spiral",
    "n_spiral_rotate",
    "n_spiral_rotate_out",
    "n_spiral_rotate_in",
    "chrysanthemum_petal",
    "chrysanthemum_by_petal",
    "rodincoil",
    "rodincoil_colorful",
    # 花朵模块
    "FlowerConfig",
    "FlowerError",
    "flower_config",
    "n_flower_petal",
    "n_flower_arc",
    "n_flowers_flower_arc_with_field",
    "one_flower_petal",
    "one_flower_arc",
    "one_flower_flower_arc_with_field",
    "flowers_flower_by_petal",
    "flowers_flower_by_arc",
    "flowers_flower_by_flower_arc_with_field",
    "flowers_flower_by_petal_multi",
    "flower_by_petal_fill",
    "n_lily_petal_fill",
    # 波形模块
    "WaveConfig",
    "WaveError",
    "wave_config",
    "wave_circle_arithmetic",
    "wave_circle_geometric",
    "wave_circle_ari_o",
    "wave_circle_ari_i",
    "wave_circle_ari",
    "wave_circle_pro_o",
    "wave_circle_pro_i",
    "wave_circle_pro",
    # matplotlib版本的函数
    # 圆形模块
    "circle_mpl",
    "draw_circle_mpl",
    "circle_p_mpl",
    "ellipse_mpl",
    "concentric_circles_mpl",
    "concentric_ellipse_mpl",
    # 弧线模块 (matplotlib)
    "arc_point_mpl",
    "arc_point_inverse_mpl",
    "arc_mpl",
    "arc_inverse_mpl",
    "arc_dot_mpl",
    "arc_dot_inverse_mpl",
    "oval_arc_mpl",
    "arc_rotate_mpl",
    # 螺旋线模块 (matplotlib)
    "logSpiral_mpl",
    "nSpiral_mpl",
    "nSpirals_mpl",
    "calla_petal_mpl",
    "calla_mpl",
    # 点阵模块 (matplotlib)
    "Dots_mpl",
    "n_dots_mpl",
    "draw_dots_mpl",
    "n_dots_array_mpl",
    "draw_n_dots_array_mpl",
    # 线条模块 (matplotlib)
    "Lines_mpl",
    "connect_mpl",
    "connect_all_mpl",
    "multi_polygon_mpl",
    "metatron_cube_mpl",
    "krystal_cube_mpl",
    "swastika_mpl",
    "swastika_lines_mpl",
    "draw_lines_mpl",
    "draw_multi_polygon_mpl",
    "draw_metatron_cube_mpl",
    "draw_krystal_cube_mpl",
    "draw_swastika_mpl",
    "draw_swastikas_mpl",
    # 花朵模块
    "flower_mpl",
    "flowers_mpl",
    "flower_petal_mpl",
    "oval_petal_mpl",
    "oval_petal_a_mpl",
    "oval_flower_mpl",
    "oval_flower_a_mpl",
    # 星形模块 (matplotlib)
    "star_mpl",
    "stars_mpl",
    # 波形模块
    "wave_mpl",
    "wave_wave_mpl",
    "wave_ari_mpl",
    "wave_geo_mpl",
]
# 版本信息
__version__ = "0.3.0"

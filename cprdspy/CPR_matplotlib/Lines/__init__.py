"""Lines 模块 — 线段连接与绘制。

公开 API:
    - Lines                 线段容器类，支持 + 拼接
    - connect               按顺序连接点（闭合/不闭合折线）
    - connect_all           所有点两两全连接
    - multi_polygon         多层多边形连线
    - metatron_cube         梅塔特隆立方体连线
    - krystal_cube          水晶立方体连线
    - swastika              卍字螺旋点
    - swastika_lines        卍字图案连线
    - draw_lines            绘制线段集合，支持统一颜色、颜色列表和渐变色
    - draw_multi_polygon    绘制多层多边形
    - draw_metatron_cube    绘制梅塔特隆立方体
    - draw_krystal_cube     绘制水晶立方体
    - draw_swastika         绘制单个卍字
    - draw_swastikas        绘制多个旋转卍字
"""

from .line import (
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

__all__ = [
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
]

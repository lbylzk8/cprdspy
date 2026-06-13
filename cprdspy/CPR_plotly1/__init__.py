"""
cprdspy.CPR_plotly1 - Plotly 绘图模块

这个模块提供了使用 Plotly 绘制各种几何图形的功能，包括：
- 圆形 (Circles)
- 弧线 (Arcs)
- 螺旋线 (Spirals)
- 花朵 (Flowers)
- 波形 (Waves)

所有函数都以 `_plotly` 后缀结尾，以区分于 Matplotlib 版本。
"""

import os
import importlib
from typing import List

# 初始化导出的函数列表
__all__: List[str] = []

# 导入 Circles 模块
try:
    from .Circles.circle import (
        circle as circle_plotly,
        draw_circle as draw_circle_plotly,
        ellipse as ellipse_plotly,
        concentric_circles as concentric_circles_plotly,
        concentric_ellipse as concentric_ellipse_plotly,
    )

    __all__.extend(
        [
            "circle_plotly",
            "draw_circle_plotly",
            "ellipse_plotly",
            "concentric_circles_plotly",
            "concentric_ellipse_plotly",
        ]
    )
except ImportError:
    pass

# 导入 Arcs 模块
try:
    from .Arcs.arc import (
        arc as arc_plotly,
        arc_inverse as arc_inverse_plotly,
        arc_point as arc_point_plotly,
        arc_point_inverse as arc_point_inverse_plotly,
        arc_dot as arc_dot_plotly,
        arc_dot_inverse as arc_dot_inverse_plotly,
        oval_arc as oval_arc_plotly,
    )

    __all__.extend(
        [
            "arc_plotly",
            "arc_inverse_plotly",
            "arc_point_plotly",
            "arc_point_inverse_plotly",
            "arc_dot_plotly",
            "arc_dot_inverse_plotly",
            "oval_arc_plotly",
        ]
    )
except ImportError:
    pass

# 导入 Spirals 模块
try:
    from .Spirals.spiral import (
        logSpiral as logSpiral_plotly,
        logSpiral_out as logSpiral_out_plotly,
        logSpiral_in as logSpiral_in_plotly,
        logSpiral_in_out as logSpiral_in_out_plotly,
        nSpiral as nSpiral_plotly,
        n_spiral as n_spiral_plotly,
        n_spiral_rotate as n_spiral_rotate_plotly,
        n_spiral_rotate_out as n_spiral_rotate_out_plotly,
        n_spiral_rotate_in as n_spiral_rotate_in_plotly,
        calla_petal as calla_petal_plotly,
        calla_by_petal as calla_by_petal_plotly,
    )

    __all__.extend(
        [
            "logSpiral_plotly",
            "logSpiral_out_plotly",
            "logSpiral_in_plotly",
            "logSpiral_in_out_plotly",
            "nSpiral_plotly",
            "n_spiral_plotly",
            "n_spiral_rotate_plotly",
            "n_spiral_rotate_out_plotly",
            "n_spiral_rotate_in_plotly",
            "calla_petal_plotly",
            "calla_by_petal_plotly",
        ]
    )
except ImportError:
    pass

# 导入 Flowers 模块
try:
    from .Flowers.flower import (
        flower_petal as flower_petal_plotly,
        flower as flower_plotly,
        flowers as flowers_plotly,
        oval_petal as oval_petal_plotly,
        oval_flower as oval_flower_plotly,
        oval_flower_a as oval_flower_a_plotly,
        rotate_point as rotate_point_plotly,
    )

    __all__.extend(
        [
            "flower_petal_plotly",
            "flower_plotly",
            "flowers_plotly",
            "oval_petal_plotly",
            "oval_flower_plotly",
            "oval_flower_a_plotly",
            "rotate_point_plotly",
        ]
    )
except ImportError:
    pass

# 导入 Waves 模块
try:
    from .Waves.waves import (
        wave as wave_plotly,
        wave_wave as wave_wave_plotly,
        wave_ari as wave_ari_plotly,
        wave_geo as wave_geo_plotly,
    )

    __all__.extend(
        [
            "wave_plotly",
            "wave_wave_plotly",
            "wave_ari_plotly",
            "wave_geo_plotly",
        ]
    )
except ImportError:
    pass


# 动态导入其他子目录中的模块
def import_submodules() -> None:
    """动态导入所有子目录中的模块并添加到 __all__"""
    base_path = os.path.dirname(__file__)

    # 获取所有子目录
    subdirs = [
        d
        for d in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, d)) and not d.startswith("__")
    ]

    for subdir in subdirs:
        subdir_path = os.path.join(base_path, subdir)

        # 获取子目录中的所有 Python 文件
        py_files = [
            f[:-3]
            for f in os.listdir(subdir_path)
            if f.endswith(".py") and not f.startswith("__")
        ]

        # 导入每个 Python 文件
        for py_file in py_files:
            try:
                # 构建模块路径
                module_path = f"cprdspy.CPR_plotly1.{subdir}.{py_file}"

                # 尝试导入模块
                module = importlib.import_module(module_path)

                # 获取模块中的所有函数
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)

                    # 只导出非私有函数
                    if callable(attr) and not attr_name.startswith("_"):
                        # 为函数添加 _plotly 后缀
                        new_name = f"{attr_name}_plotly"

                        # 避免重复导入
                        if new_name not in globals():
                            globals()[new_name] = attr
                            if new_name not in __all__:
                                __all__.append(new_name)
            except (ImportError, AttributeError):
                # 忽略导入错误，继续处理其他模块
                pass


# 执行动态导入
import_submodules()

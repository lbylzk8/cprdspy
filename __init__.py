"""
cprdspy - 一个用于绘制各种几何图形的Python库

这个库提供了绘制圆形、弧线、点阵、线条、螺旋线和花朵等几何图形的功能。
所有图形都使用Plotly绘制，支持交互式显示和自定义样式。

全局配置系统支持多种预定义主题和自定义样式，让你的图形更具个性化。
"""

# 从内层包重新导出所有公开API
from .cprdspy import *

# 注册内层子包到 sys.modules，使 from cprdspy.CPR_plotly1 import * 等导入可用
import sys as _sys

from .cprdspy import CPR_plotly1

_sys.modules["cprdspy.CPR_plotly1"] = CPR_plotly1

# 版本信息
__version__ = "0.3.0"

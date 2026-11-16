"""Move 模块完整演示 —— 运行 move.py 内置的演示图形。

直接运行：
    python cprdspy/CPR_matplotlib/Move/demo.py

无显示环境（例如服务器）时可以改成保存图片：
    MPLBACKEND=Agg python demo.py            # 然后调用 savefig("demo.png")
"""

import os
import sys

import matplotlib.pyplot as plt

# 允许不安装包、直接从仓库里运行本脚本
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from cprdspy.CPR_matplotlib.Move.move import _demo_move, savefig  # noqa: E402

_demo_move()
plt.show()

# 想保存成图片时，去掉下面一行的注释：
# savefig("move_demo.png")

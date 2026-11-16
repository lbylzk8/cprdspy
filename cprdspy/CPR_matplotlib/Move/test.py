"""Move 模块快速测试 —— 画一组基本图形并显示。

直接运行：
    python cprdspy/CPR_matplotlib/Move/test.py
"""

import os
import sys

import matplotlib.pyplot as plt

# 允许不安装包、直接从仓库里运行本脚本
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
)

from cprdspy.CPR_matplotlib.Move.move import Move, get_screen  # noqa: E402

m = Move()
m.speed(3)

# 1) 描边 + 填充的正方形
m.pensize(3)
m.color("blue", "orange")
m.begin_fill()
for _ in range(4):
    m.forward(80)
    m.left(90)
m.end_fill()

# 2) 抬笔移动到左下角，再画一段阶梯折线
m.pu()
m.goto(-150, -150)
m.pd()
m.pencolor("green")
m.pensize(2)
for _ in range(5):
    m.forward(40)
    m.left(90)
    m.forward(40)
    m.right(90)

# 3) 画一段圆弧，并把外形换成海龟
m.pu()
m.goto(0, 120)
m.pd()
m.pencolor("red")
m.pensize(1)
m.circle(60, 270)
m.shape("turtle")
m.shapesize(2)

# 4) 写一行字
m.pu()
m.goto(-300, 200)
m.write("Move on matplotlib", font=("Arial", 14, "bold"))

print("画布像素:", get_screen().canvwidth, "x", get_screen().canvheight)
print("图形对象:", get_screen().getfigure())

plt.show()

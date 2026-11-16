"""Move 模块 — 基于 matplotlib 的"海龟绘图"（move graphics）动画。

由 ``turtle.py``（Tkinter 版）改写而来：画布层换成 matplotlib，
类名由 Turtle 系列改成 Move 系列，其余方法与别名保持 turtle 语义。

公开 API（推荐用法）::

    import matplotlib.pyplot as plt
    from cprdspy.CPR_matplotlib.Move.move import Move, MoveScreen, Vec2D

    m = Move()                  # 自动创建 Figure / Axes
    m.speed(0)
    for _ in range(36):
        m.forward(120)
        m.left(170)
    plt.show()

也可以把已有坐标轴交给 Move，与其它 matplotlib 图形组合::

    fig, ax = plt.subplots()
    m = Move(fig=fig, ax=ax)

还保留了 turtle 的过程式接口（模块级同名函数）::

    from cprdspy.CPR_matplotlib.Move.move import *
    fd(100); lt(90); fd(100); done()

主要导出:

    - Move / RawMove / Pen / RawPen    Move 对象（等价 turtle 的 Turtle 系列）
    - MoveScreen / MoveScreenBase      屏幕对象（等价 TurtleScreen）
    - MoveCanvas                       画布包装（figure + axes）
    - Vec2D / Shape / Tbuffer          基础数据结构
    - TurtleGraphicsError/Terminator   异常
    - forward/fd、back/bk、left/lt、right/rt、goto/setpos、circle、
      penup/pu、pendown/pd、pensize/width、pencolor、fillcolor、
      begin_fill/end_fill、dot、stamp、write、undo、speed、shape、
      tracer、delay、bgcolor、done/mainloop ...（与 turtle 同名）
"""

from .move import (  # noqa: F401
    Move,
    MoveCanvas,
    MoveScreen,
    MoveScreenBase,
    RawMove,
    RawPen,
    Pen,
    Shape,
    Tbuffer,
    Terminator,
    TNavigator,
    TPen,
    TurtleGraphicsError,
    Vec2D,
)
from .move import *  # noqa: F401,F403  过程式接口与 turtle 同名
from .move import __all__ as _move_all

__all__ = sorted(
    set(_move_all)
    | {
        "Move",
        "MoveCanvas",
        "MoveScreen",
        "MoveScreenBase",
        "RawMove",
        "RawPen",
        "Pen",
        "Shape",
        "Tbuffer",
        "Terminator",
        "TNavigator",
        "TPen",
        "TurtleGraphicsError",
        "Vec2D",
    }
)

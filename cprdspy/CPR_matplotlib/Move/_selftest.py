"""Move 模块自测（无 GUI，Agg 后端）。

覆盖：导入、过程式 API、Move 类、MoveScreen、形状/填充/印章/文字、
撤销、世界坐标、tracer/delay、多 move 对象、图片外形（有 Pillow 时）、
savefig 落盘、事件分发、异常路径。

直接运行：
    python cprdspy/CPR_matplotlib/Move/_selftest.py
"""

import math
import os
import sys
import time

import matplotlib

matplotlib.use("Agg")  # 必须在 pyplot 之前

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from cprdspy.CPR_matplotlib.Move import move  # noqa: E402
from cprdspy.CPR_matplotlib.Move.move import (  # noqa: E402
    Move,
    MoveCanvas,
    MoveScreen,
    Shape,
    TurtleGraphicsError,
    Vec2D,
    reset_screen,
)

FAILURES = []


def check(name, cond, extra=""):
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name} {extra}")
        FAILURES.append(name)


def close_all():
    """每个小节之间彻底复位，避免 tracer/delay 状态串味。"""
    plt.close("all")
    reset_screen()
    sc = move.get_screen()
    sc.tracer(1)
    sc.delay(10)
    sc.painter.interactive = True


def _make_event(class_name, x=0.0, y=0.0, button=1, key=None):
    return type(
        class_name, (), {"button": button, "key": key, "xdata": x, "ydata": y}
    )()


HERE = os.path.dirname(__file__)


# ---------------------------------------------------------------------------
print("[1] 基础几何与向量")
close_all()
a, b = Vec2D(3, 4), Vec2D(1, 1)
check("abs(Vec2D(3,4))==5", abs(a) == 5)
check("a+b", a + b == (4, 5))
check("a-b", a - b == (2, 3))
check("a*2", a * 2 == (6, 8))
check("2*a", 2 * a == (6, 8))
check("a*b 内积", a * b == 7)
check("-a", a - b == (2, 3) and -a == (-3, -4))
_r = Vec2D(1 / 3, 2 / 7)
check("repr 保留完整精度", _r[0] == 1 / 3 and _r[1] == 2 / 7 and "0.333" in repr(_r), repr(_r))
check("repr 不再截断成 2 位", repr(Vec2D(1 / 3, 0)) != "(0.33,0.00)", repr(Vec2D(1 / 3, 0)))
check("repr 整数值简洁", repr(Vec2D(25.0, 0.0)) == "(25.0,0.0)", repr(Vec2D(25.0, 0.0)))
check("rotate(90)", tuple(round(v, 6) for v in b.rotate(90)) == (-1.0, 1.0))

# ---------------------------------------------------------------------------
print("[1b] 角度精度（回归：曾经固定 round(...,10) 丢精度）")
close_all()
mv0 = Move()
mv0.speed(0)
mv0.setheading(0)
mv0.left(90)
check("left(90) 后 heading 恰好是 90", mv0.heading() == 90.0, mv0.heading())
mv0.setheading(0)
for _ in range(90):
    mv0.left(1)
check("90 次 left(1) 后 heading 恰好是 90", mv0.heading() == 90.0, mv0.heading())
mv0.setheading(0)
for _ in range(360):
    mv0.left(1)
check("360 次 left(1) 后 heading 回到 0", mv0.heading() == 0.0, mv0.heading())
mv0.setheading(0)
mv0.left(0.1)
check("小数角度不被吞掉", abs(mv0.heading() - 0.1) < 1e-12, mv0.heading())
mv0.setheading(0)
mv0.left(1e-9)
check("极小角度仍有分辨力", mv0.heading() > 0, mv0.heading())
mv0.setheading(0)
mv0.left(33.333333333333)
check("高精度角度保持到 1e-10", abs(mv0.heading() - 33.333333333333) < 1e-10, mv0.heading())
mv0.goto(0, 100)
check("towards 竖直方向精确为 90", mv0.towards(0, 200) == 90.0, mv0.towards(0, 200))

# ---------------------------------------------------------------------------
print("[1c] 默认颜色（回归：#0f0）")
close_all()
mv0 = Move()
check("默认 pencolor 是 #0f0", mv0.pencolor() == (0.0, 1.0, 0.0), mv0.pencolor())
mv0.speed(0)
mv0.forward(10)
ax0 = move.get_axes()
drawn0 = [L for L in ax0.lines if len(L.get_xdata()) > 0]
check("画出来的线就是 #0f0", bool(drawn0) and drawn0[0].get_color() == "#0f0",
      drawn0[0].get_color() if drawn0 else None)
check("配置文件默认值也是 #0f0", move._CFG["pencolor"] == "#0f0", move._CFG["pencolor"])

# ---------------------------------------------------------------------------
print("[2] 过程式（turtle 同名函数）API")
close_all()
move.speed(0)
move.forward(100)
move.left(90)
move.forward(50)
check("forward/left 之后位置", tuple(round(v, 6) for v in move.pos()) == (100.0, 50.0), move.pos())
check("heading()==90", move.heading() == 90)
move.right(45)
check("right 后 heading==45", move.heading() == 45)
check("xcor/ycor", (move.xcor(), move.ycor()) == (100.0, 50.0))
check("distance", move.distance(0, 0) == abs(complex(100, 50)))
move.home()
check("home()", tuple(move.pos()) == (0.0, 0.0) and move.heading() == 0)
move.up()
move.goto(20, 20)
move.down()
check("setpos 别名", tuple(move.pos()) == (20.0, 20.0))
move.setheading(90)
check("seth 别名", move.heading() == 90)
check("isdown()", move.isdown() is True)
move.pu()
check("pu() 抬笔", move.isdown() is False)
move.pd()
check("pd() 落笔", move.isdown() is True)

# ---------------------------------------------------------------------------
print("[3] 折线真的被画出来（回归：曾经整条线为空）")
close_all()
m = Move()
m.speed(0)
m.forward(80)
ax = move.get_axes()
drawn = [L for L in ax.lines if len(L.get_xdata()) > 0]
check("forward 后有带数据的线", len(drawn) == 1, len(drawn))
check("线段点数==2", len(drawn[0].get_xdata()) == 2, len(drawn[0].get_xdata()))
check(
    "线段坐标正确",
    [tuple(p) for p in zip(drawn[0].get_xdata(), drawn[0].get_ydata())]
    == [(0.0, -0.0), (80.0, -0.0)],
    list(zip(drawn[0].get_xdata(), drawn[0].get_ydata())),
)
m.left(90)
m.forward(60)
drawn = [L for L in ax.lines if len(L.get_xdata()) > 0]
check("继续前进仍是同一条折线（未被误切段）", len(drawn) == 1, len(drawn))
check("折线累积到 3 点", len(drawn[0].get_xdata()) == 3, len(drawn[0].get_xdata()))

check(
    "canvwidth 与窗口像素一致",
    abs(move.get_screen().canvwidth - move.get_screen().window_width()) < 1.0,
    (move.get_screen().canvwidth, move.get_screen().window_width()),
)
xlim = ax.get_xlim()
check(
    "xlim 覆盖整块画布",
    abs((xlim[1] - xlim[0]) - move.get_screen().canvwidth) < 1.0,
    xlim,
)

# ---------------------------------------------------------------------------
print("[4] Move 类、画笔属性、颜色")
close_all()
m = Move()
m.speed(0)
m.pensize(3)
check("pensize", m.pensize() == 3)
check("width 别名", m.width() == 3)
check("默认 colormode 1.0", move.colormode() == 1.0)
m.pencolor("red")
check("colormode=1.0 下 pencolor('red')", m.pencolor() == (1.0, 0.0, 0.0), m.pencolor())
m.pencolor((0, 1, 0))
check("colormode=1.0 下 pencolor((0,1,0))", m.pencolor() == (0.0, 1.0, 0.0), m.pencolor())
try:
    m.pencolor((0, 255, 0))
    check("colormode=1.0 下越界颜色抛错", False)
except TurtleGraphicsError:
    check("colormode=1.0 下越界颜色抛错", True)
move.colormode(255)
check("colormode(255) 读回", move.colormode() == 255)
m.pencolor(0, 0, 255)
check("colormode=255 下 pencolor(0,0,255)", m.pencolor() == (0.0, 0.0, 255.0), m.pencolor())
m.color("blue", "yellow")
check("color() 读写", m.color() == ((0.0, 0.0, 255.0), (255.0, 255.0, 0.0)), m.color())
move.colormode(1.0)
pen_state = m.pen()
check(
    "pen() 字典键",
    {"shown", "pendown", "pencolor", "fillcolor", "pensize", "speed", "resizemode",
     "stretchfactor", "shearfactor", "outline", "tilt"} == set(pen_state),
)
m.pen(pen_state)
m.resizemode("auto")
check("resizemode", m.resizemode() == "auto")

# ---------------------------------------------------------------------------
print("[5] 形状与变形")
close_all()
m = Move()
m.speed(0)
check("默认形状", m.shape() == "classic", m.shape())
m.shape("turtle")
check("shape('turtle')", m.shape() == "turtle")
m.shape("square")
m.shapesize(2, 3, 4)
check("shapesize 读回", m.shapesize() == (2.0, 3.0, 4), m.shapesize())
m.shearfactor(0.5)
check("shearfactor", m.shearfactor() == 0.5)
m.tiltangle(45)
check("tiltangle", abs(m.tiltangle() - 45) < 1e-9, m.tiltangle())
m.shapetransform(2, 0, 0, 2)
check("shapetransform", m.shapetransform() == (2, 0, 0, 2), m.shapetransform())
m.shape("square")
poly = m.get_shapepoly()
check("get_shapepoly 点数", poly is not None and len(poly) == 4, poly)
m.getscreen().register_shape("tri", ((5, -3), (0, 5), (-5, -3)))
m.shape("tri")
check("register_shape + shape", m.shape() == "tri")
check("getshapes 含 tri", "tri" in m.getscreen().getshapes())
try:
    m.shape("nope")
    check("未知形状抛错", False)
except TurtleGraphicsError:
    check("未知形状抛错", True)

s = Shape("compound")
s.addcomponent(((0, 0), (10, -5), (0, 10), (-10, -5)), "red", "blue")
m.getscreen().register_shape("comp", s)
m.shape("comp")
m.speed(0)
m.stamp()
check("复合形状可用", m.shape() == "comp")
check("复合形状外形已绘制", any(len(p.get_xy()) >= 3 for p in move.get_axes().patches))

# ---------------------------------------------------------------------------
print("[6] 填充、印章、文字、点")
close_all()
m = Move()
m.speed(0)
m.color("black", "red")
m.begin_fill()
check("filling() True", m.filling() is True)
for _ in range(4):
    m.forward(60)
    m.left(90)
m.end_fill()
check("filling() False", m.filling() is False)
filled = [
    p for p in move.get_axes().patches
    if len(p.get_xy()) > 3 and tuple(p.get_facecolor()[:3]) != (0.0, 0.0, 0.0)
]
check("填充多边形已绘制", len(filled) >= 1, len(filled))
s1 = m.stamp()
s2 = m.stamp()
check("stamp 返回 id", s1 is not None and s2 is not None)
check("stampItems 长度", len(m.stampItems) == 2)
m.clearstamp(s1)
check("clearstamp", len(m.stampItems) == 1)
m.clearstamps()
check("clearstamps", len(m.stampItems) == 0)
m.write("hello", move=True)
check("write(move=True) 有文字", len(move.get_axes().texts) >= 1)
before = len(m.items)
m.dot(20, "blue")
check("dot 增加图元", len(m.items) > before)
m.begin_poly()
for _ in range(3):
    m.forward(40)
    m.left(120)
m.end_poly()
recorded = m.get_poly()
check("begin_poly/end_poly/get_poly", recorded is not None and len(recorded) >= 3, recorded)

# ---------------------------------------------------------------------------
print("[7] 撤销")
close_all()
m = Move()
m.speed(0)
for _ in range(4):
    m.forward(50)
    m.left(90)
check("undobufferentries > 0", m.undobufferentries() > 0)
for _ in range(8):
    m.undo()
check("undo 后位置回到原点", tuple(round(v, 6) for v in m.pos()) == (0.0, 0.0), m.pos())
m.setundobuffer(None)
check("setundobuffer(None) 后 undo 安全", m.undo() is None and m.undobufferentries() == 0)

# ---------------------------------------------------------------------------
print("[8] tracer / delay / speed / 屏幕方法")
close_all()
sc = move.get_screen()
check("get_screen 单例", sc is move.get_screen())
check("tracer() 默认 1", sc.tracer() == 1)
sc.tracer(0)
check("tracer(0)", sc.tracer() == 0)
sc.tracer(4, 20)
check("tracer(4,20)", sc.tracer() == 4 and sc.delay() == 20)
move.update()
sc.tracer(1)
check("bgcolor 读回", sc.bgcolor() is not None)
check("window_width>0", sc.window_width() > 0, sc.window_width())
check("window_height>0", sc.window_height() > 0, sc.window_height())
check("getcanvas 类型", isinstance(sc.getcanvas(), MoveCanvas))
check("getfigure/getaxes", sc.getfigure() is not None and sc.getaxes() is not None)
sc.screensize(300, 200)
check("screensize 读回", tuple(sc.screensize()) == (300.0, 200.0), sc.screensize())
check("screensize 后窗口同步", abs(sc.window_width() - 300) < 1.0, sc.window_width())
sc.title("move 测试")
m2 = Move()
m2.speed(3)
m2.forward(30)
check("speed 动画路径可用", m2.pos()[0] != 0, m2.pos())
m2.speed("fastest")
check("speed 字符串", m2.speed() == 0)


def count_frames(speed):
    close_all()
    t = Move()
    t.speed(speed)
    seen = []
    orig = type(t)._drawturtle

    def spy(self):
        seen.append(self._position)
        return orig(self)

    type(t)._drawturtle = spy
    try:
        t.forward(120)
    finally:
        type(t)._drawturtle = orig
    return len(seen)


check("speed=6 有中间帧", count_frames(6) > 1, count_frames(6))
check("speed=0 只有一次落笔（无插值帧）", count_frames(0) == 1, count_frames(0))
close_all()
_t = Move()
_t.speed(0)
_t.reset()
check("reset() 保留 speed 设置（回归：否则动画会莫名复活）", _t.speed() == 0, _t.speed())

# ---------------------------------------------------------------------------
print("[8b] 动画真的在刷帧（回归：曾经没有动画效果）")
close_all()
t = Move()
t.speed(6)
t.delay(0)  # 不等待，只验证帧被真正画出去
painter = t.getscreen().painter
before = painter._frames
t.forward(150)
drawn_frames = painter._frames - before
check("forward 期间真的调用了绘制帧", drawn_frames >= 1, drawn_frames)

# 无界面后端（Agg）不节流：每次 frame() 都会真的画
painter.frame(0)
f0 = painter._frames
painter.frame(0)
check("非 GUI 后端每帧都真的绘制", painter._frames == f0 + 1, painter._frames - f0)

# 节流只发生在交互式 GUI 后端，这里强制打开 GUI 分支来验证
import cprdspy.CPR_matplotlib.Move._painter as _painter_mod

_orig_gui = _painter_mod._is_gui_backend
_painter_mod._is_gui_backend = lambda fig=None: True
try:
    painter.interactive = True
    painter.set_delay(600)  # 0.6s，下一次 frame 必定还没到期
    painter.frame(600, force=True)  # 先画一帧并记录时间戳
    f0 = painter._frames
    drawn = painter.frame(600)
    check("GUI 后端上刚画过的一帧会被节流跳过",
          painter._frames == f0 and drawn is False, (painter._frames - f0, drawn))
    drawn = painter.frame(600, force=True)
    check("force=True 可以强制画出一帧",
          painter._frames == f0 + 1 and drawn is True, (painter._frames - f0, drawn))
finally:
    _painter_mod._is_gui_backend = _orig_gui

check("delay(ms) 会同步到画布帧间隔",
      abs(painter._min_frame_interval - 0.6) < 1e-9, painter._min_frame_interval)
move.get_screen().delay(10)
check("delay() 读回正确", move.get_screen().delay() == 10)

# 录制/无界面场景可以关掉动画等待
painter.interactive = False
t.delay(1000)
start = time.monotonic()
t.forward(60)
elapsed = time.monotonic() - start
check("interactive=False 时不再阻塞脚本", elapsed < 0.5, f"{elapsed:.3f}s")
painter.interactive = True

# tracer(0) 下不应产生动画帧，但 update() 必须把折线补画出来
move.get_screen().tracer(0)
f0 = painter._frames
t.forward(30)
check("tracer(0) 时不做动画帧", painter._frames == f0, painter._frames - f0)


def _lines_with_data():
    return sum(
        1 for L in t.getscreen().painter.ax.lines if len(L.get_xdata()) > 0
    )


before_lines = _lines_with_data()
t.forward(30)
check("tracer(0) 时暂不绘制折线（turtle 语义）",
      _lines_with_data() == before_lines, _lines_with_data() - before_lines)
# 换一条新折线，这样"有没有补画出来"是确定的
t._newLine()
pending_before = _lines_with_data()
t.forward(30)
check("tracer(0) 时新折线也不会立刻出现",
      _lines_with_data() == pending_before, _lines_with_data() - pending_before)
move.update()
check("tracer(0) 后 update() 把待画的折线补出来",
      _lines_with_data() > pending_before, _lines_with_data())
move.get_screen().tracer(1)
move.get_screen().delay(10)

# 帧间隔必须随 speed 单调递减（否则"速度档位"没有意义）
_intervals = []
for _sp in (1, 2, 3, 5, 8, 10):
    t.speed(_sp)
    _intervals.append(t._frame_interval())
check("帧间隔随 speed 单调不增",
      all(a >= b for a, b in zip(_intervals, _intervals[1:])), _intervals)
check("speed=1 与 speed=10 的间隔差距明显",
      _intervals[0] > 2 * _intervals[-1], (_intervals[0], _intervals[-1]))

# ---------------------------------------------------------------------------
print("[8c] 后端识别（回归：*Agg GUI 后端曾被误判成非交互）")
import cprdspy.CPR_matplotlib.Move._painter as _pm


class _FakeCanvas:
    def __init__(self, with_window):
        self.manager = type("M", (), {"window": object() if with_window else None})()
        self.flush_events = lambda: None


class _FakeFig:
    def __init__(self, with_window):
        self.canvas = _FakeCanvas(with_window)


_orig_backend = matplotlib.get_backend


def _with_backend(name):
    matplotlib.use(name, force=True)


try:
    for backend in ("TkAgg", "QtAgg", "WxAgg", "GTK3Agg"):
        try:
            _with_backend(backend)
        except Exception:
            print(f"  skip {backend} 不可用")
            continue
        # 无窗口时不应崩，有窗口时必须判为 GUI
        _pm._is_gui_backend(_FakeFig(False))
        check(f"{backend} 有 GUI 窗口时判为可交互", _pm._is_gui_backend(_FakeFig(True)))
finally:
    _with_backend("Agg")
check("Agg 判为非交互", not _pm._is_gui_backend(_FakeFig(False)))
check("Agg（即使有 window 对象）仍判为非交互",
      not _pm._is_gui_backend(_FakeFig(True)))
for backend in ("pdf", "svg", "ps"):
    try:
        _with_backend(backend)
    except Exception:
        continue
    check(f"{backend} 判为非交互", not _pm._is_gui_backend(_FakeFig(False)))
_with_backend("Agg")

# 真的推到屏幕的那一步必须存在（帧数 > 0 且 _flush_screen 可调用）
close_all()
_tt = Move()
_tt.speed(3)
_tt.delay(0)
_p = _tt.getscreen().painter
_f0 = _p._frames
_tt.forward(120)
check("动画期间确实产生了待推屏的帧", _p._frames > _f0, _p._frames - _f0)
_p._flush_screen()  # 不应抛异常
check("_flush_screen() 在非 GUI 后端安全", True)

# ---------------------------------------------------------------------------
print("[9] 世界坐标")
close_all()
m = Move()
m.speed(0)
move.get_screen().setworldcoordinates(-10, -0.5, 50, 1.5)
check("mode 变 world", move.get_screen().mode() == "world")
for _ in range(36):
    m.left(10)
    m.forward(0.5)
check("world 下绘图不报错", True)
move.get_screen().mode("standard")
check("mode('standard')", move.get_screen().mode() == "standard")
check("改回 standard 后 xscale=1", move.get_screen().xscale == 1.0)

# ---------------------------------------------------------------------------
print("[10] 多 move 对象、clone、距离")
close_all()
m = Move()
m.speed(0)
c = m.clone()
check("clone 位置一致", tuple(c.pos()) == tuple(m.pos()))
check("clone 是独立对象", c is not m)
check("屏幕 turtles 数", len(m.getscreen().turtles()) == 2)
m.forward(30)
check("clone 独立运动", tuple(c.pos()) != tuple(m.pos()))
check("getturtle/getpen", m.getturtle() is m and m.getpen() is m)
check("distance 到另一个对象", abs(m.distance(c) - 30) < 1e-9, m.distance(c))
check("towards 返回角度", 0 <= m.towards(c) <= 360)

# ---------------------------------------------------------------------------
print("[11] 事件绑定与分发")
close_all()
m = Move()
m.speed(0)
hits = []
m.onclick(lambda x, y: hits.append((x, y)))
move.get_screen().onclick(lambda x, y: hits.append("screen"))
m.ondrag(lambda x, y: hits.append("drag"))
move.get_screen().onkey(lambda: hits.append("k"), "Up")
move.get_screen().onkeypress(lambda: hits.append("kp"), "space")
move.get_screen().onkeypress(lambda: hits.append("kp"), None)  # 通配任意键
check("_item_bindings 有 2 条", len(move.get_screen()._item_bindings) == 2,
      len(move.get_screen()._item_bindings))
check("_screen_bindings 有 1 条", len(move.get_screen()._screen_bindings) == 1)
check("_key_bindings 有 3 条", len(move.get_screen()._key_bindings) == 3,
      len(move.get_screen()._key_bindings))
move.get_screen().onclick(None)
check("屏幕 onclick(None) 解绑", 1 not in move.get_screen()._screen_bindings)
m.onclick(None)
check("对象 onclick(None) 解绑", len(move.get_screen()._item_bindings) == 1,
      len(move.get_screen()._item_bindings))

screen = move.get_screen()
screen.onclick(lambda x, y: hits.append("screen"))
hits.clear()
screen._dispatch_mouse(_make_event("ButtonPress", 10.0, 10.0))
check("屏幕 click 分发", "screen" in hits, hits)

hits.clear()
screen._dispatch_key(_make_event("KeyReleaseEvent", key="up"))
check("onkey('Up') 响应 release（小写 up 也命中）", "k" in hits, hits)
hits.clear()
screen._dispatch_key(_make_event("KeyPressEvent", key="up"))
check("onkey 不响应 press（turtle 语义）", "k" not in hits, hits)
hits.clear()
screen._dispatch_key(_make_event("KeyPressEvent", key=" "))
check("onkeypress('space') 响应 press", "kp" in hits, hits)
hits.clear()
screen._dispatch_key(_make_event("KeyPressEvent", key="q"))
check("onkeypress(None) 通配任意键", "kp" in hits, hits)

fired = []
screen.ontimer(lambda: fired.append(1), 0)
screen.painter.process_timers()
check("ontimer(0) 触发", fired == [1], fired)

# ---------------------------------------------------------------------------
print("[12] savefig 落盘与外部 fig/ax 共存")
close_all()
out = os.path.join(HERE, "_selftest_out.png")
m = Move()
m.speed(0)
for _ in range(5):
    m.forward(40)
    m.left(144)
move.savefig(out)
check("PNG 已生成", os.path.isfile(out) and os.path.getsize(out) > 0)

fig, ax = plt.subplots()
ax.plot([0, 1], [0, 1], color="orange")
m = Move(fig=fig, ax=ax)
m.speed(0)
m.forward(50)
check("外部 ax 被复用", m.getscreen().getaxes() is ax, m.getscreen().getaxes())
check("共用同一图形的 Move 复用同一屏幕", Move(fig=fig, ax=ax).getscreen() is m.getscreen())
check("原有 matplotlib 图形仍在", len(ax.lines) >= 1)
check("外部 ax 上画出了 move 折线", any(len(L.get_xdata()) >= 2 for L in ax.lines))
check("外部 ax 的坐标范围等于图形像素",
      abs((ax.get_xlim()[1] - ax.get_xlim()[0]) - m.getscreen().canvwidth) < 1.0,
      (ax.get_xlim(), m.getscreen().canvwidth))
check("外部 ax 不会污染默认单例屏幕",
      move.get_screen() is not m.getscreen(), move.get_screen())
move.savefig(out)
check("外部 ax 可落盘", os.path.getsize(out) > 0)
if os.path.isfile(out):
    os.remove(out)

# ---------------------------------------------------------------------------
print("[13] 异常与边界")
close_all()
try:
    MoveScreen()
    check("MoveScreen() 缺画布抛错", False)
except TurtleGraphicsError:
    check("MoveScreen() 缺画布抛错", True)

try:
    Move().pencolor("definitely-not-a-color")
    check("非法颜色抛错", False)
except TurtleGraphicsError:
    check("非法颜色抛错", True)

m = Move()
m.speed(0)
m.circle(50)
m.circle(-30, 180)
m.circle(20, steps=6)
check("circle 变体可用", len(m.currentLine) >= 1)
m.teleport(100, 100)
check("teleport", tuple(m.pos()) == (100.0, 100.0))
m.teleport(x=5)
check("teleport(x=)", m.pos()[0] == 5 and m.pos()[1] == 100.0)
m.hideturtle()
check("hideturtle", m.isvisible() is False)
m.showturtle()
check("showturtle", m.isvisible() is True)
m.setheading(0)
m.degrees(400.0)
m.left(100)
check("degrees(400) 后 heading==100", abs(m.heading() - 100) < 1e-9, m.heading())
m.radians()
m.setheading(0)
m.left(math.pi / 2)
check("radians 后 heading==pi/2", abs(m.heading() - math.pi / 2) < 1e-9, m.heading())
m.degrees(360.0)
try:
    m.shapesize(0, 1)
    check("shapesize(0) 抛错", False)
except TurtleGraphicsError:
    check("shapesize(0) 抛错", True)
try:
    m.shapetransform(0, 0, 0, 0)
    check("奇异变换矩阵抛错", False)
except TurtleGraphicsError:
    check("奇异变换矩阵抛错", True)

# ---------------------------------------------------------------------------
print("[14] 图片外形（Pillow 可用时）")
close_all()
try:
    from PIL import Image

    img_path = os.path.join(HERE, "_selftest_shape.png")
    Image.fromarray(np.zeros((24, 24, 4), dtype=np.uint8)).save(img_path)
    m = Move()
    m.speed(0)
    move.get_screen().register_shape(img_path)
    m.shape(img_path)
    m.forward(20)
    move.update()
    check("图片外形可用", m.shape() == img_path)
    os.remove(img_path)
except ImportError:
    print("  skip Pillow 不可用")

close_all()
print()
if FAILURES:
    print(f"{len(FAILURES)} 项失败: {FAILURES}")
    sys.exit(1)
print("全部通过")

"""Move 模块示例集 —— 每个函数一个可独立运行的例子。

用法::

    python cprdspy/CPR_matplotlib/Move/examples.py            # 列出所有例子
    python cprdspy/CPR_matplotlib/Move/examples.py square     # 运行其中一个
    python cprdspy/CPR_matplotlib/Move/examples.py square star   # 运行多个
    python cprdspy/CPR_matplotlib/Move/examples.py all        # 依次运行全部

无窗口环境下可以直接出图::

    MPLBACKEND=Agg python examples.py all --save out/          # 每例存一张 PNG

在 Jupyter 里::

    from cprdspy.CPR_matplotlib.Move import examples
    examples.spiral()
"""

import math
import os
import sys

import matplotlib.pyplot as plt

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
)

from cprdspy.CPR_matplotlib.Move.move import (  # noqa: E402
    Move,
    Shape,
    Vec2D,
    reset_screen,
    savefig,
)

#: ``True`` 时不调用 ``plt.show()``（批量出图 / 自测用）
QUIET = False


def _cjk_font():
    """挑一个系统里存在、能显示中文的字体（没有就返回 None）。

    用法：``m.write("中文", font=(_cjk_font() or "Arial", 12, "normal"))``
    —— 直接写中文字符串而不指定字体，matplotlib 会因为 Arial 缺字形
    而画出空白方块（并刷一堆 UserWarning），所以这里给出字体名。
    """
    from matplotlib import font_manager

    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in (
        "Microsoft YaHei",
        "SimHei",
        "Noto Sans CJK SC",
        "Source Han Sans SC",
        "PingFang SC",
        "WenQuanYi Zen Hei",
        "Arial Unicode MS",
    ):
        if name in available:
            return name
    return None


def _pump_timers(turtle, rounds=300):
    """把 ``ontimer`` 队列里的回调全部执行掉（没有 GUI 时也能看到结果）。

    正常运行时定时器由 GUI 事件循环触发；在 Agg / 保存图片 / 自测这类
    没有事件循环的场景里，逐个把"到期时间"提前再调用 ``process_timers()``，
    就能立刻把队列跑完（否则回调里新装的定时器永远还没到期）。
    """
    painter = turtle.getscreen().painter
    for _ in range(rounds):
        if not painter._timers:
            break
        # 把每个待触发定时器的到期时间挪到过去，等效于"时间已经流过"
        for key, (when, func) in list(painter._timers.items()):
            painter._timers[key] = (when - 1.0, func)
        painter._last_frame = 0.0  # 让下一次 frame() 不被节流
        painter.process_timers()
    turtle.getscreen().update()


def _finish(turtle, show=True):
    """统一的收尾：刷新**该示例自己的屏幕**，并按需显示。"""
    turtle.getscreen().update()
    if QUIET:
        return
    if show:
        plt.show()


def _new(speed=None, delay=None, canvas=(640, 480)):
    """新建一张干净的画布并返回 Move 对象。"""
    plt.close("all")
    reset_screen()
    m = Move()
    sc = m.getscreen()
    sc.screensize(*canvas)
    sc.bgcolor("white")
    if delay is not None:
        sc.delay(delay)
    if speed is not None:
        m.speed(speed)
    return m


# ---------------------------------------------------------------------------
# 1. 入门
# ---------------------------------------------------------------------------


def square():
    """最简单的正方形（体会动画）。"""
    m = _new(speed=1)
    m.pensize(3)
    m.pencolor("#0f0")
    for _ in range(4):
        m.forward(120)
        m.left(90)
    _finish(m)


def star():
    """五角星：转 144 度画五条边。"""
    m = _new(speed=4)
    m.pencolor("red")
    m.pensize(2)
    for _ in range(5):
        m.forward(160)
        m.left(144)
    _finish(m)


def spiral():
    """螺旋线：每走一步都稍微转一点、走得更远一点。"""
    m = _new(speed=0)
    m.pencolor("#0a0")
    for i in range(120):
        m.forward(4 + i * 1.6)
        m.left(59)
    _finish(m)


def rainbow_flower():
    """彩色花瓣：用 colormode(255) 做渐变。"""
    m = _new(speed=3)
    sc = m.getscreen()
    sc.colormode(255)
    for i in range(72):
        r = 255 - i * 3 if i * 3 < 255 else 0
        m.pencolor(r, 0, i * 3 if i * 3 < 255 else 255)
        for _ in range(2):
            m.forward(90)
            m.left(75)
        m.left(5)
    sc.colormode(1.0)
    _finish(m)


# ---------------------------------------------------------------------------
# 2. 动画与轨迹
# ---------------------------------------------------------------------------


def animated_polygon():
    """同一段代码，两种速度：慢速看动画，快速看结果。"""
    m = _new(speed=1, delay=20)
    m.pensize(3)
    for _ in range(6):
        m.forward(120)
        m.left(60)
    _finish(m)
    # 第二张：speed(0) 瞬间完成
    m2 = _new(speed=0)
    m2.pensize(3)
    for _ in range(6):
        m2.forward(120)
        m2.left(60)
    _finish(m, show=False)


def hypno_spiral():
    """经典"海龟图形"：36 次前进 + 170 度转弯。"""
    m = _new(speed=0)
    for _ in range(36):
        m.forward(180)
        m.left(170)
    _finish(m)


def circle_walk():
    """circle() 的各种用法：整圆、圆弧、正多边形。"""
    m = _new(speed=0)
    m.pensize(2)
    m.pencolor("#06c")
    m.circle(60)  # 整圆
    m.penup()
    m.goto(-160, 0)
    m.pendown()
    m.pencolor("#c60")
    m.circle(60, 180)  # 半圆
    m.penup()
    m.goto(120, 0)
    m.pendown()
    m.pencolor("#0a0")
    m.circle(70, steps=6)  # 正六边形
    _finish(m)


# ---------------------------------------------------------------------------
# 3. 填充、印章、文字
# ---------------------------------------------------------------------------


def filled_house():
    """填充：墙 + 屋顶 + 门窗（begin_fill/end_fill）。"""
    m = _new(speed=0)
    m.pensize(2)

    def box(w, h, fill):
        m.color("black", fill)
        m.begin_fill()
        for _ in range(2):
            m.forward(w)
            m.left(90)
            m.forward(h)
            m.left(90)
        m.end_fill()

    # 墙
    box(160, 110, "#ffe08a")
    # 屋顶（三角形）
    m.goto(0, 110)
    m.color("black", "#c0392b")
    m.begin_fill()
    m.goto(80, 180)
    m.goto(160, 110)
    m.goto(0, 110)
    m.end_fill()
    # 门
    m.penup()
    m.goto(60, 0)
    m.pendown()
    box(40, 70, "#8b5a2b")
    _finish(m)


def stamped_ring():
    """印章：沿圆周盖一圈，做出"花瓣边框"。"""
    m = _new(speed=0)
    m.shape("circle")
    m.shapesize(1.2)
    m.color("#e67e22", "#f1c40f")
    m.penup()
    for _ in range(18):
        m.forward(150)
        m.stamp()
        m.goto(0, 0)
        m.left(20)
    _finish(m)


def poly_star_shape():
    """用 begin_poly/get_poly 记录一个形状，再注册成新外形。"""
    m = _new(speed=0)
    m.begin_poly()
    for _ in range(5):
        m.forward(30)
        m.left(144)
    m.end_poly()
    poly = m.get_poly()
    m.getscreen().register_shape("mystar", poly)

    m.reset()
    m.shape("mystar")
    m.color("#e74c3c", "#f39c12")
    m.shapesize(1.0)
    for i in range(12):
        m.penup()
        m.goto(0, 0)
        m.setheading(i * 30)
        m.forward(150)
        m.stamp()
    _finish(m)


def labels():
    """write()：对齐、字体、以及让画笔跟着文字走。"""
    m = _new(speed=0)
    m.penup()
    m.goto(-250, 150)
    m.pencolor("#2c3e50")
    m.write("align=left", font=("Arial", 14, "bold"))
    m.goto(0, 60)
    m.write("align=center", align="center", font=("Arial", 14, "normal"))
    m.goto(250, -30)
    m.write("align=right", align="right", font=("Arial", 14, "italic"))
    m.pendown()
    m.pencolor("#e67e22")
    m.pensize(2)
    m.write("-> 画笔跟着文字走", move=True, font=("Arial", 12, "bold"))
    m.forward(80)
    _finish(m)


# ---------------------------------------------------------------------------
# 4. 形状与变形
# ---------------------------------------------------------------------------


def shapes_gallery():
    """内置外形一览，以及 shapesize / tilt / shearfactor 的效果。"""
    m = _new(speed=0)
    names = ["arrow", "turtle", "classic", "triangle", "square", "circle"]
    m.penup()
    for i, name in enumerate(names):
        m.goto(-220 + i * 90, 80)
        m.shape(name)
        m.shapesize(1.5)
        m.stamp()
    m.goto(-220, -140)
    m.shape("square")
    m.shapesize(1.0)
    m.stamp()
    m.goto(-80, -140)
    m.shapesize(2.0, 1.0)
    m.stamp()
    m.goto(60, -140)
    m.shapesize(1.5)
    m.tiltangle(30)
    m.stamp()
    m.goto(210, -140)
    m.shearfactor(0.6)
    m.stamp()
    m.penup()
    m.goto(-300, 200)
    m.write("外形与变形", font=("Arial", 14, "bold"))
    _finish(m)


def compound_turtle():
    """复合（多色）外形：一次注册，整只海龟多色显示。"""
    m = _new(speed=0)
    s = Shape("compound")
    s.addcomponent(((0, 0), (-8, -14), (0, -9), (8, -14)), "#2c3e50", "black")
    s.addcomponent(((0, 10), (-6, -2), (6, -2)), "#e74c3c", "black")
    m.getscreen().register_shape("kite", s)
    m.shape("kite")
    m.shapesize(2)
    m.penup()
    m.goto(-200, 0)
    m.pendown()
    m.pencolor("#3498db")
    m.pensize(2)
    for _ in range(4):
        m.forward(120)
        m.left(90)
    m.penup()
    m.goto(150, 0)
    m.pendown()
    m.circle(80)
    _finish(m)


# ---------------------------------------------------------------------------
# 5. 数学与几何
# ---------------------------------------------------------------------------


def spirograph():
    """用向量运算画内摆线（圆内滚圆）。"""
    m = _new(speed=0)
    m.pencolor("#8e44ad")
    R, r, d = 150.0, 50.0, 80.0
    steps = 720
    m.penup()
    for i in range(steps + 1):
        t = 2 * math.pi * i / steps
        k = (R - r) / r
        x = (R - r) * math.cos(t) + d * math.cos(k * t)
        y = (R - r) * math.sin(t) - d * math.sin(k * t)
        if i == 0:
            m.goto(x, y)
            m.pendown()
        else:
            m.goto(x, y)
    _finish(m)


def math_star():
    """用 Vec2D、distance()、towards() 做几何计算。"""
    m = _new(speed=0)
    # 画一个正十七边形，并标出到某个顶点的距离
    n = 17
    R = 150
    points = []
    for i in range(n):
        ang = 2 * math.pi * i / n
        points.append(Vec2D(R * math.cos(ang), R * math.sin(ang)))
    m.penup()
    m.goto(points[0])
    m.pendown()
    m.pencolor("#16a085")
    for p in points[1:] + [points[0]]:
        m.goto(p)
    # 再从中心连到 0 号顶点
    m.pencolor("#c0392b")
    m.pensize(2)
    m.goto(0, 0)
    m.setheading(m.towards(points[0]))
    m.forward(m.distance(points[0]))
    m.write("  R = %d" % R, font=("Arial", 12, "bold"))
    _finish(m)


# ---------------------------------------------------------------------------
# 6. 世界坐标与坐标变换
# ---------------------------------------------------------------------------


def world_plot():
    """setworldcoordinates：直接画一条函数曲线。"""
    m = _new(speed=0)
    m.getscreen().setworldcoordinates(-1, -1.5, 2 * math.pi + 1, 1.5)
    m.pencolor("#2980b9")
    m.pensize(2)
    x = -1.0
    m.penup()
    m.goto(x, math.sin(x))
    m.pendown()
    while x <= 2 * math.pi:
        x += 0.05
        m.goto(x, math.sin(x))
    # 在 world 模式下，角度看起来会被拉伸（这是 turtle 的已知行为）
    m.write("sin(x)", font=("Arial", 12, "bold"))
    _finish(m)


# ---------------------------------------------------------------------------
# 7. 与 matplotlib 共存
# ---------------------------------------------------------------------------


def with_matplotlib():
    """把海龟画到已有的 figure/axes 上，与普通 matplotlib 图形叠加。"""
    import numpy as np

    plt.close("all")
    reset_screen()
    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    xs = np.linspace(-320, 320, 400)
    ax.plot(xs, 120 * np.sin(xs / 90.0), color="#bdc3c7", linewidth=2, label="sin")
    ax.legend(loc="upper right")

    m = Move(fig=fig, ax=ax)  # 复用同一块坐标轴
    m.speed(0)
    m.pencolor("#e74c3c")
    m.pensize(3)
    for i in range(24):
        m.setheading(i * 15)
        m.forward(60 + 10 * math.sin(i))
        m.penup()
        m.goto(0, 0)
        m.pendown()
    _finish(m)


# ---------------------------------------------------------------------------
# 8. 交互
# ---------------------------------------------------------------------------


def keyboard_drive():
    """键盘控制：方向键前进/后退/转向（需要图形窗口获得焦点）。

    运行后先点一下图形窗口，再按方向键；Esc 退出。
    """
    plt.close("all")
    reset_screen()
    m = Move()
    sc = m.getscreen()
    sc.bgcolor("white")
    m.shape("turtle")
    m.shapesize(1.5)
    m.pencolor("#0f0")
    m.speed(6)
    m.pensize(2)
    m.write("click the window, then use arrow keys", font=("Arial", 11, "normal"))

    def go():
        m.forward(20)

    def back():
        m.backward(20)

    def turn_left():
        m.left(15)

    def turn_right():
        m.right(15)

    def quit_():
        sc.bye()

    for key, fn in (
        ("Up", go),
        ("Down", back),
        ("Left", turn_left),
        ("Right", turn_right),
    ):
        sc.onkeypress(fn, key)
    sc.onkeypress(quit_, "Escape")
    sc.listen()
    sc.title("arrow keys to move, Esc to quit")
    _finish(m)


def click_to_move():
    """鼠标点击：海龟走到点击处（屏幕级 onclick）。"""
    plt.close("all")
    reset_screen()
    m = Move()
    sc = m.getscreen()
    sc.bgcolor("#fdfdfd")
    m.shape("turtle")
    m.shapesize(1.5)
    m.pencolor("#e67e22")
    m.speed(5)

    def walk(x, y):
        m.setheading(m.towards(x, y))
        m.goto(x, y)

    sc.onclick(walk)
    m.write("click anywhere", font=("Arial", 12, "bold"))
    _finish(m)


def timer_animation():
    """ontimer：让海龟自己"巡航"，不阻塞脚本。"""
    plt.close("all")
    reset_screen()
    m = Move()
    sc = m.getscreen()
    sc.bgcolor("#eef6ff")
    m.shape("turtle")
    m.pencolor("#2980b9")
    m.speed(0)
    m.pensize(2)
    state = {"n": 0, "limit": 60}

    def tick():
        if state["n"] >= state["limit"]:
            return
        state["n"] += 1
        m.forward(28)
        m.right(20)  # 每步转一点，走出一条舒展的弧线
        sc.ontimer(tick, 30)

    tick()
    _pump_timers(m)  # 没有 GUI 时把定时器队列跑完；有 GUI 时由事件循环驱动
    _finish(m)


# ---------------------------------------------------------------------------
# 9. 撤销与状态
# ---------------------------------------------------------------------------


def undo_demo():
    """undo()：先画一圈，再一格一格撤回来。

    注意：跑完之后画面是**空的** —— 撤销本来就是要把画过的东西收回，
    这个例子看的是过程（有窗口时能看到线一条条消失）。
    """
    m = _new(speed=0)
    m.pensize(3)
    m.pencolor("#8e44ad")
    for _ in range(4):
        m.forward(100)
        m.left(90)
    m.getscreen().update()
    if not QUIET:
        plt.pause(1.0)
    while m.undobufferentries():
        m.undo()
    _finish(m)


def pen_state():
    """pen() 保存/恢复画笔状态，以及 dot() 画点。"""
    m = _new(speed=0)

    def dashed(n, length=18, gap=12):
        for _ in range(n):
            m.pendown()
            m.forward(length)
            m.penup()
            m.forward(gap)

    # 虚线
    m.penup()
    m.goto(-300, 120)
    m.pendown()
    m.pencolor("#34495e")
    m.pensize(1)
    dashed(9)

    # 保存当前画笔状态 -> 换成粗红线 -> 恢复
    m.penup()
    m.goto(-300, 0)
    m.pendown()
    state = m.pen()
    m.pensize(6)
    m.pencolor("#e74c3c")
    m.forward(180)
    m.pen(state)  # 恢复成细深蓝虚线
    dashed(9)

    # dot()：画点
    m.penup()
    m.goto(-300, -120)
    m.pendown()
    m.pencolor("#2980b9")
    m.pensize(2)
    for i in range(8):
        m.forward(40)
        m.dot(6 + i * 3, "#f1c40f")
    _finish(m)


# ---------------------------------------------------------------------------
# 10. 综合
# ---------------------------------------------------------------------------


def mandala():
    """综合示例：渐变 + 高度对称的放射线（一次画出 36 条）。"""
    m = _new(speed=0)
    m.pensize(2)
    m.getscreen().colormode(255)
    for i in range(72):
        # 每条射线用自己的颜色，形成渐变
        m.pencolor(40 + i * 3, 120 + (i * 2) % 120, 255 - i * 3)
        m.penup()
        m.goto(0, 0)
        m.setheading(i * 5)
        m.pendown()
        # 用折线近似一条带弧度的"花瓣边"
        for step in range(1, 16):
            m.forward(12)
            m.left(4)
        m.right(60)  # 让内侧收回来，形成菱形花瓣
    m.getscreen().colormode(1.0)
    _finish(m)


def rose():
    """综合示例：用 circle() 拼一朵玫瑰（数学花）。"""
    m = _new(speed=0)
    m.pensize(1)
    m.getscreen().colormode(255)
    for i in range(60):
        m.pencolor(255 - i * 4, 40 + i * 3, 120 + i)
        m.circle(90 + i * 2, 90)
        m.left(90)
        m.circle(90 + i * 2, 90)
        m.left(18)
    m.getscreen().colormode(1.0)
    _finish(m)


def scene():
    """综合示例：一幅小风景（太阳、山、树、草地）。"""
    m = _new(speed=0)
    m.penup()

    # 太阳
    m.goto(-200, 120)
    m.pendown()
    m.color("#f39c12", "#f1c40f")
    m.begin_fill()
    m.circle(45)
    m.end_fill()

    # 草地
    m.penup()
    m.goto(-300, -150)
    m.pendown()
    m.color("#27ae60", "#2ecc71")
    m.begin_fill()
    m.goto(300, -150)
    m.goto(300, -240)
    m.goto(-300, -240)
    m.goto(-300, -150)
    m.end_fill()

    # 山
    for base_x, height, color in ((-140, 150, "#7f8c8d"), (60, 190, "#95a5a6")):
        m.penup()
        m.goto(base_x - 110, -150)
        m.pendown()
        m.color("#2c3e50", color)
        m.begin_fill()
        m.goto(base_x, -150 + height)
        m.goto(base_x + 110, -150)
        m.goto(base_x - 110, -150)
        m.end_fill()

    # 树
    for x in (170, 230):
        m.penup()
        m.goto(x, -150)
        m.pendown()
        m.color("#2c3e50", "#6d4c41")
        m.begin_fill()
        m.goto(x - 8, -150)
        m.goto(x - 8, -90)
        m.goto(x + 8, -90)
        m.goto(x + 8, -150)
        m.end_fill()
        m.color("#1e8449", "#27ae60")
        m.begin_fill()
        m.goto(x - 40, -90)
        m.goto(x, -20)
        m.goto(x + 40, -90)
        m.goto(x - 40, -90)
        m.end_fill()

    m.penup()
    m.goto(-290, 200)
    m.pencolor("#2c3e50")
    m.write("move on matplotlib", font=("Arial", 16, "bold"))
    _finish(m)


# ---------------------------------------------------------------------------
# 注册表与入口
# ---------------------------------------------------------------------------

EXAMPLES = {
    # 入门
    "square": square,
    "star": star,
    "spiral": spiral,
    "rainbow_flower": rainbow_flower,
    # 动画
    "animated_polygon": animated_polygon,
    "hypno_spiral": hypno_spiral,
    "circle_walk": circle_walk,
    # 填充 / 印章 / 文字
    "filled_house": filled_house,
    "stamped_ring": stamped_ring,
    "poly_star_shape": poly_star_shape,
    "labels": labels,
    # 形状
    "shapes_gallery": shapes_gallery,
    "compound_turtle": compound_turtle,
    # 数学
    "spirograph": spirograph,
    "math_star": math_star,
    "world_plot": world_plot,
    # 与 matplotlib 共存
    "with_matplotlib": with_matplotlib,
    # 交互
    "keyboard_drive": keyboard_drive,
    "click_to_move": click_to_move,
    "timer_animation": timer_animation,
    # 撤销 / 画笔状态
    "undo_demo": undo_demo,
    "pen_state": pen_state,
    # 综合
    "mandala": mandala,
    "rose": rose,
    "scene": scene,
}


def list_examples():
    """打印所有例子及其一句话说明。"""
    print("Move 示例（共 %d 个）：\n" % len(EXAMPLES))
    for name, fn in EXAMPLES.items():
        doc = (fn.__doc__ or "").strip().splitlines()[0]
        print("  %-18s %s" % (name, doc))
    print("\n用法：python examples.py <名字> [名字...] | all | --list")
    print("出图：MPLBACKEND=Agg python examples.py all --save out/")


def run(names, save_dir=None):
    """运行指定名字的例子；``save_dir`` 不为空时逐个保存 PNG。"""
    global QUIET
    for name in names:
        fn = EXAMPLES.get(name)
        if fn is None:
            print("未知示例：%s（用 --list 查看全部）" % name)
            continue
        print("== %s ==" % name)
        if save_dir:
            QUIET = True
            try:
                fn()
            finally:
                QUIET = False
            os.makedirs(save_dir, exist_ok=True)
            out = os.path.join(save_dir, "%s.png" % name)
            # 用当前图形保存：示例可能用的是外部 fig/ax，
            # 不能假定"默认屏幕"就是它自己那张图。
            fig = plt.gcf()
            fig.savefig(out)
            print("   已保存", out)
        else:
            try:
                fn()
            finally:
                plt.close("all")


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    save_dir = None
    if "--save" in argv:
        idx = argv.index("--save")
        try:
            save_dir = argv[idx + 1]
            if save_dir in args:
                args.remove(save_dir)
        except IndexError:
            print("--save 后面要跟目录名")
            return 2

    if not args or "--list" in argv or "-l" in argv:
        list_examples()
        return 0

    if args == ["all"]:
        names = list(EXAMPLES)
    else:
        names = args
    run(names, save_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

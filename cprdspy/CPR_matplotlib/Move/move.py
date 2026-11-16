#
# move.py: a Matplotlib based turtle-graphics ("move graphics") module
#
# 改写自 CPython 标准库 turtle.py（1.1b, 2009 版，作者 Gregor Lingl）。
# 原始版权与许可声明如下，改写版本同样适用：
#
# Copyright (C) 2006 - 2010  Gregor Lingl
# email: glingl@aon.at
#
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.
#
# 本文件是"改动后的版本"（altered source version）：画布层由 Tkinter 换成
# matplotlib，类名由 Turtle 系列改为 Move 系列，详见模块文档。

"""
move —— 基于 matplotlib 的"海龟绘图"（move graphics）动画模块。

把小海龟想象成 x-y 平面原点 (0, 0) 处的一个机器人：给它 ``forward(15)``，
它就会（在屏幕上）朝着当前朝向走 15 个像素并画出一条线；
给它 ``right(25)``，它就在原地顺时针转 25 度。

把这一类命令组合起来，就能轻松画出复杂的图形。

----- move.py

本模块是 CPython 标准库 ``turtle.py``（以及它对 Python 2.5 之前 turtle 的
扩展实现）的 matplotlib 改写版，目标是与 turtle 保持"近似 100% 的 API 兼容"：

* 所有类都保留，只是按模块主题改名（见下表），方法名、参数、返回值、
  别名（``fd`` / ``lt`` / ``pu`` ...）与 turtle 完全一致；
* 模块级函数（``forward`` / ``goto`` / ``circle`` ...）与 turtle 同名同签名，
  用 :func:`copy_api` 或 ``move.Turtle`` 之类的兼容别名即可迁移旧代码。

改名对照表：

    turtle                 move
    ---------------------  --------------------
    ScrolledCanvas         MoveCanvas
    TurtleScreen           MoveScreenBase / MoveScreen
    Screen / _Screen       MoveScreen (单例由 :func:`Screen` 提供)
    RawTurtle / RawPen     RawMove / RawPen
    Turtle / Pen           Move / Pen
    Vec2D                  Vec2D
    Shape                  Shape

相比原 turtle，改动集中在"画布层"：

* 图形由 matplotlib 渲染，绘图区就是一块"像素坐标画布"，
  1 个数据单位等于 1 像素，因此世界坐标、缩放、翻转等语义与 turtle 一致；
* 动画改用 matplotlib 的延迟重绘（``canvas.draw_idle``）驱动，
  ``speed()`` 控制中间插值步数、``delay()``/``tracer()`` 控制重绘节奏，
  ``done()``/``mainloop()`` 对应 ``plt.show()``；
* 鼠标、键盘、定时器事件改用 matplotlib 的事件系统；
* 支持把已有的 ``Figure``/``Axes``（例如 ``plt.subplots()`` 的结果）交给
  ``MoveScreen``，从而与其他 matplotlib 图形拼在同一张图上；
* 背景图、图片型外形改用 Pillow 读取位图（未安装 Pillow 时自动退化为多边形外形）；
* 去掉了 Tkinter 的滚动条画布，改用 matplotlib 坐标轴范围表示可视区域。

模块内仍保留 turtle 的配置机制：在脚本目录或本文件目录放 ``move.cfg``
（兼容读取 ``turtle.cfg``）即可修改窗口尺寸、背景色、默认速度等。

用法示例::

    import matplotlib.pyplot as plt
    from cprdspy.CPR_matplotlib.Move.move import *

    speed(0)
    for _ in range(36):
        forward(120)
        left(170)

    done()          # 等价于 plt.show()
"""

import math
import inspect
import sys
from os.path import isfile, split, join
from copy import deepcopy

import matplotlib.pyplot as plt

try:
    from ._painter import MovePainter
except ImportError:  # 直接以脚本方式运行（python move.py）时的兜底
    import os as _os
    import sys as _sys

    _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
    from _painter import MovePainter

_tg_classes = [
    "MoveCanvas",
    "MoveScreenBase",
    "MoveScreen",
    "RawMove",
    "Move",
    "RawPen",
    "Pen",
    "Shape",
    "Vec2D",
]
_tg_screen_functions = [
    "addshape",
    "bgcolor",
    "bgpic",
    "bye",
    "clearscreen",
    "colormode",
    "delay",
    "exitonclick",
    "getcanvas",
    "getshapes",
    "listen",
    "mainloop",
    "mode",
    "numinput",
    "onkey",
    "onkeypress",
    "onkeyrelease",
    "onscreenclick",
    "ontimer",
    "register_shape",
    "resetscreen",
    "screensize",
    "setup",
    "setworldcoordinates",
    "textinput",
    "title",
    "tracer",
    "turtles",
    "update",
    "window_height",
    "window_width",
]
_tg_turtle_functions = [
    "back",
    "backward",
    "begin_fill",
    "begin_poly",
    "bk",
    "circle",
    "clear",
    "clearstamp",
    "clearstamps",
    "clone",
    "color",
    "degrees",
    "distance",
    "dot",
    "down",
    "end_fill",
    "end_poly",
    "fd",
    "fillcolor",
    "filling",
    "forward",
    "get_poly",
    "getpen",
    "getscreen",
    "get_shapepoly",
    "getturtle",
    "goto",
    "heading",
    "hideturtle",
    "home",
    "ht",
    "isdown",
    "isvisible",
    "left",
    "lt",
    "onclick",
    "ondrag",
    "onrelease",
    "pd",
    "pen",
    "pencolor",
    "pendown",
    "pensize",
    "penup",
    "pos",
    "position",
    "pu",
    "radians",
    "right",
    "reset",
    "resizemode",
    "rt",
    "seth",
    "setheading",
    "setpos",
    "setposition",
    "setundobuffer",
    "setx",
    "sety",
    "shape",
    "shapesize",
    "shapetransform",
    "shearfactor",
    "showturtle",
    "speed",
    "st",
    "stamp",
    "teleport",
    "tilt",
    "tiltangle",
    "towards",
    "turtlesize",
    "undo",
    "undobufferentries",
    "up",
    "width",
    "write",
    "xcor",
    "ycor",
]
_tg_utilities = ["write_docstringdict", "done"]

__all__ = (
    _tg_classes
    + _tg_screen_functions
    + _tg_turtle_functions
    + _tg_utilities
    + ["Terminator", "TurtleGraphicsError"]
)

_alias_list = [
    "addshape",
    "backward",
    "bk",
    "fd",
    "ht",
    "lt",
    "pd",
    "pos",
    "pu",
    "rt",
    "seth",
    "setpos",
    "setposition",
    "st",
    "turtlesize",
    "up",
    "width",
]

_CFG = {
    "width": 0.5,  # 屏幕宽度（浮点数为屏占比，整数为像素）
    "height": 0.75,  # 屏幕高度
    "canvwidth": 640,  # 画布宽（像素）
    "canvheight": 480,  # 画布高（像素）
    "leftright": None,
    "topbottom": None,
    "mode": "standard",  # MoveScreen
    "colormode": 1.0,
    "delay": 10,
    "undobuffersize": 1000,  # RawMove
    "shape": "classic",
    "pencolor": "#0f0",  # 荧光绿，比纯黑更醒目也更"好看"
    "fillcolor": "#0f0",
    "resizemode": "noresize",
    "visible": True,
    "language": "english",  # docstrings
    "exampleturtle": "move",
    "examplescreen": "screen",
    "title": "Python Move Graphics",
    "using_IDLE": False,
    "figsize": None,  # (宽, 高) 英寸；None 表示按画布像素和 dpi 推算
    "dpi": 100,
}

#: 兼容 turtle 的 ``_CFG`` 名字。
_CFG_TURTLE = _CFG


def config_dict(filename):
    """Convert content of config-file into dictionary."""
    with open(filename, "r", encoding="utf-8") as f:
        cfglines = f.readlines()
    cfgdict = {}
    for line in cfglines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            key, value = line.split("=")
        except ValueError:
            print("Bad line in config-file %s:\n%s" % (filename, line))
            continue
        key = key.strip()
        value = value.strip()
        if value in ["True", "False", "None", "''", '""']:
            value = eval(value)
        else:
            try:
                if "." in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                pass  # value need not be converted
        cfgdict[key] = value
    return cfgdict


def readconfig(cfgdict):
    """读取配置文件并更新配置字典。

    优先读取当前工作目录下的 ``move.cfg``（兼容 ``turtle.cfg``），
    再从本模块所在目录读取同名文件；若配置里有 ``importconfig``，
    则读取 ``move_<name>.cfg``。找不到配置文件就用默认配置。
    """
    default_cfg = "move.cfg"
    cfgdict1 = {}
    cfgdict2 = {}
    for candidate in ("move.cfg", "turtle.cfg"):
        if isfile(candidate):
            cfgdict1 = config_dict(candidate)
            break
    if "importconfig" in cfgdict1:
        default_cfg = "move_%s.cfg" % cfgdict1["importconfig"]
    try:
        head, tail = split(__file__)
        cfg_file2 = join(head, default_cfg)
    except Exception:
        cfg_file2 = ""
    if isfile(cfg_file2):
        cfgdict2 = config_dict(cfg_file2)
    _CFG.update(cfgdict2)
    _CFG.update(cfgdict1)


try:
    readconfig(_CFG)
except Exception:
    print("No configfile read, reason unknown")


class Vec2D(tuple):
    """A 2 dimensional vector class, used as a helper class
    for implementing move graphics.
    May be useful for move graphics programs also.
    Derived from tuple, so a vector is a tuple!

    Provides (for a, b vectors, k number):
       a+b vector addition
       a-b vector subtraction
       a*b inner product
       k*a and a*k multiplication with scalar
       |a| absolute value of a
       a.rotate(angle) rotation
    """

    def __new__(cls, x, y):
        return tuple.__new__(cls, (x, y))

    def __add__(self, other):
        return Vec2D(self[0] + other[0], self[1] + other[1])

    def __mul__(self, other):
        if isinstance(other, Vec2D):
            return self[0] * other[0] + self[1] * other[1]
        return Vec2D(self[0] * other, self[1] * other)

    def __rmul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return Vec2D(self[0] * other, self[1] * other)
        return NotImplemented

    def __sub__(self, other):
        return Vec2D(self[0] - other[0], self[1] - other[1])

    def __neg__(self):
        return Vec2D(-self[0], -self[1])

    def __abs__(self):
        return math.hypot(*self)

    def rotate(self, angle):
        """rotate self counterclockwise by angle"""
        perp = Vec2D(-self[1], self[0])
        angle = math.radians(angle)
        c, s = math.cos(angle), math.sin(angle)
        return Vec2D(self[0] * c + perp[0] * s, self[1] * c + perp[1] * s)

    def __getnewargs__(self):
        return (self[0], self[1])

    def __repr__(self):
        # 用最短往返表示，既不丢精度也不会像 %r 那样刷屏
        return "(%s,%s)" % (repr(float(self[0])), repr(float(self[1])))


##############################################################################
###                  End of Matplotlib - interface                         ###
### 画布层在 ._painter 中实现（原 turtle 对应 Tkinter 接口部分）           ###
##############################################################################


class Terminator(Exception):
    """Will be raised in MoveScreen.update, if _RUNNING becomes False.

    This stops execution of a move graphics script.
    """

    pass


class TurtleGraphicsError(Exception):
    """Some MoveGraphics Error"""


class Shape(object):
    """Data structure modeling shapes.

    attribute _type is one of "polygon", "image", "compound"
    attribute _data is - depending on _type a polygon-tuple,
    an image or a list constructed using the addcomponent method.
    """

    def __init__(self, type_, data=None):
        self._type = type_
        if type_ == "polygon":
            if isinstance(data, list):
                data = tuple(data)
        elif type_ == "image":
            if isinstance(data, str):
                if data and isfile(data):
                    data = MoveScreen._image(data)
                # else data assumed to be an image array
        elif type_ == "compound":
            data = []
        else:
            raise TurtleGraphicsError("There is no shape type %s" % type_)
        self._data = data

    def addcomponent(self, poly, fill, outline=None):
        """Add component to a shape of type compound.

        Arguments: poly is a polygon, i. e. a tuple of number pairs.
        fill is the fillcolor of the component,
        outline is the outline color of the component.

        call (for a Shapeobject namend s):
        --   s.addcomponent(((0,0), (10,10), (-10,10)), "red", "blue")

        Example:
        >>> poly = ((0,0),(10,-5),(0,10),(-10,-5))
        >>> s = Shape("compound")
        >>> s.addcomponent(poly, "red", "blue")
        >>> # .. add more components and then use register_shape()
        """
        if self._type != "compound":
            raise TurtleGraphicsError("Cannot add component to %s Shape" % self._type)
        if outline is None:
            outline = fill
        self._data.append([poly, fill, outline])


class Tbuffer(object):
    """Ring buffer used as undobuffer for RawMove objects."""

    def __init__(self, bufsize=10):
        self.bufsize = bufsize
        self.buffer = [[None]] * bufsize
        self.ptr = -1
        self.cumulate = False

    def reset(self, bufsize=None):
        if bufsize is None:
            for i in range(self.bufsize):
                self.buffer[i] = [None]
        else:
            self.bufsize = bufsize
            self.buffer = [[None]] * bufsize
        self.ptr = -1

    def push(self, item):
        if self.bufsize > 0:
            if not self.cumulate:
                self.ptr = (self.ptr + 1) % self.bufsize
                self.buffer[self.ptr] = item
            else:
                self.buffer[self.ptr].append(item)

    def pop(self):
        if self.bufsize > 0:
            item = self.buffer[self.ptr]
            if item is None:
                return None
            else:
                self.buffer[self.ptr] = [None]
                self.ptr = (self.ptr - 1) % self.bufsize
                return item

    def nr_of_items(self):
        return self.bufsize - self.buffer.count([None])

    def __repr__(self):
        return str(self.buffer) + " " + str(self.ptr)


def _frame_interval_ms(delay_value, speed):
    """由 ``delay()`` 与 ``speed()`` 推出动画两帧之间的间隔（毫秒）。

    * ``delay`` 给出基准节奏（默认 10ms）；
    * ``speed`` 按几何级数缩短间隔：speed 每 +1 大约快 1.2 倍，
      speed=1 约 21ms/帧，speed=10 约 4ms/帧；
    * 返回 0 表示不等待（speed=0 或 delay=0）。

    用几何而不是线性，是为了让"速度档位"在时间上大致等距：
    线性映射下相邻档位差别太小，肉眼分不出来。
    """
    try:
        base = float(delay_value or 0)
    except (TypeError, ValueError):
        return 0.0
    if base <= 0:
        return 0.0
    base = max(0.5, base)
    try:
        raw = int(speed or 0)
    except (TypeError, ValueError):
        return 0.0
    if raw <= 0:
        # speed=0 表示完全不做动画
        return 0.0
    level = min(10, max(1, raw))
    per_frame = 9.0 * (1.2 ** (10 - 2 * level))
    # delay 作为基准的缩放：delay(10) 时就是 per_frame
    return per_frame * (base / 10.0)


def _clean_degrees(value):
    """把由三角函数反解出来的角度"整理"一下，但不损失有效精度。

    ``atan2`` 的结果在整度数处常有 1e-13 级别的噪声（例如 90.00000000000001）。
    这里只在**非常接近**某个整数（或 0.5 的整数倍）时才吸附过去，
    其余情况原样返回，因此不会像固定 ``round(..., 10)`` 那样丢掉精度。
    """
    for tolerance in (1e-12, 1e-9):
        snapped = round(value)
        if abs(value - snapped) <= tolerance:
            return float(snapped)
        snapped_half = round(value * 2) / 2.0
        if abs(value - snapped_half) <= tolerance:
            return float(snapped_half)
    return float(value)


def _norm_key(key):
    """把按键名字归一化成"大写多字符 / 原样单字符"。

    matplotlib 用小写（``"up"``、``" "``），turtle 的文档用 ``"Up"``、
    ``"space"``；这里统一成大写形式，使两种写法都能命中，
    同时保留 ``"a"`` 与 ``"A"`` 的区别。
    """
    if not isinstance(key, str):
        return key
    if key == " ":
        return "SPACE"
    if len(key) > 1:
        return key.upper()
    return key


def _key_candidates(key):
    """返回一次按键事件可能匹配的所有绑定键名（按优先级）。"""
    cand = []
    for candidate in (key, _norm_key(key)):
        if candidate not in cand:
            cand.append(candidate)
    return cand


def _ask_string(title, prompt):
    """弹出文本输入框；无 GUI 工具包时退回命令行输入。"""
    try:
        import tkinter as TK
        from tkinter import simpledialog

        root = TK.Tk()
        root.withdraw()
        try:
            root.attributes("-topmost", True)
        except Exception:
            pass
        try:
            return simpledialog.askstring(title, prompt, parent=root)
        finally:
            root.destroy()
    except Exception:
        try:
            return input("%s\n%s: " % (title, prompt))
        except EOFError:
            return None


def _ask_float(title, prompt, default=None, minval=None, maxval=None):
    """弹出数值输入框；无 GUI 工具包时退回命令行输入。"""
    try:
        import tkinter as TK
        from tkinter import simpledialog

        root = TK.Tk()
        root.withdraw()
        try:
            root.attributes("-topmost", True)
        except Exception:
            pass
        try:
            return simpledialog.askfloat(
                title,
                prompt,
                initialvalue=default,
                minvalue=minval,
                maxvalue=maxval,
                parent=root,
            )
        finally:
            root.destroy()
    except Exception:
        try:
            raw = input("%s\n%s " % (title, prompt))
        except EOFError:
            return None
        if raw is None or raw == "":
            return default
        try:
            value = float(raw)
        except ValueError:
            return None
        if minval is not None and value < minval:
            return None
        if maxval is not None and value > maxval:
            return None
        return value


class MoveCanvas(object):
    """画布对象的轻量包装。

    返回给用户的是 matplotlib 的 ``(figure, axes)`` 组合，本类只提供
    一些与 turtle 画布语义对应的便捷方法（``fig``/``ax``/``draw``）。
    """

    def __init__(self, fig, ax):
        self.fig = fig
        self.ax = ax

    def draw(self):
        """立即重绘画布。"""
        self.fig.canvas.draw()

    def draw_idle(self):
        """请求重绘（由 matplotlib 合并）。"""
        self.fig.canvas.draw_idle()

    def save(self, filename, **kwargs):
        """把当前画面保存到文件。"""
        self.fig.savefig(filename, **kwargs)

    def clear(self):
        self.ax.clear()

    def __repr__(self):
        return "<MoveCanvas figure=%s axes=%s>" % (self.fig.number, self.ax)


class MoveScreenBase(object):
    """提供画布级别的绘图与事件能力（原 TurtleScreenBase 的 matplotlib 版）。

    真实实现委托给 :class:`._painter.MovePainter`，本类只做命名转换，
    使上层 :class:`MoveScreen` 的代码与 turtle 保持一致。
    """

    def _blankimage(self):
        """return a blank image object"""
        return None

    def _image(self, filename):
        """return an image object containing the imagedata from a bitmap file."""
        from ._painter import load_image_array

        return load_image_array(filename)

    def __init__(self, cv):
        self.cv = cv
        if isinstance(cv, MoveCanvas):
            self.painter = MovePainter(
                cv.fig,
                cv.ax,
                canvwidth=self.cv.ax.get_xlim()[1] - self.cv.ax.get_xlim()[0],
                canvheight=self.cv.ax.get_ylim()[1] - self.cv.ax.get_ylim()[0],
            )
        elif isinstance(cv, MovePainter):
            self.painter = cv
        else:
            raise TurtleGraphicsError("bad canvas argument %s" % (cv,))
        self.canvwidth = self.painter.canvwidth
        self.canvheight = self.painter.canvheight
        self.xscale = self.yscale = 1.0

    # -- 折线 --------------------------------------------------------------

    def _createline(self):
        """Create an invisible line item on canvas."""
        return self.painter.create_line()

    def _drawline(self, lineitem, coordlist=None, fill=None, width=None, top=False):
        """Configure lineitem according to provided arguments.

        coordlist is sequence of coordinates, fill is drawing color,
        width is width of drawn line, top raises the item above fills.
        """
        if coordlist is None:
            self.painter.set_line(lineitem, None, fill, width, top)
            return lineitem
        coords = [(x * self.xscale, -y * self.yscale) for x, y in coordlist]
        self.painter.set_path(lineitem, coords, fill, width)
        return lineitem

    def _drawlinesegment(self, lineitem, p1, p2, fill=None, width=None):
        """只画一段线（用于逐帧动画，不做分段处理，开销最小）。"""
        coords = [
            (p1[0] * self.xscale, -p1[1] * self.yscale),
            (p2[0] * self.xscale, -p2[1] * self.yscale),
        ]
        self.painter.set_line(lineitem, coords, fill, width)
        return lineitem

    def _setline(self, lineitem, coordlist):
        """Set coordinates of lineitem without touching style."""
        coords = [(x * self.xscale, -y * self.yscale) for x, y in coordlist]
        self.painter.set_line(lineitem, coords)
        return lineitem

    def _hidelinedrawing(self, lineitem):
        """清空并隐藏动画用的临时线段。

        动画结束后必须真的把它清掉：它只是"当前进行中的那一段"的替身，
        真正的折线已经写进 currentLineItem，留着就会多画一条重复的线。
        """
        self.painter.set_line(lineitem, [], color="none")
        return lineitem

    def _deleteline(self, lineitem):
        self.painter.delete(lineitem)

    # -- 多边形 ------------------------------------------------------------

    def _createpoly(self):
        """Create an invisible polygon item on canvas."""
        return self.painter.create_poly()

    def _createstamppoly(self):
        return self.painter.create_poly(stamp=True)

    def _drawpoly(
        self, polyitem, coordlist, fill=None, outline=None, width=None, top=False
    ):
        """Configure polygonitem polyitem according to provided arguments."""
        coords = [(x * self.xscale, -y * self.yscale) for x, y in coordlist]
        self.painter.set_poly(
            polyitem, coords, fill=fill, outline=outline, width=width, top=top
        )
        return polyitem

    # -- 删除、更新 --------------------------------------------------------

    def _delete(self, item):
        """Delete graphics item from canvas. If item is "all", delete all."""
        self.painter.delete(item)

    def _update(self):
        """Redraw graphics items on canvas (deferred, coalesced)."""
        self.painter.request_repaint()

    def _flush(self):
        """Force an immediate full redraw."""
        self.painter.flush()

    def _delay(self, delay):
        """Delay subsequent canvas actions for delay ms."""
        self.painter.request_repaint(delay)

    def _iscolorstring(self, color):
        """Check if the string color is a legal matplotlib color string."""
        return self.painter.is_color_string(color)

    def _bgcolor(self, color=None):
        """Set canvas' backgroundcolor if color is not None, else return it."""
        if color is not None:
            self.painter.background(color)
        else:
            return self.painter.background()

    def _write(self, pos, txt, align, font, pencolor):
        """Write txt at pos in canvas with specified font and color.

        Return text item and x-coord of right bottom corner of text's
        bounding box.
        """
        x, y = pos
        return self.painter.write_text(
            (x * self.xscale, -y * self.yscale), txt, align, font, pencolor
        )

    # -- 事件 --------------------------------------------------------------

    def _onclick(self, item, fun, num=1, add=None):
        """Bind fun to mouse-click event on a given canvas item (turtle)."""
        self._bind_item(item, fun, "click", num)

    def _onrelease(self, item, fun, num=1, add=None):
        """Bind fun to mouse-button-release event on a given canvas item."""
        self._bind_item(item, fun, "release", num)

    def _ondrag(self, item, fun, num=1, add=None):
        """Bind fun to mouse-move-with-pressed-button event on a canvas item."""
        self._bind_item(item, fun, "drag", num)

    def _bind_item(self, item, fun, kind, num=1):
        """Register/remove a per-item (move object) mouse binding."""
        screen = getattr(self.painter, "_screen", None)
        if screen is None:
            return
        # 同一个图元 + 事件 + 按键只保留一个绑定
        for key, entry in list(screen._item_bindings.items()):
            if entry is not None and entry[0] is item and key[1] == kind and key[2] == num:
                del screen._item_bindings[key]
        if fun is not None:
            screen._item_bindings[(id(item), kind, num)] = (item, fun)

    def _onscreenclick(self, fun, num=1, add=None):
        """Bind fun to mouse-click event on canvas."""
        screen = getattr(self.painter, "_screen", None)
        if screen is None:
            return
        if fun is None:
            screen._screen_bindings.pop(num, None)
        else:
            screen._screen_bindings[num] = fun

    def _onkeyrelease(self, fun, key):
        """Bind fun to key-release event of key."""
        screen = getattr(self.painter, "_screen", None)
        if screen is None:
            return
        if fun is None:
            screen._key_bindings.pop(("release", key), None)
        else:
            screen._key_bindings[("release", key)] = fun

    def _onkeypress(self, fun, key=None):
        """If key is given, bind fun to key-press event of key, else to any key."""
        screen = getattr(self.painter, "_screen", None)
        if screen is None:
            return
        if fun is None:
            screen._key_bindings.pop(("press", key), None)
        else:
            screen._key_bindings[("press", key)] = fun

    def _listen(self):
        """Set focus on the figure window (in order to collect key-events)."""
        self.painter.focus()

    def _ontimer(self, fun, t):
        """Install a timer, which calls fun after t milliseconds."""
        return self.painter.after(t, fun)

    # -- 图片 --------------------------------------------------------------

    def _createimage(self, image=None):
        """Create and return image item on canvas."""
        return self.painter.create_image(image)

    def _createblankimage(self):
        return self.painter.create_image(None)

    def _drawimage(self, item, pos, image):
        """Configure image item as to draw image object at position (x,y)."""
        x, y = pos
        self.painter.set_image(item, (x * self.xscale, -y * self.yscale), image)

    def _drawturtleimage(self, item, pos, image):
        x, y = pos
        self.painter.set_image(item, (x * self.xscale, -y * self.yscale), image)

    def _setbgpic(self, item, image):
        """Configure background image, drawn below every other item."""
        self.painter.set_background_image(image, self.canvwidth, self.canvheight)

    def _type(self, item):
        """Return 'line' or 'polygon' or 'image' or 'text'."""
        return self.painter.item_type(item)

    def _pointlist(self, item):
        """returns list of coordinate-pairs of points of item"""
        return self.painter.pointlist(item)

    def _setscrollregion(self, srx1, sry1, srx2, sry2):
        self.painter.set_scroll_region(srx1, sry1, srx2, sry2)

    def _rescale(self, xscalefactor, yscalefactor):
        self.painter.rescale(xscalefactor, yscalefactor)

    def _resize(self, canvwidth=None, canvheight=None, bg=None):
        """Resize the canvas the move objects are drawing on."""
        if canvwidth is None and canvheight is None and bg is None:
            return self.canvwidth, self.canvheight
        self.canvwidth, self.canvheight = self.painter.resize_canvas(canvwidth, canvheight)
        if bg is not None:
            color = bg if isinstance(bg, str) else self._colorstr((bg,))
            self._bgcolor(color)
        self.painter.request_repaint()
        return self.canvwidth, self.canvheight

    def _window_size(self):
        """Return the width and height of the figure window in pixels."""
        return self.painter.window_size()

    def mainloop(self):
        """Starts the matplotlib event loop (``plt.show()``).

        Must be last statement in a move graphics program
        (unless the backend is non-interactive, where it simply returns).
        """
        self.painter.mainloop()

    def textinput(self, title, prompt):
        """Pop up a dialog window for input of a string.

        Arguments: title is the title of the dialog window,
        prompt is a text mostly describing what information to input.

        Return the string input. If the dialog is canceled, return None.
        """
        return _ask_string(title, prompt)

    def numinput(self, title, prompt, default=None, minval=None, maxval=None):
        """Pop up a dialog window for input of a number.

        Return the number input, or None if the dialog was canceled.
        """
        return _ask_float(title, prompt, default, minval, maxval)


##############################################################################
###                End of Matplotlib - interface                           ###
##############################################################################


class MoveScreen(MoveScreenBase):
    """Provides screen oriented methods like bgcolor etc.

    Only relies upon the methods of MoveScreenBase and NOT upon components
    of the underlying graphics toolkit - which is matplotlib in this case.
    """

    _RUNNING = True

    def __init__(
        self, cv=None, mode=_CFG["mode"], colormode=_CFG["colormode"], delay=_CFG["delay"]
    ):
        if cv is None:
            raise TurtleGraphicsError(
                "MoveScreen 需要一个画布：请使用 MoveScreen(fig, ax) "
                "或 MoveCanvas(fig, ax)，或直接用 Move() 自动创建。"
            )
        MoveScreenBase.__init__(self, cv)

        self._shapes = {
            "arrow": Shape("polygon", ((-10, 0), (10, 0), (0, 10))),
            "turtle": Shape(
                "polygon",
                (
                    (0, 16),
                    (-2, 14),
                    (-1, 10),
                    (-4, 7),
                    (-7, 9),
                    (-9, 8),
                    (-6, 5),
                    (-7, 1),
                    (-5, -3),
                    (-8, -6),
                    (-6, -8),
                    (-4, -5),
                    (0, -7),
                    (4, -5),
                    (6, -8),
                    (8, -6),
                    (5, -3),
                    (7, 1),
                    (6, 5),
                    (9, 8),
                    (7, 9),
                    (4, 7),
                    (1, 10),
                    (2, 14),
                ),
            ),
            "classic": Shape("polygon", ((0, 0), (-5, -9), (0, -7), (5, -9))),
            "triangle": Shape("polygon", ((10, -5.77), (0, 11.55), (-10, -5.77))),
            "square": Shape("polygon", ((10, -10), (10, 10), (-10, 10), (-10, -10))),
            "circle": Shape(
                "polygon",
                (
                    (10, 0),
                    (9.51, 3.09),
                    (8.09, 5.88),
                    (5.88, 8.09),
                    (3.09, 9.51),
                    (0, 10),
                    (-3.09, 9.51),
                    (-5.88, 8.09),
                    (-8.09, 5.88),
                    (-9.51, 3.09),
                    (-10, 0),
                    (-9.51, -3.09),
                    (-8.09, -5.88),
                    (-5.88, -8.09),
                    (-3.09, -9.51),
                    (-0.00, -10.00),
                    (3.09, -9.51),
                    (5.88, -8.09),
                    (8.09, -5.88),
                    (9.51, -3.09),
                ),
            ),
            "blank": Shape("image", None),
        }

        self._bgpics = {"nopic": None}

        self._mode = mode
        self._delayvalue = delay
        self._colormode = _CFG["colormode"]
        self._keys = []

        # 事件绑定表（由 MoveScreenBase 的事件方法填充）
        self._screen_bindings = {}  # button -> fun
        self._item_bindings = {}  # (item_id, kind, num) -> (item, fun)
        self._key_bindings = {}  # (kind, key) -> fun
        self._mpl_cids = []
        self._drag_target = None
        self._mouse_hooks = False

        # 让画布反过来能找到本屏幕（事件分发需要）
        self.painter._screen = self

        self.clear()
        if sys.platform == "darwin":
            # Force the figure window to the front on macOS; otherwise it may
            # show behind the terminal when started from the command line.
            try:
                manager = self.painter.fig.canvas.manager
                window = getattr(manager, "window", None)
                if window is not None:
                    window.raise_()
            except Exception:
                pass

    def _ensure_mouse_hooks(self):
        """惰性挂上 matplotlib 鼠标/键盘回调（只在首次绑定时做一次）。"""
        if self._mouse_hooks:
            return
        self._mouse_hooks = True
        try:
            self._mpl_cids.extend(self.painter.bind_mouse(self._dispatch_mouse))
            self._mpl_cids.extend(self.painter.bind_key(self._dispatch_key))
        except Exception:
            self._mpl_cids = []

    def _drop_mouse_hooks(self):
        """断开 matplotlib 回调，避免旧屏幕继续响应已关闭图形的事件。"""
        canvas = self.painter.canvas
        for cid in self._mpl_cids:
            try:
                canvas.mpl_disconnect(cid)
            except Exception:
                pass
        self._mpl_cids = []
        self._mouse_hooks = False

    # -- 事件分发 ----------------------------------------------------------

    def _hit_test(self, x, y):
        """返回被点中的 turtle 外形图元（无命中则为 None）。"""
        for (item_id, kind, num), entry in list(self._item_bindings.items()):
            if entry is None:
                continue
            item = entry[0]
            if kind not in ("click", "release", "drag"):
                continue
            try:
                if item.contains_point((x, y)):
                    return item
            except Exception:
                continue
        return None

    def _event_xy(self, event):
        """把 matplotlib 事件坐标换算成 move 的画布坐标。"""
        try:
            x, y = event.xdata, event.ydata
        except Exception:
            return None
        if x is None or y is None:
            return None
        return float(x), float(y)

    def _dispatch_mouse(self, event):
        """把 matplotlib 鼠标事件分发给 turtle 的事件绑定。"""
        if not self._screen_bindings and not self._item_bindings:
            return
        xy = self._event_xy(event)
        if xy is None:
            return
        name = type(event).__name__
        num = int(getattr(event, "button", 1) or 1)

        if name == "MotionEvent":
            self._press_fired.clear()
        elif name == "ButtonPress":
            self._drag_target = self._hit_test(*xy)
        elif name == "ButtonRelease":
            self._drag_target = None
            self._press_fired.clear()

        # 拖动回调
        if name == "MotionEvent" and self._drag_target is None:
            self._drag_target = self._hit_test(*xy)
        if name == "MotionEvent" and self._drag_target is not None:
            for (item_id, kind, btn), entry in list(self._item_bindings.items()):
                if entry is None or kind != "drag" or btn != num:
                    continue
                if entry[0] is not self._drag_target:
                    continue
                try:
                    entry[1](*xy)
                except Exception:
                    if not sys.is_finalizing():
                        raise

        # 点击/释放回调（按 turtle 的语义：先点中的 turtle，再是屏幕）
        if name in ("ButtonPress", "ButtonRelease"):
            kind = "click" if name == "ButtonPress" else "release"
            item = self._hit_test(*xy)
            if item is not None:
                for (item_id, k, btn), entry in list(self._item_bindings.items()):
                    if entry is None or k != kind or btn != num:
                        continue
                    if entry[0] is not item:
                        continue
                    try:
                        entry[1](*xy)
                    except Exception:
                        if not sys.is_finalizing():
                            raise
            fun = self._screen_bindings.get(num)
            if fun is not None:
                try:
                    fun(*xy)
                except Exception:
                    if not sys.is_finalizing():
                        raise

    def _dispatch_key(self, event):
        """把 matplotlib 键盘事件分发给 move 的键绑定。"""
        if not self._key_bindings:
            return
        name = type(event).__name__
        key = getattr(event, "key", None)
        if key is None:
            return
        cand = _key_candidates(key)

        if name == "KeyPressEvent":
            matched = False
            for candidate in cand:
                fun = self._key_bindings.get(("press", candidate))
                if fun is not None:
                    matched = True
                    fun()
            if not matched:
                fun = self._key_bindings.get(("press", None))
                if fun is not None:
                    fun()
        elif name == "KeyReleaseEvent":
            matched = False
            for candidate in cand:
                fun = self._key_bindings.get(("release", candidate))
                if fun is not None:
                    matched = True
                    fun()
            if not matched:
                fun = self._key_bindings.get(("release", None))
                if fun is not None:
                    fun()

    # -- 屏幕状态 ----------------------------------------------------------

    def clear(self):
        """Delete all drawings and all move objects from the screen.

        Reset empty screen to its initial state: no drawings, no background
        image, no event bindings and tracing on.
        """
        self._delayvalue = _CFG["delay"]
        self._colormode = _CFG["colormode"]
        self._delete("all")
        self._bgpic = self._createimage(None)
        self._bgpicname = "nopic"
        self._tracing = 1
        self._updatecounter = 0
        self._turtles = []
        self._screen_bindings.clear()
        self._item_bindings.clear()
        self._key_bindings.clear()
        self._keys = []
        self.bgcolor("white")
        Move._pen = None

    def mode(self, mode=None):
        """Set move-mode ('standard', 'logo' or 'world') and perform reset.

        If mode is not given, return the current mode.
        """
        if mode is None:
            return self._mode
        mode = mode.lower()
        if mode not in ["standard", "logo", "world"]:
            raise TurtleGraphicsError("No move-graphics-mode %s" % mode)
        self._mode = mode
        if mode in ["standard", "logo"]:
            self._setscrollregion(
                -self.canvwidth // 2,
                -self.canvheight // 2,
                self.canvwidth // 2,
                self.canvheight // 2,
            )
            self.xscale = self.yscale = 1.0
        self.reset()

    def setworldcoordinates(self, llx, lly, urx, ury):
        """Set up a user defined coordinate-system.

        Arguments:
        llx -- a number, x-coordinate of lower left corner of canvas
        lly -- a number, y-coordinate of lower left corner of canvas
        urx -- a number, x-coordinate of upper right corner of canvas
        ury -- a number, y-coordinate of upper right corner of canvas

        ATTENTION: in user-defined coordinate systems angles may appear
        distorted.
        """
        if self.mode() != "world":
            self.mode("world")
        xspan = float(urx - llx)
        yspan = float(ury - lly)
        if xspan == 0 or yspan == 0:
            raise TurtleGraphicsError("setworldcoordinates: empty coordinate span")
        wx, wy = self._window_size()
        self.screensize(wx - 20, wy - 20)
        oldxscale, oldyscale = self.xscale, self.yscale
        self.xscale = self.canvwidth / xspan
        self.yscale = self.canvheight / yspan
        srx1 = llx * self.xscale
        sry1 = -ury * self.yscale
        srx2 = self.canvwidth + srx1
        sry2 = self.canvheight + sry1
        self._setscrollregion(srx1, sry1, srx2, sry2)
        self._rescale(self.xscale / oldxscale, self.yscale / oldyscale)
        self.update()

    def register_shape(self, name, shape=None):
        """Adds a move shape to the screen's shapelist.

        Arguments:
        (1) name is the name of a bitmap file and shape is None.
        (2) name is an arbitrary string and shape is a tuple of pairs of
            coordinates (polygon shape).
        (3) name is an arbitrary string and shape is a (compound) Shape object.
        """
        if shape is None:
            # image
            data = self._image(name) if isfile(name) else None
            if data is None:
                raise TurtleGraphicsError(
                    "Bad arguments for register_shape.\n"
                    + "Use  help(register_shape)"
                )
            shape = Shape("image", data)
        elif isinstance(shape, tuple):
            shape = Shape("polygon", shape)
        ## else shape assumed to be Shape-instance
        self._shapes[name] = shape
        # 新形状可能被现有 move 对象使用，强制它们重画外形
        for turtle in self._turtles:
            turtle._needs_turtle_update = True

    def _colorstr(self, color):
        """Return color string corresponding to args.

        Argument may be a string or a tuple of three numbers corresponding to
        actual colormode, i.e. in the range 0<=n<=colormode.
        """
        if len(color) == 1:
            color = color[0]
        if isinstance(color, str):
            if self._iscolorstring(color) or color == "":
                return color
            else:
                raise TurtleGraphicsError("bad color string: %s" % str(color))
        try:
            r, g, b = color
        except (TypeError, ValueError):
            raise TurtleGraphicsError("bad color arguments: %s" % str(color))
        if self._colormode == 1.0:
            r, g, b = [round(255.0 * x) for x in (r, g, b)]
        if not ((0 <= r <= 255) and (0 <= g <= 255) and (0 <= b <= 255)):
            raise TurtleGraphicsError("bad color sequence: %s" % str(color))
        return "#%02x%02x%02x" % (r, g, b)

    def _color(self, cstr):
        """把颜色转换成 ``(r, g, b)``，分量按当前 colormode 归一化。"""
        if cstr is None or cstr == "":
            return ""
        if cstr == "none":
            return ""
        try:
            from matplotlib.colors import to_rgb
        except Exception:  # pragma: no cover
            return cstr
        try:
            r, g, b = to_rgb(cstr)
        except Exception:
            return cstr
        scale = self._colormode
        out = []
        for c in (r, g, b):
            value = c * scale
            # 往返转换会产生 1e-16 级别的浮点噪声，吸附回整数值
            nearest = round(value)
            if abs(value - nearest) < 1e-9:
                value = float(nearest)
            out.append(value)
        return tuple(out)

    def colormode(self, cmode=None):
        """Return the colormode or set it to 1.0 or 255."""
        if cmode is None:
            return self._colormode
        if cmode == 1.0:
            self._colormode = float(cmode)
        elif cmode == 255:
            self._colormode = int(cmode)

    def reset(self):
        """Reset all move objects on the screen to their initial state."""
        for turtle in self._turtles:
            turtle._setmode(self._mode)
            turtle.reset()

    def turtles(self):
        """Return the list of turtles on the screen."""
        return self._turtles

    def bgcolor(self, *args):
        """Set or return backgroundcolor of the screen."""
        if args:
            color = self._colorstr(args)
        else:
            color = None
        color = self._bgcolor(color)
        if color is not None:
            color = self._color(color)
        return color

    def tracer(self, n=None, delay=None):
        """Turns move animation on/off and set delay for update drawings.

        Optional arguments:
        n -- nonnegative  integer
        delay -- nonnegative  integer

        If n is given, only each n-th regular screen update is really
        performed. Second argument sets delay value (see RawMove.delay()).
        """
        if n is None:
            return self._tracing
        self._tracing = int(n)
        self._updatecounter = 0
        if delay is not None:
            self._delayvalue = int(delay)
        if self._tracing:
            self.update()

    def delay(self, delay=None):
        """Return or set the drawing delay in milliseconds.

        这里同时决定动画两帧之间的最小间隔：值越大动画越慢越"顺滑"，
        ``delay(0)`` 表示不等待（动画会在一次刷新内跑完）。
        """
        if delay is None:
            return self._delayvalue
        self._delayvalue = int(delay)
        self._sync_animation_interval()

    def _sync_animation_interval(self):
        """按当前 delay 与海龟速度刷新画布帧间隔。

        取所有海龟中**最慢**的那一档；只要有一只海龟的 speed 是 0
        （"瞬间完成"），间隔就是 0 —— 不能为了别的海龟去阻塞整个脚本。
        """
        speeds = [getattr(t, "_speed", 0) or 0 for t in getattr(self, "_turtles", [])]
        animated = [s for s in speeds if s]
        speed = min(animated) if animated else 0
        self.painter.set_delay(_frame_interval_ms(self._delayvalue, speed))

    def _incrementudc(self):
        """Increment update counter."""
        if not MoveScreen._RUNNING:
            MoveScreen._RUNNING = True
            raise Terminator
        if self._tracing > 0:
            self._updatecounter += 1
            self._updatecounter %= self._tracing

    def update(self):
        """Perform a screen update: flush every move object, then repaint."""
        tracing = self._tracing
        self._tracing = True
        try:
            for t in self.turtles():
                t._update_data()
                t._drawturtle()
        finally:
            self._tracing = tracing
        self.painter.process_timers()
        self._flush()

    def window_width(self):
        """Return the width of the move window."""
        return self._window_size()[0]

    def window_height(self):
        """Return the height of the move window."""
        return self._window_size()[1]

    def getcanvas(self):
        """Return the MoveCanvas of this screen."""
        return MoveCanvas(self.painter.fig, self.painter.ax)

    def getfigure(self):
        """Return the matplotlib Figure of this screen."""
        return self.painter.fig

    def getaxes(self):
        """Return the matplotlib Axes of this screen."""
        return self.painter.ax

    def getshapes(self):
        """Return a list of names of all currently available move shapes."""
        return sorted(self._shapes.keys())

    def onclick(self, fun, btn=1, add=None):
        """Bind fun to mouse-click event on canvas.

        fun -- a function with two arguments, the coordinates of the
               clicked point on the canvas.
        btn -- the number of the mouse-button, defaults to 1
        """
        self._onscreenclick(fun, btn, add)

    def onkey(self, fun, key):
        """Bind fun to key-release event of key.

        key 可以是单字符（``"a"``）或按键名（``"Up"``/``"space"``，
        大小写不敏感）。为了让 figure 收到键盘事件，需要先 ``listen()``。
        """
        key = _norm_key(key)
        if fun is None:
            if key in self._keys:
                self._keys.remove(key)
        elif key not in self._keys:
            self._keys.append(key)
        self._ensure_mouse_hooks()
        self._onkeyrelease(fun, key)

    def onkeypress(self, fun, key=None):
        """Bind fun to key-press event of key if key is given,
        or to any key-press-event if no key is given.
        """
        key = _norm_key(key)
        if fun is None:
            if key in self._keys:
                self._keys.remove(key)
        elif key is not None and key not in self._keys:
            self._keys.append(key)
        self._ensure_mouse_hooks()
        self._onkeypress(fun, key)

    def listen(self, xdummy=None, ydummy=None):
        """Set focus on the figure window (in order to collect key-events)."""
        self._listen()

    def ontimer(self, fun, t=0):
        """Install a timer, which calls fun after t milliseconds."""
        self._ontimer(fun, t)

    def bgpic(self, picname=None):
        """Set background image or return name of current backgroundimage.

        Optional argument:
        picname -- a string, name of a bitmap file or "nopic".
        """
        if picname is None:
            return self._bgpicname
        if picname not in self._bgpics:
            if isfile(picname):
                self._bgpics[picname] = self._image(picname)
            else:
                raise TurtleGraphicsError("no such file: %s" % picname)
        if picname == "nopic":
            self.painter.clear_background_image()
        else:
            self.painter.set_background_image(
                self._bgpics[picname], self.canvwidth, self.canvheight
            )
        self._bgpicname = picname

    def screensize(self, canvwidth=None, canvheight=None, bg=None):
        """Resize the canvas the move objects are drawing on.

        If no arguments are given, return current (canvaswidth, canvasheight).
        """
        return self._resize(canvwidth, canvheight, bg)

    def __deepcopy__(self, memo):
        """屏幕对象（含 matplotlib 画布）不参与深拷贝。

        ``RawMove.clone()`` 会深拷贝海龟，而画布是不可复制的资源，
        因此这里让屏幕按引用共享。
        """
        return self

    onscreenclick = onclick
    resetscreen = reset
    clearscreen = clear
    addshape = register_shape
    onkeyrelease = onkey


class TNavigator(object):
    """Navigation part of the RawMove.
    Implements methods for move-object movement.
    """

    START_ORIENTATION = {
        "standard": Vec2D(1.0, 0.0),
        "world": Vec2D(1.0, 0.0),
        "logo": Vec2D(0.0, 1.0),
    }
    DEFAULT_MODE = "standard"
    DEFAULT_ANGLEOFFSET = 0
    DEFAULT_ANGLEORIENT = 1

    def __init__(self, mode=DEFAULT_MODE):
        self._angleOffset = self.DEFAULT_ANGLEOFFSET
        self._angleOrient = self.DEFAULT_ANGLEORIENT
        self._mode = mode
        self.undobuffer = None
        self.degrees()
        self._mode = None
        self._setmode(mode)
        TNavigator.reset(self)

    def reset(self):
        """reset move object to its initial values

        Will be overwritten by parent class
        """
        self._position = Vec2D(0.0, 0.0)
        self._orient = TNavigator.START_ORIENTATION[self._mode]

    def _setmode(self, mode=None):
        """Set move-mode to 'standard', 'world' or 'logo'."""
        if mode is None:
            return self._mode
        if mode not in ["standard", "logo", "world"]:
            return
        self._mode = mode
        if mode in ["standard", "world"]:
            self._angleOffset = 0
            self._angleOrient = 1
        else:  # mode == "logo":
            self._angleOffset = self._fullcircle / 4.0
            self._angleOrient = -1

    def _setDegreesPerAU(self, fullcircle):
        """Helper function for degrees() and radians()"""
        self._fullcircle = fullcircle
        self._degreesPerAU = 360 / fullcircle
        if self._mode == "standard":
            self._angleOffset = 0
        else:
            self._angleOffset = fullcircle / 4.0

    def degrees(self, fullcircle=360.0):
        """Set angle measurement units to degrees.

        >>> move.degrees()
        >>> move.left(90)
        >>> move.heading()
        90
        """
        self._setDegreesPerAU(fullcircle)

    def radians(self):
        """Set the angle measurement units to radians."""
        self._setDegreesPerAU(math.tau)

    def _go(self, distance):
        """move forward by specified distance"""
        ende = self._position + self._orient * distance
        self._goto(ende)

    def _rotate(self, angle):
        """Turn counterclockwise by specified angle if angle > 0."""
        angle *= self._degreesPerAU
        self._orient = self._orient.rotate(angle)

    def _goto(self, end):
        """move to position end."""
        self._position = end

    def teleport(self, x=None, y=None, *, fill_gap: bool = False) -> None:
        """To be overwritten by child class RawMove.
        Includes no TPen references."""
        new_x = x if x is not None else self._position[0]
        new_y = y if y is not None else self._position[1]
        self._position = Vec2D(new_x, new_y)

    def forward(self, distance):
        """Move the move object forward by the specified distance.

        Aliases: forward | fd

        Argument:
        distance -- a number (integer or float)
        """
        self._go(distance)

    def back(self, distance):
        """Move the move object backward by distance.

        Aliases: back | backward | bk
        """
        self._go(-distance)

    def right(self, angle):
        """Turn right by angle units.

        Aliases: right | rt
        """
        self._rotate(-angle)

    def left(self, angle):
        """Turn left by angle units.

        Aliases: left | lt
        """
        self._rotate(angle)

    def pos(self):
        """Return the current location (x,y), as a Vec2D-vector.

        Aliases: pos | position
        """
        return self._position

    def xcor(self):
        """Return the x coordinate."""
        return self._position[0]

    def ycor(self):
        """Return the y coordinate."""
        return self._position[1]

    def goto(self, x, y=None):
        """Move to an absolute position.

        Aliases: setpos | setposition | goto:

        call: goto(x, y)         # two coordinates
        --or: goto((x, y))       # a pair (tuple) of coordinates
        --or: goto(vec)          # e.g. as returned by pos()
        """
        if y is None:
            self._goto(Vec2D(*x))
        else:
            self._goto(Vec2D(x, y))

    def home(self):
        """Move to the origin - coordinates (0,0) and reset the heading."""
        self.goto(0, 0)
        self.setheading(0)

    def setx(self, x):
        """Set the first coordinate to x, leave second coordinate unchanged."""
        self._goto(Vec2D(x, self._position[1]))

    def sety(self, y):
        """Set the second coordinate to y, leave first coordinate unchanged."""
        self._goto(Vec2D(self._position[0], y))

    def distance(self, x, y=None):
        """Return the distance from the move object to (x,y).

        Argument may also be a pair/vector of numbers or another move object.
        """
        if y is not None:
            pos = Vec2D(x, y)
        if isinstance(x, Vec2D):
            pos = x
        elif isinstance(x, tuple):
            pos = Vec2D(*x)
        elif isinstance(x, TNavigator):
            pos = x._position
        return abs(pos - self._position)

    def towards(self, x, y=None):
        """Return the angle of the line from the position to (x, y)."""
        if y is not None:
            pos = Vec2D(x, y)
        if isinstance(x, Vec2D):
            pos = x
        elif isinstance(x, tuple):
            pos = Vec2D(*x)
        elif isinstance(x, TNavigator):
            pos = x._position
        x, y = pos - self._position
        # 只在 360 度空间里做一次轻量整理，避免 1e-10 级别的舍入损失
        result = _clean_degrees(math.degrees(math.atan2(y, x))) % 360.0
        result /= self._degreesPerAU
        return _clean_degrees(
            (self._angleOffset + self._angleOrient * result) % self._fullcircle
        )

    def heading(self):
        """Return the current heading."""
        x, y = self._orient
        result = _clean_degrees(math.degrees(math.atan2(y, x))) % 360.0
        result /= self._degreesPerAU
        return _clean_degrees(
            (self._angleOffset + self._angleOrient * result) % self._fullcircle
        )

    def setheading(self, to_angle):
        """Set the orientation to to_angle.

        Aliases:  setheading | seth
        """
        angle = (to_angle - self.heading()) * self._angleOrient
        full = self._fullcircle
        angle = (angle + full / 2.0) % full - full / 2.0
        self._rotate(angle)

    def circle(self, radius, extent=None, steps=None):
        """Draw a circle with given radius.

        Arguments:
        radius -- a number
        extent (optional) -- a number
        steps (optional) -- an integer

        The center is radius units left of the move object; extent - an angle -
        determines which part of the circle is drawn. As the circle is
        approximated by an inscribed regular polygon, steps determines the
        number of steps to use.
        """
        if self.undobuffer:
            self.undobuffer.push(["seq"])
            self.undobuffer.cumulate = True
        speed = self.speed()
        if extent is None:
            extent = self._fullcircle
        if steps is None:
            frac = abs(extent) / self._fullcircle
            steps = 1 + int(min(11 + abs(radius) / 6.0, 59.0) * frac)
        w = 1.0 * extent / steps
        w2 = 0.5 * w
        l = 2.0 * radius * math.sin(math.radians(w2) * self._degreesPerAU)
        if radius < 0:
            l, w, w2 = -l, -w, -w2
        tr = self._tracer()
        dl = self._delay()
        if speed == 0:
            self._tracer(0, 0)
        else:
            self.speed(0)
        self._rotate(w2)
        for i in range(steps):
            self.speed(speed)
            self._go(l)
            self.speed(0)
            self._rotate(w)
        self._rotate(-w2)
        if speed == 0:
            self._tracer(tr, dl)
        self.speed(speed)
        if self.undobuffer:
            self.undobuffer.cumulate = False

    ## three dummy methods to be implemented by child class:

    def speed(self, s=0):
        """dummy method - to be overwritten by child class"""

    def _tracer(self, a=None, b=None):
        """dummy method - to be overwritten by child class"""

    def _delay(self, n=None):
        """dummy method - to be overwritten by child class"""

    fd = forward
    bk = back
    backward = back
    rt = right
    lt = left
    position = pos
    setpos = goto
    setposition = goto
    seth = setheading


class TPen(object):
    """Drawing part of the RawMove.
    Implements drawing properties.
    """

    def __init__(self, resizemode=_CFG["resizemode"]):
        self._resizemode = resizemode  # or "user" or "noresize"
        self.undobuffer = None
        TPen._reset(self)

    def _reset(self, pencolor=_CFG["pencolor"], fillcolor=_CFG["fillcolor"]):
        self._pensize = 1
        self._shown = True
        self._pencolor = pencolor
        self._fillcolor = fillcolor
        self._drawing = True
        self._speed = 3
        self._stretchfactor = (1.0, 1.0)
        self._shearfactor = 0.0
        self._tilt = 0.0
        self._shapetrafo = (1.0, 0.0, 0.0, 1.0)
        self._outlinewidth = 1

    def resizemode(self, rmode=None):
        """Set resizemode to one of the values: "auto", "user", "noresize".

        Different resizemodes have the following effects:
          - "auto" adapts the appearance to the value of pensize.
          - "user" adapts according to stretchfactor and outlinewidth.
          - "noresize" no adaption of the appearance takes place.
        """
        if rmode is None:
            return self._resizemode
        rmode = rmode.lower()
        if rmode in ["auto", "user", "noresize"]:
            self.pen(resizemode=rmode)

    def pensize(self, width=None):
        """Set or return the line thickness.

        Aliases:  pensize | width
        """
        if width is None:
            return self._pensize
        self.pen(pensize=width)

    def penup(self):
        """Pull the pen up -- no drawing when moving.

        Aliases: penup | pu | up
        """
        if not self._drawing:
            return
        self.pen(pendown=False)

    def pendown(self):
        """Pull the pen down -- drawing when moving.

        Aliases: pendown | pd | down
        """
        if self._drawing:
            return
        self.pen(pendown=True)

    def isdown(self):
        """Return True if pen is down, False if it's up."""
        return self._drawing

    def speed(self, speed=None):
        """Return or set the speed.

        Optional argument:
        speed -- an integer in the range 0..10 or a speedstring

        Speedstrings are mapped to speedvalues in the following way:
            'fastest' :  0
            'fast'    :  10
            'normal'  :  6
            'slow'    :  3
            'slowest' :  1

        speed = 0 means: *no* animation takes place. forward/back makes the
        move object jump and likewise left/right make it turn instantly.
        """
        speeds = {"fastest": 0, "fast": 10, "normal": 6, "slow": 3, "slowest": 1}
        if speed is None:
            return self._speed
        if speed in speeds:
            speed = speeds[speed]
        elif 0.5 < speed < 10.5:
            speed = int(round(speed))
        else:
            speed = 0
        self.pen(speed=speed)
        self._sync_animation_interval()

    def color(self, *args):
        """Return or set the pencolor and fillcolor.

        color()
            Return the current pencolor and the current fillcolor
            as a pair of color specification strings.
        color(colorstring), color((r,g,b)), color(r,g,b)
            Set both, fillcolor and pencolor, to the given value.
        color(colorstring1, colorstring2), color((r1,g1,b1), (r2,g2,b2))
            Equivalent to pencolor(colorstring1) and fillcolor(colorstring2).
        """
        if args:
            l = len(args)
            if l == 1:
                pcolor = fcolor = args[0]
            elif l == 2:
                pcolor, fcolor = args
            elif l == 3:
                pcolor = fcolor = args
            pcolor = self._colorstr(pcolor)
            fcolor = self._colorstr(fcolor)
            self.pen(pencolor=pcolor, fillcolor=fcolor)
        else:
            return self._color(self._pencolor), self._color(self._fillcolor)

    def pencolor(self, *args):
        """Return or set the pencolor.

        Four input formats are allowed: pencolor(), pencolor(colorstring),
        pencolor((r, g, b)) and pencolor(r, g, b).
        """
        if args:
            color = self._colorstr(args)
            if color == self._pencolor:
                return
            self.pen(pencolor=color)
        else:
            return self._color(self._pencolor)

    def fillcolor(self, *args):
        """Return or set the fillcolor.

        Four input formats are allowed: fillcolor(), fillcolor(colorstring),
        fillcolor((r, g, b)) and fillcolor(r, g, b).
        """
        if args:
            color = self._colorstr(args)
            if color == self._fillcolor:
                return
            self.pen(fillcolor=color)
        else:
            return self._color(self._fillcolor)

    def teleport(self, x=None, y=None, *, fill_gap: bool = False) -> None:
        """To be overwritten by child class RawMove.
        Includes no TNavigator references.
        """
        pendown = self.isdown()
        if pendown:
            self.pen(pendown=False)
        self.pen(pendown=pendown)

    def showturtle(self):
        """Makes the move object visible.

        Aliases: showturtle | st
        """
        self.pen(shown=True)

    def hideturtle(self):
        """Makes the move object invisible.

        Aliases: hideturtle | ht

        It's a good idea to do this while you're in the middle of a complicated
        drawing, because hiding the move object speeds up the drawing.
        """
        self.pen(shown=False)

    def isvisible(self):
        """Return True if the object is shown, False if it's hidden."""
        return self._shown

    def pen(self, pen=None, **pendict):
        """Return or set the pen's attributes.

        Return or set the pen's attributes in a 'pen-dictionary' with the
        following key/value pairs:
           "shown"      :   True/False
           "pendown"    :   True/False
           "pencolor"   :   color-string or color-tuple
           "fillcolor"  :   color-string or color-tuple
           "pensize"    :   positive number
           "speed"      :   number in range 0..10
           "resizemode" :   "auto" or "user" or "noresize"
           "stretchfactor": (positive number, positive number)
           "shearfactor":   number
           "outline"    :   positive number
           "tilt"       :   number
        """
        _pd = {
            "shown": self._shown,
            "pendown": self._drawing,
            "pencolor": self._pencolor,
            "fillcolor": self._fillcolor,
            "pensize": self._pensize,
            "speed": self._speed,
            "resizemode": self._resizemode,
            "stretchfactor": self._stretchfactor,
            "shearfactor": self._shearfactor,
            "outline": self._outlinewidth,
            "tilt": self._tilt,
        }

        if not (pen or pendict):
            return _pd

        if isinstance(pen, dict):
            p = pen
        else:
            p = {}
        p.update(pendict)

        _p_buf = {}
        for key in p:
            _p_buf[key] = _pd[key]

        if self.undobuffer:
            self.undobuffer.push(("pen", _p_buf))

        newLine = False
        if "pendown" in p:
            if self._drawing != p["pendown"]:
                newLine = True
        if "pencolor" in p:
            if isinstance(p["pencolor"], tuple):
                p["pencolor"] = self._colorstr((p["pencolor"],))
            if self._pencolor != p["pencolor"]:
                newLine = True
        if "pensize" in p:
            if self._pensize != p["pensize"]:
                newLine = True
        if "fillcolor" in p:
            if isinstance(p["fillcolor"], tuple):
                p["fillcolor"] = self._colorstr((p["fillcolor"],))
        if newLine:
            self._newLine()
        if "pendown" in p:
            self._drawing = p["pendown"]
        if "pencolor" in p:
            self._pencolor = p["pencolor"]
        if "pensize" in p:
            self._pensize = p["pensize"]
        if "fillcolor" in p:
            self._fillcolor = p["fillcolor"]
        if "speed" in p:
            self._speed = p["speed"]
        if "resizemode" in p:
            self._resizemode = p["resizemode"]
        if "stretchfactor" in p:
            sf = p["stretchfactor"]
            if isinstance(sf, (int, float)):
                sf = (sf, sf)
            self._stretchfactor = sf
        if "shearfactor" in p:
            self._shearfactor = p["shearfactor"]
        if "outline" in p:
            self._outlinewidth = p["outline"]
        if "shown" in p:
            self._shown = p["shown"]
        if "tilt" in p:
            self._tilt = p["tilt"]
        if "stretchfactor" in p or "tilt" in p or "shearfactor" in p:
            scx, scy = self._stretchfactor
            shf = self._shearfactor
            sa, ca = math.sin(self._tilt), math.cos(self._tilt)
            self._shapetrafo = (
                scx * ca,
                scy * (shf * ca + sa),
                -scx * sa,
                scy * (ca - shf * sa),
            )
        self._update()

    ## three dummy methods to be implemented by child class:

    def _newLine(self, usePos=True):
        """dummy method - to be overwritten by child class"""

    def _update(self, count=True, forced=False):
        """dummy method - to be overwritten by child class"""

    def _color(self, args):
        """dummy method - to be overwritten by child class"""

    def _colorstr(self, args):
        """dummy method - to be overwritten by child class"""

    width = pensize
    up = penup
    pu = penup
    pd = pendown
    down = pendown
    st = showturtle
    ht = hideturtle


class _MoveImage(object):
    """Helper class: Datatype to store move-object attributes"""

    def __init__(self, screen, shapeIndex):
        self.screen = screen
        self._type = None
        self._setshape(shapeIndex)

    def _setshape(self, shapeIndex):
        screen = self.screen
        self.shapeIndex = shapeIndex
        if self._type == "polygon" == screen._shapes[shapeIndex]._type:
            return
        if self._type == "image" == screen._shapes[shapeIndex]._type:
            return
        if self._type in ["image", "polygon"]:
            screen._delete(self._item)
        elif self._type == "compound":
            for item in self._item:
                screen._delete(item)
        self._type = screen._shapes[shapeIndex]._type
        if self._type == "polygon":
            self._item = screen._createpoly()
        elif self._type == "image":
            self._item = screen._createimage(screen._shapes[shapeIndex]._data)
        elif self._type == "compound":
            self._item = [
                screen._createpoly() for item in screen._shapes[shapeIndex]._data
            ]


class RawMove(TPen, TNavigator):
    """Animation part of the RawMove.
    Puts RawMove upon a MoveScreen and provides tools for its animation.
    """

    screens = []

    def __init__(
        self,
        canvas=None,
        shape=_CFG["shape"],
        undobuffersize=_CFG["undobuffersize"],
        visible=_CFG["visible"],
    ):
        if isinstance(canvas, MoveScreen):
            self.screen = canvas
        elif isinstance(canvas, MoveScreenBase):
            if canvas not in RawMove.screens:
                RawMove.screens.append(canvas)
            self.screen = canvas
        elif isinstance(canvas, MovePainter):
            for screen in RawMove.screens:
                if screen.painter is canvas:
                    self.screen = screen
                    break
            else:
                self.screen = MoveScreen(canvas)
                RawMove.screens.append(self.screen)
        elif isinstance(canvas, MoveCanvas):
            for screen in RawMove.screens:
                if screen.painter.fig is canvas.fig:
                    self.screen = screen
                    break
            else:
                self.screen = MoveScreen(canvas)
                RawMove.screens.append(self.screen)
        else:
            raise TurtleGraphicsError("bad canvas argument %s" % (canvas,))

        screen = self.screen
        TNavigator.__init__(self, screen.mode())
        TPen.__init__(self)
        screen._turtles.append(self)
        self.drawingLineItem = screen._createline()
        self.turtle = _MoveImage(screen, shape)
        self._poly = None
        self._creatingPoly = False
        self._fillitem = self._fillpath = None
        self._shown = visible
        self._hidden_from_screen = False
        self.currentLineItem = screen._createline()
        self.currentLine = [self._position]
        self.items = [self.currentLineItem]
        self.stampItems = []
        self._undobuffersize = undobuffersize
        self.undobuffer = Tbuffer(undobuffersize)
        self._needs_data_update = False
        self._needs_turtle_update = True
        # 把外形图元登记进 items，这样它不会因为 start 时的清屏动作而消失
        self._update()

    # -- 需要上报给画布的数据 -------------------------------------------------

    def _flush_data(self):
        """把当前折线的坐标写进画布（等价于 turtle 的 ``_update_data``）。

        ``tracer(n)`` 的"每 n 次更新才画一次"就是靠这里的
        ``_incrementudc()`` + ``_updatecounter`` 实现的；
        ``tracer(0)`` 时 ``_updatecounter`` 恒为 0，因此只要 ``update()``
        被调用（或 ``_update`` 走到这里）就会把折线补画出来。
        """
        self.screen._incrementudc()
        if self.screen._updatecounter != 0:
            self._needs_data_update = True
            return
        if len(self.currentLine) > 1:
            self.screen._drawline(
                self.currentLineItem, self.currentLine, self._pencolor, self._pensize
            )
        self._needs_data_update = False

    def _update_data(self):
        """Compat wrapper：turtle 名字保留，语义同上。"""
        self._flush_data()

    # -- 重绘调度 -----------------------------------------------------------

    def _request_repaint(self):
        delay = getattr(self.screen, "_delayvalue", 0) or 0
        self.screen.painter.request_repaint(delay)

    def _frame_interval(self):
        """动画两帧之间的间隔（毫秒），由 ``delay()`` 与 ``speed()`` 共同决定。"""
        return _frame_interval_ms(
            getattr(self.screen, "_delayvalue", 0), self._speed
        )

    def _sync_animation_interval(self):
        """要求屏幕按当前 delay/speed 重新计算帧间隔（海龟对象侧调用）。"""
        self.screen._sync_animation_interval()

    def _render_frame(self):
        """动画帧：把当前状态真正刷到屏幕（受 delay/speed 节流）。"""
        self.screen.painter.frame(self._frame_interval())

    def _hop_count(self, distance_px):
        """按当前 speed 计算插值步数（与 turtle 的公式一致）。

        turtle 对慢速会给出很多步；matplotlib 每帧都要重绘一次整张图，
        步数过多会明显拖慢脚本，所以这里再按 speed 设一个**随 speed 递减**
        的步数上限：既限制总时长，也保证"speed 越大越快"单调成立。
        """
        speed = self._speed
        if not speed:
            return 1
        level = max(1, min(int(speed), 10))
        turtle_hops = 1 + int(distance_px / (3 * (1.1**speed) * speed))
        # 步数上限随 speed 递减：总时长 ≈ 步数 × 帧间隔，两者相乘单调递减，
        # 因此"speed 越大越快"在时间上确实成立，且总量有界
        # （speed=1 时约 20 步 × 39ms ≈ 0.8s，speed=10 时 2 步 × 1.5ms）。
        # 步数上限随 speed 递减：总时长 ≈ 步数 × 帧间隔，两者相乘单调递减，
        # 因此"speed 越大越快"在时间上确实成立，且总量有界。
        # 下限 2 保证任何 speed>0 都至少有一次中间帧（否则就不是动画了）。
        cap = max(2, 1 + int(4 // level))
        return max(1, min(turtle_hops, cap))

    def _update(self, render=False):
        """Perform a move-object data update.

        ``render=True`` 走"动画帧"路径（真正刷屏并受 ``delay`` 节流），
        ``render=False`` 只更新状态并安排一次延迟重绘。

        注意：``_incrementudc()`` 只在 :meth:`_flush_data` 里调用一次，
        避免 tracer(n) 的计数被加了两次。
        """
        screen = self.screen
        if screen._tracing == 0:
            self._needs_data_update = True
            self._needs_turtle_update = True
            self._request_repaint()
            return
        if screen._tracing == 1 or screen._updatecounter == 0:
            self._drawturtle()
            self._needs_turtle_update = False
        self._flush_data()
        if render:
            self._render_frame()
        else:
            self._request_repaint()

    def _tracer(self, flag=None, delay=None):
        """Turns move animation on/off and set delay for update drawings."""
        return self.screen.tracer(flag, delay)

    def _color(self, args):
        return self.screen._color(args)

    def _colorstr(self, args):
        return self.screen._colorstr(args)

    def _cc(self, args):
        """Convert colortriples to hexstrings."""
        if isinstance(args, str):
            return args
        try:
            r, g, b = args
        except (TypeError, ValueError):
            raise TurtleGraphicsError("bad color arguments: %s" % str(args))
        if self.screen._colormode == 1.0:
            r, g, b = [round(255.0 * x) for x in (r, g, b)]
        if not ((0 <= r <= 255) and (0 <= g <= 255) and (0 <= b <= 255)):
            raise TurtleGraphicsError("bad color sequence: %s" % str(args))
        return "#%02x%02x%02x" % (r, g, b)

    def reset(self):
        """Delete the object's drawings and restore its default values.

        Delete the drawings from the screen, re-center the object and set
        variables to the default values.

        与 turtle 的一个小差异：**保留 speed 设置**。
        turtle 的 ``reset()`` 会把 speed 恢复成默认的 3，
        于是 ``speed(0); reset()`` 这种常见写法会莫名其妙地重新开始做动画；
        move 里 speed 只影响"画得多细"，不属于被清理的绘图状态，
        因此这里显式保留它（``delay()`` 与 ``tracer()`` 同理，它们属于屏幕）。
        """
        speed = self._speed
        TNavigator.reset(self)
        TPen._reset(self)
        self._speed = speed
        self._sync_animation_interval()
        self._clear()
        self._needs_turtle_update = True
        self._drawturtle()
        self._update()

    def setundobuffer(self, size):
        """Set or disable undobuffer.

        If size is an integer an empty undobuffer of given size is installed.
        If size is None, no undobuffer is present.
        """
        if size is None or size <= 0:
            self.undobuffer = None
        else:
            self.undobuffer = Tbuffer(size)

    def undobufferentries(self):
        """Return count of entries in the undobuffer."""
        if self.undobuffer is None:
            return 0
        return self.undobuffer.nr_of_items()

    def _clear(self):
        """Delete all of pen's drawings"""
        self._fillitem = self._fillpath = None
        for item in self.items:
            self.screen._delete(item)
        self.currentLineItem = self.screen._createline()
        self.currentLine = []
        if self._drawing:
            self.currentLine.append(self._position)
        self.items = [self.currentLineItem]
        self.clearstamps()
        self.setundobuffer(self._undobuffersize)

    def clear(self):
        """Delete the drawings from the screen. Do not move the object.

        State and position as well as drawings of other objects are not
        affected.
        """
        self._clear()
        self._update()

    def teleport(self, x=None, y=None, *, fill_gap: bool = False) -> None:
        """Instantly move the object to an absolute position.

        call: teleport(x, y)         # two coordinates
        --or: teleport(x)            # teleport to x position, keeping y as is
        --or: teleport(y=y)          # teleport to y position, keeping x as is
        --or: teleport(x, y, fill_gap=True)   # fill the gap in between

        Unlike goto(x, y), no line is drawn. If currently filling, the
        polygon(s) teleported from will be filled after leaving, and filling
        begins again after teleporting, unless fill_gap=True.
        """
        pendown = self.isdown()
        was_filling = self.filling()
        if pendown:
            self.pen(pendown=False)
        if was_filling and not fill_gap:
            self.end_fill()
        new_x = x if x is not None else self._position[0]
        new_y = y if y is not None else self._position[1]
        self._position = Vec2D(new_x, new_y)
        self.pen(pendown=pendown)
        if was_filling and not fill_gap:
            self.begin_fill()

    def clone(self):
        """Create and return a clone with same position, heading and properties."""
        screen = self.screen
        self._newLine(self._drawing)

        turtle = self.turtle
        self.screen = None
        self.turtle = None  # too make self deepcopy-able

        q = deepcopy(self)

        self.screen = screen
        self.turtle = turtle

        q.screen = screen
        q.turtle = _MoveImage(screen, self.turtle.shapeIndex)

        screen._turtles.append(q)
        ttype = screen._shapes[self.turtle.shapeIndex]._type
        if ttype == "polygon":
            q.turtle._item = screen._createpoly()
        elif ttype == "image":
            q.turtle._item = screen._createimage(screen._shapes["blank"]._data)
        elif ttype == "compound":
            q.turtle._item = [
                screen._createpoly()
                for item in screen._shapes[self.turtle.shapeIndex]._data
            ]
        q.currentLineItem = screen._createline()
        q._needs_turtle_update = True
        q._update()
        return q

    def shape(self, name=None):
        """Set shape to shape with given name / return current shapename.

        Initially there are the following polygon shapes: 'arrow', 'turtle',
        'circle', 'square', 'triangle', 'classic'.
        """
        if name is None:
            return self.turtle.shapeIndex
        if not name in self.screen.getshapes():
            raise TurtleGraphicsError("There is no shape named %s" % name)
        self.turtle._setshape(name)
        self._needs_turtle_update = True
        self._update()

    def shapesize(self, stretch_wid=None, stretch_len=None, outline=None):
        """Set/return the stretchfactors/outline. Set resizemode to "user".

        Optional arguments:
           stretch_wid : positive number
           stretch_len : positive number
           outline  : positive number
        """
        if stretch_wid is stretch_len is outline is None:
            stretch_wid, stretch_len = self._stretchfactor
            return stretch_wid, stretch_len, self._outlinewidth
        if stretch_wid == 0 or stretch_len == 0:
            raise TurtleGraphicsError("stretch_wid/stretch_len must not be zero")
        if stretch_wid is not None:
            if stretch_len is None:
                stretchfactor = stretch_wid, stretch_wid
            else:
                stretchfactor = stretch_wid, stretch_len
        elif stretch_len is not None:
            stretchfactor = self._stretchfactor[0], stretch_len
        else:
            stretchfactor = self._stretchfactor
        if outline is None:
            outline = self._outlinewidth
        self.pen(resizemode="user", stretchfactor=stretchfactor, outline=outline)

    def shearfactor(self, shear=None):
        """Set or return the current shearfactor.

        Shear the shape according to the given shearfactor shear, which is the
        tangent of the shear angle. DO NOT change the heading.
        """
        if shear is None:
            return self._shearfactor
        self.pen(resizemode="user", shearfactor=shear)

    def tiltangle(self, angle=None):
        """Set or return the current tilt-angle.

        Rotate the shape to point in the direction specified by angle,
        regardless of its current tilt-angle. DO NOT change the heading.
        """
        if angle is None:
            tilt = -math.degrees(self._tilt) * self._angleOrient
            return (tilt / self._degreesPerAU) % self._fullcircle
        else:
            tilt = -angle * self._degreesPerAU * self._angleOrient
            tilt = math.radians(tilt) % math.tau
            self.pen(resizemode="user", tilt=tilt)

    def tilt(self, angle):
        """Rotate the shape by angle, without changing the heading."""
        self.tiltangle(angle + self.tiltangle())

    def shapetransform(self, t11=None, t12=None, t21=None, t22=None):
        """Set or return the current transformation matrix of the shape.

        Optional arguments: t11, t12, t21, t22 -- numbers.
        """
        if t11 is t12 is t21 is t22 is None:
            return self._shapetrafo
        m11, m12, m21, m22 = self._shapetrafo
        if t11 is not None:
            m11 = t11
        if t12 is not None:
            m12 = t12
        if t21 is not None:
            m21 = t21
        if t22 is not None:
            m22 = t22
        if t11 * t22 - t12 * t21 == 0:
            raise TurtleGraphicsError(
                "Bad shape transform matrix: must not be singular"
            )
        self._shapetrafo = (m11, m12, m21, m22)
        alfa = math.atan2(-m21, m11) % math.tau
        sa, ca = math.sin(alfa), math.cos(alfa)
        a11, a12, a21, a22 = (
            ca * m11 - sa * m21,
            ca * m12 - sa * m22,
            sa * m11 + ca * m21,
            sa * m12 + ca * m22,
        )
        self._stretchfactor = a11, a22
        self._shearfactor = a12 / a22
        self._tilt = alfa
        self.pen(resizemode="user")

    def _polytrafo(self, poly):
        """Computes transformed polygon shapes from a shape
        according to current position and heading.
        """
        screen = self.screen
        p0, p1 = self._position
        e0, e1 = self._orient
        e = Vec2D(e0, e1 * screen.yscale / screen.xscale)
        e0, e1 = (1.0 / abs(e)) * e
        return [
            (
                p0 + (e1 * x + e0 * y) / screen.xscale,
                p1 + (-e0 * x + e1 * y) / screen.yscale,
            )
            for (x, y) in poly
        ]

    def get_shapepoly(self):
        """Return the current shape polygon as tuple of coordinate pairs."""
        shape = self.screen._shapes[self.turtle.shapeIndex]
        if shape._type == "polygon":
            return self._getshapepoly(shape._data, shape._type == "compound")
        # else return None

    def _getshapepoly(self, polygon, compound=False):
        """Calculate transformed shape polygon according to resizemode
        and shapetransform.
        """
        if self._resizemode == "user" or compound:
            t11, t12, t21, t22 = self._shapetrafo
        elif self._resizemode == "auto":
            l = max(1, self._pensize / 5.0)
            t11, t12, t21, t22 = l, 0, 0, l
        elif self._resizemode == "noresize":
            return polygon
        return tuple((t11 * x + t12 * y, t21 * x + t22 * y) for (x, y) in polygon)

    def _shape_width(self):
        """按 resizemode 决定外形描边宽度。"""
        if self._resizemode == "noresize":
            return 1
        if self._resizemode == "auto":
            return self._pensize
        return self._outlinewidth

    def _drawturtle(self):
        """Manages the correct rendering of the object with respect to
        its shape, resizemode, stretch and tilt etc."""
        screen = self.screen
        shape = screen._shapes[self.turtle.shapeIndex]
        ttype = shape._type
        titem = self.turtle._item
        painter = screen.painter

        visible = self._shown and screen._updatecounter == 0 and screen._tracing > 0

        if not visible:
            if self._hidden_from_screen:
                return
            if ttype == "compound":
                for item in titem:
                    painter.set_turtle(
                        item, ((0, 0), (0, 0), (0, 0)), fill="", outline="",
                        visible=False,
                    )
            else:
                painter.set_turtle(
                    titem, ((0, 0), (0, 0), (0, 0)), fill="", outline="", visible=False
                )
            self._hidden_from_screen = True
            return

        self._hidden_from_screen = False
        tshape = shape._data
        if ttype == "polygon":
            poly = self._polytrafo(self._getshapepoly(tshape))
            coords = [(x * screen.xscale, -y * screen.yscale) for x, y in poly]
            painter.set_turtle(
                titem,
                coords,
                fill=self._pencolor,
                outline=self._pencolor,
                width=self._shape_width(),
                visible=True,
            )
        elif ttype == "image":
            if hasattr(titem, "get_array"):
                pos = (self._position[0] * screen.xscale, -self._position[1] * screen.yscale)
                painter.set_turtle(titem, [pos], visible=True)
            else:
                # blank 形状：图元是空多边形，直接隐藏
                painter.set_turtle(
                    titem, ((0, 0), (0, 0), (0, 0)), fill="", outline="", visible=False
                )
        elif ttype == "compound":
            for item, (poly, fc, oc) in zip(titem, tshape):
                poly = self._polytrafo(self._getshapepoly(poly, True))
                coords = [(x * screen.xscale, -y * screen.yscale) for x, y in poly]
                painter.set_turtle(
                    item,
                    coords,
                    fill=self._cc(fc),
                    outline=self._cc(oc),
                    width=self._outlinewidth,
                    visible=True,
                )

    ##############################  stamp stuff  ###############################

    def stamp(self):
        """Stamp a copy of the shape onto the canvas and return its id.

        Return a stamp_id for that stamp, which can be used to delete it by
        calling clearstamp(stamp_id).
        """
        screen = self.screen
        shape = screen._shapes[self.turtle.shapeIndex]
        ttype = shape._type
        tshape = shape._data
        if ttype == "polygon":
            stitem = screen._createstamppoly()
            poly = self._polytrafo(self._getshapepoly(tshape))
            coords = [(x * screen.xscale, -y * screen.yscale) for x, y in poly]
            screen.painter.set_poly(
                stitem,
                coords,
                fill=self._pencolor,
                outline=self._pencolor,
                width=self._shape_width(),
                top=True,
            )
        elif ttype == "image":
            stitem = screen._createimage(tshape)
            screen._drawimage(stitem, self._position, tshape)
        elif ttype == "compound":
            stitem = []
            for element in tshape:
                item = screen._createstamppoly()
                stitem.append(item)
            stitem = tuple(stitem)
            for item, (poly, fc, oc) in zip(stitem, tshape):
                poly = self._polytrafo(self._getshapepoly(poly, True))
                coords = [(x * screen.xscale, -y * screen.yscale) for x, y in poly]
                screen.painter.set_poly(
                    item,
                    coords,
                    fill=self._cc(fc),
                    outline=self._cc(oc),
                    width=self._outlinewidth,
                    top=True,
                )
        self.stampItems.append(stitem)
        self.undobuffer.push(("stamp", stitem))
        return stitem

    def _clearstamp(self, stampid):
        """does the work for clearstamp() and clearstamps()"""
        if stampid in self.stampItems:
            if isinstance(stampid, tuple):
                for subitem in stampid:
                    self.screen._delete(subitem)
            else:
                self.screen._delete(stampid)
            self.stampItems.remove(stampid)
        # Delete stampitem from undobuffer if necessary
        # if clearstamp is called directly.
        item = ("stamp", stampid)
        buf = self.undobuffer
        if buf is None or item not in buf.buffer:
            return
        index = buf.buffer.index(item)
        buf.buffer.remove(item)
        if index <= buf.ptr:
            buf.ptr = (buf.ptr - 1) % buf.bufsize
        buf.buffer.insert((buf.ptr + 1) % buf.bufsize, [None])

    def clearstamp(self, stampid):
        """Delete stamp with given stampid"""
        self._clearstamp(stampid)
        self._update()

    def clearstamps(self, n=None):
        """Delete all or first/last n of the stamps.

        If n is None, delete all stamps, else if n > 0 delete first n stamps,
        else if n < 0 delete last n stamps.
        """
        if n is None:
            toDelete = self.stampItems[:]
        elif n >= 0:
            toDelete = self.stampItems[:n]
        else:
            toDelete = self.stampItems[n:]
        for item in toDelete:
            self._clearstamp(item)
        self._update()

    def _goto(self, end):
        """Move the pen to the point end, thereby drawing a line
        if pen is down. All other methods for movement depend on this one.
        """
        ## Version with undo-stuff
        go_modes = (
            self._drawing,
            self._pencolor,
            self._pensize,
            isinstance(self._fillpath, list),
        )
        screen = self.screen
        undo_entry = (
            "go",
            self._position,
            end,
            go_modes,
            (
                self.currentLineItem,
                self.currentLine[:],
                screen._pointlist(self.currentLineItem),
                self.items[:],
            ),
        )
        if self.undobuffer:
            self.undobuffer.push(undo_entry)
        start = self._position
        animate = self._speed and screen._tracing == 1
        if animate:
            diff = end - start
            diffsq = (diff[0] * screen.xscale) ** 2 + (diff[1] * screen.yscale) ** 2
            distance_px = diffsq**0.5
            nhops = self._hop_count(distance_px)
            delta = diff * (1.0 / nhops)
            for n in range(1, nhops):
                self._position = start + delta * n
                if self._drawing:
                    screen._drawlinesegment(
                        self.drawingLineItem,
                        start,
                        self._position,
                        self._pencolor,
                        self._pensize,
                    )
                    self._drawturtle()
                self._update(render=True)
            screen._hidelinedrawing(self.drawingLineItem)
        # Move object now at end,
        if self._drawing:  # now update currentLine
            self.currentLine.append(end)
        if isinstance(self._fillpath, list):
            self._fillpath.append(end)
        self._position = end
        if self._creatingPoly:
            self._poly.append(end)
        if len(self.currentLine) > 42:  # 42! answer to the ultimate question
            # of life, the universe and everything
            self._newLine()
        self._update()

    def _undogoto(self, entry):
        """Reverse a _goto. Used for undo()"""
        old, new, go_modes, coodata = entry
        drawing, pc, ps, filling = go_modes
        cLI, cL, pl, items = coodata
        screen = self.screen
        # restore former situation
        self.currentLineItem = cLI
        self.currentLine = cL

        if pl == [(0, 0), (0, 0)]:
            usepc = ""
        else:
            usepc = pc
        screen._drawline(cLI, pl, fill=usepc, width=ps)

        todelete = [
            i for i in self.items if (i not in items) and (screen._type(i) == "line")
        ]
        for i in todelete:
            screen._delete(i)
            self.items.remove(i)

        # 把动画用的临时线段藏起来
        screen._hidelinedrawing(self.drawingLineItem)
        # Move object now at position old,
        self._position = old
        ##  if undo is done during creating a polygon, the last vertex
        ##  will be deleted. if the polygon is entirely deleted,
        ##  creatingPoly will be set to False.
        if self._creatingPoly:
            if len(self._poly) > 0:
                self._poly.pop()
            if self._poly == []:
                self._creatingPoly = False
                self._poly = None
        if filling:
            if self._fillpath == []:
                self._fillpath = None
            elif self._fillpath is not None:
                self._fillpath.pop()
        self._update()

    def _rotate(self, angle):
        """Turns pen clockwise by angle."""
        if self.undobuffer:
            self.undobuffer.push(("rot", angle, self._degreesPerAU))
        angle *= self._degreesPerAU
        # 终点朝向由"起始朝向 + 总角度"一次算出，而不是把中间步累加起来：
        # 逐步 rotate() 会累积 1e-13 级别的浮点误差，
        # 于是 left(33.333333333333) 会变成 33.33333333333297。
        neworient = self._orient.rotate(angle)
        startorient = self._orient
        tracing = self.screen._tracing
        # 角度小到肉眼看不出来（< ~0.06°）时不做插值：既省时间，
        # 也避免中间步（按 delta = angle/n 旋转）引入浮点噪声。
        animate = tracing == 1 and self._speed > 0 and abs(angle) > 1e-3
        if animate:
            anglevel = 3.0 * self._speed
            steps = 1 + int(abs(angle) / anglevel)
            # 与 _hop_count 同理：随 speed 递减的步数上限
            level = max(1, min(int(self._speed), 10))
            steps = max(2, min(steps, 1 + int(3 // level)))
            if steps > 1:
                delta = 1.0 * angle / steps
                for n in range(1, steps):
                    self._orient = startorient.rotate(delta * n)
                    self._drawturtle()
                    self._update(render=True)
        self._orient = neworient
        self._update()

    def _newLine(self, usePos=True):
        """Closes current line item and starts a new one.

        Remark: if current line became too long, animation performance
        (via _drawline) slowed down considerably.
        """
        if len(self.currentLine) > 1:
            self.screen._drawline(
                self.currentLineItem, self.currentLine, self._pencolor, self._pensize
            )
            self.currentLineItem = self.screen._createline()
            self.items.append(self.currentLineItem)
        else:
            self.screen._drawline(self.currentLineItem, top=True)
        self.currentLine = []
        if usePos:
            self.currentLine = [self._position]
        self._needs_data_update = True

    def filling(self):
        """Return fillstate (True if filling, False else)."""
        return isinstance(self._fillpath, list)

    def begin_fill(self):
        """Called just before drawing a shape to be filled."""
        if not self.filling():
            self._fillitem = self.screen._createpoly()
            self.items.append(self._fillitem)
        self._fillpath = [self._position]
        self._newLine()
        if self.undobuffer:
            self.undobuffer.push(("beginfill", self._fillitem))
        self._update()

    def end_fill(self):
        """Fill the shape drawn after the call begin_fill()."""
        if self.filling():
            if len(self._fillpath) > 2:
                self.screen._drawpoly(
                    self._fillitem, self._fillpath, fill=self._fillcolor
                )
                if self.undobuffer:
                    self.undobuffer.push(("dofill", self._fillitem))
            self._fillitem = self._fillpath = None
            self._update()

    def dot(self, size=None, *color):
        """Draw a dot with diameter size, using color.

        Optional arguments:
        size -- an integer >= 1 (if given)
        color -- a colorstring or a numeric color tuple
        """
        if not color:
            if isinstance(size, (str, tuple)):
                color = self._colorstr(size)
                size = self._pensize + max(self._pensize, 4)
            else:
                color = self._pencolor
                if not size:
                    size = self._pensize + max(self._pensize, 4)
        else:
            if size is None:
                size = self._pensize + max(self._pensize, 4)
            color = self._colorstr(color)
        pen = self.pen()
        if self.undobuffer:
            self.undobuffer.push(["seq"])
            self.undobuffer.cumulate = True
        try:
            if self.resizemode() == "auto":
                self.ht()
            self.pendown()
            self.pensize(size)
            self.pencolor(color)
            self.forward(0)
        finally:
            self.pen(pen)
        if self.undobuffer:
            self.undobuffer.cumulate = False

    def _write(self, txt, align, font):
        """Performs the writing for write()"""
        item, end = self.screen._write(self._position, txt, align, font, self._pencolor)
        self._update()
        self.items.append(item)
        self._needs_data_update = True
        if self.undobuffer:
            self.undobuffer.push(("wri", item))
        return end

    def write(self, arg, move=False, align="left", font=("Arial", 8, "normal")):
        """Write text at the current position.

        Arguments:
        arg -- info, which is to be written to the screen
        move (optional) -- True/False
        align (optional) -- one of the strings "left", "center" or right"
        font (optional) -- a triple (fontname, fontsize, fonttype)
        """
        if self.undobuffer:
            self.undobuffer.push(["seq"])
            self.undobuffer.cumulate = True
        end = self._write(str(arg), align.lower(), font)
        if move:
            x, y = self.pos()
            self.setpos(end, y)
        if self.undobuffer:
            self.undobuffer.cumulate = False

    def begin_poly(self):
        """Start recording the vertices of a polygon."""
        self._poly = [self._position]
        self._creatingPoly = True

    def end_poly(self):
        """Stop recording the vertices of a polygon."""
        self._creatingPoly = False

    def get_poly(self):
        """Return the lastly recorded polygon."""
        ## check if there is any poly?
        if self._poly is not None:
            return tuple(self._poly)

    def getscreen(self):
        """Return the MoveScreen object the move object is drawing on."""
        return self.screen

    def getturtle(self):
        """Return the object itself."""
        return self

    getpen = getturtle

    ################################################################
    ### screen oriented methods recurring to methods of MoveScreen
    ################################################################

    def _delay(self, delay=None):
        """Return or set the delay value which determines animation speed.

        turtle 用同步 sleep 实现延迟；matplotlib 版把延迟交给重绘调度，
        因此这里只读写配置值（不再阻塞脚本）。
        """
        return self.screen.delay(delay)

    def delay(self, delay=None):
        """返回或设置动画延迟（毫秒），等价于 ``getscreen().delay()``。

        这是 move 相对 turtle 增加的一个便捷方法：turtle 里 ``delay()``
        只存在于屏幕层，这里在海龟对象上也能直接调用。
        """
        return self.screen.delay(delay)

    def _should_animate(self):
        return self.screen._tracing == 1 and self._speed > 0

    def onclick(self, fun, btn=1, add=None):
        """Bind fun to mouse-click event on this object.

        Arguments:
        fun --  a function with two arguments, to which will be assigned
                the coordinates of the clicked point on the canvas.
        btn --  number of the mouse-button defaults to 1 (left mouse button).
        add --  True or False. If True, new binding will be added, otherwise
                it will replace a former binding.
        """
        self.screen._ensure_mouse_hooks()
        self.screen._onclick(self.turtle._item, fun, btn, add)
        self._update()

    def onrelease(self, fun, btn=1, add=None):
        """Bind fun to mouse-button-release event on this object."""
        self.screen._ensure_mouse_hooks()
        self.screen._onrelease(self.turtle._item, fun, btn, add)
        self._update()

    def ondrag(self, fun, btn=1, add=None):
        """Bind fun to mouse-move event on this object."""
        self.screen._ensure_mouse_hooks()
        self.screen._ondrag(self.turtle._item, fun, btn, add)

    def _undo(self, action, data):
        """Does the main part of the work for undo()"""
        if self.undobuffer is None:
            return
        if action == "rot":
            angle, degPAU = data
            self._rotate(-angle * degPAU / self._degreesPerAU)
            dummy = self.undobuffer.pop()
        elif action == "stamp":
            stitem = data[0]
            self.clearstamp(stitem)
        elif action == "go":
            self._undogoto(data)
        elif action in ["wri", "dot"]:
            item = data[0]
            self.screen._delete(item)
            if item in self.items:
                self.items.remove(item)
        elif action == "dofill":
            item = data[0]
            self.screen._drawpoly(item, ((0, 0), (0, 0), (0, 0)), fill="", outline="")
        elif action == "beginfill":
            item = data[0]
            self._fillitem = self._fillpath = None
            if item in self.items:
                self.screen._delete(item)
                self.items.remove(item)
        elif action == "pen":
            TPen.pen(self, data[0])
            self.undobuffer.pop()

    def undo(self):
        """undo (repeatedly) the last action.

        Number of available undo actions is determined by the size of the
        undobuffer.
        """
        if self.undobuffer is None:
            return
        item = self.undobuffer.pop()
        action = item[0]
        data = item[1:]
        if action == "seq":
            while data:
                item = data.pop()
                self._undo(item[0], item[1:])
        else:
            self._undo(action, data)

    turtlesize = shapesize


RawPen = RawMove


###  MoveScreen - Singleton  ########################


def Screen():
    """Return the singleton screen object.

    If none exists at the moment, create a new one and return it,
    else return the existing one.
    """
    if _Screen._default_painter is None:
        Move._screen = _Screen()
    return Move._screen


class _Screen(MoveScreen):
    """带"自动创建 matplotlib 图形窗口"能力的屏幕（turtle 的 Screen 对应物）。"""

    _painter = None  # 兼容旧名字
    _default_painter = None  # 默认（单例）图形的画布
    _title = _CFG["title"]

    def __init__(self, fig=None, ax=None):
        own_figure = fig is None and ax is None
        target = _Screen._default_painter if own_figure else None
        if target is None:
            canvwidth = _CFG["canvwidth"]
            canvheight = _CFG["canvheight"]
            figsize = _CFG["figsize"]
            dpi = _CFG["dpi"] or 100
            if own_figure:
                if figsize is None:
                    figsize = (float(canvwidth) / dpi, float(canvheight) / dpi)
                fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
            target = MovePainter(fig, ax, canvwidth=canvwidth, canvheight=canvheight)
            target.background("white")
            target.set_delay(_CFG["delay"])
            if own_figure:
                _Screen._default_painter = target
                _Screen._painter = target
        MoveScreen.__init__(self, target)
        self._is_default = own_figure
        self._title = _Screen._title
        self._apply_title()
        self.setup(_CFG["width"], _CFG["height"], _CFG["leftright"], _CFG["topbottom"])

    def _apply_title(self):
        try:
            manager = self.painter.fig.canvas.manager
            if manager is not None:
                manager.set_window_title(self._title)
        except Exception:
            pass

    def setup(
        self,
        width=_CFG["width"],
        height=_CFG["height"],
        startx=_CFG["leftright"],
        starty=_CFG["topbottom"],
    ):
        """Set the size and position of the main window.

        Arguments:
        width: as integer a size in pixels, as float a fraction of the screen.
        height: as integer the height in pixels, as float a fraction of screen.
        startx: if positive, starting position in pixels from the left edge of
          the screen, if negative from the right edge.
        starty: if positive, starting position in pixels from the top edge of
          the screen, if negative from the bottom edge.
        """
        fig = self.painter.fig
        dpi = float(fig.get_dpi()) or 100.0
        if width is None:
            width = self.painter.canvwidth
        if height is None:
            height = self.painter.canvheight
        if isinstance(width, float) and 0 <= width <= 1:
            width = self.painter.pixel_width * width
        if isinstance(height, float) and 0 <= height <= 1:
            height = self.painter.pixel_height * height
        width = max(50.0, float(width))
        height = max(50.0, float(height))
        try:
            fig.set_size_inches(width / dpi, height / dpi, forward=True)
        except Exception:
            pass
        # 让 axes 的数据范围跟随新的窗口尺寸
        self.painter.resize_canvas(None, None)
        self.canvwidth = self.painter.canvwidth
        self.canvheight = self.painter.canvheight
        # matplotlib 没有统一的跨后端"移动窗口"接口，有则用之
        if startx is not None or starty is not None:
            self._move_window(startx, starty, width, height)
        self.update()

    def _move_window(self, startx, starty, width, height):
        try:
            manager = self.painter.fig.canvas.manager
            window = getattr(manager, "window", None)
            if window is None:
                return
            screen_w, screen_h = self.painter.window_size()
            x = 0 if startx is None else int(startx)
            y = 0 if starty is None else int(starty)
            if hasattr(window, "move"):
                window.move(x, y)
            elif hasattr(window, "setPosition"):
                window.setPosition(x, y)
        except Exception:
            pass

    def title(self, titlestring):
        """Set title of the move window."""
        _Screen._title = titlestring
        self._title = titlestring
        self._apply_title()

    def _destroy(self):
        painter = self.painter
        self._drop_mouse_hooks()
        if painter is _Screen._default_painter:
            Move._pen = None
            Move._screen = None
            _Screen._default_painter = None
            _Screen._painter = None
        MoveScreen._RUNNING = False
        try:
            painter.destroy()
        except Exception:
            pass

    def bye(self):
        """Shut the move graphics window."""
        self._destroy()

    def exitonclick(self):
        """Go into mainloop until the mouse is clicked.

        Bind bye() method to mouseclick on the screen. This is a method of the
        Screen-class and not available for MoveScreen instances.
        """

        def exitGracefully(x, y):
            """Screen.bye() with two dummy-parameters"""
            self.bye()

        self.onclick(exitGracefully)
        if _CFG["using_IDLE"]:
            return
        try:
            mainloop()
        except AttributeError:
            pass


class Move(RawMove):
    """RawMove auto-creating a matplotlib figure.

    When a Move object is created or a function derived from some Move method
    is called, a MoveScreen object is automatically created.
    """

    _pen = None
    _screen = None
    _extra_screens = {}  # (fig.number, id(ax)) -> MoveScreen

    def __init__(
        self,
        shape=_CFG["shape"],
        undobuffersize=_CFG["undobuffersize"],
        visible=_CFG["visible"],
        fig=None,
        ax=None,
    ):
        if fig is None and ax is None:
            screen = Screen()
        else:
            if ax is not None and fig is None:
                fig = ax.get_figure()
            key = (fig.number, id(ax))
            screen = Move._extra_screens.get(key)
            if screen is None:
                screen = _Screen(fig, ax)
                Move._extra_screens[key] = screen
        RawMove.__init__(
            self,
            screen,
            shape=shape,
            undobuffersize=undobuffersize,
            visible=visible,
        )


Pen = Move


def write_docstringdict(filename="move_docstringdict"):
    """Create and write docstring-dictionary to file.

    Optional argument:
    filename -- a string, used as filename
                default value is move_docstringdict

    Has to be called explicitly, (not used by the move-graphics classes)
    The docstring dictionary will be written to the Python script <filename>.py
    It is intended to serve as a template for translation of the docstrings
    into different languages.
    """
    docsdict = {}

    for methodname in _tg_screen_functions:
        key = "_Screen." + methodname
        docsdict[key] = eval(key).__doc__
    for methodname in _tg_turtle_functions:
        key = "Move." + methodname
        docsdict[key] = eval(key).__doc__

    with open("%s.py" % filename, "w", encoding="utf-8") as f:
        keys = sorted(x for x in docsdict if x.split(".")[1] not in _alias_list)
        f.write("docsdict = {\n\n")
        for key in keys[:-1]:
            f.write("%s :\n" % repr(key))
            f.write('        """%s\n""",\n\n' % docsdict[key])
        key = keys[-1]
        f.write("%s :\n" % repr(key))
        f.write('        """%s\n"""\n\n' % docsdict[key])
        f.write("}\n")
        f.close()


def read_docstrings(lang):
    """Read in docstrings from lang-specific docstring dictionary.

    Transfer docstrings, translated to lang, from a dictionary-file
    to the methods of classes _Screen and Move and - in revised form -
    to the corresponding functions.
    """
    modname = "move_docstringdict_%(language)s" % {"language": lang.lower()}
    module = __import__(modname)
    docsdict = module.docsdict
    for key in docsdict:
        try:
            eval(key).__doc__ = docsdict[key]
        except Exception:
            print("Bad docstring-entry: %s" % key)


_LANGUAGE = _CFG["language"]

try:
    if _LANGUAGE != "english":
        read_docstrings(_LANGUAGE)
except ImportError:
    print("Cannot find docsdict for", _LANGUAGE)
except Exception:
    print("Unknown Error when trying to import %s-docstring-dictionary" % _LANGUAGE)


def getmethparlist(ob):
    """Get strings describing the arguments for the given object

    Returns a pair of strings representing function parameter lists
    including parenthesis.  The first string is suitable for use in
    function definition and the second is suitable for use in
    function call.  The "self" parameter is not included.
    """
    orig_sig = inspect.signature(ob)
    # bit of a hack for methods - turn it into a function
    # but we drop the "self" param.
    func_sig = orig_sig.replace(
        parameters=list(orig_sig.parameters.values())[1:],
    )

    call_args = []
    for param in func_sig.parameters.values():
        match param.kind:
            case (
                inspect.Parameter.POSITIONAL_ONLY
                | inspect.Parameter.POSITIONAL_OR_KEYWORD
            ):
                call_args.append(param.name)
            case inspect.Parameter.VAR_POSITIONAL:
                call_args.append(f"*{param.name}")
            case inspect.Parameter.KEYWORD_ONLY:
                call_args.append(f"{param.name}={param.name}")
            case inspect.Parameter.VAR_KEYWORD:
                call_args.append(f"**{param.name}")
            case _:
                raise RuntimeError("Unsupported parameter kind", param.kind)
    call_text = f"({', '.join(call_args)})"

    return str(func_sig), call_text


def _move_docrevise(docstr):
    """To reduce docstrings from RawMove class for functions"""
    import re

    if docstr is None:
        return None
    turtlename = _CFG["exampleturtle"]
    newdocstr = docstr.replace("%s." % turtlename, "")
    parexp = re.compile(r" \(.+ %s\):" % turtlename)
    newdocstr = parexp.sub(":", newdocstr)
    return newdocstr


def _screen_docrevise(docstr):
    """To reduce docstrings from MoveScreen class for functions"""
    import re

    if docstr is None:
        return None
    screenname = _CFG["examplescreen"]
    newdocstr = docstr.replace("%s." % screenname, "")
    parexp = re.compile(r" \(.+ %s\):" % screenname)
    newdocstr = parexp.sub(":", newdocstr)
    return newdocstr


## The following mechanism makes all methods of RawMove and Move available
## as functions. So we can enhance, change, add, delete methods to these
## classes and do not need to change anything here.

__func_body = """\
def {name}{paramslist}:
    if {obj} is None:
        if not MoveScreen._RUNNING:
            MoveScreen._RUNNING = True
            raise Terminator
        {obj} = {init}
    try:
        return {obj}.{name}{argslist}
    except TurtleGraphicsError:
        raise
"""


def _make_global_funcs(functions, cls, obj, init, docrevise):
    for methodname in functions:
        method = getattr(cls, methodname)
        pl1, pl2 = getmethparlist(method)
        if pl1 == "":
            print(">>>>>>", pl1, pl2)
            continue
        defstr = __func_body.format(
            obj=obj, init=init, name=methodname, paramslist=pl1, argslist=pl2
        )
        exec(defstr, globals())
        globals()[methodname].__doc__ = docrevise(method.__doc__)


_make_global_funcs(
    _tg_screen_functions, _Screen, "Move._screen", "Screen()", _screen_docrevise
)
_make_global_funcs(
    _tg_turtle_functions, Move, "Move._pen", "Move()", _move_docrevise
)


done = mainloop


# ---------------------------------------------------------------------------
# 便捷别名 / 迁移辅助
# ---------------------------------------------------------------------------

#: turtle 用户迁移时常用的旧类名（不放进 ``__all__``，避免污染星号导入）。
Turtle = Move
TurtleScreen = MoveScreen
RawTurtle = RawMove
ScrolledCanvas = MoveCanvas

#: 当前屏幕（等价于 turtle 的 ``getscreen()``，但没有参数）。
def get_screen():
    """返回（必要时创建）当前 MoveScreen 单例。"""
    return Screen()


def get_figure():
    """返回当前绘图的 matplotlib Figure。"""
    return Screen().painter.fig


def get_axes():
    """返回当前绘图的 matplotlib Axes。"""
    return Screen().painter.ax


def savefig(filename, **kwargs):
    """把当前画面保存到文件（``update()`` 后调用最保险）。"""
    update()
    return Screen().painter.fig.savefig(filename, **kwargs)


def reset_screen():
    """丢弃当前屏幕单例，让下一次绘图重新创建图形窗口。"""
    Move._pen = None
    Move._screen = None
    painter = _Screen._default_painter
    _Screen._default_painter = None
    _Screen._painter = None
    extras = list(Move._extra_screens.values())
    Move._extra_screens = {}
    RawMove.screens = []
    if painter is not None:
        screen = getattr(painter, "_screen", None)
        if screen is not None:
            try:
                screen._drop_mouse_hooks()
            except Exception:
                pass
        try:
            painter.destroy()
        except Exception:
            pass
    for screen in extras:
        try:
            screen._drop_mouse_hooks()
        except Exception:
            pass
        try:
            screen.painter.destroy()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# 演示
# ---------------------------------------------------------------------------


def _demo_move():
    """画一幅演示图（turtle 原 demo 的 matplotlib 版）。"""

    def switchpen():
        if isdown():
            pu()
        else:
            pd()

    speed(0)
    reset()
    tracer(True)
    up()
    backward(100)
    down()
    # draw 3 squares; the last filled
    width(3)
    for i in range(3):
        if i == 2:
            begin_fill()
        for _ in range(4):
            forward(20)
            left(90)
        if i == 2:
            color("maroon")
            end_fill()
        up()
        forward(30)
        down()
    width(1)
    color("black")
    # move out of the way
    up()
    right(90)
    forward(100)
    right(90)
    forward(100)
    right(180)
    down()
    # some text
    write("startstart", 1)
    write("start", 1)
    color("red")
    # staircase
    for i in range(5):
        forward(20)
        left(90)
        forward(20)
        right(90)
    # filled staircase
    begin_fill()
    for i in range(5):
        forward(20)
        left(90)
        forward(20)
        right(90)
    end_fill()

    # --- 第二部分：彩色三角、圆弧花瓣与"猫抓老鼠" ---
    speed(0)
    st()
    pensize(3)
    setheading(towards(0, 0))
    radius = distance(0, 0) / 2.0
    rt(90)
    for _ in range(18):
        switchpen()
        circle(radius, 10)
    write("wait a moment...")
    while undobufferentries():
        undo()
    reset()
    lt(90)
    colormode(255)
    laenge = 10
    pencolor("green")
    pensize(3)
    lt(180)
    for i in range(-2, 16):
        if i > 0:
            begin_fill()
            fillcolor(255 - 15 * i, 0, 15 * i)
        for _ in range(3):
            fd(laenge)
            lt(120)
        end_fill()
        laenge += 10
        lt(15)

    lt(120)
    pu()
    fd(70)
    rt(30)
    pd()
    color("red", "yellow")
    speed(0)
    begin_fill()
    for _ in range(4):
        circle(50, 90)
        rt(90)
        fd(30)
        rt(90)
    end_fill()
    lt(90)
    pu()
    fd(30)
    pd()
    shape("turtle")

    tri = getturtle()
    tri.resizemode("auto")
    turtle = Move()
    turtle.resizemode("auto")
    turtle.shape("turtle")
    turtle.reset()
    turtle.left(90)
    turtle.speed(0)
    turtle.up()
    turtle.goto(280, 40)
    turtle.lt(30)
    turtle.down()
    turtle.speed(0)
    turtle.color("blue", "orange")
    turtle.pensize(2)
    tri.speed(0)
    setheading(towards(turtle))
    count = 1
    while tri.distance(turtle) > 4:
        turtle.fd(3.5)
        turtle.lt(0.6)
        tri.setheading(tri.towards(turtle))
        tri.fd(4)
        if count % 20 == 0:
            turtle.stamp()
            tri.stamp()
            switchpen()
        count += 1
    tri.write("CAUGHT! ", font=("Arial", 16, "bold"), align="right")
    tri.pencolor("black")
    tri.pencolor("red")
    return tri


if __name__ == "__main__":
    _demo_move()
    done()

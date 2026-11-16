"""matplotlib 绘制与动画后端（move 模块内部实现）。

本模块把原先 turtle 的 Tkinter 画布层（``TurtleScreenBase`` 中用
``TK.Canvas`` 实现的 ``_createline/_drawline/_createpoly/_drawpoly/
_createimage/_drawimage/_write`` 等）换成了 matplotlib 的画布层。

设计要点
--------
* 所有图元的坐标都保存在 **画布坐标** 中（与 turtle 原实现一致：x 向右、
  y 向下为负，即 ``-y``），绘图区 ``xlim/ylim`` 直接对应该坐标系，
  因此 turtle 世界坐标变换（``setworldcoordinates``）只需修改轴范围。
* 线条 / 多边形 / 文字 / 图片都做成可复用的 matplotlib artist，
  由上层 ``RawMove`` 统一创建、更新和删除。
* 动画采用 matplotlib 的 ``canvas.draw_idle()`` 延迟重绘：
  连续调用会产生合并重绘，无需每个中间步都强制刷新，
  这正是原 turtle 用 ``tk.after`` 达到的效果。
* 鼠标 / 键盘 / 定时器事件用 matplotlib 的事件系统实现。

绘图区（axes）的坐标范围在数值上等于画布像素范围，例如画布为
400x300 时 ``xlim=(-200, 200)``、``ylim=(-150, 150)``，
所以 1 个数据单位 = 1 像素。
"""

import atexit
import math
import sys
import time
import weakref

import numpy as np

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import colors as _mcolors
from matplotlib.patches import Polygon

try:  # 可选：只有安装 Pillow 时才能读位图当 turtle 形状
    from PIL import Image
except Exception:  # pragma: no cover - Pillow 缺失时降级
    Image = None


# ---------------------------------------------------------------------------
# 小工具
# ---------------------------------------------------------------------------

#: 背景色与"空"颜色的别名，避免 Tk 与 matplotlib 命名差异带来的问题。
_COLOR_ALIASES = {
    "": "none",
    "None": "none",
    "transparent": "none",
}

#: 明确的非交互式后端名（没有事件循环、收不到用户事件、不会刷屏）。
#: 注意：**不能**用"名字里含 agg"来判断非交互 —— TkAgg / QtAgg / WxAgg
#: 这些 GUI 后端都含 "agg"，那样会把真正的交互后端误判成非交互，
#: 结果就是中间帧全部被合并、看不到运动过程。
_NON_GUI_BACKENDS = {
    "agg",
    "cairo",
    "pdf",
    "pgf",
    "ps",
    "svg",
    "template",
    "module://matplotlib_inline.backend_inline",
    "module://ipympl.backend_nbagg",
    "module://ipykernel.pylab.backend_inline",
    "nbagg",
    "webagg",
    "widget",
    "notebook",
}

#: 已经登记"程序退出时关闭图形窗口"的图形对象。
_ATEXIT_FIGS = weakref.WeakSet()


#: 动画每帧最长等待时间（秒）：即使 delay 很大也不会把脚本卡住
_MAX_FRAME_SLEEP = 0.1


def _clamp(value, limit):
    """把坐标限制在合理范围内，避免非有限值把坐标轴搞坏。"""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return -limit
    if not math.isfinite(value):
        return math.copysign(limit, value if value == value else 1.0)
    return max(-limit, min(limit, value))


def _norm_color(color):
    """把 turtle 风格的颜色串翻译成 matplotlib 能接受的形式。"""
    if color is None:
        return None
    if isinstance(color, str):
        return _COLOR_ALIASES.get(color.strip(), color)
    return color


def _as_color(color):
    """返回 ``(颜色, 是否透明)``。"""
    color = _norm_color(color)
    return color, color in (None, "none")


def _is_gui_backend(fig=None):
    """当前后端是否能真正把每一帧刷到屏幕上。

    判定顺序：
    1. 后端名在非交互后端名单里 -> False；
    2. 图形有真实的 GUI 窗口（``manager.window``）-> True；
    3. 其余情况交给 ``canvas`` 是否提供 ``flush_events`` 决定。

    ``fig`` 可选；给了就用它的 canvas 判断，没给就用当前后端的名字。
    """
    canvas = None
    if fig is not None:
        canvas = getattr(fig, "canvas", None)

    try:
        backend = str(matplotlib.get_backend()).lower()
    except Exception:  # pragma: no cover - 后端不可用时保守处理
        backend = ""
    if backend in _NON_GUI_BACKENDS:
        return False
    if any(key in backend for key in ("inline", "nbagg")):
        return False

    if canvas is not None:
        manager = getattr(canvas, "manager", None)
        window = getattr(manager, "window", None) if manager is not None else None
        if window is not None:
            return True
        return bool(getattr(canvas, "flush_events", None)) and backend not in (
            "agg",
            "cairo",
            "pdf",
            "pgf",
            "ps",
            "svg",
            "template",
        )
    return backend not in _NON_GUI_BACKENDS


def _reg_atexit_close(fig):
    """登记图形窗口在解释器退出时自动关闭。"""
    if fig in _ATEXIT_FIGS:
        return
    _ATEXIT_FIGS.add(fig)

    def _close():
        try:
            if plt.fignum_exists(fig.number):
                plt.close(fig)
        except Exception:
            pass

    atexit.register(_close)


def _simplify(coords, max_points=4000):
    """点太多时按等间隔抽稀，避免 PNG/交互重绘过慢。"""
    n = len(coords)
    if n <= max_points:
        return list(coords)
    step = int(math.ceil(n / float(max_points)))
    return list(coords[::step])


def load_image_array(filename):
    """读取图片为 numpy 数组；失败或缺少 Pillow 时返回 ``None``。"""
    try:
        if Image is None:
            return None
        with Image.open(filename) as img:
            return np.asarray(img.convert("RGBA"))
    except Exception:
        return None


# ---------------------------------------------------------------------------
# 画布后端
# ---------------------------------------------------------------------------


class MovePainter:
    """把 turtle 的绘图原语映射到 matplotlib 的 axes 上。

    上层只通过本类操作画布，从而与具体的图形库解耦
    （对应原 turtle.py 中 ``TurtleScreenBase`` 的角色）。
    """

    def __init__(self, fig=None, ax=None, canvwidth=None, canvheight=None):
        if ax is not None and fig is None:
            fig = ax.get_figure()
        created = fig is None
        if fig is None:
            fig, ax = plt.subplots()
        if ax is None:
            ax = fig.add_subplot(111)

        self.fig = fig
        self.ax = ax
        self._created_figure = created
        self._owns_figure = created

        dpi = float(fig.get_dpi()) or 100.0
        self._dpi = dpi
        win_w, win_h = self._figure_pixel_size()

        if created:
            # 自己创建的图形窗口：按 canvwidth/canvheight 设定大小
            if canvwidth is not None and canvheight is not None:
                try:
                    fig.set_size_inches(
                        float(canvwidth) / dpi, float(canvheight) / dpi, forward=True
                    )
                except Exception:
                    pass
                win_w, win_h = self._figure_pixel_size()
            self.canvwidth, self.canvheight = win_w, win_h
        else:
            # 复用用户的图形：画布就是整块图形，忽略 canvwidth/canvheight，
            # 避免出现"坐标范围与实际窗口不一致"的隐形错误。
            self.canvwidth, self.canvheight = win_w, win_h

        # 同一个 axes 只建一把锁，多屏共享时避免互相抢图
        self._lock = _AXES_LOCKS.setdefault(id(ax), _threading_lock())

        ax.set_aspect("auto")
        ax.set_axis_off()
        ax.set_xlim(-self.canvwidth / 2.0, self.canvwidth / 2.0)
        ax.set_ylim(-self.canvheight / 2.0, self.canvheight / 2.0)
        ax.set_autoscale_on(False)
        ax.set_navigate(False)  # 禁用 matplotlib 自带的平移/缩放手势

        # 记录属于本画布的所有 artist，便于整屏清理
        self._items = set()
        self._lines = []
        self._polys = []
        self._images = []
        self._texts = []
        self._turtle_artists = []
        self._figure_images = []

        # 图元层级：背景图 < 填充 < 画笔 < 印章/置顶 < 文字 < move 外形
        self._z = {
            "bg": 0,
            "fill": 1,
            "line": 2,
            "stamp": 3,
            "top": 4,
            "text": 5,
            "turtle": 6,
        }

        self._repaint_pending = False
        self._timer_seq = 0
        self._timers = {}
        self._closed = False
        self._zoom_disabled = False
        self._screen = None  # 由 MoveScreen 注册，用于事件分发

        # 动画帧节流：delay() 决定两帧之间至少间隔多少毫秒，
        # ``interactive=False`` 可强制关闭（无界面/录制场景）
        self.interactive = True
        self._min_frame_interval = 0.010
        self._last_frame = time.monotonic()
        self._frames = 0

        self._disable_zoom_pan()
        _reg_atexit_close(fig)

    def _disable_zoom_pan(self):
        """关闭工具栏缩放/平移，否则会破坏"1 单位=1 像素"的映射。"""
        if self._zoom_disabled:
            return
        self._zoom_disabled = True
        try:
            for key in ("keymap.zoom", "keymap.pan", "keymap.home", "keymap.save"):
                try:
                    matplotlib.rcParams[key] = []
                except Exception:
                    pass
        except Exception:
            pass
        # 世界坐标模式下用户可能确实想缩放，所以只解除导航限制，
        # 不强行改写工具栏状态；此处仅保留 rcParams 处理。

    # -- 基本属性 ----------------------------------------------------------

    @property
    def canvas(self):
        return self.fig.canvas

    @property
    def owns_figure(self):
        """图形窗口是否由本画布创建（决定 ``bye()`` 是否关闭它）。"""
        return self._owns_figure

    @property
    def figure(self):
        return self.fig

    @property
    def axes(self):
        return self.ax

    @property
    def lock(self):
        return self._lock

    def _canvas_pixel_size(self):
        """图形画布的像素尺寸（用于 ``window_size``，会随窗口大小变化）。"""
        try:
            w, h = self.fig.canvas.get_width_height()
            return max(1.0, float(w)), max(1.0, float(h))
        except Exception:
            pass
        return self._figure_pixel_size()

    def _figure_pixel_size(self):
        """由 ``figsize`` 与 dpi 推算的像素尺寸（未渲染时的估算）。"""
        dpi = float(self.fig.get_dpi()) or 100.0
        fig_w, fig_h = self.fig.get_size_inches()
        return max(1.0, float(fig_w) * dpi), max(1.0, float(fig_h) * dpi)

    @property
    def pixel_width(self):
        return self._canvas_pixel_size()[0]

    @property
    def pixel_height(self):
        return self._canvas_pixel_size()[1]

    def window_size(self):
        """图形窗口的宽高（像素），等价于原 Tk 的 ``winfo_width/height``。"""
        return self._canvas_pixel_size()

    def resize_canvas(self, canvwidth=None, canvheight=None):
        """改变画布（以及图形窗口）的像素尺寸。

        同时把 axes 的数据范围调整为新的画布范围，
        保持"1 数据单位 = 1 像素"的映射。
        """
        cur_w, cur_h = self.canvwidth, self.canvheight
        new_w = float(canvwidth) if canvwidth else cur_w
        new_h = float(canvheight) if canvheight else cur_h
        self.canvwidth, self.canvheight = new_w, new_h

        win_w, win_h = self._canvas_pixel_size()
        if abs(new_w - win_w) > 0.5 or abs(new_h - win_h) > 0.5:
            dpi = float(self.fig.get_dpi()) or 100.0
            try:
                self.fig.set_size_inches(new_w / dpi, new_h / dpi, forward=True)
            except Exception:
                pass
            win_w, win_h = self._figure_pixel_size()
            self.canvwidth, self.canvheight = new_w, new_h

        self.set_scroll_region(-new_w / 2.0, -new_h / 2.0, new_w / 2.0, new_h / 2.0)
        self.request_repaint()
        return new_w, new_h

    # -- 重绘调度 ----------------------------------------------------------

    def request_repaint(self, delay=0.0):
        """请求一次重绘（turtle ``update()`` 的语义：调用即"标记脏"）。

        * 有 ``delay`` 时交给定时器，由 ``frame()`` 在到期后真正绘制；
        * 无 ``delay`` 时立刻标记重绘，但**不会**阻塞脚本 ——
          真正的逐帧刷新由 :meth:`frame` 在动画过程中完成。
        """
        if self._closed:
            return
        self._repaint_pending = True
        if delay and delay > 0:
            self.after(int(delay), self._repaint_now)
        else:
            self._repaint_now()

    def set_delay(self, delay_ms):
        """设置两帧之间的最小间隔（毫秒），用于动画节流。"""
        try:
            self._min_frame_interval = max(0.0, float(delay_ms) / 1000.0)
        except (TypeError, ValueError):
            self._min_frame_interval = 0.0

    def frame(self, delay_ms=None, force=False):
        """把当前状态真正画到屏幕上，形成一帧动画，并返回是否真的画了。

        与 :meth:`request_repaint` 的区别：本方法立即完成一次真实绘制
        （并让 GUI 处理事件），而且**按帧间隔节流**，
        从而让 ``speed()>0`` 的插值过程肉眼可见。

        * 距上一帧还不够 ``delay`` 毫秒时，会**等待到下一帧**再画
          （而不是丢掉这一帧 —— 丢帧就等于没有动画）；
        * 在没有事件循环的后端（Agg / inline）上照样绘制，只是不等待，
          这样"录制动画"和单元测试都能拿到每一帧；
        * 每次等待有上限 :data:`_MAX_FRAME_SLEEP`，避免 delay 很大时卡死。
        """
        if self._closed:
            return False
        if delay_ms is not None:
            self.set_delay(delay_ms)

        gui = self.interactive and _is_gui_backend(self.fig)
        if gui:
            now = time.monotonic()
            wait = self._min_frame_interval - (now - self._last_frame)
            if wait > 0:
                if not force and wait > _MAX_FRAME_SLEEP:
                    # 帧间隔过大（delay 设得很大）：不阻塞脚本，只标记重绘
                    self._repaint_pending = True
                    return False
                time.sleep(min(wait, _MAX_FRAME_SLEEP))

        self._draw_frame_now(gui=gui)
        return True

    def _draw_frame_now(self, gui=None):
        """立即绘制一帧，并让窗口系统真的把它显示出来。

        只调用 ``canvas.draw()`` 是不够的：matplotlib 把图画进后端缓冲区，
        真正"刷到屏幕上"要靠 GUI 事件循环。TkAgg 必须显式
        ``window.update()``（``flush_events()`` 只处理事件队列、不做 blit），
        缺了这一步中间帧就会被合并 —— 表现就是"没有运动过程，一下就出来了"。
        """
        if gui is None:
            gui = self.interactive and _is_gui_backend(self.fig)
        self._repaint_pending = False
        self._last_frame = time.monotonic()
        self.process_timers()
        canvas = self.fig.canvas
        try:
            canvas.draw()
        except Exception:
            return
        if gui:
            self._flush_screen()
        self._frames += 1

    def _flush_screen(self):
        """把刚画好的帧推到屏幕上（按后端能力逐个尝试）。"""
        canvas = self.fig.canvas
        window = None
        try:
            manager = getattr(canvas, "manager", None)
            window = getattr(manager, "window", None) if manager is not None else None
        except Exception:
            window = None

        # 1) Tk：draw() 之后还需要 update() 才会真正 blit 到窗口
        if window is not None:
            for name in ("update", "update_idletasks"):
                meth = getattr(window, name, None)
                if meth is None:
                    continue
                try:
                    meth()
                    return
                except Exception:
                    continue
        # 2) Qt / wx / GTK / nbagg 等：flush_events() 会处理事件并重绘
        flush = getattr(canvas, "flush_events", None)
        if flush is not None:
            try:
                flush()
                return
            except Exception:
                pass
        # 3) 兜底：部分后端只有 plt.pause() 能推动事件循环。
        #    注意这里不 sleep 很久，否则每帧固定开销会盖过动画本身。
        try:
            plt.pause(0.0001)
        except Exception:
            pass

    def _repaint_now(self):
        self._repaint_pending = False
        if self.interactive and _is_gui_backend(self.fig):
            # 交互后端上用 draw_idle 即可，GUI 会安排一次重绘；
            # 若调用方需要立刻看到结果，会用 frame()/flush()。
            try:
                self.fig.canvas.draw_idle()
            except Exception:
                pass
            return
        try:
            self.fig.canvas.draw_idle()
        except Exception:
            try:
                self.fig.canvas.draw()
            except Exception:
                pass

    def flush(self):
        """立即完成一次真正的绘制。

        用于 ``tracer(0)`` 之后手工调用 ``update()``，
        以及把结果落盘（``savefig``）之前。
        """
        if self._closed:
            return
        self._repaint_pending = False
        try:
            self.fig.canvas.draw()
        except Exception:
            pass

    # -- 颜色 --------------------------------------------------------------

    def is_color_string(self, color):
        """字符串是否是 matplotlib 认识的颜色。"""
        if not isinstance(color, str):
            return False
        if color == "":
            return True
        try:
            _mcolors.to_rgba(color)
            return True
        except Exception:
            return False

    def background(self, color=None):
        """设置/读取背景色。"""
        if color is None:
            return _norm_color(self.ax.get_facecolor())
        color = _norm_color(color)
        try:
            self.ax.set_facecolor(color)
            self.fig.set_facecolor(color)
            self.ax.patch.set_visible(True)
            self.ax.patch.set_alpha(1.0)
            self.ax.patch.set_zorder(-1)
        except Exception:
            pass
        self.request_repaint()
        return color

    # -- 直线 --------------------------------------------------------------

    def create_line(self):
        """在画布上创建一条隐藏的折线，返回 Line2D 对象。"""
        (line,) = self.ax.plot(
            [], [], color="none", linewidth=1.0, solid_capstyle="round"
        )
        line.set_zorder(self._z["line"])
        line.set_antialiased(False)
        self._lines.append(line)
        self._items.add(line)
        return line

    def set_line(self, line, coords, color=None, width=None, top=False):
        """按给定点集（画布坐标）更新折线。"""
        if line is None:
            return
        if coords is not None:
            coords = _simplify(coords)
            if len(coords) > 1:
                xs = np.asarray([p[0] for p in coords], dtype=float)
                ys = np.asarray([p[1] for p in coords], dtype=float)
                line.set_data(xs, ys)
            else:
                line.set_data([], [])
        if color is not None:
            line.set_color(_norm_color(color))
        if width is not None:
            try:
                line.set_linewidth(float(width))
            except Exception:
                pass
        line.set_zorder(self._z["line"])

    def set_path(self, item, coords, color=None, width=None):
        """更新一条 move 折线。

        折线始终由上一层通过 ``_newLine()`` 分段，因此这里不需要再切段：
        直接整条写入，保证"一条直线"不会被误判成断点。
        """
        self.set_line(item, coords, color, width)

    def delete(self, item):
        """从画布删除图元（``item`` 为 ``"all"`` 时清空画布）。"""
        if item == "all":
            for artist in list(self._items):
                self._erase(artist)
            self._items.clear()
            self._lines.clear()
            self._polys.clear()
            self._images.clear()
            self._texts.clear()
            self._turtle_artists.clear()
            for img in self._figure_images:
                try:
                    img.remove()
                except Exception:
                    pass
            self._figure_images.clear()
            self.request_repaint()
            return
        self._erase(item)
        self._items.discard(item)

    def _erase(self, item):
        try:
            item.remove()
        except Exception:
            try:
                item.set_visible(False)
            except Exception:
                pass

    def pointlist(self, item):
        """返回图元坐标点列表（画布坐标）。"""
        if isinstance(item, Polygon):
            return [(float(x), float(y)) for x, y in item.get_xy()]
        try:
            data = item.get_data()
        except Exception:
            return []
        return [(float(x), float(y)) for x, y in zip(data[0], data[1])]

    def item_type(self, item):
        """返回 ``"line"`` / ``"polygon"`` / ``"image"`` / ``"text"``。"""
        if isinstance(item, Polygon):
            return "polygon"
        if item in self._texts:
            return "text"
        if item in self._images:
            return "image"
        return "line"

    def set_item_color(self, item, color):
        """把图元改色（用于 turtle 的 ``_recolor``）。"""
        color = _norm_color(color)
        try:
            if isinstance(item, Polygon):
                if item.get_fill():
                    item.set_facecolor(color)
                if item.get_edgecolor() not in (None, ()):
                    item.set_edgecolor(color)
            elif item in self._texts:
                item.set_color(color)
            else:
                item.set_color(color)
        except Exception:
            pass

    # -- 多边形（填充、turtle 外形、印章） ---------------------------------

    def create_poly(self, stamp=False):
        """创建一个不可见的多边形图元（填充、印章、turtle 外形）。"""
        poly = Polygon(
            np.zeros((3, 2)), closed=True, facecolor="none", edgecolor="none"
        )
        poly.set_zorder(self._z["stamp"] if stamp else self._z["fill"])
        self.ax.add_patch(poly)
        self._polys.append(poly)
        self._items.add(poly)
        return poly

    def set_poly(
        self, item, coords, fill=None, outline=None, width=None, top=False, alpha=None
    ):
        """更新多边形的位置与颜色。"""
        if item is None:
            return
        if coords is not None:
            coords = [(float(x), float(y)) for x, y in coords]
            if len(coords) >= 3:
                item.set_xy(np.asarray(coords, dtype=float))
                item.set_visible(True)
            else:
                item.set_xy(np.zeros((3, 2)))
                item.set_visible(False)
        fill_c, fill_none = _as_color(fill)
        out_c, out_none = _as_color(outline)
        if fill is not None:
            item.set_facecolor(fill_c if not fill_none else "none")
            item.set_fill(not fill_none)
        if outline is not None:
            item.set_edgecolor(out_c if not out_none else "none")
            item.set_linewidth(1.0 if out_none or width is None else float(width))
        elif width is not None:
            item.set_linewidth(float(width))
        if alpha is not None:
            item.set_alpha(alpha)
        item.set_zorder(self._z["top"] if top else self._z["stamp"])

    # -- 文字 --------------------------------------------------------------

    def write_text(self, pos, txt, align, font, color):
        """在画布坐标 ``pos`` 处写文字。

        返回 ``(文字图元, 文字右端点的 x 坐标)``，后者供 ``write(move=True)``
        把画笔移到文字右下角。
        """
        x, y = pos
        ha = {"left": "left", "center": "center", "right": "right"}[align]

        fontname, fontsize, fontstyle = ("Arial", 8, "normal")
        if isinstance(font, (tuple, list)):
            if len(font) > 0 and font[0]:
                fontname = font[0]
            if len(font) > 1 and font[1]:
                fontsize = font[1]
            if len(font) > 2 and font[2]:
                fontstyle = font[2]
        weight = "bold" if str(fontstyle).lower() == "bold" else "normal"
        style = {
            "italic": "italic",
            "oblique": "oblique",
        }.get(str(fontstyle).lower(), "normal")

        text = self.ax.text(
            x,
            y,
            str(txt),
            ha=ha,
            va="bottom",
            color=_norm_color(color) or "black",
            fontname=str(fontname),
            fontsize=float(fontsize),
            fontweight=weight,
            fontstyle=style,
            zorder=self._z["text"],
        )
        self._texts.append(text)
        self._items.add(text)

        # 计算文字右端 x 坐标（数据坐标），失败时退化为原始位置
        try:
            renderer = self.fig.canvas.get_renderer()
            bbox = text.get_window_extent(renderer=renderer)
            x1 = self.ax.transData.inverted().transform((bbox.x1, bbox.y0))[0]
        except Exception:
            x1 = x
        return text, x1

    # -- 图片 --------------------------------------------------------------

    def create_image(self, image=None, kind="stamp"):
        """创建图片图元；``image`` 可以是路径或 numpy 数组。"""
        z = self._z.get(kind, self._z["stamp"])
        artist = self.ax.imshow(
            np.zeros((1, 1, 4), dtype=np.uint8),
            extent=(-0.5, 0.5, -0.5, 0.5),
            zorder=z,
            interpolation="nearest",
        )
        artist.set_visible(False)
        self._images.append(artist)
        self._items.add(artist)
        if kind == "turtle":
            self._turtle_artists.append(artist)
        if image is not None:
            self.set_image(artist, (0, 0), image)
        return artist

    def set_image(self, item, pos, image):
        """把图片放到画布坐标 ``pos``（图片中心）。"""
        if item is None:
            return
        array = image
        if isinstance(image, str):
            array = load_image_array(image) if image else None
        if array is None:
            item.set_visible(False)
            return
        array = np.asarray(array)
        height, width = array.shape[0], array.shape[1]
        x, y = pos
        item.set_data(array)
        item.set_extent(
            (x - width / 2.0, x + width / 2.0, y - height / 2.0, y + height / 2.0)
        )
        item.set_visible(True)

    def destroy_image(self, item):
        self._erase(item)
        self._items.discard(item)
        if item in self._turtle_artists:
            self._turtle_artists.remove(item)

    def set_background_image(self, image, canvwidth=None, canvheight=None):
        """设置背景图（铺满整块画布并置于最底层）。"""
        array = load_image_array(image) if isinstance(image, str) else image
        if array is None:
            return False
        w = float(canvwidth if canvwidth is not None else self.canvwidth)
        h = float(canvheight if canvheight is not None else self.canvheight)
        bg = self.ax.imshow(
            np.asarray(array),
            extent=(-w / 2.0, w / 2.0, -h / 2.0, h / 2.0),
            zorder=self._z["bg"],
            interpolation="nearest",
            aspect="auto",
        )
        self._figure_images.append(bg)
        self.request_repaint()
        return True

    def clear_background_image(self):
        for img in self._figure_images:
            try:
                img.remove()
            except Exception:
                pass
        self._figure_images.clear()
        self.request_repaint()

    # -- turtle 外形 -------------------------------------------------------

    def create_turtle(self, kind="polygon"):
        """为一只 turtle 创建外形图元。

        ``kind`` 为 ``"polygon"``/``"compound"`` 时返回可任意旋转的
        ``Polygon``；为 ``"image"`` 时返回可平移的图片图元。
        """
        if kind == "image":
            return self.create_image(kind="turtle")
        poly = Polygon(
            np.zeros((3, 2)),
            closed=True,
            facecolor="none",
            edgecolor="black",
            linewidth=1.0,
            zorder=self._z["turtle"],
        )
        self.ax.add_patch(poly)
        self._turtle_artists.append(poly)
        return poly

    def set_turtle(
        self, item, coords, fill=None, outline=None, width=None, visible=True, alpha=None
    ):
        """更新 turtle 外形的位置、颜色与可见性。"""
        if item is None:
            return
        if isinstance(item, Polygon):
            self.set_poly(
                item, coords, fill=fill, outline=outline, width=width, alpha=alpha
            )
            item.set_zorder(self._z["turtle"])
            if not visible:
                item.set_visible(False)
        else:
            # 图片外形：coords 只有一个中心点
            if coords:
                pos = coords[0] if isinstance(coords[0], (tuple, list)) else coords
                image = None
                try:
                    image = item.get_array()
                except Exception:
                    image = None
                if image is not None:
                    height, width = image.shape[0], image.shape[1]
                    x, y = pos
                    item.set_extent(
                        (
                            x - width / 2.0,
                            x + width / 2.0,
                            y - height / 2.0,
                            y + height / 2.0,
                        )
                    )
            item.set_visible(bool(visible))

    def delete_turtle(self, item):
        self._erase(item)
        if item in self._turtle_artists:
            self._turtle_artists.remove(item)

    # -- 坐标范围 ----------------------------------------------------------

    def set_scroll_region(self, x1, y1, x2, y2):
        """设置可视坐标范围（世界坐标模式的实现基础）。"""
        limit = 1e8
        try:
            xa, xb = sorted((_clamp(x1, limit), _clamp(x2, limit)))
            ya, yb = sorted((_clamp(y1, limit), _clamp(y2, limit)))
            if xa == xb or ya == yb:
                return
            self.ax.set_xlim(xa, xb)
            self.ax.set_ylim(ya, yb)
        except Exception:
            pass

    def get_scroll_region(self):
        x1, x2 = self.ax.get_xlim()
        y1, y2 = self.ax.get_ylim()
        return x1, y1, x2, y2

    def rescale(self, xfactor, yfactor):
        """按比例缩放画布上所有图元（世界坐标切换时使用）。"""
        for artist in list(self._items):
            try:
                if isinstance(artist, Polygon):
                    xy = artist.get_xy()
                    artist.set_xy(xy * np.asarray([xfactor, yfactor]))
                elif artist in self._images:
                    continue
                else:
                    data = artist.get_data()
                    if len(data) >= 2 and len(data[0]):
                        artist.set_data(
                            np.asarray(data[0]) * xfactor, np.asarray(data[1]) * yfactor
                        )
            except Exception:
                continue
        for artist in self._turtle_artists:
            try:
                xy = artist.get_xy()
                artist.set_xy(xy * np.asarray([xfactor, yfactor]))
            except Exception:
                continue

    # -- 事件与定时器 ------------------------------------------------------

    def bind_mouse(self, handler):
        """绑定鼠标事件，返回连接 id 列表。"""
        ids = []
        for name in ("button_press_event", "button_release_event", "motion_notify_event"):
            ids.append(self.fig.canvas.mpl_connect(name, handler))
        return ids

    def bind_key(self, handler):
        ids = [
            self.fig.canvas.mpl_connect("key_press_event", handler),
            self.fig.canvas.mpl_connect("key_release_event", handler),
        ]
        return ids

    def focus(self):
        """把键盘焦点交给图形窗口。"""
        try:
            manager = self.fig.canvas.manager
            window = getattr(manager, "window", None)
            if window is not None and hasattr(window, "focus_force"):
                window.focus_force()
        except Exception:
            pass

    def after(self, delay_ms, func):
        """``delay_ms`` 毫秒后调用 ``func``（等价于 Tk 的 ``after``）。

        能拿到 GUI 主循环时交给图形后端，否则放进内部队列，
        由 ``process_timers()``（在 ``mainloop`` 或显式 ``update()`` 时）触发。
        """
        if self._closed:
            return None
        delay_ms = max(0, int(delay_ms))
        timer = self._gui_timer(delay_ms, func)
        if timer is not None:
            return timer
        self._timer_seq += 1
        key = self._timer_seq
        self._timers[key] = (time.monotonic() + delay_ms / 1000.0, func)
        return key

    def _gui_timer(self, delay_ms, func):
        """只有真正的交互式后端才把定时器交给 matplotlib 事件循环。

        Agg/inline 等后端也提供 ``new_timer()``，但定时器永远不会触发，
        所以这类后端必须走内部队列。
        """
        if not _is_gui_backend(self.fig):
            return None
        canvas = self.fig.canvas
        new_timer = getattr(canvas, "new_timer", None)
        if new_timer is None:
            return None
        try:
            # matplotlib 的 TimerBase 要求每个回调是 (func, args, kwargs) 三元组，
            # 直接传函数会在定时器触发时抛 "cannot unpack non-iterable"。
            timer = new_timer(
                interval=delay_ms, callbacks=[(lambda *a, **k: func(), (), {})]
            )
            timer.start()
            return timer
        except Exception:
            return None

    def after_idle(self, func):
        return self.after(0, func)

    def process_timers(self):
        """执行到期的定时器回调；返回还有多少未到期。"""
        if not self._timers:
            return 0
        now = time.monotonic()
        due = [key for key, (when, _) in self._timers.items() if when <= now]
        for key in due:
            entry = self._timers.pop(key, None)
            if entry is None:
                continue
            try:
                entry[1]()
            except Exception:
                if not sys.is_finalizing():  # pragma: no cover
                    raise
        return len(self._timers)

    def cancel_timers(self):
        for _, func in self._timers.values():
            del func
        self._timers.clear()

    # -- 主循环与关闭 ------------------------------------------------------

    def mainloop(self):
        """进入 matplotlib 事件循环（``plt.show()``）。

        在 Jupyter 的 inline/matplotlib-inline 后端下不会阻塞，
        动画已经逐帧画好，直接返回即可。
        """
        self.process_timers()
        if not _is_gui_backend(self.fig):
            return
        try:
            plt.show(self.fig)
        except Exception:
            try:
                plt.show()
            except Exception:
                pass

    def destroy(self):
        """释放画布资源；只有当图形窗口由本画布创建时才关闭它。"""
        self.cancel_timers()
        self.delete("all")
        if self._closed:
            return
        self._closed = True
        try:
            self._screen = None
        except Exception:
            pass
        if self._owns_figure:
            try:
                plt.close(self.fig)
            except Exception:
                pass


# ---------------------------------------------------------------------------
# 内部小工具
# ---------------------------------------------------------------------------

_AXES_LOCKS = {}


def _threading_lock():
    import threading

    return threading.RLock()


__all__ = [
    "MovePainter",
    "split_path",
    "load_image_array",
]

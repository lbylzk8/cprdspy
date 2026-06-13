"""Generate example images for README.md — each module in its own figure."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import sys, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, "..")
from cprdspy.CPR_matplotlib import *

OUT = "images"
os.makedirs(OUT, exist_ok=True)

# ── 1. Flowers (2x3 subplots) ──
fig, axes = plt.subplots(2, 3, figsize=(14, 9))
plt.subplots_adjust(wspace=0.05, hspace=0.05)
for ax in axes.flat: plt.sca(ax); ax.axis("off")

plt.sca(axes[0, 0]); flowers(1, 1, 4, color="#e74c3c"); axes[0, 0].set_title("flowers", fontsize=11)
plt.sca(axes[0, 1]); oval_flower_a(1, 0.6, 0.3, 6, color="#3498db"); axes[0, 1].set_title("oval_flower_a", fontsize=11)
plt.sca(axes[0, 2]); flower_petal(R=1, r=0.8, n=5, rotation=30, color="#2ecc71", plot_center=True); axes[0, 2].set_title("flower_petal", fontsize=11)
plt.sca(axes[1, 0]); flowers(1, 0.6, 6, color="#f39c12"); axes[1, 0].set_title("flowers (r=0.6)", fontsize=11)
plt.sca(axes[1, 1]); oval_flower(1, 0.6, 0.3, 6, color="#9b59b6"); axes[1, 1].set_title("oval_flower", fontsize=11)
plt.sca(axes[1, 2]); oval_petal(1.5, 0.7, 0.3, color="#e67e22"); axes[1, 2].set_title("oval_petal", fontsize=11)
plt.savefig(f"{OUT}/flowers.png", dpi=130, bbox_inches="tight")
plt.close()

# ── 2. Circles (2x3) ──
fig, axes = plt.subplots(2, 3, figsize=(14, 9))
plt.subplots_adjust(wspace=0.25, hspace=0.25)
plt.sca(axes[0, 0]); circle(1, color="#e74c3c"); circle(1.5, color="#3498db"); axes[0, 0].set_title("circle")
plt.sca(axes[0, 1]); concentric_circles(n=3, radius=0.8, param=0.5, mode="arithmetic", color="#2ecc71"); axes[0, 1].set_title("concentric_circles")
plt.sca(axes[0, 2]); concentric_ellipse(n=4, a=1.5, b=0.6, param=0.4, color="#f39c12"); axes[0, 2].set_title("concentric_ellipse")
plt.sca(axes[1, 0]); circle_p((0, 0), (1, 0), color="#e74c3c"); circle_p((0, 0), (0, 1.5), color="#3498db"); axes[1, 0].set_title("circle_p")
plt.sca(axes[1, 1]); ellipse(1.5, 0.8, rotation=30, color="#9b59b6"); axes[1, 1].set_title("ellipse")
plt.sca(axes[1, 2]); draw_circle(1, color="#e67e22"); draw_circle(0.5, color="#1abc9c"); axes[1, 2].set_title("draw_circle")
plt.savefig(f"{OUT}/circles.png", dpi=130, bbox_inches="tight")
plt.close()

# ── 3. Arcs (2x3) ──
fig, axes = plt.subplots(2, 3, figsize=(14, 9))
plt.subplots_adjust(wspace=0.25, hspace=0.25)
plt.sca(axes[0, 0]); arc(1, 30, 180, color="#e74c3c"); axes[0, 0].set_title("arc (30→180)")
plt.sca(axes[0, 1]); arc_inverse(1, 30, 180, color="#3498db"); axes[0, 1].set_title("arc_inverse")
plt.sca(axes[0, 2]); arc_point(point1=(1, 0), point2=(0, 1), color="#2ecc71"); axes[0, 2].set_title("arc_point")
plt.sca(axes[1, 0]); oval_arc(2, 1, 0, 180, angle=30, color="#f39c12"); axes[1, 0].set_title("oval_arc")
plt.sca(axes[1, 1]); arc_dot(1, 0, 360, points=12, color="#9b59b6", marker="o"); axes[1, 1].set_title("arc_dot (12 pts)")
plt.sca(axes[1, 2])
for i in range(8):
    arc_rotate(center=(0, 0), angle1=30, angle2=150, rotation=i*45, color="#e67e22", linewidth=2)
axes[1, 2].set_title("arc_rotate x8")
plt.savefig(f"{OUT}/arcs.png", dpi=130, bbox_inches="tight")
plt.close()

# ── 4. Spirals (2x3) ──
fig, axes = plt.subplots(2, 3, figsize=(14, 9))
plt.subplots_adjust(wspace=0.2, hspace=0.3)
for ax in axes.flat: plt.sca(ax); ax.axis("off")

plt.sca(axes[0, 0]); logSpiral(4, 1, 1, 1, color="#e74c3c"); axes[0, 0].set_title("logSpiral", fontsize=11)
plt.sca(axes[0, 1]); nSpiral(4, 1, 4, 1, color="#3498db"); axes[0, 1].set_title("nSpiral", fontsize=11)
plt.sca(axes[0, 2]); nSpirals(5, 4, 1.5, color="#2ecc71"); axes[0, 2].set_title("nSpirals", fontsize=11)
plt.sca(axes[1, 0]); calla_petal(4, 1, 1.25, color="#f39c12"); axes[1, 0].set_title("calla_petal", fontsize=11)
plt.sca(axes[1, 1]); calla(4, 1, 1.25, 12, colors=["#9b59b6"]*12)
axes[1, 1].set_title("calla", fontsize=11)
plt.sca(axes[1, 2])
for i in range(8):
    logSpiral(3, 1, 1, 0.3, theta=i*45, color="#e67e22")
axes[1, 2].set_title("logSpiral x8 rotated", fontsize=11)
plt.savefig(f"{OUT}/spirals.png", dpi=130, bbox_inches="tight")
plt.close()

# ── 5. Waves (2x2) ──
fig, axes = plt.subplots(2, 2, figsize=(11, 11))
plt.subplots_adjust(wspace=0.1, hspace=0.1)
plt.sca(axes[0, 0]); wave_ari(A=0.2, F=4, P=12, color="#e74c3c", show_center=False); axes[0, 0].set_title("wave_ari")
plt.sca(axes[0, 1]); wave_geo(A=0.15, F=4, P=12, color="#3498db", show_center=False); axes[0, 1].set_title("wave_geo")
plt.sca(axes[1, 0]); wave(A=0.2, F=4, P=12, color="#2ecc71", show_center=False); axes[1, 0].set_title("wave")
plt.sca(axes[1, 1]); wave_wave(A=0.15, F=4, P=12, color="#f39c12", show_center=False); axes[1, 1].set_title("wave_wave")
plt.savefig(f"{OUT}/waves.png", dpi=130, bbox_inches="tight")
plt.close()

# ── 6. Stars (1x3) ──
fig, axes = plt.subplots(1, 3, figsize=(14, 5))
plt.subplots_adjust(wspace=0.0)
for ax in axes: plt.sca(ax); ax.axis("off")

plt.sca(axes[0]); star(1, 1, 6, 12, color="#e74c3c"); axes[0].set_title("star (n=6, N=12)")
plt.sca(axes[1]); stars(1, 1, 5, ratio=1.3, M=3, N=12, color="#3498db"); axes[1].set_title("stars")
plt.sca(axes[2]); stars(1, 1, 7, ratio=1.2, M=5, N=14, color="#2ecc71"); axes[2].set_title("stars (M=5)")
plt.savefig(f"{OUT}/stars.png", dpi=130, bbox_inches="tight")
plt.close()

# ── 7. Dots (2x3) ──
fig, axes = plt.subplots(2, 3, figsize=(14, 9))
plt.subplots_adjust(wspace=0.25, hspace=0.25)
plt.sca(axes[0, 0]); draw_dots(n_dots(3, 1), color="#e74c3c"); axes[0, 0].set_title("n_dots (n=3)")
plt.sca(axes[0, 1]); draw_dots(n_dots(4, 1) + n_dots(6, 1.5) + n_dots(12, 2), color="#3498db"); axes[0, 1].set_title("Dots + (concatenate)")
plt.sca(axes[0, 2]); draw_dots(n_dots(4, 1, shape="ellipse", a=1.5, b=0.6), color="#2ecc71"); axes[0, 2].set_title("n_dots (ellipse)")
plt.sca(axes[1, 0]); draw_n_dots_array(6, 3, 1, color="#f39c12"); axes[1, 0].set_title("draw_n_dots_array")
plt.sca(axes[1, 1]); draw_dots(n_dots(12, 1), color="#9b59b6"); draw_dots(n_dots(12, 2.5), color="#e67e22"); axes[1, 1].set_title("multi-layer dots")
plt.sca(axes[1, 2]); draw_dots(n_dots(24, 1) + n_dots(24, 1.5) + n_dots(24, 2), color="#1abc9c"); axes[1, 2].set_title("concentric dots")
plt.savefig(f"{OUT}/dots.png", dpi=130, bbox_inches="tight")
plt.close()

# ── 8. Lines (2x3) ──
fig, axes = plt.subplots(2, 3, figsize=(14, 9))
plt.subplots_adjust(wspace=0.15, hspace=0.25)
for ax in axes.flat: plt.sca(ax); ax.axis("off")

plt.sca(axes[0, 0]); draw_lines(connect(n_dots(6, 1), closed=True), color="#e74c3c"); axes[0, 0].set_title("connect (hexagon)", fontsize=11)
plt.sca(axes[0, 1]); draw_lines(connect_all(n_dots(8, 1)), color="#3498db", alpha=0.6, linewidth=1); axes[0, 1].set_title("connect_all", fontsize=11)
plt.sca(axes[0, 2]); draw_multi_polygon(4, 6, 1, color="#2ecc71"); axes[0, 2].set_title("draw_multi_polygon", fontsize=11)
plt.sca(axes[1, 0]); draw_metatron_cube(6, 3, color="#f39c12"); axes[1, 0].set_title("draw_metatron_cube", fontsize=11)
plt.sca(axes[1, 1]); draw_krystal_cube(6, 4, color="#9b59b6"); axes[1, 1].set_title("draw_krystal_cube", fontsize=11)
plt.sca(axes[1, 2]); draw_swastika(6, 1, color="#e67e22"); axes[1, 2].set_title("draw_swastika", fontsize=11)
plt.savefig(f"{OUT}/lines.png", dpi=130, bbox_inches="tight")
plt.close()

print("All images generated in docs/images/")

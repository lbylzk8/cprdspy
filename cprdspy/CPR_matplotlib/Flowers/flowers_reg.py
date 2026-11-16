import numpy as np
import matplotlib.pyplot as plt
from cprdspy.CPR_matplotlib.Flowers.flower import *


def flowers_reg(
    R=1,
    r=1,
    n=4,
    M=3,
    N=12,
    color="b",
    alpha=1,
    theta=0,
    center=(0, 0),
    points=1000,
    linestyle="-",
    linewidth=1,
    label=None,
    marker=None,
    markersize=5,
    markerfacecolor="r",
    markeredgecolor="b",
    markeredgewidth=1,
    ax=None,
):
    flowers(
        R=R,
        r=r,
        n=n,
        ratio=np.cos(np.pi / n) / np.cos(np.pi / n + np.pi / N),
        M=M,
        N=N,
        color=color,
        alpha=alpha,
        theta=theta,
        center=center,
        points=points,
        linestyle=linestyle,
        linewidth=linewidth,
        label=label,
        marker=marker,
        markersize=markersize,
        markerfacecolor=markerfacecolor,
        markeredgecolor=markeredgecolor,
        markeredgewidth=markeredgewidth,
        ax=ax,
    )


# flowers_reg(ax=plt.gca())
# plt.show()

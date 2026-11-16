"""
rotor_discontinuous_demo.py — Rotor 模块的"不连续"效果演示

问题：flower_mpl() 画的是独立花瓣（不连续），Rotor 能画吗？

答案：Rotor 组合 γ(t) = Σ r_k·e^{iω_kt} 本质是连续曲线，
但可以通过以下方式实现"不连续"效果：

1. 多段独立绘制 — 每个花瓣作为单独的 RotorComposition
2. 散点模式 — 用 marker 代替 line
3. NaN 间隔 — 在轨迹中插入 NaN 断开曲线
4. 多 Rotor 圆 — 绘制每个 Rotor 的本轮圆（本身就是离散的）
"""

import numpy as np
import matplotlib.pyplot as plt
from cprdspy.rotor import Rotor2D, RotorComposition, trace


# ============================================================
# 方法 1: 连续曲线画"花朵"
# ============================================================

def rotor_flower_continuous(n_petals=5, R=3, r=1, ax=None):
    """
    用单个 Rotor 组合画连续的花朵曲线
    
    γ(t) = R·e^{it} + r·e^{i·n·t}
    
    这是一个连续曲线，依次 traced 所有花瓣
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 8))
    
    # 外摆线：R·e^{it} + r·e^{i·n·t}
    curve = Rotor2D(R, 1) + Rotor2D(r, n_petals)
    t, x, y = trace(curve, n_points=2000)
    
    ax.plot(x, y, 'b-', lw=1.5, label=f'{curve}')
    ax.set_title(f'连续花朵 (n={n_petals})\n{curve}', fontsize=12)
    ax.axis('equal')
    ax.grid(True, alpha=0.3)
    
    return ax


# ============================================================
# 方法 2: 独立花瓣（模拟 flower_mpl）
# ============================================================

def rotor_flower_discrete(n_petals=6, R=2, r=1.5, ax=None):
    """
    每个花瓣作为独立的 Rotor，分别绘制
    
    每个花瓣 = 一个 Rotor 在有限时间范围内的轨迹
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 8))
    
    colors = plt.cm.viridis(np.linspace(0, 1, n_petals))
    
    for i in range(n_petals):
        # 每个花瓣的旋转角度
        angle = 2 * np.pi * i / n_petals
        
        # 花瓣 = 小圆在大圆上滚动
        # 用 Rotor 表示：R·e^{it} + r·e^{i·n·t}
        # 但只取一小段弧线
        petal = Rotor2D(R, 1) + Rotor2D(r, n_petals)
        
        # 只取第 i 个花瓣对应的 t 范围
        t_start = angle
        t_end = angle + 2 * np.pi / n_petals
        t = np.linspace(t_start, t_end, 200)
        
        z = petal(t)
        x, y = z.real, z.imag
        
        ax.plot(x, y, '-', color=colors[i], lw=2, 
                label=f'Petal {i+1}')
    
    ax.set_title(f'离散花瓣 (n={n_petals})\n每个花瓣独立绘制', fontsize=12)
    ax.axis('equal')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8, loc='upper right')
    
    return ax


# ============================================================
# 方法 3: 散点模式
# ============================================================

def rotor_scatter(n_points=500, ax=None):
    """
    用散点代替连续线条
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 8))
    
    curve = Rotor2D(3, 1) + Rotor2D(1, 5)
    t, x, y = trace(curve, n_points=n_points)
    
    # 用颜色映射时间
    scatter = ax.scatter(x, y, c=t, cmap='viridis', s=10, alpha=0.7)
    
    ax.set_title(f'散点模式 ({n_points} points)\n{curve}', fontsize=12)
    ax.axis('equal')
    ax.grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=ax, label='t')
    
    return ax


# ============================================================
# 方法 4: NaN 间隔断开曲线
# ============================================================

def rotor_with_gaps(n_segments=8, gap_ratio=0.2, ax=None):
    """
    在轨迹中插入 NaN，形成间断效果
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 8))
    
    curve = Rotor2D(3, 1) + Rotor2D(1, 7)
    t, x, y = trace(curve, n_points=2000)
    
    # 将轨迹分成 n_segments 段，每段之间插入 NaN
    segment_len = len(x) // n_segments
    x_gapped = []
    y_gapped = []
    
    for i in range(n_segments):
        start = i * segment_len
        end = start + int(segment_len * (1 - gap_ratio))
        x_gapped.extend(x[start:end])
        y_gapped.extend(y[start:end])
        # 插入 NaN
        x_gapped.append(np.nan)
        y_gapped.append(np.nan)
    
    ax.plot(x_gapped, y_gapped, 'r-', lw=1.5)
    ax.set_title(f'NaN 间隔 ({n_segments} segments, gap={gap_ratio})', fontsize=12)
    ax.axis('equal')
    ax.grid(True, alpha=0.3)
    
    return ax


# ============================================================
# 方法 5: 绘制 Rotor 的本轮圆（离散圆）
# ============================================================

def rotor_circles(ax=None):
    """
    绘制每个 Rotor 的本轮圆（本身就是离散的）
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 10))
    
    # 三个 Rotor
    rotors = [
        Rotor2D(5, 1),
        Rotor2D(3, -2),
        Rotor2D(1, 5),
    ]
    
    colors = ['red', 'green', 'blue']
    
    # 绘制每个 Rotor 的圆
    pos = 0 + 0j
    for i, (rotor, color) in enumerate(zip(rotors, colors)):
        # 本轮圆
        theta = np.linspace(0, 2*np.pi, 200)
        circle_x = pos.real + rotor.radius * np.cos(theta)
        circle_y = pos.imag + rotor.radius * np.sin(theta)
        
        ax.plot(circle_x, circle_y, '--', color=color, lw=1, alpha=0.5,
                label=f'R{i+1}: r={rotor.radius}, ω={rotor.frequency}')
        
        # 当前位置（t=1）
        z = rotor.evaluate(1.0)
        ax.plot([pos.real, pos.real + z.real], 
                [pos.imag, pos.imag + z.imag],
                '-', color=color, lw=2)
        
        pos += z
    
    # 末端点
    ax.plot(pos.real, pos.imag, 'ko', ms=8, label='P(t=1)')
    
    ax.set_title('Rotor 本轮圆（离散圆）', fontsize=14)
    ax.axis('equal')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9)
    
    return ax


# ============================================================
# 方法 6: 花瓣的 Rotor 近似（圆弧）
# ============================================================

def rotor_petal_arc(R=2, r=1.5, petal_angle=0, n_points=100, ax=None):
    """
    用单个 Rotor 画一段圆弧（花瓣的一半）
    
    花瓣 = 两段圆弧
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 8))
    
    # 花瓣的一段弧 = 一个 Rotor 在有限时间范围
    rotor = Rotor2D(r, 3, petal_angle)
    
    # 只取 1/3 周期（一段弧）
    t = np.linspace(0, 2*np.pi/3, n_points)
    z = rotor(t)
    x, y = z.real, z.imag
    
    ax.plot(x, y, 'g-', lw=2)
    ax.plot(x[0], y[0], 'go', ms=8)
    ax.plot(x[-1], y[-1], 'rs', ms=8)
    
    ax.set_title(f'Rotor 圆弧\nR(r={r}, ω=3, φ={petal_angle:.2f})')
    ax.axis('equal')
    ax.grid(True, alpha=0.3)
    
    return ax


# ============================================================
# 主程序：对比所有方法
# ============================================================

if __name__ == '__main__':
    fig = plt.figure(figsize=(16, 12))
    
    # 1. 连续花朵
    ax1 = fig.add_subplot(2, 3, 1)
    rotor_flower_continuous(n_petals=5, R=3, r=1, ax=ax1)
    
    # 2. 离散花瓣
    ax2 = fig.add_subplot(2, 3, 2)
    rotor_flower_discrete(n_petals=6, R=2, r=1.5, ax=ax2)
    
    # 3. 散点模式
    ax3 = fig.add_subplot(2, 3, 3)
    rotor_scatter(n_points=300, ax=ax3)
    
    # 4. NaN 间隔
    ax4 = fig.add_subplot(2, 3, 4)
    rotor_with_gaps(n_segments=10, gap_ratio=0.3, ax=ax4)
    
    # 5. 本轮圆
    ax5 = fig.add_subplot(2, 3, 5)
    rotor_circles(ax=ax5)
    
    # 6. 圆弧花瓣
    ax6 = fig.add_subplot(2, 3, 6)
    rotor_petal_arc(R=2, r=1.5, petal_angle=0, ax=ax6)
    
    plt.tight_layout()
    plt.savefig('rotor_discontinuous_demo.png', dpi=150, bbox_inches='tight')
    print('✓ Saved: rotor_discontinuous_demo.png')
    plt.close()
    
    # 单独保存每个方法
    methods = [
        ('1_continuous_flower', lambda: rotor_flower_continuous()),
        ('2_discrete_petals', lambda: rotor_flower_discrete()),
        ('3_scatter', lambda: rotor_scatter()),
        ('4_nan_gaps', lambda: rotor_with_gaps()),
        ('5_rotor_circles', lambda: rotor_circles()),
        ('6_petal_arc', lambda: rotor_petal_arc()),
    ]
    
    for name, func in methods:
        fig, ax = plt.subplots(figsize=(8, 8))
        func(ax=ax)
        fig.savefig(f'rotor_{name}.png', dpi=100, bbox_inches='tight')
        plt.close()
        print(f'✓ Saved: rotor_{name}.png')
    
    print('\n=== All demos completed ===')

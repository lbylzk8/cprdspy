# Rotor 模块：如何实现"不连续"效果

## 问题

`flower_mpl()` 画的是**独立花瓣**（不连续的圆弧），而 Rotor 组合 `γ(t) = Σ r_k·e^{iω_kt}` 本质上是**连续曲线**。

能用 Rotor 画不连续的图形吗？

## 答案

**可以**，但需要理解：
- Rotor 数学上生成的是连续曲线（复指数函数的和）
- "不连续"效果需要通过**绘图技巧**实现，而非数学本质

## 5 种实现方法

### 方法 1：连续曲线（默认行为）

```python
from cprdspy.rotor import Rotor2D, trace

# 外摆线：R·e^{it} + r·e^{i·n·t}
curve = Rotor2D(3, 1) + Rotor2D(1, 5)
t, x, y = trace(curve, n_points=2000)
plt.plot(x, y)
```

**效果**：一条连续曲线，依次 traced 所有花瓣  
**适用**：Fourier 逼近、摆线、利萨如  
**图片**：`demo_1_continuous.png`

---

### 方法 2：离散花瓣（独立绘制）

```python
n_petals = 6
for i in range(n_petals):
    angle = 2 * np.pi * i / n_petals
    petal = Rotor2D(2, 1) + Rotor2D(1.5, n_petals)
    
    # 只取每个花瓣对应的 t 范围
    t = np.linspace(angle, angle + 2*np.pi/n_petals, 200)
    z = petal(t)
    plt.plot(z.real, z.imag, '-', color=colors[i])
```

**效果**：每个花瓣作为独立曲线绘制，之间有间隙  
**适用**：模拟 `flower_mpl()` 的离散花瓣  
**图片**：`demo_2_discrete.png`

**关键**：通过**分段调用 trace()** 实现离散效果

---

### 方法 3：散点模式

```python
curve = Rotor2D(3, 1) + Rotor2D(1, 5)
t, x, y = trace(curve, n_points=500)
plt.scatter(x, y, c=t, cmap='viridis', s=10)
```

**效果**：用离散点代替连续线条  
**适用**：粒子效果、点云可视化  
**图片**：`demo_3_scatter.png`

**关键**：用 `scatter()` 代替 `plot()`

---

### 方法 4：NaN 间隔

```python
curve = Rotor2D(3, 1) + Rotor2D(1, 7)
t, x, y = trace(curve, n_points=2000)

# 将轨迹分成 10 段，每段之间插入 NaN
n_segments = 10
gap_ratio = 0.3
segment_len = len(x) // n_segments
x_gapped, y_gapped = [], []

for i in range(n_segments):
    start = i * segment_len
    end = start + int(segment_len * (1 - gap_ratio))
    x_gapped.extend(x[start:end])
    y_gapped.extend(y[start:end])
    x_gapped.append(np.nan)  # 断开
    y_gapped.append(np.nan)

plt.plot(x_gapped, y_gapped)
```

**效果**：连续曲线被周期性断开  
**适用**：虚线效果、分段高亮  
**图片**：`demo_4_nan_gaps.png`

**关键**：matplotlib 遇到 NaN 会自动断开线条

---

### 方法 5：绘制 Rotor 的本轮圆

```python
rotors = [Rotor2D(5, 1), Rotor2D(3, -2), Rotor2D(1, 5)]
pos = 0 + 0j

for rotor, color in zip(rotors, colors):
    # 每个 Rotor 的圆（本身就是离散的）
    theta = np.linspace(0, 2*np.pi, 200)
    circle_x = pos.real + rotor.radius * np.cos(theta)
    circle_y = pos.imag + rotor.radius * np.sin(theta)
    plt.plot(circle_x, circle_y, '--', color=color)
    
    # 当前位置向量
    z = rotor.evaluate(1.0)
    plt.plot([pos.real, pos.real + z.real], 
             [pos.imag, pos.imag + z.imag],
             '-', color=color)
    
    pos += z  # 下一个 Rotor 的起点
```

**效果**：展示每个 Rotor 的独立圆（本轮）  
**适用**：教学演示、几何理解  
**图片**：`demo_5_circles.png`

**关键**：每个 Rotor 的圆本身就是独立的几何对象

---

## 对比总结

| 方法 | 数学本质 | 绘图技巧 | 适用场景 |
|------|---------|---------|---------|
| 1. 连续曲线 | 连续 | 直接 plot | Fourier、摆线 |
| 2. 离散花瓣 | 连续 | 分段 plot | 模拟 flower_mpl |
| 3. 散点 | 连续 | scatter | 粒子、点云 |
| 4. NaN 间隔 | 连续 | 插入 NaN | 虚线、分段 |
| 5. 本轮圆 | 离散 | 独立绘制 | 教学、几何 |

---

## 核心思想

**Rotor 数学上是连续的，但绘图可以是离散的。**

要实现 `flower_mpl()` 的效果，关键是：
1. 理解每个花瓣对应 Rotor 的**一段 t 范围**
2. 用**循环**分别绘制每个花瓣
3. 或者用**散点/NaN**等绘图技巧

---

## 完整代码示例

见 `rotor_discontinuous_demo.py`

运行：
```bash
python cprdspy/rotor/rotor_discontinuous_demo.py
```

生成的图片：
- `demo_1_continuous.png`
- `demo_2_discrete.png`
- `demo_3_scatter.png`
- `demo_4_nan_gaps.png`
- `demo_5_circles.png`

---

## 未来扩展

如果需要更强大的"不连续"支持，可以考虑：

1. **RotorComposition 支持分段**：
   ```python
   curve = Rotor2D(3, 1).segment(0, np.pi) + Rotor2D(1, 5).segment(np.pi, 2*np.pi)
   ```

2. **离散 Rotor 集合**：
   ```python
   petals = [Rotor2D(1, k) for k in range(1, 6)]
   draw_discrete(petals, gap=0.1)
   ```

3. **混合模式**：
   ```python
   curve = Rotor2D(3, 1) + Rotor2D(1, 5, mode='scatter')
   ```

这些需要在 API 层面扩展，目前可以通过绘图技巧实现。

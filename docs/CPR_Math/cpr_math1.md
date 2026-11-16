# 环面及环面螺旋线
## 环面方程
直角坐标：$\boldsymbol{(x^2+y^2+z^2+R^2-r^2)^2=4R^2(x^2+y^2)}$ 或 $\boldsymbol{(R-\sqrt{x^2+y^2})^2+z^2=r^2}$
参数方程：
$$
\begin{cases}
x=(R+r\cos v)\cos u\\
y=(R+r\cos v)\sin u\\
z=r\sin v
\end{cases}\quad u,v\in[0,2\pi]
$$
环面表面积：$\boldsymbol{S=(2\pi r)(2\pi R)=4\pi^2Rr}$
环面体积：$\boldsymbol{V=(\pi r^2)(2\pi R)=2\pi^2Rr^2}$

**GeoGebra 验证（3D 绘图区）：**
```geogebra
R = 2
r = 1
环面 = Surface((R + r cos(v)) cos(u), (R + r cos(v)) sin(u), r sin(v), u, 0, 2π, v, 0, 2π)
```

**Python 验证（matplotlib）：**
```python
import numpy as np
import matplotlib.pyplot as plt

R, r = 2, 1
u = np.linspace(0, 2 * np.pi, 80)
v = np.linspace(0, 2 * np.pi, 40)
u, v = np.meshgrid(u, v)

x = (R + r * np.cos(v)) * np.cos(u)
y = (R + r * np.cos(v)) * np.sin(u)
z = r * np.sin(v)

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(x, y, z, cmap='viridis', alpha=0.85, edgecolor='none')
ax.set_xlabel('x'); ax.set_ylabel('y'); ax.set_zlabel('z')
ax.set_title(f'Torus: R={R}, r={r}')
ax.set_box_aspect([1, 1, 1])
plt.show()
```

## 环面螺旋线（单螺设定）
参数方程：
右旋
$$
\begin{cases}
x=(R+r\cos\omega t)\cos t\\
y=(R+r\cos\omega t)\sin t\\
z=r\sin\omega t
\end{cases}
$$
左旋
$$
\begin{cases}
x=(R-r\cos\omega t)\cos t\\
y=(R-r\cos\omega t)\sin t\\
z=r\sin\omega t
\end{cases}\quad t\in[0,2\pi]
$$

**GeoGebra 验证（3D 绘图区）：**
```geogebra
R = 2
r = 1
ω = 12
右旋 = Curve((R + r cos(ω t)) cos(t), (R + r cos(ω t)) sin(t),  r sin(ω t), t, 0, 2π)
左旋 = Curve((R - r cos(ω t)) cos(t), (R - r cos(ω t)) sin(t), r sin(ω t), t, 0, 2π)
```
可调整 `R`、`r`、`ω` 滑块观察不同参数下的左右旋螺旋线。

**Python 验证：**
```python
import numpy as np
import matplotlib.pyplot as plt

R, r, ω = 2, 1, 12
t = np.linspace(0, 2 * np.pi, 2000)

# 右旋
xR = (R + r * np.cos(ω * t)) * np.cos(t)
yR = (R + r * np.cos(ω * t)) * np.sin(t)
zR = r * np.sin(ω * t)

# 左旋 (R - r cos ωt 版本：从小圆内侧起点出发)
xL = (R - r * np.cos(ω * t)) * np.cos(t)
yL = (R - r * np.cos(ω * t)) * np.sin(t)
zL = r * np.sin(ω * t)

fig = plt.figure(figsize=(14, 6))
ax1 = fig.add_subplot(121, projection='3d')
ax1.plot(xR, yR, zR, lw=0.6, color='red')
ax1.set_title(f'右旋 (R={R}, r={r}, ω={ω})')
ax1.set_box_aspect([1, 1, 1])

ax2 = fig.add_subplot(122, projection='3d')
ax2.plot(xL, yL, zL, lw=0.6, color='blue')
ax2.set_title(f'左旋 (R={R}, r={r}, ω={ω})')
ax2.set_box_aspect([1, 1, 1])
plt.show()
```

## 环形螺旋线(Circular Helix) 一般方程
$$
\begin{cases}
x=(R+r\cos\omega t)\cos \phi t\\
y=(R+r\cos\omega t)\sin \phi t\\
z=r\sin\omega t+at
\end{cases}\quad t\in \mathbb{R}
$$

**GeoGebra 验证（3D 绘图区，含轴向漂移）：**
```geogebra
R = 2
r = 1
ω = 12
φ = 13
a = 0.05
广义螺旋线 = Curve((R + r cos(ω t)) cos(φ t), (R + r cos(ω t)) sin(φ t), r sin(ω t) + a t, t, 0, 4π)
```

**Python 验证（对比不同参数）：**
```python
import numpy as np
import matplotlib.pyplot as plt

R, r, ω, φ = 2, 1, 12, 13
t = np.linspace(0, 4 * np.pi, 3000)

fig = plt.figure(figsize=(16, 5))
configs = [(12, 13, 0, 'ω=12, φ=13, a=0 (纯环面)'),
            (12, 13, 0.05, 'ω=12, φ=13, a=0.05 (轴向漂移)'),
            (5, 7, 0, 'ω=5, φ=7, a=0 (不同缠绕)')]
for i, (w, p, a, title) in enumerate(configs):
    ax = fig.add_subplot(1, 3, i+1, projection='3d')
    x = (R + r * np.cos(w * t)) * np.cos(p * t)
    y = (R + r * np.cos(w * t)) * np.sin(p * t)
    z = r * np.sin(w * t) + a * t
    ax.plot(x, y, z, lw=0.5)
    ax.set_title(title); ax.set_box_aspect([1, 1, 1])
plt.show()
```

## 罗丹线圈标准数学形式
$$
\begin{cases}
x(t)=(2+\cos(12t))\cos(13t)\\
y(t)=(2+\cos(12t))\sin(13t)\\
z(t)=\sin(12t)
\end{cases}\quad t\in[0,2\pi]
$$

**GeoGebra 验证：**
```geogebra
罗丹线圈 = Curve((2 + cos(12 t)) cos(13 t), (2 + cos(12 t)) sin(13 t), sin(12 t), t, 0, 2π)
```

**Python 验证：**
```python
import numpy as np
import matplotlib.pyplot as plt

t = np.linspace(0, 2 * np.pi, 2000)
x = (2 + np.cos(12 * t)) * np.cos(13 * t)
y = (2 + np.cos(12 * t)) * np.sin(13 * t)
z = np.sin(12 * t)

fig = plt.figure(figsize=(9, 8))
ax = fig.add_subplot(111, projection='3d')
ax.plot(x, y, z, lw=0.5, color='darkorange')
ax.set_title('罗丹线圈: (2+cos12t)cos13t, (2+cos12t)sin13t, sin12t')
ax.set_box_aspect([1, 1, 1])
plt.show()
```

## 摆线
### 直摆线
$$
\begin{cases}
x=r(t-\sin t)\\
y=r(1-\cos t)
\end{cases}
$$

**GeoGebra 验证：**
```geogebra
r = 1
n = 3
直摆线 = Curve(r (t - sin(t)), r (1 - cos(t)), t, 0, 2n π)
```

**Python 验证：**
```python
import numpy as np
import matplotlib.pyplot as plt

r, n = 1, 3
t = np.linspace(0, 2 * n * np.pi, 1000)
x = r * (t - np.sin(t))
y = r * (1 - np.cos(t))

plt.figure(figsize=(12, 3))
plt.plot(x, y, 'b', lw=1)
plt.title(f'Cycloid: r={r}, {n} arches'); plt.axis('equal')
plt.show()
```

**中心摆线(Centered Trochoid)一般方程**
$$
\begin{cases}
x=r_1\cos(\omega_1 t)+r_2\cos(\omega_2 t)\\
y=r_1\sin(\omega_1 t)+r_2\sin(\omega_2 t)
\end{cases}\quad f(t)=r_1e^{j\omega_1 t}+r_2e^{j\omega_2 t},\ r_1,r_2,\omega_1,\omega_2\neq0,\omega_1\neq\omega_2
$$

**GeoGebra 验证：**
```geogebra
r1 = 2;  ω1 = 3
r2 = 1;  ω2 = 5
中心摆线 = Curve(r1 cos(ω1 t) + r2 cos(ω2 t), r1 sin(ω1 t) + r2 sin(ω2 t), t, 0, 2π)
```

**Python 验证：**
```python
import numpy as np
import matplotlib.pyplot as plt

r1, ω1, r2, ω2 = 2, 3, 1, 5
t = np.linspace(0, 2 * np.pi, 2000)
x = r1 * np.cos(ω1 * t) + r2 * np.cos(ω2 * t)
y = r1 * np.sin(ω1 * t) + r2 * np.sin(ω2 * t)

plt.figure(figsize=(7, 7))
plt.plot(x, y, 'purple', lw=0.8)
plt.title(f'Centered Trochoid: r₁={r1}, ω₁={ω1}, r₂={r2}, ω₂={ω2}')
plt.axis('equal'); plt.show()
```
### 圆内摆线
$$
\begin{cases}
x=(R-r)\cos t+h\cos\left(\frac{R-r}{r}t\right)\\
y=(R-r)\sin t-h\sin\left(\frac{R-r}{r}t\right)
\end{cases}
$$
极坐标方程：$\boldsymbol{\rho^2=x^2+y^2=(R-r)^2+h^2+2(R-r)h\cos\left(\frac{R}{r}t\right)}$

**GeoGebra 验证：**
```geogebra
R = 5;  r = 2;  h = 1.5
圆内摆线 = Curve((R - r) cos(t) + h cos((R - r) / r t), (R - r) sin(t) - h sin((R - r) / r t), t, 0, 2r π)
```

**Python 验证（h=r 即标准内摆线 vs h<r 短摆线 vs h>r 长摆线）：**
```python
import numpy as np
import matplotlib.pyplot as plt

R, r = 5, 2
t = np.linspace(0, 2 * r * np.pi, 2000)

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for ax, h, label in zip(axes, [1.0, 2.0, 3.0],
                         ['h<r (Curtate hypocycloid)', 'h=r (Hypocycloid)', 'h>r (Prolate hypocycloid)']):
    x = (R - r) * np.cos(t) + h * np.cos((R - r) / r * t)
    y = (R - r) * np.sin(t) - h * np.sin((R - r) / r * t)
    ax.plot(x, y, lw=0.6)
    ax.set_title(f'{label}\nR={R}, r={r}, h={h}')
    ax.axis('equal')
plt.tight_layout(); plt.show()
```
### 圆外摆线
$$
\begin{cases}
x=(R+r)\cos t-h\cos\left(\frac{R+r}{r}t\right)\\
y=(R+r)\sin t-h\sin\left(\frac{R+r}{r}t\right)
\end{cases}
$$
极坐标方程：$\boldsymbol{\rho^2=x^2+y^2=(R+r)^2+h^2-2(R+r)h\cos\frac{R}{r}t}$

**GeoGebra 验证：**
```geogebra
R = 4;  r = 1;  h = 1
圆外摆线 = Curve((R + r) cos(t) - h cos((R + r) / r t), (R + r) sin(t) - h sin((R + r) / r t), t, 0, 2r π)
```

**Python 验证（h=r 标准外摆线 vs h<r vs h>r）：**
```python
import numpy as np
import matplotlib.pyplot as plt

R, r = 4, 1
t = np.linspace(0, 2 * r * np.pi, 2000)

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for ax, h, label in zip(axes, [0.5, 1.0, 2.0],
                         ['h<r (Curtate epicycloid)', 'h=r (Epicycloid)', 'h>r (Prolate epicycloid)']):
    x = (R + r) * np.cos(t) - h * np.cos((R + r) / r * t)
    y = (R + r) * np.sin(t) - h * np.sin((R + r) / r * t)
    ax.plot(x, y, lw=0.6)
    ax.set_title(f'{label}\nR={R}, r={r}, h={h}')
    ax.axis('equal')
plt.tight_layout(); plt.show()
```

---

# 摆线公式推导
## 外摆线（动点$P$的轨迹）
![alt text](./images/image-1.png)
几何关系：
$$
\begin{cases}
l_R=l_r\\
l_R=\theta R,\ l_r=\alpha r \Rightarrow \theta R=\alpha r \Rightarrow \alpha=\frac{R}{r}\theta\\
\text{令}\ \frac{R}{r}=n,\ \alpha=n\theta
\end{cases}
$$
参数方程：
$$
\begin{cases}
x=(R+r)\cos\theta-r\cos(\theta+\alpha)=(R+r)\cos\theta-r\cos\left(\frac{R+r}{r}\theta\right)=(R+r)\cos\theta-r\cos(n+1)\theta\\
y=(R+r)\sin\theta-r\sin(\theta+\alpha)=(R+r)\sin\theta-r\sin\left(\frac{R+r}{r}\theta\right)=(R+r)\sin\theta-r\sin(n+1)\theta
\end{cases}
$$

## 内摆线

![alt text](./images/image-2.png)
$\varphi=\frac{R-r}{r}\theta,\ \varphi r=(R-r)\theta$
几何：
$$
\begin{cases}
l_R=l_r\\
l_R=\theta R,\ l_r=\alpha r \Rightarrow \theta R=\alpha r\Rightarrow \alpha=\frac{R}{r}\theta
\end{cases}
$$
参数方程：
$$
\begin{cases}
x=(R-r)\cos\theta+r\cos(\alpha-\theta)=(R-r)\cos\theta+r\cos\left(\frac{R-r}{r}\theta\right)=(R-r)\cos\theta+r\cos(n-1)\theta\\
y=(R-r)\sin\theta-r\sin(\alpha-\theta)=(R-r)\sin\theta-r\sin\left(\frac{R-r}{r}\theta\right)=(R-r)\sin\theta-r\sin(n-1)\theta
\end{cases}
$$

---

## 短摆线：$P$点不取$r$上，而取半径$\boldsymbol{h<r}$的$O_r$同心圆上
### 外短摆线
$$
\begin{cases}
x=(R+r)\cos\theta-h\cos(\theta+\alpha)=(R+r)\cos\theta-h\cos\left(\frac{R+r}{r}\theta\right)=(R+r)\cos\theta-h\cos(n+1)\theta\\
y=(R+r)\sin\theta-h\sin(\theta+\alpha)=(R+r)\sin\theta-h\sin\left(\frac{R+r}{r}\theta\right)=(R+r)\sin\theta-h\sin(n+1)\theta
\end{cases}
$$
### 内短摆线
$$
\begin{cases}
x=(R-r)\cos\theta+h\cos(\alpha-\theta)=(R-r)\cos\theta+h\cos\left(\frac{R-r}{r}\theta\right)=(R-r)\cos\theta+h\cos(n-1)\theta\\
y=(R-r)\sin\theta-h\sin(\alpha-\theta)=(R-r)\sin\theta-h\sin\left(\frac{R-r}{r}\theta\right)=(R-r)\sin\theta-h\sin(n-1)\theta
\end{cases}
$$
**长摆线：$P$点不取$r$上，而取半径$\boldsymbol{h>r}$的$O_r$同心圆上，方程同上**

## 变换
将大小圆半径作如下变换：
$R+r\Rightarrow R'$，即：$R'-R\Rightarrow r$，则：
外摆线：
$$
\begin{cases}
x=(R+r)\cos\theta-r\cos\left(\frac{R+r}{r}\theta\right)=R'\cos\theta-r\cos\left(\frac{R'}{r}\theta\right)=R'\cos\theta-r\cos(n'\theta)\\
y=(R+r)\sin\theta-r\sin\left(\frac{R+r}{r}\theta\right)=R'\sin\theta-r\sin\left(\frac{R'}{r}\theta\right)=R'\sin\theta-r\sin(n'\theta)
\end{cases}\quad n'=\frac{R'}{r}
$$
若 $R-r\Rightarrow R'$（此时 $R-R'=r$），则：
内摆线：
$$
\begin{cases}
x=(R-r)\cos\theta+r\cos\left(\frac{R-r}{r}\theta\right)=R'\cos\theta+r\cos\left(\frac{R'}{r}\theta\right)=R'\cos\theta+r\cos(n'\theta)\\
y=(R-r)\sin\theta-r\sin\left(\frac{R-r}{r}\theta\right)=R'\sin\theta-r\sin\left(\frac{R'}{r}\theta\right)=R'\sin\theta-r\sin(n'\theta)
\end{cases}\quad n'=\frac{R'}{r}
$$

这样，内外摆线方程就统一了，为：
$$
\begin{cases}
x=R\cos\theta+r\cos\alpha\\
y=R\sin\theta+r\sin\alpha
\end{cases}\quad \alpha=n\theta=\frac{R}{r}\theta
$$
注意到这里都是加$(+)$号，而之前的公式有负$(-)$号。这是因为$\alpha$的相位不同导致的，正$(+)$、负$(-)$号的选取只与$\alpha$初始相位在哪个区间有关，一象限$x,y$两个方程符号为$(+,+)$，二象限$(-,+)$，三象限$(-,-)$，四象限$(+,-)$。


## 圆中转圈与傅里叶级数
把上节摆线统一方程变换一下：
$$
\begin{cases}
x-R\cos\theta=r\cos\alpha\\
y-R\sin\theta=r\sin\alpha
\end{cases}
\iff
(x-R\cos\theta)^2+(y-R\sin\theta)^2=r^2
$$
这不是一个圆的方程吗？只不过圆心为动点，且在半径为$R$的圆周上运动（牵连动力）。

由此推广成傅里叶级数：
$$
\begin{cases}
x=r_1\cos\theta_1+r_2\cos\theta_2+\dots+r_n\cos\theta_n=\displaystyle\sum_{i=1}^n r_i\cos\theta_i\\
y=r_1\sin\theta_1+r_2\sin\theta_2+\dots+r_n\sin\theta_n=\displaystyle\sum_{i=1}^n r_i\sin\theta_i
\end{cases}
$$
即：
$$
\begin{cases}
\big(\dots\big((x-r_1\cos\theta_1)-r_2\cos\theta_2\big)-\dots\big)-r_{n-1}\cos\theta_{n-1}=r_n\cos\theta_n\\
\big(\dots\big((y-r_1\sin\theta_1)-r_2\sin\theta_2\big)-\dots\big)-r_{n-1}\sin\theta_{n-1}=r_n\sin\theta_n
\end{cases}
$$
亦即：
$$
\Big(\big(\dots((x-r_1\cos\theta_1)-r_2\cos\theta_2)-\dots\big)-r_{n-1}\cos\theta_{n-1}\Big)^2
+\Big(\big(\dots((y-r_1\sin\theta_1)-r_2\sin\theta_2)-\dots\big)-r_{n-1}\sin\theta_{n-1}\Big)^2=r_n^2
$$
这便形成了类似星球运转的模式：卫星围绕行星转，行星围绕恒星，恒星围绕星系转……

傅里叶级数告诉我们它可以模拟任意函数，同样，只要$r_i$和$\theta_i$选取得当，我们的方程可以模拟以半径$\displaystyle\sum_{i=1}^n r_i$的圆内的任何图案。
即：
$$
\begin{cases}
x=\displaystyle\sum_{i=1}^n r_i\cos(a_i\theta+\varphi_i)\\
y=\displaystyle\sum_{i=1}^n r_i\sin(a_i\theta+\varphi_i)
\end{cases}
$$
是原点中心半径$\displaystyle\sum_{i=1}^n r_i$的圆内任意图形

**Python 验证（计算外摆线 / Epicycles — DFT 逼近任意闭合曲线）：**
```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# --- 1. 定义目标曲线 (可替换为任意闭合曲线的采样点) ---
N = 200  # 采样点数
t = np.linspace(0, 2 * np.pi, N, endpoint=False)
# 示例：心形 + 三角形混合
target_x = 2 * np.sin(t) + np.sin(2 * t) + 0.5 * np.cos(3 * t)
target_y = 2 * np.cos(t) - np.cos(2 * t) + 0.5 * np.sin(3 * t)

# --- 2. DFT 提取外摆线系数 ---
coeffs_x = np.fft.fft(target_x) / N
coeffs_y = np.fft.fft(target_y) / N

# 按振幅降序排列（从最大圆开始画）
amps = np.abs(coeffs_x) + np.abs(coeffs_y)
order = np.argsort(-amps)

# --- 3. 静态绘制外摆线叠加 ---
fig, ax = plt.subplots(figsize=(8, 8))
ax.plot(target_x, target_y, 'k-', lw=2, label='目标曲线')

cum_x, cum_y = 0, 0
for k in order[:12]:  # 取前12个频率分量
    r = np.sqrt(np.abs(coeffs_x[k])**2 + np.abs(coeffs_y[k])**2)
    if r < 0.02:
        continue
    # 这个圆的圆心在 (cum_x, cum_y)，半径 r
    circ = plt.Circle((cum_x, cum_y), r, fill=False, ec='gray', lw=0.4)
    ax.add_patch(circ)
    cum_x += 2 * np.real(coeffs_x[k])
    cum_y += 2 * np.real(coeffs_y[k])

ax.plot(cum_x, cum_y, 'ro', ms=4, label='末端点')
ax.axis('equal'); ax.set_title(f'Epicycles: {len(order)} 个频率分量逼近曲线')
ax.legend(); plt.show()

# --- 4. 动画（可选） ---
# fig, ax = plt.subplots(figsize=(8, 8))
# def update(frame):
#     ax.clear(); ax.axis('equal')
#     ax.set_xlim(-5, 5); ax.set_ylim(-5, 5)
#     px, py = 0, 0
#     t_now = frame * 2 * np.pi / 100
#     for k in order[:12]:
#         r = np.sqrt(np.abs(coeffs_x[k])**2 + np.abs(coeffs_y[k])**2)
#         phi = np.angle(coeffs_x[k] + 1j * coeffs_y[k])
#         if r < 0.02: continue
#         circ = plt.Circle((px, py), r, fill=False, ec='gray', lw=0.4)
#         ax.add_patch(circ)
#         px += 2 * r * np.cos(k * t_now + phi)
#         py += 2 * r * np.sin(k * t_now + phi)
#     ax.plot(px, py, 'ro', ms=4)
# ani = FuncAnimation(fig, update, frames=100, interval=50)
# plt.show()
```

有了平面的圆中转圈我们自然会想三维空间的转动呢？它是球面内的转动，由于傅里叶级数只有$\sin\theta$和$\cos\theta$，没有其它；我们可以用它俩表示$x,y$但不能新创一个表示$z$，怎么办？最好的办法是从球的参数方程找灵感：
$$
\begin{cases}
x=R\cos\theta\cos\varphi\\
y=R\cos\theta\sin\varphi\\
z=R\sin\theta
\end{cases}
$$
多么触动！$x,y$是一对，它们的平方和根号下与$z$是一对，傅里叶级数只涉及正余弦的加减法，推广到三维则借助了它们的乘法！

---

由此，我们可以构建三维空间的傅里叶及摆线了，先从三维摆线开始
## 圆圈上的球面运动
摆线在大圆$R$上转动，有$\begin{cases}x=R\cos\theta\\y=R\sin\theta\end{cases}$，然后它们在小球上运动：
$$
\begin{cases}
x-R\cos\theta=r\cos(n\theta)\cos\varphi\\
y-R\sin\theta=r\sin(n\theta)\cos\varphi\\
z-0=r\sin\varphi
\end{cases}
$$

## 球面上的球面运动
$$
\begin{cases}
x-R\cos\theta_1\cos\varphi_1=r\cos\theta_2\cos\varphi_2\\
y-R\cos\theta_1\sin\varphi_1=r\cos\theta_2\sin\varphi_2\\
z-R\sin\theta_1=r\sin\theta_2
\end{cases}
\Rightarrow\text{推广}
\begin{cases}
x=\displaystyle\sum_{i=1}^n r_i\cos\theta_i\cos\varphi_i\\
y=\displaystyle\sum_{i=1}^n r_i\cos\theta_i\sin\varphi_i\\
z=\displaystyle\sum_{i=1}^n r_i\sin\theta_i
\end{cases}
$$

## 球面上的圈运动
$$
\begin{cases}
x-R\cos\theta_1\cos\varphi_1=r\cos\varphi_1\\
y-R\cos\theta_1\sin\varphi_1=r\sin\varphi_1\\
z-R\sin\theta_1=0
\end{cases}
$$

由此我们看到，多一种运动用加法，多一个维度用乘法！
少一种运动（换一个方向）用减法，少一个维度用除法！

**备查：球坐标参数方程 GeoGebra：**
```geogebra
R = 3
球面 = Surface(R cos(θ) cos(φ), R cos(θ) sin(φ), R sin(θ), θ, -π/2, π/2, φ, 0, 2π)
```

**备查：球坐标参数方程 Python：**
```python
import numpy as np
import matplotlib.pyplot as plt

R = 3
θ = np.linspace(-np.pi/2, np.pi/2, 40)
φ = np.linspace(0, 2*np.pi, 60)
θ, φ = np.meshgrid(θ, φ)
x = R * np.cos(θ) * np.cos(φ)
y = R * np.cos(θ) * np.sin(φ)
z = R * np.sin(θ)

fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(x, y, z, cmap='Blues', alpha=0.6, edgecolor='none')
ax.set_box_aspect([1, 1, 1]); plt.show()
```

**圆圈上的球面运动的 Python 验证（三维摆线）：**
```python
import numpy as np
import matplotlib.pyplot as plt

R, r, n = 3, 1, 5  # 大圆半径, 小球半径, 缠绕数
t = np.linspace(0, 2*np.pi, 1000)
φ = np.linspace(0, 2*np.pi, 1000)  # 球面纬度方向

# 大圆上的动点 (圆心在圆周上运动)
cx, cy = R * np.cos(t), R * np.sin(t)

# 三维摆线：圆心在 (cx,cy,0)，在小球面上作纬圈运动
x = cx + r * np.cos(n * t)[:, None] * np.cos(φ)[None, :]
y = cy + r * np.sin(n * t)[:, None] * np.cos(φ)[None, :]
z = np.zeros_like(t)[:, None] + r * np.sin(φ)[None, :]

# 取 φ=0 截线（小球的赤道）
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.plot(cx, cy, 0, 'gray', lw=1, label='大圆 R')
# 画几根小球在球面上的轨迹
for phi in [0, np.pi/4, np.pi/2]:
    xx = cx + r * np.cos(n * t) * np.cos(phi)
    yy = cy + r * np.sin(n * t) * np.cos(phi)
    zz = r * np.sin(phi) * np.ones_like(t)
    ax.plot(xx, yy, zz, lw=0.6, label=f'φ={phi:.2f}')
ax.set_box_aspect([1, 1, 1]); ax.legend(); plt.show()
```

**球面上球面运动推广的 Python 验证（多级球面外摆线）：**
```python
import numpy as np
import matplotlib.pyplot as plt

# 三级球面转圈
radii = [2, 1, 0.5]       # r₁, r₂, r₃
alphas = [1, 7, 23]       # 纬向频率 (θ = α*t)
betas = [3, 11, 29]       # 经向频率 (φ = β*t)
phases = [0, 1, 2]        # 初始相位
t = np.linspace(0, 2*np.pi, 3000)

x = np.zeros_like(t)
y = np.zeros_like(t)
z = np.zeros_like(t)

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

cum = np.zeros((3, len(t)))
for r, a, b, p in zip(radii, alphas, betas, phases):
    dx = r * np.cos(a * t + p) * np.cos(b * t + p)
    dy = r * np.cos(a * t + p) * np.sin(b * t + p)
    dz = r * np.sin(a * t + p)
    cum[0] += dx; cum[1] += dy; cum[2] += dz
    ax.plot(cum[0], cum[1], cum[2], lw=0.5, alpha=0.5,
            label=f'r={r}, α={a}, β={b}')

ax.plot(cum[0], cum[1], cum[2], 'k', lw=1.2, label='合成轨迹')
ax.set_box_aspect([1, 1, 1]); ax.legend(loc='upper right')
ax.set_title('球面上球面运动: 多级转圈的叠加')
plt.show()
```

**球面上圈运动的 Python 验证：**
```python
import numpy as np
import matplotlib.pyplot as plt

R, r = 3, 1
t = np.linspace(0, 2*np.pi, 2000)

# 球面上大圆旋转中心的轨迹
θ1, φ1 = np.pi/4, t  # 大圆在赤纬 π/4 处绕 z 轴旋转

# 运动限制在球面切平面上的小圈 (z 无变化)
θ2, φ2 = 0, t        # 小圈在赤道面上

x = R * np.cos(θ1) * np.cos(φ1) + r * np.cos(φ2)
y = R * np.cos(θ1) * np.sin(φ1) + r * np.sin(φ2)
z = R * np.sin(θ1) * np.ones_like(t)

fig = plt.figure(figsize=(9, 8))
ax = fig.add_subplot(111, projection='3d')
ax.plot(x, y, z, lw=0.6)
# 标注大圆参考
ax.plot(R*np.cos(t), R*np.sin(t), 0, 'gray', lw=0.5, alpha=0.5, label='参考大圆')
ax.set_box_aspect([1, 1, 1]); ax.legend(); plt.show()
```

---

# 三维傅里叶级数的一般形式

前面我们从环面和摆线出发，逐步推广到了球面上的多级转动。本节给出三维空间周期曲线傅里叶级数的完整数学形式。

## 一、Cartesian 实数形式

设空间周期曲线 $\gamma(t)=(x(t),y(t),z(t))$，周期 $T=2\pi/\omega$。三个坐标分量各自展开为一维傅里叶级数：

$$
\boxed{
\begin{aligned}
x(t) &= \frac{a_0^{(x)}}{2} + \sum_{n=1}^{\infty} \Big[ a_n^{(x)} \cos(n\omega t) + b_n^{(x)} \sin(n\omega t) \Big] \\[8pt]
y(t) &= \frac{a_0^{(y)}}{2} + \sum_{n=1}^{\infty} \Big[ a_n^{(y)} \cos(n\omega t) + b_n^{(y)} \sin(n\omega t) \Big] \\[8pt]
z(t) &= \frac{a_0^{(z)}}{2} + \sum_{n=1}^{\infty} \Big[ a_n^{(z)} \cos(n\omega t) + b_n^{(z)} \sin(n\omega t) \Big]
\end{aligned}
}
$$

其中系数由正交投影给出（以 $x$ 坐标为例）：

$$
a_n^{(x)} = \frac{2}{T}\int_0^T x(t)\cos(n\omega t)\,dt,\qquad
b_n^{(x)} = \frac{2}{T}\int_0^T x(t)\sin(n\omega t)\,dt
$$

写成向量形式，令 $\mathbf{A}_n=(a_n^{(x)},a_n^{(y)},a_n^{(z)})^\top,\ \mathbf{B}_n=(b_n^{(x)},b_n^{(y)},b_n^{(z)})^\top$：

$$
\boxed{\gamma(t) = \frac{\mathbf{A}_0}{2} + \sum_{n=1}^{\infty} \Big[ \mathbf{A}_n \cos(n\omega t) + \mathbf{B}_n \sin(n\omega t) \Big]}
$$

## 二、Cartesian 复数形式

利用 Euler 公式 $\cos\theta=\frac{e^{i\theta}+e^{-i\theta}}{2},\ \sin\theta=\frac{e^{i\theta}-e^{-i\theta}}{2i}$，将实数形式合并为双边复指数级数：

$$
\boxed{\gamma(t) = \sum_{n=-\infty}^{\infty} \mathbf{c}_n\, e^{i n \omega t}, \qquad \mathbf{c}_n = \begin{pmatrix} c_n^{(x)} \\ c_n^{(y)} \\ c_n^{(z)} \end{pmatrix} \in \mathbb{C}^3}
$$

系数由复内积给出：

$$
\mathbf{c}_n = \frac{1}{T}\int_0^T \gamma(t)\,e^{-i n \omega t}\,dt
$$

实数系数与复数系数的转换关系（对每个坐标 $k=x,y,z$）：

$$
c_0^{(k)} = \frac{a_0^{(k)}}{2},\qquad
c_n^{(k)} = \frac{a_n^{(k)} - i b_n^{(k)}}{2},\qquad
c_{-n}^{(k)} = \overline{c_n^{(k)}}\quad (n>0)
$$

**注：** 复数形式虽然更简洁，但复数向量 $\mathbf{c}_n\in\mathbb{C}^3$ 在几何上不易直观。下面给出与本文"球面转动"思路一脉相承的几何形式。

## 三、球面几何形式（球面外摆线基）

本文从球的参数方程获得了"乘法"灵感，自然得到球面基下的展开。每个基向量是一个半径为 $r_i$ 的球面上的点，其球坐标为 $(\theta_i(t),\varphi_i(t))$：

$$
\boxed{
\gamma(t) = \sum_{i=1}^{N} r_i\,
\begin{pmatrix}
\cos\theta_i(t)\,\cos\varphi_i(t) \\[2pt]
\cos\theta_i(t)\,\sin\varphi_i(t) \\[2pt]
\sin\theta_i(t)
\end{pmatrix}
}
$$

取 $\theta_i(t)=\alpha_i t+\delta_i,\ \varphi_i(t)=\beta_i t+\gamma_i$（亦可为无理频率），则得一簇在球面上旋转的向量之和。**几何上，每个分量相当于一个半径为 $r_i$ 的球面"转圈"，它们的和即描出空间曲线。**

当 $\alpha_i:\beta_i$ 取不同比值时，第 $i$ 个球面分量在球面上的轨迹呈 Lissajous 型图案（球面 Lissajous 曲线），这是二维 Lissajous 图形的自然三维推广。

## 四、两种形式的等价性

球面形式与 Cartesian 复数形式通过积化和差相互转换。以单个球面分量为例：

$$
r\begin{pmatrix}\cos(\alpha t+\delta)\cos(\beta t+\gamma)\\\cos(\alpha t+\delta)\sin(\beta t+\gamma)\\\sin(\alpha t+\delta)\end{pmatrix}
$$

**$x$ 坐标的分解：**

$$
r\cos(\alpha t+\delta)\cos(\beta t+\gamma)=\frac{r}{2}\Big[\cos\big((\alpha+\beta)t+(\delta+\gamma)\big)+\cos\big((\alpha-\beta)t+(\delta-\gamma)\big)\Big]
$$

**$y$ 坐标的分解：**

$$
r\cos(\alpha t+\delta)\sin(\beta t+\gamma)=\frac{r}{2}\Big[\sin\big((\alpha+\beta)t+(\delta+\gamma)\big)-\sin\big((\alpha-\beta)t+(\delta-\gamma)\big)\Big]
$$

**$z$ 坐标的分解：**
$$
r\sin(\alpha t+\delta)\ \text{——本身已是单频}
$$

**结论：一个球面分量 $(\alpha,\beta)$ 等价于 Cartesian 形式中的三个频率分量：**

| 频率           | $x$ 项            | $y$ 项             | $z$ 项  |
| -------------- | ----------------- | ------------------ | ------- |
| $\alpha+\beta$ | $\frac{r}{2}\cos$ | $\frac{r}{2}\sin$  | —       |
| $\alpha-\beta$ | $\frac{r}{2}\cos$ | $-\frac{r}{2}\sin$ | —       |
| $\alpha$       | —                 | —                  | $r\sin$ |

反之，**Cartesian 形式中的每一对 $(x,y,z)$ 频率分量都可以重新组合为球面形式**，只要满足 $x,y$ 振幅相等且相位正交的约束（这正是球面转动在代数上的体现）。不满足此约束的一般空间曲线需用 Cartesian 形式。

## 五、复向量极化基形式

引入三维复极化基向量，可以给出球面形式最紧凑的复数表达。定义：

$$
\mathbf{e}_R=\frac{1}{\sqrt{2}}\begin{pmatrix}1\\ i\\0\end{pmatrix},\quad
\mathbf{e}_L=\frac{1}{\sqrt{2}}\begin{pmatrix}1\\-i\\0\end{pmatrix},\quad
\mathbf{e}_z=\begin{pmatrix}0\\0\\1\end{pmatrix}
$$

则球面基向量分解为四项（含正、负频率）：

$$
\begin{pmatrix}\cos\theta\cos\varphi\\\cos\theta\sin\varphi\\\sin\theta\end{pmatrix}
=\frac{1}{2\sqrt{2}}\Big[\,\mathbf{e}_L\,e^{i(\theta+\varphi)}+\mathbf{e}_R\,e^{i(\theta-\varphi)}+\overline{\mathbf{e}_R}\,e^{-i(\theta-\varphi)}+\overline{\mathbf{e}_L}\,e^{-i(\theta+\varphi)}\Big]+\frac{1}{2i}\,\mathbf{e}_z\,e^{i\theta}-\frac{1}{2i}\,\overline{\mathbf{e}_z}\,e^{-i\theta}
$$

代入 $\theta=\alpha t+\delta,\ \varphi=\beta t+\gamma$，每一球面分量展开为频率 $\pm\alpha,\ \pm(\alpha\pm\beta)$ 的六个复指数项。整个球面展开式即上述各项对 $i$ 求和。

**注：** $\mathbf{e}_R$ 和 $\mathbf{e}_L$ 分别是右旋和左旋圆极化基向量（对应电磁学中的 RCP/LCP），它们与本文"右旋/左旋螺旋线"有同一几何来源。

## 六、四元数嵌入形式

将 $\mathbb{R}^3$ 嵌入纯四元数空间 $\operatorname{Im}(\mathbb{H})=\{xi+yj+zk\}$，三维曲线变为纯四元数值函数：

$$
\Gamma(t)=x(t)\,\mathbf{i}+y(t)\,\mathbf{j}+z(t)\,\mathbf{k},\qquad \Gamma:\mathbb{R}\to\operatorname{Im}(\mathbb{H})
$$

Cartesian 复数形式在四元数框架下写作：

$$
\boxed{\Gamma(t)=\sum_{n=-\infty}^{\infty} Q_n\, e^{i n\omega t},\qquad Q_n=c_n^{(x)}\mathbf{i}+c_n^{(y)}\mathbf{j}+c_n^{(z)}\mathbf{k}\in\mathbb{H}\otimes\mathbb{C}}
$$

球面形式则在四元数框架下获得最简洁的旋转解释。球面上点 $\mathbf{u}(\theta,\varphi)=(\cos\theta\cos\varphi,\cos\theta\sin\varphi,\sin\theta)^\top$ 作为纯四元数：

$$
\mathbf{u}(\theta,\varphi)=q\,\mathbf{k}\,\overline{q},\qquad q=\cos\frac{\theta}{2}+\sin\frac{\theta}{2}\big(\cos\varphi\,\mathbf{i}+\sin\varphi\,\mathbf{j}\big)\in\mathrm{SU}(2)
$$

这正是二重覆盖 $\mathrm{SU}(2)\twoheadrightarrow\mathrm{SO}(3)$ 的具体实现：四元数 $q$ 将 $z$ 轴（$\mathbf{k}$）旋转至 $(\theta,\varphi)$ 方向。于是三维傅里叶级数的球面形式化为：

$$
\boxed{\Gamma(t)=\sum_{i=1}^{N} r_i\, q_i(t)\,\mathbf{k}\,\overline{q_i(t)},\qquad q_i(t)=\cos\frac{\alpha_i t+\delta_i}{2}+\sin\frac{\alpha_i t+\delta_i}{2}\big(\cos(\beta_i t+\gamma_i)\,\mathbf{i}+\sin(\beta_i t+\gamma_i)\,\mathbf{j}\big)}
$$

**每一项都是一根被四元数旋转的 $\mathbf{k}$ 轴——多一种运动用加法（叠加转动），多一个维度用乘法（四元数乘法编码三维旋转）。** 这正是本文从第一页到最后一页贯穿始终的洞察的形式化归宿。

## 七、形式总结

| 形式           | 表达式                                                                                              | 自由度                                | 适用场景           |
| -------------- | --------------------------------------------------------------------------------------------------- | ------------------------------------- | ------------------ |
| Cartesian 实数 | $\frac{\mathbf{A}_0}{2}+\sum_{n=1}^\infty[\mathbf{A}_n\cos(n\omega t)+\mathbf{B}_n\sin(n\omega t)]$ | 每频 $6$ 实参数                       | 通用展开           |
| Cartesian 复数 | $\sum_{n=-\infty}^\infty \mathbf{c}_n e^{in\omega t}$                                               | 每频 $3$ 复参数                       | 理论推导、DFT 计算 |
| 球面几何       | $\sum_i r_i(\cos\theta_i\cos\varphi_i,\ \cos\theta_i\sin\varphi_i,\ \sin\theta_i)^\top$             | 每分量 $r,\alpha,\beta,\delta,\gamma$ | 几何直观、旋转动画 |
| 四元数         | $\sum_i r_i\, q_i\,\mathbf{k}\,\overline{q_i}$                                                      | 每分量 $r,q\in\mathrm{SU}(2)$         | 刚体运动、姿态插值 |

---



**Python 验证 — 三维傅里叶级数的三种形式：**
```python
import numpy as np
import matplotlib.pyplot as plt
t = np.linspace(0, 2 * np.pi, 2000)
N = 5
# --- 形式一：Cartesian 实数 ---
np.random.seed(42)
A = np.random.randn(3, N) * 0.5
B = np.random.randn(3, N) * 0.5
x_cart = sum(A[0, n] * np.cos((n+1)*t) + B[0, n] * np.sin((n+1)*t) for n in range(N))
y_cart = sum(A[1, n] * np.cos((n+1)*t) + B[1, n] * np.sin((n+1)*t) for n in range(N))
z_cart = sum(A[2, n] * np.cos((n+1)*t) + B[2, n] * np.sin((n+1)*t) for n in range(N))
# --- 形式二：球面几何 ---
r_vals = [2, 1.5, 0.8, 0.4, 0.2]
a_vals = [1, 3, 5, 7, 11]
b_vals = [2, 4, 8, 13, 17]
x_sph = np.sum([r * np.cos(a*t) * np.cos(b*t) for r, a, b in zip(r_vals, a_vals, b_vals)], axis=0)
y_sph = np.sum([r * np.cos(a*t) * np.sin(b*t) for r, a, b in zip(r_vals, a_vals, b_vals)], axis=0)
z_sph = np.sum([r * np.sin(a*t) for r, a in zip(r_vals, a_vals)], axis=0)
# --- 形式三：Cartesian 复数 (由实数系数重建) ---
x_cplx = np.zeros_like(t, dtype=complex)
for k, n in enumerate(range(-N, N+1)):
    if n > 0:
        cn = (A[0, n-1] - 1j * B[0, n-1]) / 2
        x_cplx += cn * np.exp(1j * n * t) + np.conj(cn) * np.exp(-1j * n * t)
fig = plt.figure(figsize=(15, 5))
datasets = [(x_cart, y_cart, z_cart, 'Cartesian 实数形式'),
            (x_sph, y_sph, z_sph, '球面几何形式')]
for i, (x, y, z, title) in enumerate(datasets):
    ax = fig.add_subplot(1, 3, i+1, projection='3d')
    ax.plot(x, y, z, lw=0.5)
    ax.set_title(title); ax.set_box_aspect([1, 1, 1])
# 对比两种形式
ax3 = fig.add_subplot(1, 3, 3, projection='3d')
ax3.plot(x_cart, y_cart, z_cart, 'b', lw=0.5, alpha=0.6, label='Cartesian')
ax3.plot(x_sph, y_sph, z_sph, 'r', lw=0.5, alpha=0.6, label='球面几何')
ax3.set_title('两种形式对比 (不同参数)')
ax3.set_box_aspect([1, 1, 1]); ax3.legend()
plt.tight_layout(); plt.show()
```

## 一、环面纽结（Torus Knot）——螺旋线何时闭合

文档中的环面螺旋线 $\omega$ 为任意实数时，曲线在环面上无限缠绕。当 $\omega$ 为有理数 $\omega=\frac{p}{q}$（$p,q$ 互质）时，曲线经过 $q$ 个大圆周后在环面上闭合，称为 **$(p,q)$ 环面纽结**：

$$
\begin{cases}
x=(R+r\cos(qt))\cos(pt)\\
y=(R+r\cos(qt))\sin(pt)\\
z=r\sin(qt)
\end{cases}\quad t\in[0,2\pi]
$$

- 罗丹线圈中 $\omega=12,\ \phi=13$ 实际就是 $(12,13)$ 环面纽结
- $p,q$ 互质时是单纽结；$\gcd(p,q)=g>1$ 时是 $g$ 个纽结的链环（Link）
- 平凡环面纽结 $(1,q)$ 就是平凡结（Unknot）——拓扑上与圆等价
- 环面纽结是纽结理论中最基本的研究对象，其 Jones 多项式、Alexander 多项式均有闭式解

**GeoGebra 验证（3D 绘图区，对比不同 (p,q) 纽结）：**
```geogebra
R = 2; r = 1
p = 2; q = 3
(p,q)纽结 = Curve((R + r cos(q t)) cos(p t), (R + r cos(q t)) sin(p t), r sin(q t), t, 0, 2π)
```

**Python 验证（对比多个环面纽结）：**
```python
import numpy as np
import matplotlib.pyplot as plt
R, r = 2, 1
t = np.linspace(0, 2*np.pi, 2000)
knots = [(2, 3), (3, 2), (3, 5), (5, 7)]
fig = plt.figure(figsize=(12, 10))
for idx, (p, q) in enumerate(knots):
    ax = fig.add_subplot(2, 2, idx+1, projection='3d')
    x = (R + r * np.cos(q * t)) * np.cos(p * t)
    y = (R + r * np.cos(q * t)) * np.sin(p * t)
    z = r * np.sin(q * t)
    ax.plot(x, y, z, lw=0.8)
    ax.set_title(f'({p},{q}) Torus Knot'); ax.set_box_aspect([1, 1, 1])
plt.tight_layout(); plt.show()
```

这为文档的"螺旋线"赋予了深刻的拓扑内涵：闭合或不闭合，取决于 $\omega$ 是否有理——**无理数螺旋线在环面上稠密**，这正是 Kronecker 稠密性定理的几何体现。

$$
\lim_{T\to\infty}\frac{\text{曲线在 }[0,T]\text{ 内绕大圆次数}}{\text{绕小圆次数}}=\frac{1}{\omega}
$$

当 $\omega$ 为无理数时，这个比值在整个环面上形成处处稠密的缠绕。

## 二、Hopf 纤维化（Hopf Fibration）——球面与环面的隐秘桥梁

文档中从平面转圈推广到三维球面运动的思路，实际上触及了一个深刻结构。三维球面 $S^3$（四维空间中单位球面）**纤维化**为：底空间 $S^2$（二维球面），纤维 $S^1$（圆）：

$$
S^1 \hookrightarrow S^3 \xrightarrow{\pi} S^2
$$

Hopf 映射 $\pi:S^3\to S^2$ 将四维球面上的点映射到普通三维球面上，而每个 $S^2$ 上的点对应 $S^3$ 上的一整个圆（纤维）。**这些纤维在 $S^3$ 中两两链接（linked），形成 Clifford 平行环面。**

参数形式（取 $S^3\subset\mathbb{R}^4\cong\mathbb{C}^2$）：

$$
(z_1,z_2)=(\cos\eta\,e^{i\xi_1},\ \sin\eta\,e^{i\xi_2})\in S^3,\quad \eta\in[0,\pi/2],\ \xi_1,\xi_2\in[0,2\pi]
$$

- 固定 $\eta$，$(\xi_1,\xi_2)$ 张成一个环面（Clifford 环面）——这是文档中"球面上的圈运动"的自然推广
- $\eta=0$ 和 $\eta=\pi/2$ 时环面退化为两个互相链接的圆（Hopf 链环）
- 文档中"多一个维度用乘法"的直觉，在 Hopf 纤维化中获得了精确的数学表达：$\mathbb{C}^2$ 中的乘法结构通过 Hopf 映射投影为 $\mathbb{R}^3$ 中的旋转

**Python 验证 — Hopf 纤维化的立体投影可视化：**
```python
import numpy as np
import matplotlib.pyplot as plt
# S^3 参数: (z1, z2) = (cos η e^{i ξ1}, sin η e^{i ξ2})
# 固定 η 得 Clifford 环面，立体投影到 R^3
t = np.linspace(0, 2*np.pi, 200)
etas = [0.1, 0.3, 0.5, 0.7, 0.9, 1.2]  # 不同 η 的纤维
fig = plt.figure(figsize=(12, 5))
# 子图1: 在 S^3 中的纤维 (显示 (Re(z1), Im(z1), Re(z2)) 投影)
ax1 = fig.add_subplot(121, projection='3d')
for eta in etas:
    xi1 = t
    xi2 = t * 3  # (1,3) torus knot fiber
    z1_r = np.cos(eta) * np.cos(xi1)
    z1_i = np.cos(eta) * np.sin(xi1)
    z2_r = np.sin(eta) * np.cos(xi2)
    ax1.plot(z1_r, z1_i, z2_r, lw=0.8, label=f'η={eta:.2f}')
ax1.set_title('S³ 中 Hopf 纤维 (Re(z₁),Im(z₁),Re(z₂))')
ax1.set_box_aspect([1,1,1]); ax1.legend(fontsize=7)
# 子图2: Hopf 映射像 — S² 上的点
# π(z1, z2) = (|z1|² - |z2|², 2 z1 conj(z2)) ∈ C × R ≅ R³
ax2 = fig.add_subplot(122, projection='3d')
u = np.linspace(0, np.pi, 30)
v = np.linspace(0, 2*np.pi, 40)
sx = np.outer(np.sin(u), np.cos(v))
sy = np.outer(np.sin(u), np.sin(v))
sz = np.outer(np.cos(u), np.ones_like(v))
ax2.plot_surface(sx, sy, sz, cmap='Blues', alpha=0.3, edgecolor='none')
for eta in etas[:4]:
    xi1, xi2 = t, t * 3
    z1 = np.cos(eta) * np.exp(1j * xi1)
    z2 = np.sin(eta) * np.exp(1j * xi2)
    hx = np.abs(z1)**2 - np.abs(z2)**2
    hy = 2 * np.real(z1 * np.conj(z2))
    hz = 2 * np.imag(z1 * np.conj(z2))
    ax2.plot(hx, hy, hz, lw=0.8, label=f'η={eta:.2f}')
ax2.set_title('Hopf 映射像 (S² 上的曲线)')
ax2.set_box_aspect([1,1,1]); ax2.legend(fontsize=7)
plt.tight_layout(); plt.show()
```

## 三、四元数（Quaternions）——旋转的代数

文档中"加法为运动、乘法为维度"的洞见，在四元数代数中获得完美统一。单位四元数群与 $S^3$ 同构：

$$
q=\cos\frac{\theta}{2}+(ai+bj+ck)\sin\frac{\theta}{2},\quad a^2+b^2+c^2=1
$$

文档中三维球面推广方程：

$$
\begin{cases}
x=\displaystyle\sum_{i=1}^n r_i\cos\theta_i\cos\varphi_i\\
y=\displaystyle\sum_{i=1}^n r_i\cos\theta_i\sin\varphi_i\\
z=\displaystyle\sum_{i=1}^n r_i\sin\theta_i
\end{cases}
$$

在四元数框架下等价于：每一个 $r_i(\cos\theta_i\cos\varphi_i,\ \cos\theta_i\sin\varphi_i,\ \sin\theta_i)$ 是纯四元数域中的向量，而它们的线性叠加正是多级旋转的代数表达。四元数乘法（Hamilton 积）**同时编码了旋转的角度和旋转轴**——这是文档结尾"加法与乘法"直觉的形式化。

进一步，SO(3) 旋转群的双覆盖 SU(2) $\cong S^3$ 意味着：**三维空间中的刚体旋转天然生活在四维球面上**。文档中球面运动的方程已经在描述这件事，只是未曾言明。

## 四、相空间与可积系统——环面作为动力学舞台

环面不仅是几何对象，也是经典力学的核心结构。**Arnold-Liouville 定理**指出：$n$ 自由度的 Liouville 可积 Hamilton 系统的运动限制在 $n$ 维不变环面上。对于二自由度可积系统（如平面单摆耦合振子），相空间是 $T^2=S^1\times S^1$，运动轨迹正是本文描述的环面螺旋线。

- $\omega=\omega_1/\omega_2$ 为有理数 → 闭合轨道（共振）
- $\omega$ 为无理数 → 准周期轨道在环面上稠密

**KAM（Kolmogorov-Arnold-Moser）理论**进一步说明：微小扰动只破坏共振环面，大部分无理环面得以幸存。文档中环面螺旋线的"闭合 vs 稠密"二分为理解非线性动力系统的稳定性提供了核心图景。

这可以直观地称为：**"上帝用环面编织了确定性混沌的边界"**。

## 五、计算外摆线——用傅里叶级数画任意图形

文档结尾指出 $\displaystyle\sum r_i\cos(a_i\theta+\varphi_i)$ 可以逼近圆盘内任意图形，这正是**计算外摆线（Computational Epicycles）**的原理：

给定平面闭合曲线 $\gamma(t)=(x(t),y(t))$，通过离散傅里叶变换（DFT）提取系数：

$$
\begin{aligned}
c_k^{(x)}&=\frac{1}{N}\sum_{n=0}^{N-1}x(n\Delta t)\,e^{-2\pi i k n/N}\\
c_k^{(y)}&=\frac{1}{N}\sum_{n=0}^{N-1}y(n\Delta t)\,e^{-2\pi i k n/N}
\end{aligned}
$$

每一对复系数 $\{c_k^{(x)},c_k^{(y)}\}$ 映射为一根以频率 $k$ 旋转的半径棍，所有棍首尾相接，末端即描出原图形。

**推广到空间曲线**则用球面傅里叶基：

$$
\gamma(t)=\sum_{k=0}^{n}\Big(r_k\cos(k t+\alpha_k)\cos(\omega_k t+\beta_k),\ r_k\cos(k t+\alpha_k)\sin(\omega_k t+\beta_k),\ r_k\sin(k t+\alpha_k)\Big)
$$

这正是文档末尾三维推广方程的应用。**任何三维闭合曲线都可以用足够多的"球面外摆线"来逼近。**

**Python 验证 — 三维 DFT 外摆线（球面傅里叶基逼近空间曲线）：**
```python
import numpy as np
import matplotlib.pyplot as plt
# --- 1. 目标空间曲线 ---
N = 200
t = np.linspace(0, 2*np.pi, N, endpoint=False)
# 示例: 三维 Lissajous 结
target_x = np.sin(2*t) + 0.5*np.cos(3*t)
target_y = np.cos(2*t) + 0.5*np.sin(5*t)
target_z = np.sin(3*t)
# --- 2. 三坐标独立 DFT ---
cx = np.fft.fft(target_x) / N
cy = np.fft.fft(target_y) / N
cz = np.fft.fft(target_z) / N
# --- 3. 用球面基重建 (前 M 个最强频率) ---
M = 10
amps = np.abs(cx) + np.abs(cy) + np.abs(cz)
top_k = np.argsort(-amps)[:M]
t_fine = np.linspace(0, 2*np.pi, 1000)
x_recon = np.zeros_like(t_fine)
y_recon = np.zeros_like(t_fine)
z_recon = np.zeros_like(t_fine)
for k in top_k:
    amp_x, phi_x = np.abs(cx[k]), np.angle(cx[k])
    amp_y, phi_y = np.abs(cy[k]), np.angle(cy[k])
    amp_z, phi_z = np.abs(cz[k]), np.angle(cz[k])
    x_recon += 2 * amp_x * np.cos(k * t_fine + phi_x)
    y_recon += 2 * amp_y * np.cos(k * t_fine + phi_y)
    z_recon += 2 * amp_z * np.cos(k * t_fine + phi_z)
fig = plt.figure(figsize=(14, 6))
ax1 = fig.add_subplot(121, projection='3d')
ax1.plot(target_x, target_y, target_z, lw=1.5, label='原始曲线')
ax1.set_title(f'原始空间曲线 (N={N} 采样点)')
ax1.set_box_aspect([1,1,1]); ax1.legend()
ax2 = fig.add_subplot(122, projection='3d')
ax2.plot(x_recon, y_recon, z_recon, lw=0.8, color='red', label=f'{M} 个球面基重建')
ax2.set_title(f'球面傅里叶基重建 (前{M}个频率分量)')
ax2.set_box_aspect([1,1,1]); ax2.legend()
plt.tight_layout(); plt.show()
```

## 六、$n$ 维推广

沿文档的自然推广方向，$n$ 维环面 $T^n=\underbrace{S^1\times S^1\times\cdots\times S^1}_{n\text{ 个}}$ 上的一般螺旋线：

$$
\boldsymbol{\gamma}(t)=\big(r_1\cos(\omega_1 t+\varphi_1),\ r_1\sin(\omega_1 t+\varphi_1),\ r_2\cos(\omega_2 t+\varphi_2),\ r_2\sin(\omega_2 t+\varphi_2),\ \dots\big)
$$

当推广到无穷维时，退化为 **Bohr 的殆周期函数（Almost Periodic Functions）**：

$$
f(t)\sim\sum_{k=1}^{\infty}a_k e^{i\lambda_k t},\quad \lambda_k\in\mathbb{R}
$$

这正是文档中"傅里叶级数可以模拟任意函数"在无穷维环面上的严格表述。

## 七、复结构与椭圆函数——环面的解析视角

环面 $\mathbb{C}/\Lambda$（复平面模格 $\Lambda=\{m+n\tau:m,n\in\mathbb{Z},\ \operatorname{Im}\tau>0\}$）与文档中的参数环面同胚：

$$
z\mapsto (\Re\,\wp(z),\ \Im\,\wp(z),\ \Re\,\wp'(z))
$$

其中 $\wp(z)$ 为 Weierstrass $\wp$ 函数。这个视角将环面螺旋线解释为：**复平面上的一条射线在格商下的像**。若斜率 $\omega$ 为有理数则闭合，无理数则在环面中稠密——与第一节殊途同归。

更进一步，模群 $\mathrm{SL}(2,\mathbb{Z})$ 作用于 $\tau$ 上，将文档中"不同 $R,r$ 的环面"进行分类，相等的 $j$-不变量意味着共形等价的环面（椭圆曲线）。这是 Birch 和 Swinnerton-Dyer 猜想的舞台。

## 八、几何代数与几何微积分——"乘法即维度"的代数归宿

> 前七节从环面走到复结构，线索是：**复数 → 四元数 → 球面旋转**。几何代数（Geometric/Clifford Algebra, GA）把这条线索收束为一个对象——**多重向量（multivector）**；几何微积分（Geometric Calculus, GC）则给出它的导数与积分。本节既给出概念地图，也给出可以直接长进 `cprdspy` 的创意方向。

### 8.1 几何积：一个乘法同时给出度量与维度

对向量 \(a,b\)，定义几何积
$$
\boxed{ab=a\cdot b+a\wedge b}
$$
其中
$$
a\cdot b=\frac12(ab+ba),\qquad a\wedge b=\frac12(ab-ba).
$$
- \(a\cdot b\) 是通常的内积（度量、长度、夹角）；
- \(a\wedge b\) 是外积，表示由 \(a,b\) 张成的**有向平面**（二重向量，bivector）；
- 二者满足 \(a\wedge a=0,\ e_ie_j=-e_je_i\ (i\neq j)\)。

三维欧氏空间 \(\mathrm{Cl}(3)\) 的基：

| 阶 | 基元素 | 几何意义 | 个数 |
| --- | --- | --- | --- |
| 0 | \(1\) | 标量 | 1 |
| 1 | \(e_1,e_2,e_3\) | 有向线段（向量） | 3 |
| 2 | \(e_{23},e_{31},e_{12}\) | 有向平面（二重向量） | 3 |
| 3 | \(I=e_1e_2e_3\) | 有向体积（伪标量） | 1 |

共 \(2^3=8\) 个基元素。一般地 \(\dim\mathrm{Cl}(n)=2^n\)。**每加入一个新维度，代数维数翻倍——这正是"多一个维度用乘法"的代数版本：乘上一个新的基向量，会把原来的对象分裂成"平行部分 + 垂直部分"，于是生成新的几何阶。**

两个同构关系把本文前面的"圆"与"旋转"接回来：
$$
\mathrm{Cl}^+(2)=\operatorname{span}\{1,e_{12}\}\cong\mathbb{C},\qquad
\mathrm{Cl}^+(3)=\operatorname{span}\{1,e_{23},e_{31},e_{12}\}\cong\mathbb{H}.
$$
在适当符号约定下，四元数单位可显式对应为
$$
\mathbf{i}\leftrightarrow -e_{23},\qquad
\mathbf{j}\leftrightarrow -e_{31},\qquad
\mathbf{k}\leftrightarrow -e_{12}.
$$
因此第三节的四元数并不是另一套代数，而是 \(\mathrm{Cl}^+(3)\) 的一个坐标影子。

**转子（rotor）** 是几何代数中的旋转算子。对单位二重向量 \(B\)（\(B^2=-1\)）：
$$
R=e^{-B\theta/2}=\cos\frac{\theta}{2}-\hat B\sin\frac{\theta}{2},\qquad
v\mapsto Rv\tilde R=RvR^{-1},
$$
其中 \(\tilde R\) 是反转（reverse）。与矩阵或欧拉角相比，转子有三个直接好处：

1. **无坐标**：旋转平面就是 \(B\) 本身；
2. **无万向锁**：任意维数、任意旋转平面都统一处理；
3. **可复合**：\(R_2R_1\) 仍是转子，"多一种运动"就是转子相乘。

一个漂亮的几何事实是：**任意旋转都是两次反射的复合**。对单位向量 \(a\)，反射为 \(v\mapsto -ava\)；于是
$$
v\mapsto -b(-ava)b=(ba)v(ab)=Rv\tilde R,\qquad R=ba.
$$
这正是万花筒（kaleidoscope）与反射群图案的代数基础：给定几面"镜子"，反复做反射和它们的乘积，就能生成整个图案群。

### 8.2 本文曲线的转子写法

**平面外摆线 / 傅里叶级数。** 令 \(I=e_1e_2\)，则
$$
\boxed{\gamma(t)=\sum_{i=1}^{n}r_i\,R_i(t)\,e_1\,\tilde R_i(t)},\qquad
R_i(t)=e^{-\frac12 I(\omega_i t+\varphi_i)}.
$$
展开即本文的
$$
x=\sum_i r_i\cos(\omega_i t+\varphi_i),\qquad
y=\sum_i r_i\sin(\omega_i t+\varphi_i).
$$
转子写法的价值在于：它不依赖 \(\cos/\sin\) 的坐标记账，而且把"每个本轮是一个旋转"直接写成了代数。

**三维球面运动。** 把参考轴换成 \(e_3\)，把旋转平面换成任意二重向量。单个固定平面的转子在球面上画出圆；要得到球面 Lissajous，需要用两个不同平面的转子相乘：
$$
\boxed{\gamma(t)=\sum_{i=1}^{n}r_i\,R_i(t)\,e_3\,\tilde R_i(t)},\qquad
R_i(t)=e^{-\frac12\alpha_i t\,e_{23}}\,e^{-\frac12\beta_i t\,e_{31}}.
$$
这与第六节（四元数嵌入）的公式逐字对应，但不再需要"把四元数翻译成矩阵"这一步。每一项都是**被转子转动的一根参考轴**；求和就是运动的叠加，两个转子不交换时便产生球面 Lissajous。

**环面螺旋线。** 设大圆在 \(I_{12}=e_{12}\) 平面内，径向单位向量
$$
\rho(u)=e^{-\frac12 I_{12}u}\,e_1\,e^{\frac12 I_{12}u},
$$
则环面螺旋线可写成两个转子的复合：
$$
\boxed{\gamma(u,v)=(R+r\cos v)\,\rho(u)+r\sin v\,e_3}
$$
或更"转子化"地，
$$
\gamma=R\rho+r\,R_v\rho\tilde R_v,\qquad
R=e^{-\frac12 I_{12}u},\quad R_v=e^{-\frac12(\rho\wedge e_3)v}.
$$
第一个转子驱动大圆，第二个转子在随动的子午面 \(\rho\wedge e_3\) 内驱动小圆。**频率比 \(v/u=\omega\) 就是两个转子的转速比：有理数→闭合的环面纽结，无理数→稠密缠绕。** 这正是第一节（环面纽结）的转子语言版本。

**Hopf 纤维化。** 单位转子群 \(\mathrm{Spin}(3)\cong S^3\)。Hopf 映射可写成
$$
h:\mathrm{Spin}(3)\to S^2,\qquad h(q)=q\,e_3\,\tilde q.
$$
它的纤维是
$$
q\mapsto q\,e^{-e_3\theta/2}.
$$
也就是说，**Hopf 纤维正是"绕参考轴 \(e_3\) 的转子规范自由度"**；底空间 \(S^2\) 上的点是被转子转过去的 \(e_3\) 方向。第二节的 Hopf 纤维化、第三节的四元数、第六节的球面傅里叶，在这里被同一个 sandwich 乘积 \(q\,e_3\,\tilde q\) 统一。

### 8.3 几何微积分：一个导数统一梯度、散度与旋度

在 \(\mathrm{Cl}(n)\) 中定义向量导数
$$
\nabla=\sum_{k=1}^{n}e^k\partial_k,\qquad e^k\cdot e_j=\delta^k_j.
$$
对向量场 \(F\)，有基本的**几何微积分乘积法则**
$$
\boxed{\nabla F=\nabla\cdot F+\nabla\wedge F}.
$$
- \(\nabla\cdot F\) 是标量——散度；
- \(\nabla\wedge F\) 是二重向量——旋度；
- 对数量场 \(f\)，\(\nabla f\) 是梯度。

在三维中，旋度与经典叉积只差一个 Hodge 对偶：
$$
\nabla\wedge F=I(\nabla\times F),\qquad I=e_1e_2e_3.
$$
所以"梯度、散度、旋度"不是三个算子，而是同一个 \(\nabla\) 的三个阶分量。

**基本定理（Fundamental Theorem of Geometric Calculus）** 统一了微积分基本定理、Green 公式、Gauss 散度定理、Stokes 定理与 Cauchy 定理：
$$
\boxed{\int_V\dot\nabla\dot F\,dV=\oint_{\partial V}nF\,dS},
$$
其中点号表示 \(\dot\nabla\) 只作用于其后的 \(\dot F\)，\(n\) 是外法向。取 \(F\) 为标量得到梯度定理；取 \(F\) 为向量同时得到散度定理与旋度定理；在二维复情形，取单演函数即得 Cauchy 积分定理。

**曲线几何的无坐标公式。** 设曲线 \(\gamma(t)\)，记 \(v=\dot\gamma,\ a=\ddot\gamma,\ \dot a=\dddot\gamma\)，则
$$
\boxed{\kappa=\frac{|v\wedge a|}{|v|^3}},\qquad
\boxed{\tau=\frac{(v\wedge a\wedge\dot a)\,I^{-1}}{|v\wedge a|^2}}.
$$
曲率向量为
$$
\mathbf{k}=\frac{(a\wedge v)v}{|v|^4},\qquad |\mathbf{k}|=\kappa,
$$
它把"弯曲方向"也保留了下来，而不仅仅是曲率大小。与经典公式 \(\kappa=|\gamma'\times\gamma''|/|\gamma'|^3\)、\(\tau=(\gamma'\times\gamma'')\cdot\gamma'''/|\gamma'\times\gamma''|^2\) 相比，GA 版本不需要叉积、不需要选坐标，而且可以直接推广到任意维数。

**活动标架的转子方程。** 若 \(R(t)\) 携带一个标准正交标架，定义角速度二重向量
$$
\Omega=-2\tilde R\dot R,
$$
则
$$
\dot R=-\frac12\Omega R.
$$
整条 Frenet 方程被压缩成一个转子微分方程；\(|\Omega|\) 是转速，\(\Omega\) 的方向是瞬时旋转平面。对动画与管道生成来说，这比逐点求解 Frenet 标架更稳定——尤其在直线段 Frenet 标架会退化，而转子方程不会。

**曲线流。** 几何微积分最自然的应用之一是几何演化方程。曲线缩短流
$$
\partial_t\gamma=\partial_s^2\gamma=\kappa N
$$
在 GA 中无需坐标即可离散化；它可以把任意初始曲线"熨平"成圆，也可以反过来作为生成艺术中的形态演化引擎。

### 8.4 共形几何代数（CGA）：圆、球与 Möbius 变换

共形几何代数 \(\mathrm{Cl}(4,1)\) 在三维欧氏空间中加入两个零向量 \(e_0,e_\infty\)：
$$
e_0^2=e_\infty^2=0,\qquad e_0\cdot e_\infty=-1.
$$
点 \(x\in\mathbb{R}^3\) 嵌入为
$$
X=x+\frac12 x^2e_\infty+e_0,\qquad X^2=0.
$$
球、平面、圆都成为单个 blade：
$$
S=X_c-\frac12 r^2e_\infty\quad(\text{球心 }X_c,\text{半径 }r),\qquad
\Pi=n+d\,e_\infty\quad(\text{单位法向 }n),
$$
球面由 \(X\cdot S=0\) 给出，平面由 \(X\cdot\Pi=0\) 给出。两个球 \(S_1,S_2\) 的交是圆（对偶表示中记为 \(S_1\wedge S_2\)）；三个球的交是点对。**"点、线、面、圆、球"第一次被放进同一个线性空间。**

更重要的是，**Möbius 变换就是 versor 的 sandwich 作用**：
$$
X\mapsto M X\tilde M.
$$
反射、旋转、平移、缩放、球反演全部是同一类对象。对生成艺术而言，这意味着：

- **圆反演万花筒**：选一组反演圆，反复做 \(X\mapsto M X\tilde M\)，自动生成极限集/分形图案；
- **Dupin 四次圆纹曲面**：环面在 Möbius 变换下的像，可在 CGA 中紧凑表示；
- **立体投影与 Hopf**：\(S^3\to\mathbb{R}^3\) 的立体投影把 Clifford 环面变成 \(\mathbb{R}^3\) 中的环面，把 Hopf 纤维变成 **Villarceau 圆**——环面上每一根"斜着绕两圈"的圆，都是一条 Hopf 纤维。这是把第二节的抽象纤维化变成可画图像的捷径。

**环面的球面族包络表示。** 环面本身不是 CGA 的单个 blade，但它是一个单参数球面族的包络：球心在大圆上、半径固定为 \(r\)，
$$
S(u)=C(u)-\frac12 r^2e_\infty,\qquad
C(u)=c(u)+\frac12 c(u)^2e_\infty+e_0,\quad
c(u)=R\,e^{-\frac12 I_{12}u}e_1e^{\frac12 I_{12}u}.
$$
相邻球面的交线在极限下收敛到子午圆；所有子午圆的并集就是环面。这个视角把"环面 = 圆沿圆扫掠"写成了一个包络问题，非常适合做参数化曲面生成。

### 8.5 创意与前瞻建议：让 GA/GC 长进 cprdspy

下面按"可立即落地"与"研究型"两组给出建议。

**A. 可立即落地的库扩展**

1. **`cprdspy.ga` 转子曲线模块。** 提供 `rotor(plane, angle)`、`rotor_curve(...)`、`epicycles_rotor(...)`、`spherical_epicycles(...)`。用户在 API 里直接指定"旋转平面 + 转速 + 相位"，而不必写 \(\cos/\sin\)。2D 用 \(\mathrm{Cl}(2)\)，3D 用 \(\mathrm{Cl}(3)\)，代码路径完全一致。

2. **曲率/挠率诊断与着色。** 对库中现有的螺线、波形、花朵、星形统一计算 \(\kappa(t),\tau(t)\)，用颜色或线宽编码；标出 \(\kappa=0\)（拐点）与 \(\tau=0\)（局部共面）的位置。这既是数学诊断，也是新的视觉语言。

3. **无奇异标架与管道/缎带生成。** 用转子平行移动或双重反射构造沿曲线的光滑标架，再把圆/多边形截面挤出成管道、缎带。与 Plotly 3D 结合，可把环面纽结变成可交互的"实体雕塑"。重点解决 Frenet 标架在直线段的退化问题。

4. **转子关键帧动画。** 两个姿态 \(R_0,R_1\) 之间的测地插值为
   $$
   R(t)=R_0\big(R_0^{-1}R_1\big)^t,\qquad t\in[0,1],
   $$
   即 \(S^3\) 上的 slerp。用转子关键帧驱动 `FuncAnimation`/Plotly frames，彻底告别欧拉角万向锁。

5. **轻量 Möbius 后处理层。** 先实现二维 Möbius 变换的 \(4\times4\) 实矩阵表示（作用于齐次坐标），即可对任意已生成的平面图案做反演、旋转、平移、缩放；后续再用 CGA 扩展到三维球面/环面。典型的"后处理即创作"：一张曼陀罗 → 一次圆反演 → 一张新曼陀罗。

6. **Hopf/Clifford 环面可视化。** 用立体投影把 \(S^3\) 中的 Clifford 环面画到 \(\mathbb{R}^3\)，并把不同 Hopf 纤维染成不同颜色。由于每条纤维都是 Villarceau 圆，这个演示会同时讲清"Hopf 纤维化、环面纽结、转子规范"三件事，非常适合作为 `cprdspy` 的旗舰示例。

7. **反射群万花筒生成器。** 用 \(v\mapsto -ava\) 的反射和它们的乘积生成二面体群/考克斯特群图案；输入几面镜子，输出整个轨道。与现有的曼陀罗生成器相比，这种方法天然保证对称群的封闭性。

**B. 研究型 / 前瞻方向**

8. **Clifford 傅里叶与"转子谱"。** 把复数单位 \(i\) 换成二重向量 \(I\)，把信号值换成多重向量，得到 Clifford/超复 Fourier 变换；每个频率分量不再是一根复指数，而是一个旋转平面中的转子。可以研究：任意空间曲线的转子谱稀疏性、收敛速度，以及"用少量转子逼近目标曲线"的算法。这会直接升级本文的计算外摆线。

9. **环面上的 Dirac 算子与旋量傅里叶。** 在平坦环面 \(T^n\) 上，Dirac 算子
   $$
   D=\sum_{k=1}^{n}e_k\partial_k
   $$
   的特征函数是旋量值的傅里叶模态；\(D\psi=0\) 的解（单演函数，monogenic functions）是复解析函数在高维的推广。第七节的椭圆函数可以看作"双周期单演函数"的特例。这条线把环面、复结构、傅里叶与旋量真正接在一起。

10. **几何微积分驱动的曲线流生成艺术。** 用 \(\partial_t\gamma=\partial_s^2\gamma\)（曲线缩短流）、Willmore 流等几何演化方程生成形态；GA 提供无坐标、任意维、易离散的公式。可以做成"输入一笔涂鸦，输出一族演化图案"的交互工具。

11. **GA 等变神经网络（前瞻）。** 把网络特征从标量/向量升级为多重向量，构造对旋转、反射等变的 Clifford 层（Clifford neural layers、Geometric Algebra Transformer 等方向）。对 `cprdspy` 的意义：可以从手绘草图直接学习曲线/图案的参数，而且天然尊重旋转与镜像对称。

12. **时空代数（STA）可视化。** 在 \(\mathrm{Cl}(1,3)\) 中，Lorentz boost 是时间-空间平面内的转子；摆线、螺旋线可以解释为世界线，光锥、双曲运动、相对论视觉效应都可以做成教学动画。这是"几何代数 + 物理美学"的交叉题材。

13. **工具链建议。** Python 端首选 `clifford`（数值）与 `galgebra`（符号），`kingdon` 可作为高性能替代；Web 端 `ganja.js` 可直接在浏览器里做 GA 交互。对 `cprdspy` 建议把 GA 做成**可选依赖**，并为 \(\mathrm{Cl}(2),\mathrm{Cl}(3)\) 提供纯 NumPy 回退，保证无 GA 库时核心绘图仍可用。

**如果只做一件事**：先做第 2 条（曲率/挠率着色）和第 3 条（无奇异管道）。它们不需要引入完整 GA 依赖，却能立刻让现有曲线生成器获得"可解释的几何"与"可实体化的三维形态"，是从本文数学走向可视化的最短路径。

### 8.6 与本文主题的对应表

| 本文对象 | 几何代数 / 几何微积分表述 |
| --- | --- |
| 平面旋转、复数 \(e^{i\theta}\) | 转子 \(R=e^{-I\theta/2}\)，\(I=e_1e_2\) |
| 四元数旋转 | 偶子代数 \(\mathrm{Cl}^+(3)\cong\mathbb{H}\) |
| 球面运动、球面傅里叶 | \(\gamma=\sum_i r_iR_ie_3\tilde R_i\) |
| 环面、Clifford 环面 | 两个交换/嵌套转子的复合 |
| 环面纽结的闭合条件 | 两个转子转速比的有理性 |
| Hopf 纤维化 | \(h(q)=qe_3\tilde q\) 的纤维 \(qe^{-e_3\theta/2}\) |
| 傅里叶级数、DFT | 转子谱 / Clifford Fourier |
| 曲率、挠率 | \(\kappa=\frac{|v\wedge a|}{|v|^3}\)，\(\tau=\frac{(v\wedge a\wedge\dot a)I^{-1}}{|v\wedge a|^2}\) |
| 复结构、椭圆函数 | 二重向量 \(I\) 作为复结构；单演函数 |
| 梯度/散度/旋度/Stokes | 同一个 \(\nabla\) 与基本定理 |

**Python 验证 — 转子外摆线与几何微积分曲率：**
```python
# pip install clifford numpy matplotlib
import numpy as np
import matplotlib.pyplot as plt
from clifford import Cl


def scalar(M):
    """多重向量的标量部分 (clifford 中 value[0] 即标量系数)"""
    return float(np.real(M.value[0]))


def mag(M):
    """多重向量的模长: |M| = sqrt(|<~M M>_0|)"""
    return float(np.sqrt(abs(scalar(~M * M))))


# ---------- (1) 平面转子外摆线：Cl(2) ----------
layout2, blades2 = Cl(2)
e1, e2 = blades2['e1'], blades2['e2']
I = e1 ^ e2                         # 复结构


def rotor(B, theta):
    """单位二重向量 B 张成平面内、转角 theta 的转子"""
    return (-0.5 * theta * B).exp()


def to_xy(v):
    """取出多重向量的 e1, e2 坐标 (bitmask: e1=1, e2=2)"""
    return float(np.real(v.value[1])), float(np.real(v.value[2]))


# 验证：R e1 ~R = cos(theta) e1 + sin(theta) e2
theta = 0.7
R = rotor(I, theta)
print("R e1 ~R =", R * e1 * ~R)

coeffs = [(2.0, 1, 0.0), (1.0, 3, 0.5), (0.5, -5, 1.2), (0.25, 8, 0.0)]
t = np.linspace(0, 2 * np.pi, 2000)

# (a) 逐点用 GA 计算（抽样，验证用）
pts = []
for ti in t[::50]:
    acc = 0 * e1
    for r, w, phi in coeffs:
        R = rotor(I, w * ti + phi)
        acc += r * (R * e1 * ~R)
    pts.append(to_xy(acc))
pts = np.array(pts)

# (b) 等价的 numpy 闭式（批量绘图用）
x = sum(r * np.cos(w * t + phi) for r, w, phi in coeffs)
y = sum(r * np.sin(w * t + phi) for r, w, phi in coeffs)

plt.figure(figsize=(6, 6))
plt.plot(x, y, lw=1, label='转子外摆线')
plt.plot(pts[:, 0], pts[:, 1], 'r.', ms=8, label='GA 逐点验证')
plt.axis('equal')
plt.legend()
plt.title(r'Rotor epicycles: $\sum_i r_i R_i e_1 \tilde{R}_i$')
plt.show()

# ---------- (2) 几何微积分：环面螺旋线的 κ, τ ----------
layout3, blades3 = Cl(3)
E1, E2, E3 = blades3['e1'], blades3['e2'], blades3['e3']
I3 = E1 ^ E2 ^ E3

R0, r0, omega = 2.0, 0.6, 7
s = np.linspace(0, 2 * np.pi, 1200)
X = (R0 + r0 * np.cos(omega * s)) * np.cos(s)
Y = (R0 + r0 * np.cos(omega * s)) * np.sin(s)
Z = r0 * np.sin(omega * s)


def d(q):
    return np.gradient(q, s)


vx, vy, vz = d(X), d(Y), d(Z)
ax, ay, az = d(vx), d(vy), d(vz)
jx, jy, jz = d(ax), d(ay), d(az)

kappa = np.zeros_like(s)
tau = np.zeros_like(s)
for i in range(len(s)):
    v = vx[i] * E1 + vy[i] * E2 + vz[i] * E3
    a = ax[i] * E1 + ay[i] * E2 + az[i] * E3
    da = jx[i] * E1 + jy[i] * E2 + jz[i] * E3
    B = v ^ a
    kappa[i] = mag(B) / mag(v) ** 3
    tau[i] = scalar((B ^ da) * I3.inv()) / mag(B) ** 2

fig = plt.figure(figsize=(14, 5))
ax1 = fig.add_subplot(121, projection='3d')
p = ax1.scatter(X, Y, Z, c=kappa, cmap='plasma', s=4)
ax1.set_title('环面螺旋线：按曲率 κ 着色')
fig.colorbar(p, ax=ax1, shrink=0.6, label='κ')
ax2 = fig.add_subplot(122)
ax2.plot(s, kappa, label='曲率 κ')
ax2.plot(s, tau, label='挠率 τ', alpha=0.7)
ax2.set_xlabel('s')
ax2.legend()
ax2.set_title('几何微积分：κ 与 τ')
plt.tight_layout()
plt.show()
```

**延伸阅读（按入门顺序）**

- D. Hestenes, *Clifford Algebra to Geometric Calculus* —— 几何微积分的源头。
- C. Doran & A. Lasenby, *Geometric Algebra for Physicists* —— 物理与可视化直觉最好的教材之一。
- E. Hitzer, *Introduction to Clifford's Geometric Algebra* —— 简短综述，适合快速建立坐标系。
- L. Dorst, D. Fontijne & S. Mann, *Geometric Algebra for Computer Science* —— CGA 与图形学的桥梁。
- `clifford`（Python）、`galgebra`（符号）、`ganja.js`（WebGL）—— 可立即上手的工具链。

**本节小结**：如果说环面是"圆的乘积"，那么几何代数就是"圆与旋转的代数"——它用一个几何积同时编码度量、平面与旋转；几何微积分则让这个代数可以求导、积分与流动。本文从复数出发，经过四元数，最终抵达的不是一个终点，而是一整套可以继续生长的语言。

---

**小结**：这份文档从环面出发，经螺旋线、摆线、傅里叶级数，最终抵达三维球面运动——这条线索本身就是数学中"圆"的万有性（universality）的缩影。上述八个方向——纽结拓扑、Hopf 纤维化、四元数代数、可积系统、计算外摆线、高维推广、复解析、几何代数与几何微积分——每一个都是同一主题的不同侧面。它们共同指向一个深刻的数学事实：

**圆是最简单的周期运动，而环面是圆与圆的乘积。当我们在环面上绕行时，既在画几何图案，也在写动力学方程，还在编织拓扑不变量——这三者本是一回事。**

**而几何代数把这"一回事"写成了一个乘法：度量、旋转与维度，都是同一个几何积的不同分量。**

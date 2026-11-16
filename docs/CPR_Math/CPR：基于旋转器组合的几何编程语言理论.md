# CPR：基于旋转器组合的几何编程语言理论

## ——从圆周运动、摆线与傅里叶级数到高维几何程序

**版本：0.1 · 理论草案**

---

# 摘要

CPR 是一种面向几何生成、几何动画与几何计算的编程语言构想。

本文提出一种基本观点：

> **复杂几何可以被理解为基本运动的组合，而基本运动可以由旋转器（Rotor）描述。**

这一思想最初来自圆周运动、摆线和环面螺旋线的研究。当一个圆的圆心沿另一个圆运动时，得到摆线、外摆线、内摆线以及更一般的旋轮线；当多个圆周运动进行叠加时，可以得到有限 Fourier 型曲线；当运动进入三维空间时，球面参数化、四元数旋转以及 \(SO(3)\) 的结构自然出现。

因此，本文尝试建立如下理论链：

$$
\boxed{
\text{Circle}
\rightarrow
\text{Rotor}
\rightarrow
\text{Motion Composition}
\rightarrow
\text{Fourier Geometry}
\rightarrow
\text{Spatial Geometry}
\rightarrow
\text{Geometric Programming}
}
$$

CPR 的目标不是建立一个包含大量 `circle()`、`spiral()`、`torus()` 等预定义图形函数的传统绘图库，而是建立一个较小而具有生成能力的几何语言核心。

本文进一步提出：

$$
\boxed{
\text{Geometry}
=
\text{Composition of Motions}
}
$$

作为 CPR 的核心研究假设。

---

# 1. 引言：为什么需要一种几何编程语言

传统程序语言主要描述：

$$
\text{数据}
+
\text{控制流}
+
\text{算法}.
$$

传统绘图库则通常描述：

$$
\text{图元}
+
\text{坐标}
+
\text{变换}.
$$

例如，一个几何系统可能提供：

```text
circle()
rectangle()
polygon()
sphere()
torus()
bezier()
```

这些接口非常直接，但它们存在一个根本问题：

> **复杂图形往往不是由“一个复杂图元”产生的，而是由多个简单运动共同产生的。**

摆线就是一个典型例子。

设半径为 \(R\) 的圆沿直线滚动，圆周上一点的轨迹为：

$$
x=r(t-\sin t),
$$

$$
y=r(1-\cos t).
$$

外摆线则来自一个圆绕另一个圆的滚动：

$$
\begin{aligned}
x&=(R+r)\cos\theta-r\cos\left(\frac{R+r}{r}\theta\right),\\
y&=(R+r)\sin\theta-r\sin\left(\frac{R+r}{r}\theta\right).
\end{aligned}
$$

将其重新解释，可以得到：

$$
x=R_1\cos\theta+r\cos(n\theta+\phi),
$$

$$
y=R_1\sin\theta+r\sin(n\theta+\phi).
$$

于是，一个看似特殊的“摆线公式”，变成了：

$$
\boxed{\text{一个圆周运动}+\text{另一个圆周运动}}
$$

这成为 CPR 理论的第一个出发点。

---

# 2. 从摆线到运动组合

## 2.1 两个圆周运动

考虑：

$$
\gamma(t)
=
r_1
\begin{pmatrix}
\cos(\omega_1t+\phi_1)\\
\sin(\omega_1t+\phi_1)
\end{pmatrix}
+
r_2
\begin{pmatrix}
\cos(\omega_2t+\phi_2)\\
\sin(\omega_2t+\phi_2)
\end{pmatrix}.
$$

令：

$$
z=x+iy,
$$

则：

$$
\boxed{
z(t)
=
r_1e^{i(\omega_1t+\phi_1)}
+
r_2e^{i(\omega_2t+\phi_2)}
}
$$

这就是两个旋转运动的叠加。

当：

$$
\omega_1=1,\qquad \omega_2=n,
$$

便得到典型的外摆线/中心摆线型结构。

---

## 2.2 多个圆周运动

自然推广为：

$$
\boxed{
z(t)=
\sum_{k=1}^{N}
r_ke^{i(\omega_kt+\phi_k)}
}
$$

或者实数形式：

$$
\boxed{
\begin{aligned}
x(t)&=
\sum_{k=1}^{N}
r_k\cos(\omega_kt+\phi_k),\\
y(t)&=
\sum_{k=1}^{N}
r_k\sin(\omega_kt+\phi_k).
\end{aligned}}
$$

这就是 CPR 最基本的二维运动组合形式。

本文将这种基本运动称为：

# Rotor

---

# 3. 定义一：二维旋转器

## Definition 3.1 ——二维旋转器

给定：

* 半径 \(r\ge0\)
* 角频率 \(\omega\)
* 初始相位 \(\phi\)

定义二维旋转器：

$$
\boxed{
R(r,\omega,\phi;t)
=
r
\begin{pmatrix}
\cos(\omega t+\phi)\\
\sin(\omega t+\phi)
\end{pmatrix}
}
$$

等价地：

$$
\boxed{
R(r,\omega,\phi;t)
=
re^{i(\omega t+\phi)}
}
$$

其中复数表示仅用于数学表达；几何对象本身仍然是 \(\mathbb R^2\) 中的向量。

---

# 4. 定义二：旋转器组合

给定 \(N\) 个旋转器：

$$
R_1,R_2,\dots,R_N,
$$

定义它们的组合：

$$
\boxed{
\Gamma(t)
=
p+
\sum_{k=1}^{N}R_k(t)
}
$$

其中 \(p\in\mathbb R^2\) 为基准位置。

我们称：

$$
\Gamma
$$

为一个 **Rotor Composition**。

即：

$$
\boxed{
\text{Rotor Composition}
=
\text{Point}
+
\sum \text{Rotor}
}
$$

这将成为 CPR 的第一类核心几何程序。

---

# 5. 几何程序的第一个例子

例如：

```cpr
r1 = rotor(radius=3, frequency=1)
r2 = rotor(radius=2, frequency=7)
r3 = rotor(radius=1, frequency=13)

curve = r1 + r2 + r3
```

其数学语义定义为：

$$
\gamma(t)
=
3e^{it}
+
2e^{7it}
+
e^{13it}.
$$

因此：

```text
r1 + r2 + r3
```

并不是简单的数据相加，而是：

> **三个运动状态的几何叠加。**

---

# 6. “圆”不再是 CPR 的最高层概念

传统几何系统通常将：

$$
Circle
$$

视为基本对象。

CPR 则尝试反过来：

$$
\boxed{
Circle = Rotor
}
$$

即：

$$
\operatorname{Circle}(r)
=
R(r,1,0;t).
$$

这意味着：

```cpr
circle(radius=5)
```

可以被理解为一种语法糖：

```cpr
rotor(radius=5, frequency=1)
```

因此，圆不是特殊对象，而是最简单的周期运动。

---

# 7. 从 Rotor 到 Fourier

设：

$$
\Gamma(t)
=
\sum_{k=1}^{N}
r_ke^{i(\omega_kt+\phi_k)}.
$$

当：

$$
\omega_k=k\omega_0
$$

时：

$$
\Gamma(t)
=
\sum_{k=1}^{N}
r_ke^{i(k\omega_0t+\phi_k)}.
$$

这与 Fourier 级数具有直接联系。

更一般地，一个周期函数可以表示为：

$$
f(t)
=
\sum_{k=-\infty}^{\infty}
c_ke^{ik\omega_0t}.
$$

因此，CPR 可以将 Fourier 分解重新解释为：

$$
\boxed{
\text{Fourier Series}
=
\text{Infinite Rotor Composition}
}
$$

而有限 Fourier 和对应：

$$
\boxed{
\text{Finite Rotor Composition}
}
$$

---

# 8. 一个重要的数学区分

这里必须严格区分：

$$
\text{精确表示}
$$

与：

$$
\text{逼近}.
$$

有限 Rotor：

$$
\Gamma_N(t)
=
\sum_{k=1}^{N}R_k(t)
$$

只能产生有限频谱的函数族。

对于一般周期曲线，通常需要：

$$
N\rightarrow\infty
$$

才能得到完整的 Fourier 展开。

因此，CPR 的更严谨表述不是：

> 有限个旋转器可以精确表示任意曲线。

而是：

> 在适当的函数空间和参数化条件下，一般周期曲线可以通过增加旋转器数量获得任意精度的逼近。

这一区分是 CPR 理论必须保留的数学基础。

---

# 9. Definition 3：Rotor Approximation

给定目标周期曲线：

$$
\gamma:S^1\rightarrow\mathbb R^n,
$$

若存在 Rotor Composition：

$$
\gamma_N(t)
=
p+
\sum_{k=1}^{N}R_k(t)
$$

使某种误差度量满足：

$$
d(\gamma_N,\gamma)<\varepsilon,
$$

则称：

$$
\gamma_N
$$

为 \(\gamma\) 的一个 \(\varepsilon\)-Rotor Approximation。

---

# 10. 几何逆问题

这立即产生一个与 CPR 编译器直接相关的问题：

给定：

$$
\gamma(t),
$$

寻找：

$$
\{r_k,\omega_k,\phi_k\}_{k=1}^{N}
$$

使：

$$
\gamma(t)
\approx
p+\sum_{k=1}^{N}
r_ke^{i(\omega_kt+\phi_k)}.
$$

这可以通过 Fourier / DFT 完成。

因此：

$$
\boxed{
Geometry
\rightarrow
Fourier Analysis
\rightarrow
Rotor Program
}
$$

可以成为 CPR 的一个核心编译流程。

---

# 11. CPR 的第一个编译器思想

输入：

```text
SVG / sampled curve
```

经过：

```text
Sampling
    ↓
Fourier / DFT
    ↓
Frequency analysis
    ↓
Rotor decomposition
    ↓
CPR program
```

得到：

```cpr
shape =
    rotor(...)
  + rotor(...)
  + rotor(...)
  + rotor(...)
```

因此 CPR 不仅可以：

$$
\text{Program}\rightarrow\text{Geometry},
$$

还可以研究：

$$
\boxed{
\text{Geometry}\rightarrow\text{Program}
}
$$

这构成 CPR 的“几何反编译”方向。

---

# 12. 定义四：旋转器链

当旋转器不是全部从同一个固定点出发，而是首尾连接时，定义：

$$
P_0(t)=p
$$

$$
P_1(t)=P_0(t)+R_1(t)
$$

$$
P_2(t)=P_1(t)+R_2(t)
$$

一般地：

$$
\boxed{
P_k(t)
=
P_{k-1}(t)+R_k(t)
}
$$

最终：

$$
P_N(t)
=
p+\sum_{k=1}^{N}R_k(t).
$$

称：

$$
P_0,P_1,\dots,P_N
$$

为 **Rotor Chain**。

---

# 13. Rotor Chain 与传统外摆线

外摆线的经典图像实际上可以看成非常特殊的 Rotor Chain：

```text
O
│
├── Rotor 1
│
└── Rotor 2
        ↓
      Trace
```

因此：

```cpr
trace(
    rotor(5, 1)
  + rotor(2, 7)
)
```

即可产生一类中心摆线/外摆线型曲线。

这里：

```text
trace
```

表示记录末端点：

$$
\gamma(t)=P_N(t).
$$

---

# 14. 时间参数成为 CPR 的基本坐标

传统几何语言通常把：

$$
x,y,z
$$

视为空间坐标。

CPR 中还需要把：

$$
t
$$

提升为一等公民。

因为：

$$
\gamma(t)
$$

同时具有两个含义：

1. 一条参数曲线；
2. 一个随时间运动的对象。

因此：

$$
\boxed{
Geometry = State(t)
}
$$

而：

$$
\boxed{
Animation = Evaluation\ of\ Geometry\ at\ time\ t
}
$$

这意味着 CPR 可以天然统一：

```text
geometry
animation
simulation
trajectory
```

---

# 15. 三维推广

二维旋转器使用：

$$
(\cos\theta,\sin\theta).
$$

进入三维后，可以使用球面单位向量：

$$
u(\theta,\varphi)
=
\begin{pmatrix}
\cos\theta\cos\varphi\\
\cos\theta\sin\varphi\\
\sin\theta
\end{pmatrix}.
$$

因此定义三维球面旋转器：

$$
\boxed{
R_3(r,\theta,\varphi;t)
=
r\,u(\theta(t),\varphi(t))
}
$$

即：

$$
R_3=
r
\begin{pmatrix}
\cos\theta(t)\cos\varphi(t)\\
\cos\theta(t)\sin\varphi(t)\\
\sin\theta(t)
\end{pmatrix}.
$$

当：

$$
\theta(t)=\alpha t+\delta,
$$

$$
\varphi(t)=\beta t+\gamma,
$$

得到：

$$
\boxed{
R_3(t)
=
r
\begin{pmatrix}
\cos(\alpha t+\delta)\cos(\beta t+\gamma)\\
\cos(\alpha t+\delta)\sin(\beta t+\gamma)\\
\sin(\alpha t+\delta)
\end{pmatrix}
}
$$

这正是 CPR 原始研究中提出的球面运动基本形式。

---

# 16. 三维 Rotor Composition

于是：

$$
\boxed{
\gamma(t)
=
p+
\sum_{k=1}^{N}
R_{3,k}(t)
}
$$

即：

$$
\begin{aligned}
x(t)
&=
p_x+
\sum_k r_k
\cos\theta_k(t)
\cos\varphi_k(t),\\
y(t)
&=
p_y+
\sum_k r_k
\cos\theta_k(t)
\sin\varphi_k(t),\\
z(t)
&=
p_z+
\sum_k r_k
\sin\theta_k(t).
\end{aligned}
$$

这构成 CPR 的第一种三维生成模型。

---

# 17. 球面 Rotor 与 Cartesian Fourier

你的研究已经给出了一个非常重要的联系。

利用：

$$
\cos A\cos B
=
\frac12[\cos(A+B)+\cos(A-B)],
$$

以及：

$$
\cos A\sin B
=
\frac12[\sin(A+B)-\sin(A-B)],
$$

三维球面 Rotor 可以展开为 Cartesian Fourier 频率组合。

因此一个球面 Rotor 并不是一个神秘的新对象，而是：

$$
\boxed{
\text{多个 Cartesian harmonic components 的结构化组合}
}
$$

这给出了两个不同的表示层：

### Cartesian Representation

适合：

* Fourier 分析
* DFT
* 数值拟合
* 通用曲线表示

### Rotor Representation

适合：

* 几何直觉
* 动画
* 运动层级
* 参数设计
* CPR 程序表达

两者应当作为 CPR 内部的两种等价/相关表示，而不是互相竞争。

---

# 18. 四元数层

三维旋转进一步可以使用单位四元数：

$$
q=
\cos\frac{\theta}{2}
+
\mathbf u\sin\frac{\theta}{2},
$$

其中：

$$
|\mathbf u|=1.
$$

三维向量可以嵌入纯四元数：

$$
v=xi+yj+zk.
$$

旋转可以写成：

$$
\boxed{
v'
=
qvq^{-1}
}
$$

因此，CPR 的三维 Rotor 可以进一步解释为：

$$
\boxed{
\text{Vector}
\xrightarrow{\quad q\quad}
\text{Rotated Vector}
}
$$

原研究已经将球面表达式与：

$$
q\mathbf{k}\bar q
$$

联系起来。

---

# 19. 从 Complex 到 Quaternion

CPR 的数学结构因此呈现：

$$
\boxed{
\mathbb C
\rightarrow
\mathbb H
}
$$

二维：

$$
e^{i\theta}
$$

描述平面旋转。

三维：

$$
qvq^{-1}
$$

描述空间旋转。

这提示一个进一步研究方向：

$$
\boxed{
\mathbb C
\rightarrow
\mathbb H
\rightarrow
Cl_n
}
$$

即从复数、四元数进一步进入 Clifford / Geometric Algebra，以寻找统一的高维旋转表达。

这一部分目前作为 CPR 的**理论研究方向**，而不是已经完成的语言规范。

---

# 20. 环面：两个独立周期的乘积

环面可以写为：

$$
T^2=S^1\times S^1.
$$

标准参数方程：

$$
\begin{aligned}
x&=(R+r\cos v)\cos u,\\
y&=(R+r\cos v)\sin u,\\
z&=r\sin v.
\end{aligned}
$$

如果令：

$$
u=pt,\qquad v=qt,
$$

则得到：

$$
\boxed{
\begin{aligned}
x&=(R+r\cos qt)\cos pt,\\
y&=(R+r\cos qt)\sin pt,\\
z&=r\sin qt.
\end{aligned}
}
$$

这就是环面上的动力轨迹。

当 \(p/q\) 为有理数时，轨迹具有闭合周期；当频率比满足适当无理性条件时，则出现准周期行为。你的原研究已经沿这一方向将环面螺旋线联系到动力系统与 Kronecker 型稠密轨道。

---

# 21. 一个关键展开

注意：

$$
x+iy
=
(R+r\cos qt)e^{ipt}.
$$

利用：

$$
\cos qt
=
\frac12(e^{iqt}+e^{-iqt}),
$$

得到：

$$
\boxed{
x+iy
=
Re^{ipt}
+
\frac r2e^{i(p+q)t}
+
\frac r2e^{i(p-q)t}.
}
$$

这说明一个非常重要的事实：

> **环面运动可以在平面投影中表现为多个 Rotor 的频率叠加。**

因此：

$$
\text{Torus Motion}
$$

与：

$$
\text{Rotor Composition}
$$

之间存在直接的代数联系。

这为 CPR 将 Fourier、环面运动和拓扑曲线统一到同一个语言核心提供了依据。

---

# 22. Rotor 与拓扑

对于：

$$
\gamma(t)
=
(R+r\cos qt)
(\cos pt,\sin pt)
+
(0,0,r\sin qt),
$$

当 \(p,q\) 互质时得到典型的 \((p,q)\) 环面纽结参数化。

因此 CPR 中的：

```cpr
torus_knot(p, q)
```

理论上不应被视为最底层 primitive。

更基础的表达应当是：

```cpr
torus_motion(
    major_frequency=p,
    minor_frequency=q
)
```

然后：

```text
torus_knot
```

只是该运动的拓扑解释。

这是 CPR 一个重要的设计原则：

> **高层几何名称应该尽可能是低层运动结构的派生概念。**

---

# 23. Motion Graph

当一个 Rotor 的起点不再固定，而是另一个运动的终点时：

$$
P_1(t)=R_1(t),
$$

$$
P_2(t)=P_1(t)+R_2(t),
$$

$$
P_3(t)=P_2(t)+R_3(t),
$$

就形成了运动层级。

因此 CPR 内部不应只保存普通 AST，而可以考虑一种：

$$
\boxed{
Motion\ Graph
}
$$

其中节点代表：

```text
Point
Rotor
Transform
Curve
Surface
```

边表示：

```text
attached-to
composed-with
transformed-by
traced-by
```

这为以后实现复杂动画、机械结构、行星系统以及程序化建模提供基础。

---

# 24. CPR 的核心代数对象

第一版可以暂定：

$$
\boxed{
\mathcal G=
\{
Scalar,
Vector,
Point,
Rotor,
Transform,
Curve,
Surface,
Solid
\}
}
$$

其中：

### Scalar

$$
s\in\mathbb R
$$

### Vector

$$
v\in\mathbb R^n
$$

### Point

$$
p\in\mathbb R^n
$$

### Rotor

$$
R(t)\in\mathbb R^n
$$

### Curve

$$
\gamma:I\rightarrow\mathbb R^n
$$

### Surface

$$
S:U\rightarrow\mathbb R^3
$$

### Solid

三维空间中的体对象。

---

# 25. 核心运算符

CPR 第一版理论可以考虑：

$$
+
$$

运动叠加：

$$
R_1+R_2.
$$

$$
\circ
$$

变换组合：

$$
T_1\circ T_2.
$$

$$
@
$$

层级附着：

$$
child@parent.
$$

$$
\operatorname{trace}
$$

记录运动轨迹：

$$
\gamma(t)=P(t).
$$

$$
\operatorname{sample}
$$

离散采样：

$$
\{P(t_0),\dots,P(t_N)\}.
$$

---

# 26. 第一版 CPR 示例

二维：

```cpr
r1 = rotor(radius=3, frequency=1)
r2 = rotor(radius=2, frequency=7)
r3 = rotor(radius=1, frequency=13)

curve = trace(r1 + r2 + r3)
```

三维：

```cpr
r1 = rotor3(radius=3, theta=1*t, phi=2*t)
r2 = rotor3(radius=1, theta=7*t, phi=11*t)

curve = trace(r1 + r2)
```

环面运动：

```cpr
torus =
    orbit(
        major=3,
        minor=1,
        major_frequency=5,
        minor_frequency=7
    )
```

其核心不是 `torus()` 这个名字，而是两个周期运动的组合。

---

# 27. Geometry → Program

对于一条已有曲线：

```cpr
shape = import("shape.svg")
```

可以进行：

```cpr
program = decompose(shape, basis=rotor)
```

得到：

```cpr
shape =
    rotor(...)
  + rotor(...)
  + rotor(...)
  + ...
```

然后：

```cpr
error(program, shape)
```

给出：

$$
\varepsilon.
$$

这使 CPR 具有：

$$
\boxed{
\text{生成}
+
\text{分析}
+
\text{反演}
}
$$

三种能力。

---

# 28. Rotor Complexity

定义目标曲线 \(\gamma\) 的 \(\varepsilon\)-Rotor 复杂度：

$$
\boxed{
C_\varepsilon(\gamma)
=
\min
\left\{
N:
d(\gamma,\gamma_N)<\varepsilon
\right\}.
}
$$

其中：

$$
\gamma_N
=
\sum_{k=1}^{N}R_k.
$$

这只是一个**研究定义**，目前不宣称它具有某种已经证明的唯一性或最优算法。

它提出了一个值得研究的问题：

> 一个几何对象需要多少个基本运动才能描述？

这可能成为 CPR 理论中的一种几何复杂度概念。

---

# 29. CPR 的第一条核心猜想

## Rotor Universality Conjecture

设：

$$
\gamma:S^1\rightarrow\mathbb R^n
$$

为满足适当正则性条件的周期曲线。

猜想存在一列有限 Rotor Composition：

$$
\gamma_N(t)
=
p+
\sum_{k=1}^{N}R_k(t)
$$

使：

$$
\gamma_N\rightarrow\gamma
$$

在适当函数空间中成立。

该命题需要针对：

* 函数空间；
* 参数化；
* 收敛范数；
* Rotor 的允许形式；

分别进行严格定义。

因此在当前版本中，它应标记为：

$$
\boxed{\text{Conjecture / Research Problem}}
$$

而不是定理。

---

# 30. 第二条研究路线：高维 Rotor

二维使用：

$$
\mathbb C.
$$

三维使用：

$$
\mathbb H.
$$

进一步研究：

$$
Cl_n
$$

中的旋转。

目标是寻找统一表达：

$$
\boxed{
Rotor_n(t)=e^{B t}
}
$$

其中 \(B\) 为适当的旋转生成元。

如果这一框架成立，则 CPR 可以获得：

$$
2D,\ 3D,\ 4D,\dots,nD
$$

统一的运动模型。

---

# 31. 第三条研究路线：Frequency Geometry

对 Rotor Composition：

$$
\gamma(t)
=
\sum_iR_i(t),
$$

定义频率集合：

$$
\Omega=\{\omega_1,\omega_2,\dots,\omega_N\}.
$$

研究：

$$
\operatorname{rank}_{\mathbb Q}(\Omega).
$$

频率之间的有理关系决定轨迹的周期性结构。

因此：

```cpr
curve.closed
curve.period
curve.frequency_rank
curve.resonance
```

可以成为 CPR 的分析能力。

这会把 CPR 从单纯几何语言推进到：

$$
\boxed{
Geometry + Dynamical Systems
}
$$

---

# 32. 第四条研究路线：Hopf 与高维结构

原研究进一步进入：

$$
S^1\hookrightarrow S^3\rightarrow S^2
$$

的 Hopf 纤维化，并将球面运动与四元数联系起来。

这提示一个更深层的问题：

> CPR 的 Rotor 是否可以不仅生成曲线，还能生成纤维化、环面、纽结以及高维投影结构？

因此未来可以研究：

```cpr
fiber(...)
lift(...)
project(...)
hopf(...)
```

但这些不应进入 CPR 0.1 的核心语法；它们应该作为高级数学模块。

---

# 33. CPR 的理论分层

因此暂定：

```text
CPR
│
├── Level 0：Scalar / Vector / Point
│
├── Level 1：Rotor
│
├── Level 2：Rotor Composition
│
├── Level 3：Curve / Surface / Solid
│
├── Level 4：Fourier / DFT
│
├── Level 5：Quaternion / Rotation
│
├── Level 6：Motion Graph
│
├── Level 7：Topology / Dynamical Systems
│
└── Level 8：Clifford / Higher Dimensions
```

其中真正的核心应该尽量保持很小：

$$
\boxed{
Point+Vector+Rotor+Transform+Trace
}
$$

其余大量几何对象都应该尽可能从它们构造出来。

---

# 34. CPR 的核心哲学

传统几何程序通常是：

$$
\boxed{
Shape \rightarrow Draw
}
$$

CPR 希望成为：

$$
\boxed{
Motion \rightarrow Geometry
}
$$

进一步：

$$
\boxed{
Algebra
\rightarrow
Motion
\rightarrow
Geometry
\rightarrow
Animation
}
$$

最终形成：

$$
\boxed{
\text{用最简单的运动，编程最复杂的形状。}
}
$$

英文可以表述为：

> **CPR — Geometry by Composition of Motion.**

---

# 35. 下一阶段的严格研究任务

CPR 理论 V0.1 暂不试图证明全部理论，而确定以下研究任务。

### Problem 1

严格定义二维 Rotor。

### Problem 2

证明二维周期曲线与 Fourier-Rotor 表示之间的关系。

### Problem 3

研究一般椭圆 Fourier 分量如何分解为圆形 Rotor。

### Problem 4

建立 DFT → Rotor Program 的算法。

### Problem 5

定义三维 Rotor，并研究其与 Cartesian Fourier 的关系。

### Problem 6

研究四元数 Rotor 的统一表达。

### Problem 7

定义 Rotor Chain 与 Motion Graph。

### Problem 8

研究 Rotor Composition 的闭合性、周期性和频率结构。

### Problem 9

定义 \(C_\varepsilon\) 并研究其性质。

### Problem 10

研究：

$$
\mathbb C\rightarrow\mathbb H\rightarrow Cl_n
$$

是否能够成为统一的 CPR 高维旋转基础。

---

# 36. 结语

CPR 的研究起点并不是“如何画出更多图形”。

它真正试图回答的问题是：

> **复杂几何是否可以被还原为简单运动的组合？**

从摆线开始：

$$
\text{Circle}
+
\text{Circle}
\rightarrow
\text{Cycloid}
$$

从多个圆周运动：

$$
\sum_iR_i
\rightarrow
\text{Fourier Geometry}
$$

从二维进入三维：

$$
\mathbb C
\rightarrow
\mathbb H
$$

从单一周期进入多个独立周期：

$$
S^1
\rightarrow
T^n
$$

从几何进入动力系统：

$$
\text{Frequency}
\rightarrow
\text{Orbit}
$$

从程序进入反演：

$$
\text{Geometry}
\leftrightarrow
\text{Program}.
$$

因此，CPR 最终希望建立的不是一个“几何函数库”，而是一种：

$$
\boxed{
\textbf{Geometry Programming Algebra}
}
$$

即：

> **以旋转器为基本运动原子，以组合为基本生成规则，以代数为内部基础，以几何为最终表现形式的程序化几何体系。**

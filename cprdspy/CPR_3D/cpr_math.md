# 空间单点旋转

以下是关于空间物体绕单点旋转的完整公式体系及深度解析，结合数学原理与应用场景展开说明：
一、核心旋转公式分类
1. 旋转矩阵法  
适用场景：计算机图形学、机器人运动学  
绕坐标轴旋转（右手系）：  
X轴（俯仰角θ）：  
    $$R_x(\theta) = \begin{bmatrix} 1 & 0 & 0 \\ 0 & \cos\theta & -\sin\theta \\ 0 & \sin\theta & \cos\theta \end{bmatrix}$$  
Y轴（偏航角θ）：  
    $$R_y(\theta) = \begin{bmatrix} \cos\theta & 0 & \sin\theta \\ 0 & 1 & 0 \\ -\sin\theta & 0 & \cos\theta \end{bmatrix}$$  
Z轴（滚转角θ）：  
    $$R_z(\theta) = \begin{bmatrix} \cos\theta & -\sin\theta & 0 \\ \sin\theta & \cos\theta & 0 \\ 0 & 0 & 1 \end{bmatrix}$$  
绕任意轴旋转（Rodrigues公式的矩阵形式）：  
  单位轴向量 \(\mathbf{u} = [ux, uy, u_z]^T\)，旋转角θ：  
  $$
  R = I + \sin\theta [\mathbf{u}]\times + (1-\cos\theta)[\mathbf{u}]\times^2  
  $$  
  其中 \([u]_\times\) 为叉积矩阵：  
  $$[u]\times = \begin{bmatrix} 0 & -uz & uy \\ uz & 0 & -ux \\ -uy & u_x & 0 \end{bmatrix}$$
1. 四元数法  
适用场景：游戏开发、VR/AR（避免万向节死锁）  
单位四元数 \(\mathbf{q} = (w, x, y, z) = \cos\frac{\theta}{2} + \sin\frac{\theta}{2}(ux\mathbf{i} + uy\mathbf{j} + u_z\mathbf{k})\)  
旋转计算：\(\mathbf{v}' = \mathbf{q} \mathbf{v} \mathbf{q}^{-1}\)（\(\mathbf{v}\) 转为纯虚四元数）
1. 欧拉角  
适用场景：飞行器姿态控制（直观但需注意死锁）  
按顺序绕Z-Y-X轴旋转（偏航-俯仰-滚转）：  
  $$R = Rz(\psi) Ry(\theta) R_x(\phi)$$  
局限性：当俯仰角θ=±90°时出现万向节死锁。
二、Rodrigues公式的几何推导  
1. 向量分解  
将向量 \(\mathbf{v}\) 分解为：  
平行于旋转轴的分量 \(\mathbf{v}_{\parallel} = (\mathbf{v} \cdot \mathbf{u})\mathbf{u}\)  
垂直分量 \(\mathbf{v}{\perp} = \mathbf{v} - \mathbf{v}{\parallel}\)  
1. 旋转后的垂直分量  
在垂直平面内旋转θ角，引入正交向量 \(\mathbf{w} = \mathbf{u} \times \mathbf{v}_{\perp}\)：  
$$\mathbf{v}{\perp}' = \cos\theta \mathbf{v}{\perp} + \sin\theta \mathbf{w}$$  
1. 合成最终结果  
$$\mathbf{v}' = \mathbf{v}{\parallel} + \mathbf{v}{\perp}' = \cos\theta \mathbf{v} + (1-\cos\theta)(\mathbf{u} \cdot \mathbf{v})\mathbf{u} + \sin\theta (\mathbf{u} \times \mathbf{v})$$  
三、实际应用注意事项  
1. 旋转中心非原点时：  
   需先平移物体至原点，旋转后再平移回原位置：  
   $$\mathbf{v}' = T^{-1} R T \mathbf{v}$$  
   （\(T\) 为平移矩阵）
 
2. 性能优化：  
四元数适合插值（如SLERP），矩阵适合连续变换。  
避免频繁的欧拉角转换以减少死锁风险。
 
1. 物理引擎中的角速度：  
   角速度 \(\boldsymbol{\omega}\) 与旋转导数关系：  
   $$\frac{dR}{dt} = [\boldsymbol{\omega}]_\times R$$
四、可视化理解  
右手定则：拇指指向旋转轴 \(\mathbf{u}\)，四指弯曲方向为θ正方向。  
交互示例：  
  python 
Python示例：使用scipy的Rotation类
  from scipy.spatial.transform import Rotation 
  axis = [0, 1, 0]  # Y轴
  angle_deg = 45
  rot = Rotation.fromrotvec(np.radians(angledeg) * axis)
  v_rotated = rot.apply([1, 0, 0])  # 旋转X轴单位向量
  
五、扩展阅读建议  
李群与李代数：SO(3)群与\(\mathfrak{so}(3)\)代数的指数映射。  
四元数微分方程：描述动态旋转（如IMU数据融合）。  
 
如需具体领域的深入探讨（如机器人逆运动学或游戏引擎实现），可进一步补充说明！


以上内容均由AI搜集总结并生成，仅供参考

空间物体绕单点（即空间中某一点，不一定是坐标原点）旋转的公式，通常涉及以下步骤：

一、问题描述

给定一个三维空间中的点 P（坐标为 \(\mathbf{p} = (x, y, z)\)），要将其绕空间中某一点 C（坐标为 \(\mathbf{c} = (c_x, c_y, c_z)\)）按某个轴（单位向量 \(\mathbf{u} = (u_x, u_y, u_z)\)）旋转角度 \(\theta\)，求旋转后的新位置 \(\mathbf{p}'\)。

二、解决思路（三步法）

1. 平移：将旋转中心 C 平移到原点
\[
\mathbf{p}_1 = \mathbf{p} - \mathbf{c}
\]

2. 绕原点旋转：使用罗德里格斯旋转公式（Rodrigues' rotation formula）或旋转矩阵对 \(\mathbf{p}_1\) 绕单位向量 \(\mathbf{u}\) 旋转角度 \(\theta\)
\[
\mathbf{p}_2 = \mathbf{p}_1 \cos\theta + (\mathbf{u} \times \mathbf{p}_1) \sin\theta + \mathbf{u} (\mathbf{u} \cdot \mathbf{p}_1)(1 - \cos\theta)
\]

3. 平移回去：将结果平移回原坐标系
\[
\mathbf{p}' = \mathbf{p}_2 + \mathbf{c}
\]

三、罗德里格斯公式详解

若 \(\mathbf{v}\) 是任意向量，绕单位向量 \(\mathbf{u}\) 旋转 \(\theta\) 后的结果为：
\[
\mathbf{v}_{\text{rot}} = \mathbf{v} \cos\theta + (\mathbf{u} \times \mathbf{v}) \sin\theta + \mathbf{u} (\mathbf{u} \cdot \mathbf{v})(1 - \cos\theta)
\]

该公式适用于任意轴方向的旋转。

四、用旋转矩阵表示（可选）

也可以先构造绕任意轴 \(\mathbf{u}\) 的 3×3 旋转矩阵 \(R\)（基于罗德里格斯公式）：

\[
R =
\begin{bmatrix}
\cos\theta + u_x^2(1-\cos\theta) & u_x u_y(1-\cos\theta) - u_z \sin\theta & u_x u_z(1-\cos\theta) + u_y \sin\theta \\
u_y u_x(1-\cos\theta) + u_z \sin\theta & \cos\theta + u_y^2(1-\cos\theta) & u_y u_z(1-\cos\theta) - u_x \sin\theta \\
u_z u_x(1-\cos\theta) - u_y \sin\theta & u_z u_y(1-\cos\theta) + u_x \sin\theta & \cos\theta + u_z^2(1-\cos\theta)
\end{bmatrix}
\]

然后计算：
\[
\mathbf{p}' = R(\mathbf{p} - \mathbf{c}) + \mathbf{c}
\]

五、特殊情况
若绕 坐标轴（如 x、y、z 轴）旋转，则可直接使用标准旋转矩阵。
若旋转中心是原点（\(\mathbf{c} = \mathbf{0}\)），则无需平移步骤。

六、总结公式（最终形式）

\[
\boxed{
\mathbf{p}' = \mathbf{c} + R(\mathbf{p} - \mathbf{c})
}
\]

其中 \(R\) 是绕单位向量 \(\mathbf{u}\) 旋转 \(\theta\) 的旋转矩阵，或通过罗德里格斯公式直接计算。

如果你有具体的旋转轴（比如绕 z 轴）、旋转角度、旋转中心等，我可以给出更具体的表达式。是否需要？



# Rodrigues' rotation formula

（罗德里格斯旋转公式）是描述三维空间中向量绕任意轴旋转的经典方法，其推导过程结合了几何直观与代数运算。以下是详细推导步骤：
1. 问题描述
给定：
单位旋转轴向量 \(\mathbf{u} = (ux, uy, u_z)\)（满足 \(\|\mathbf{u}\| = 1\)），
旋转角度 \(\theta\)，
待旋转向量 \(\mathbf{v}\)。
 
目标：求旋转后的向量 \(\mathbf{v}'\)。
2. 向量分解
将 \(\mathbf{v}\) 分解为平行于旋转轴 \(\mathbf{u}\) 的分量 \(\mathbf{v}{\parallel}\) 和垂直于 \(\mathbf{u}\) 的分量 \(\mathbf{v}{\perp}\)：
\[ 
\mathbf{v} = \mathbf{v}{\parallel} + \mathbf{v}{\perp}
\]
其中：
平行分量：\(\mathbf{v}_{\parallel} = (\mathbf{v} \cdot \mathbf{u}) \mathbf{u}\)（投影到 \(\mathbf{u}\)），
垂直分量：\(\mathbf{v}{\perp} = \mathbf{v} - \mathbf{v}{\parallel}\)。
 
几何意义：旋转时，\(\mathbf{v}{\parallel}\) 不变，\(\mathbf{v}{\perp}\) 在垂直于 \(\mathbf{u}\) 的平面内旋转。
3. 垂直分量的旋转
在垂直于 \(\mathbf{u}\) 的平面内，\(\mathbf{v}{\perp}\) 旋转角度 \(\theta\) 后得到 \(\mathbf{v}{\perp}'\)。  
可通过以下步骤构造：
1. 建立正交基：  
   设 \(\mathbf{w} = \mathbf{u} \times \mathbf{v}{\perp}\)（方向满足右手定则），则 \(\{\mathbf{v}{\perp}, \mathbf{w}, \mathbf{u}\}\) 构成正交坐标系。
2. 极坐标表示：  
   旋转后的分量可表示为：
   \[
   \mathbf{v}{\perp}' = \cos\theta \, \mathbf{v}{\perp} + \sin\theta \, \mathbf{w}
   \]
   其中 \(\mathbf{w} = \mathbf{u} \times \mathbf{v}{\perp} = \mathbf{u} \times \mathbf{v}\)（因 \(\mathbf{u} \times \mathbf{v}{\parallel} = 0\)）。
4. 合并结果
旋转后的向量为平行分量与旋转后的垂直分量之和：
\[
\mathbf{v}' = \mathbf{v}{\parallel} + \mathbf{v}{\perp}' = (\mathbf{v} \cdot \mathbf{u}) \mathbf{u} + \cos\theta \, \mathbf{v}_{\perp} + \sin\theta \, (\mathbf{u} \times \mathbf{v})
\]
将 \(\mathbf{v}_{\perp} = \mathbf{v} - (\mathbf{v} \cdot \mathbf{u}) \mathbf{u}\) 代入：
\[
\mathbf{v}' = (\mathbf{v} \cdot \mathbf{u}) \mathbf{u} + \cos\theta \, (\mathbf{v} - (\mathbf{v} \cdot \mathbf{u}) \mathbf{u}) + \sin\theta \, (\mathbf{u} \times \mathbf{v})
\]
5. 整理公式
合并同类项，得到 Rodrigues公式：
\[
\mathbf{v}' = \cos\theta \, \mathbf{v} + (1 - \cos\theta)(\mathbf{u} \cdot \mathbf{v}) \mathbf{u} + \sin\theta \, (\mathbf{u} \times \mathbf{v})
\]
 
矩阵形式：  
定义叉积矩阵 \([\mathbf{u}]\times = \begin{bmatrix} 0 & -uz & uy \\ uz & 0 & -ux \\ -uy & u_x & 0 \end{bmatrix}\)，则：
\[
\mathbf{v}' = \left[ I + \sin\theta \, [\mathbf{u}]\times + (1 - \cos\theta) [\mathbf{u}]\times^2 \right] \mathbf{v}
\]
其中 \(I\) 为单位矩阵。
6. 几何验证
平行分量不变：若 \(\mathbf{v} \parallel \mathbf{u}\)，则 \(\mathbf{u} \times \mathbf{v} = 0\)，公式退化为 \(\mathbf{v}' = \mathbf{v}\)。
垂直分量旋转：若 \(\mathbf{v} \perp \mathbf{u}\)，公式简化为 \(\mathbf{v}' = \cos\theta \, \mathbf{v} + \sin\theta \, (\mathbf{u} \times \mathbf{v})\)，符合平面旋转定义。
7. 与旋转矩阵的关系
Rodrigues公式的矩阵形式等价于绕任意轴 \(\mathbf{u}\) 的旋转矩阵 \(R\)：
\[
R = I + \sin\theta \, [\mathbf{u}]\times + (1 - \cos\theta) [\mathbf{u}]\times^2 
\]
8. 应用场景
计算机图形学：高效计算物体旋转。
机器人学：描述关节旋转。
物理学：刚体动力学中的角动量分析。
总结
Rodrigues公式通过向量分解与几何直观，将三维旋转简化为叉积和点积运算，兼具数学严谨性与计算高效性。其核心思想是：将旋转分解为平行分量的保持与垂直分量的圆周运动。


# 四元数与三维旋转
下面我们将从四元数（Quaternion）的角度推导三维旋转，并揭示它与罗德里格斯公式以及李代数指数映射（即 \(\exp(\theta [\mathbf{k}]_\times)\)）之间的深刻联系。

一、目标
用单位四元数表示绕单位轴 \(\mathbf{k}\) 旋转角度 \(\theta\) 的操作；
推导四元数作用于向量的旋转公式；
证明其等价于罗德里格斯公式；
建立四元数、旋转矩阵、李代数指数映射三者之间的关系。

二、四元数基础回顾

一个四元数 \(q\) 可写为：
\[
q = w + x\,\mathbf{i} + y\,\mathbf{j} + z\,\mathbf{k} = (w, \mathbf{v}) \in \mathbb{R}^4
\]
其中标量部 \(w \in \mathbb{R}\)，矢量部 \(\mathbf{v} = (x, y, z) \in \mathbb{R}^3\)。
单位四元数表示旋转

绕单位轴 \(\mathbf{k} \in \mathbb{R}^3\)（\(\ \mathbf{k}\ = 1\)）旋转角度 \(\theta\) 对应的单位四元数为：
\[
q = \cos\frac{\theta}{2} + \sin\frac{\theta}{2} \, (\mathbf{k}_x \mathbf{i} + \mathbf{k}_y \mathbf{j} + \mathbf{k}_z \mathbf{k})
= \left( \cos\frac{\theta}{2},\; \sin\frac{\theta}{2} \, \mathbf{k} \right)
\]
注意：使用 半角 \(\theta/2\) 是关键！

三、四元数旋转向量

将三维向量 \(\mathbf{v}\) 视为纯虚四元数：
\[
p = (0, \mathbf{v})
\]

旋转操作定义为共轭作用：
\[
p' = q \, p \, q^{-1}
\]

由于 \(q\) 是单位四元数，有 \(q^{-1} = q^ = (\cos\frac{\theta}{2}, -\sin\frac{\theta}{2} \mathbf{k})\)

于是：
\[
p' = q \, p \, q^*
\]

计算这个乘积（利用四元数乘法规则），可得结果仍为纯虚四元数，其矢量部分即为旋转后的向量 \(\mathbf{v}_{\text{rot}}\)。

四、显式推导：从四元数到罗德里格斯公式

令：
\(c = \cos\frac{\theta}{2}\)
\(s = \sin\frac{\theta}{2}\)
\(q = (c, s\mathbf{k})\)
\(p = (0, \mathbf{v})\)

先计算 \(q p\)：

\[
q p = (c, s\mathbf{k}) (0, \mathbf{v}) = (-s \mathbf{k} \cdot \mathbf{v},\; c \mathbf{v} + s \mathbf{k} \times \mathbf{v})
\]

再乘以 \(q^ = (c, -s\mathbf{k})\)：

\[
p' = (q p) q^ = (a, \mathbf{b}) (c, -s\mathbf{k})
= \big( a c - \mathbf{b} \cdot (-s\mathbf{k}),\; a(-s\mathbf{k}) + c \mathbf{b} + \mathbf{b} \times (-s\mathbf{k}) \big)
\]

但我们只关心矢量部分（因为结果是纯虚四元数，标量部应为0）。直接计算矢量部：

\[
\begin{aligned}
\mathbf{v}_{\text{rot}}
&= c (c \mathbf{v} + s \mathbf{k} \times \mathbf{v})
s (\mathbf{k} \cdot \mathbf{v}) s \mathbf{k}
s \mathbf{k} \times (c \mathbf{v} + s \mathbf{k} \times \mathbf{v}) \\
&= c^2 \mathbf{v} + c s (\mathbf{k} \times \mathbf{v})
s^2 (\mathbf{k} \cdot \mathbf{v}) \mathbf{k}
c s (\mathbf{k} \times \mathbf{v}) + s^2 \mathbf{k} \times (\mathbf{k} \times \mathbf{v})
\end{aligned}
\]

合并项：
\[
\mathbf{v}_{\text{rot}} = c^2 \mathbf{v} + 2 c s (\mathbf{k} \times \mathbf{v}) + s^2 (\mathbf{k} \cdot \mathbf{v}) \mathbf{k} + s^2 \mathbf{k} \times (\mathbf{k} \times \mathbf{v})
\]

利用向量恒等式：
\[
\mathbf{k} \times (\mathbf{k} \times \mathbf{v}) = \mathbf{k} (\mathbf{k} \cdot \mathbf{v}) - \mathbf{v} (\mathbf{k} \cdot \mathbf{k}) = (\mathbf{k} \cdot \mathbf{v}) \mathbf{k} - \mathbf{v}
\quad (\text{因 } \ \mathbf{k}\ =1)
\]

代入：
\[
s^2 \mathbf{k} \times (\mathbf{k} \times \mathbf{v}) = s^2 [(\mathbf{k} \cdot \mathbf{v}) \mathbf{k} - \mathbf{v}]
\]

所以：
\[
\begin{aligned}
\mathbf{v}_{\text{rot}}
&= c^2 \mathbf{v} + 2cs (\mathbf{k} \times \mathbf{v}) + s^2 (\mathbf{k} \cdot \mathbf{v}) \mathbf{k} + s^2 [(\mathbf{k} \cdot \mathbf{v}) \mathbf{k} - \mathbf{v}] \\
&= (c^2 - s^2) \mathbf{v} + 2cs (\mathbf{k} \times \mathbf{v}) + 2 s^2 (\mathbf{k} \cdot \mathbf{v}) \mathbf{k}
\end{aligned}
\]

利用三角恒等式：
\(c^2 - s^2 = \cos\theta\)
\(2cs = \sin\theta\)
\(2s^2 = 1 - \cos\theta\)

因此：
\[
\boxed{
\mathbf{v}_{\text{rot}} = \mathbf{v} \cos\theta + (\mathbf{k} \times \mathbf{v}) \sin\theta + \mathbf{k} (\mathbf{k} \cdot \mathbf{v}) (1 - \cos\theta)
}
\]

✅ 这正是罗德里格斯旋转公式！

五、与指数映射 \(\exp(\theta [\mathbf{k}]_\times)\) 的关系
1. 李代数视角：so(3) 与 SO(3)
三维旋转群 \(SO(3)\) 的李代数是 \(\mathfrak{so}(3)\)，由反对称矩阵组成。
任意向量 \(\boldsymbol{\omega} = \theta \mathbf{k}\) 可通过“帽子”映射（hat map）变为反对称矩阵：
\[
[\boldsymbol{\omega}]_\times = \theta [\mathbf{k}]_\times
\]
指数映射：
\[
R = \exp([\boldsymbol{\omega}]_\times) = \exp(\theta [\mathbf{k}]_\times)
\]
2. 矩阵指数展开

利用泰勒展开和 \([\mathbf{k}]_\times\) 的性质（如 \([\mathbf{k}]_\times^3 = -[\mathbf{k}]_\times\)），可得：

\[
\exp(\theta [\mathbf{k}]_\times) = I + \sin\theta [\mathbf{k}]_\times + (1 - \cos\theta) [\mathbf{k}]_\times^2
\]

而注意到：
\([\mathbf{k}]_\times \mathbf{v} = \mathbf{k} \times \mathbf{v}\)
\([\mathbf{k}]_\times^2 \mathbf{v} = \mathbf{k} \times (\mathbf{k} \times \mathbf{v}) = (\mathbf{k} \cdot \mathbf{v}) \mathbf{k} - \mathbf{v}\)

因此：
\[
R \mathbf{v} = \mathbf{v} + \sin\theta (\mathbf{k} \times \mathbf{v}) + (1 - \cos\theta) [(\mathbf{k} \cdot \mathbf{v}) \mathbf{k} - \mathbf{v}]
= \mathbf{v} \cos\theta + (\mathbf{k} \times \mathbf{v}) \sin\theta + (\mathbf{k} \cdot \mathbf{v}) \mathbf{k} (1 - \cos\theta)
\]

✅ 再次得到罗德里格斯公式！

六、三者统一关系图

表示方式 数学对象 与旋转的关系
-------- -------- ------------
四元数 \(q = (\cos\frac{\theta}{2}, \sin\frac{\theta}{2} \mathbf{k})\) 通过 \(p' = q p q^*\) 旋转
旋转矩阵 \(R = \exp(\theta [\mathbf{k}]_\times)\) \( \mathbf{v}' = R \mathbf{v} \)
罗德里格斯公式 向量表达式 直接给出 \(\mathbf{v}_{\text{rot}}\)

并且：
四元数 → 旋转矩阵：
\[
R = (2w^2 - 1)I + 2\mathbf{v}\mathbf{v}^\top + 2w[\mathbf{v}]_\times
\quad \text{（其中 } q = (w, \mathbf{v}) \text{）}
\]
旋转矩阵 ↔ 指数映射：\(R = \exp(\theta [\mathbf{k}]_\times)\)
四元数 ↔ 指数映射：两者都是 \(SO(3)\) 的参数化，分别来自 \(S^3\)（双覆盖）和 \(\mathfrak{so}(3)\)
特别地，单位四元数构成的群 \(S^3\) 是 \(SO(3)\) 的双覆盖（每个旋转对应两个四元数：\(q\) 和 \(-q\)）。

七、总结
四元数旋转通过共轭作用实现，天然避免万向节死锁，计算高效；
罗德里格斯公式是四元数或矩阵指数作用于向量的显式结果；
指数映射 \(\exp(\theta [\mathbf{k}]_\times)\) 是李群理论中连接 \(\mathfrak{so}(3)\) 与 \(SO(3)\) 的桥梁；
三者在数学上完全等价，只是表达形式不同，适用于不同场景（图形学常用四元数，控制理论常用李代数）。




# 四元数运算法则
四元数（Quaternion）的乘法是其最核心、也最独特的运算，它不满足交换律（即一般情况下 \( q_1 q_2 \ne q_2 q_1 \)），但满足结合律和分配律。下面我们将系统讲解四元数的乘法法则。

一、四元数的基本形式

一个四元数 \( q \) 通常表示为：

\[
q = w + x\,\mathbf{i} + y\,\mathbf{j} + z\,\mathbf{k}
\]

也可写作标量-向量形式：

\[
q = (w, \mathbf{v}), \quad \text{其中 } \mathbf{v} = (x, y, z) \in \mathbb{R}^3
\]
\( w \in \mathbb{R} \)：实部（标量部分）
\( \mathbf{v} \in \mathbb{R}^3 \)：虚部（向量部分）

二、四元数乘法的定义（代数形式）

设两个四元数：
\[
q_1 = w_1 + x_1 \mathbf{i} + y_1 \mathbf{j} + z_1 \mathbf{k} = (w_1, \mathbf{v}_1)
\]
\[
q_2 = w_2 + x_2 \mathbf{i} + y_2 \mathbf{j} + z_2 \mathbf{k} = (w_2, \mathbf{v}_2)
\]

它们的乘积 \( q = q_1 q_2 = (w, \mathbf{v}) \) 定义为：

\[
\boxed{
q_1 q_2 = \big( w_1 w_2 - \mathbf{v}_1 \cdot \mathbf{v}_2,\; w_1 \mathbf{v}_2 + w_2 \mathbf{v}_1 + \mathbf{v}_1 \times \mathbf{v}_2 \big)
}
\]
✅ 关键点：乘积的标量部包含点积（负号），向量部包含线性组合 + 叉积。

三、推导来源：基于虚单位的乘法规则

四元数的虚单位 \(\mathbf{i}, \mathbf{j}, \mathbf{k}\) 满足以下乘法表（由哈密顿提出）：

\[
\begin{aligned}
\mathbf{i}^2 &= \mathbf{j}^2 = \mathbf{k}^2 = -1 \\
\mathbf{ij} &= \mathbf{k}, \quad \mathbf{ji} = -\mathbf{k} \\
\mathbf{jk} &= \mathbf{i}, \quad \mathbf{kj} = -\mathbf{i} \\
\mathbf{ki} &= \mathbf{j}, \quad \mathbf{ik} = -\mathbf{j}
\end{aligned}
\]

这些规则体现了非交换性和右手定则结构。

通过展开 \( q_1 q_2 \) 的多项式乘法，并应用上述规则，即可得到前述的标量-向量公式。

四、举例计算

设：
\( q_1 = (1, (1, 0, 0)) = 1 + \mathbf{i} \)
\( q_2 = (0, (0, 1, 0)) = \mathbf{j} \)

计算 \( q_1 q_2 \)：
标量部：\( w = 1 \cdot 0 - (1,0,0) \cdot (0,1,0) = 0 - 0 = 0 \)
向量部：
\[
w_1 \mathbf{v}_2 + w_2 \mathbf{v}_1 + \mathbf{v}_1 \times \mathbf{v}_2
= 1 \cdot (0,1,0) + 0 \cdot (1,0,0) + (1,0,0) \times (0,1,0)
= (0,1,0) + (0,0,1) = (0,1,1)
\]

所以：
\[
q_1 q_2 = (0, (0,1,1)) = \mathbf{j} + \mathbf{k}
\]

而反过来：
\[
q_2 q_1 = \mathbf{j}(1 + \mathbf{i}) = \mathbf{j} + \mathbf{ji} = \mathbf{j} - \mathbf{k} \ne q_1 q_2
\]

✅ 验证了不可交换性。

五、重要性质

性质 说明
------ ------
非交换性 \( q_1 q_2 \ne q_2 q_1 \)（一般情况）
结合律 \( (q_1 q_2) q_3 = q_1 (q_2 q_3) \)
分配律 \( q_1 (q_2 + q_3) = q_1 q_2 + q_1 q_3 \)
单位元 \( 1 = (1, \mathbf{0}) \)，满足 \( 1 \cdot q = q \cdot 1 = q \)
共轭 \( q^ = (w, -\mathbf{v}) \)，满足 \( q q^ = q^ q = \ q\ ^2 \)
逆元（若 \( q \ne 0 \)） \( q^{-1} = \dfrac{q^}{\ q\ ^2} \)

特别地，单位四元数（\(\ q\ = 1\)）满足 \( q^{-1} = q^ \)，这在旋转中至关重要。

六、矩阵形式（可选）

四元数乘法也可以用矩阵表示。例如，左乘 \( q_1 = (w_1, \mathbf{v}_1) \) 等价于：

\[
q_1 q_2 =
\begin{bmatrix}
w_1 & -x_1 & -y_1 & -z_1 \\
x_1 & w_1 & -z_1 & y_1 \\
y_1 & z_1 & w_1 & -x_1 \\
z_1 & -y_1 & x_1 & w_1
\end{bmatrix}
\begin{bmatrix}
w_2 \\ x_2 \\ y_2 \\ z_2
\end{bmatrix}
\]

类似地可构造右乘矩阵（不同！因为不可交换）。

七、与向量旋转的关系回顾

当用单位四元数 \( q \) 旋转一个向量 \(\mathbf{v}\) 时：

1. 将 \(\mathbf{v}\) 表示为纯虚四元数：\( p = (0, \mathbf{v}) \)
2. 计算：\( p' = q \, p \, q^ \)
3. 结果 \( p' = (0, \mathbf{v}_{\text{rot}}) \)，其向量部即为旋转后的向量

这里两次使用了四元数乘法，且顺序不能颠倒（否则旋转方向错误）。

八、小结

四元数乘法公式（标量-向量形式）是理解和应用四元数的关键：

\[
\boxed{
(w_1, \mathbf{v}_1)(w_2, \mathbf{v}_2) = \big( w_1 w_2 - \mathbf{v}_1 \cdot \mathbf{v}_2,\; w_1 \mathbf{v}_2 + w_2 \mathbf{v}_1 + \mathbf{v}_1 \times \mathbf{v}_2 \big)
}
\]
它融合了点积（标量交互）和叉积（方向旋转）；
非交换性源于叉积的反对称性；
是三维旋转、姿态插值（slerp）、刚体动力学等领域的数学基础。

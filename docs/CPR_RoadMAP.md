# CPR 项目发展路线图

> **核心哲学：用最简单的运动，编程最复杂的形状。**
> **CPR — Geometry by Composition of Motion.**

---

## 阶段零：Rotor 内核（最高优先级）

> 目标：让 Rotor 组合在代码中真正跑起来，替代现有的花/螺线/星形等专用函数。
> 预计工期：1-2 周

### 0.1 定义 Rotor 基础类

- [ ] 实现 `Rotor2D` 类：`radius`, `frequency`, `phase`
- [ ] 实现 `__add__`（运动叠加）和 `__repr__`（数学表达式显示）
- [ ] 底层用复数 `r * exp(i*(ωt + φ))`，接口面向几何直觉
- [ ] 实现 `trace(rotors, t_range, n_points)` → 返回坐标数组

### 0.2 Rotor 组合引擎

- [ ] 实现 `RotorComposition`：多个 Rotor 的叠加
- [ ] 实现 `evaluate(t)` → 复数坐标
- [ ] 实现 `to_xy(t)` → (x, y) 数组，直接可绘图
- [ ] 支持 `direction`（顺/逆时针）和 `center`（中心偏移）

### 0.3 用 Rotor 统一现有图形

- [ ] `circle(r)` = `Rotor(r, 1, 0)`
- [ ] `flower(R, r, n, ratio)` = 若干 Rotor 的组合（推导现有 flowers 函数的 Rotor 分解）
- [ ] `spiral(r, omega)` = `Rotor(r, omega, 0)`（变频率）
- [ ] `star(n)` = Rotor 组合（频率为 n 的倍数）
- [ ] `epicycle(R, r, n)` = `Rotor(R, 1) + Rotor(r, n)`
- [ ] `lissajous(a, b, delta)` = 两个正交 Rotor 的组合
- [ ] **验证：所有现有 cprdspy 图形都能用 Rotor 组合生成**

### 0.4 最小可视化集成

- [ ] `rotor_plot(composition, backend='matplotlib')` 一键绘图
- [ ] `rotor_plot(composition, backend='plotly')` 交互绘图
- [ ] 保持与现有 `cprdspy` 的 API 兼容

**里程碑：`python -c "from cprdspy import *; rotor_plot(Rotor(3,1) + Rotor(1,7))"` 画出外摆线**

---

## 阶段一：3D Rotor 与球面运动

> 目标：把 Rotor 从 2D 推广到 3D，支持球面曲线。
> 预计工期：1-2 周

### 1.1 Rotor3D 类

- [ ] 实现 `Rotor3D`：`radius`, `theta_freq`, `phi_freq`, `theta_phase`, `phi_phase`
- [ ] 底层用球面坐标：`(r cosθ cosφ, r cosθ sinφ, r sinθ)`
- [ ] 支持 `+` 叠加和 `trace3d()`

### 1.2 四元数后端（可选但推荐）

- [ ] 引入 `scipy.spatial.transform.Rotation` 或自实现四元数乘法
- [ ] `Rotor3D` 内部用四元数表示旋转
- [ ] 用户接口保持球面坐标，四元数作为"发动机"

### 1.3 3D 图形生成

- [ ] 环面纽结 `torus_knot(p, q)` = Rotor3D 组合
- [ ] 罗丹线圈 `rhodonea_3d(n, m)` = Rotor3D 组合
- [ ] 球面 Lissajous = 两个 Rotor3D 叠加
- [ ] 多级球面外摆线（文档中已有的验证代码 → 封装为 API）

### 1.4 3D 可视化

- [ ] `rotor_plot3d(composition, backend='plotly')` 3D 交互绘图
- [ ] 支持颜色映射（按弧长、曲率、时间）
- [ ] 支持动画（`animate=True`）

**里程碑：一行代码画出 (5,7) 环面纽结并交互旋转查看**

---

## 阶段二：几何分析工具

> 目标：让 CPR 不仅能"生成"几何，还能"分析"几何。
> 预计工期：1-2 周

### 2.1 曲率与挠率

- [ ] 实现 `curvature(composition, t)` — 用 GA 公式 `κ = |v∧a| / |v|³`
- [ ] 实现 `torsion(composition, t)` — 用 GA 公式 `τ = (v∧a∧ȧ)·I⁻¹ / |v∧a|²`
- [ ] 提供纯 NumPy 回退（不依赖 clifford 库）
- [ ] 曲率/挠率着色绘图 `rotor_plot(comp, color_by='curvature')`

### 2.2 频率分析

- [ ] `frequency_spectrum(composition)` → 返回所有 (ω, r, φ) 列表
- [ ] `is_closed(composition)` → 判断频率比是否有理 → 曲线是否闭合
- [ ] `period(composition)` → 计算最小正周期
- [ ] `resonance(composition)` → 分析频率间的有理关系

### 2.3 Fourier 反编译（杀手功能）

- [ ] `decompose(x, y, n_rotors)` → DFT 提取频率分量 → 返回 Rotor 组合
- [ ] `decompose_svg(filename, n_rotors)` → 从 SVG 反编译
- [ ] `decompose_image(filename, n_rotors)` → 从图片边缘提取 → 反编译
- [ ] `explain(composition)` → 打印数学表达式 + 频率分析 + 拓扑属性

**里程碑：导入一张心形 SVG → `decompose_svg` → 输出 Rotor 程序 → 重新画出心形**

---

## 阶段三：Clifford 代数扩展

> 目标：引入 GA 作为可选后端，统一 2D/3D/5D。
> 预计工期：2-3 周

### 3.1 GA Rotor 内核

- [ ] 依赖 `clifford` 库（可选安装：`pip install cprdspy[ga]`）
- [ ] 实现 `GARotor(layout, bivector, angle)` — 通用 Rotor
- [ ] 实现 `ga_trace(rotors, t_range)` — 通用曲线生成
- [ ] 2D 用 Cl(2)，3D 用 Cl(3)，5D 用 Cl(5)

### 3.2 高维曲线

- [ ] `rotor_4d(...)` — 4D Rotor 组合 → 投影到 3D 可视化
- [ ] `rotor_5d(...)` — 5D 双重旋转曲线
- [ ] 投影方法：立体投影、超平面截面、Perspective projection

### 3.3 GA 工具集

- [ ] `geometric_curvature(curve)` — 任意维曲率（无需叉积）
- [ ] `rotor_decompose(curve, layout)` — 用 GA 做反编译
- [ ] `bivector_analysis(rotor)` — 显示旋转平面和角度

**里程碑：5D Rotor 组合曲线 → 投影到 3D → 按 GA 曲率着色**

---

## 阶段四：Hopf 纤维化与拓扑可视化

> 目标：把文档中的 Hopf 理论变成可交互的旗舰 demo。
> 预计工期：1 周

### 4.1 Hopf 模块

- [ ] `hopf_fiber(eta, delta, n_points)` — 计算单条纤维的立体投影
- [ ] `hopf_fibration(n_fibers)` — Fibonacci 球面分布生成多条纤维
- [ ] `clifford_torus(n_fibers)` — 展示 η=π/4 的特殊纤维

### 4.2 交互可视化

- [ ] Plotly 3D 交互（已在对话中实现 HTML demo）
- [ ] 集成到 cprdspy：`hopf_plot(n_fibers, color_mode='hsv')`
- [ ] 动画：η 从 0 → π/2，展示纤维从点到圆的演化

### 4.3 纽结可视化

- [ ] `torus_knot_link(p, q)` — 展示 (p,q) 环面纽结
- [ ] `hopf_link()` — 展示两条纤维的 Hopf 链环
- [ ] 可选：计算 linking number

**里程碑：`hopf_plot(200, color_mode='rainbow', animate=True)` 一键生成旗舰展示**

---

## 阶段五：运动树与层级系统

> 目标：实现 Motion Graph，支持嵌套运动（卫星-行星-恒星）。
> 预计工期：2 周

### 5.1 Motion Tree 数据结构

- [ ] `MotionNode`：包含 Rotor + 子节点列表
- [ ] `attach(child, parent)` — 子节点跟随父节点运动
- [ ] `evaluate(t)` — 递归计算所有节点的绝对位置

### 5.2 太阳系示例

- [ ] `sun = Rotor(...)` / `earth = Rotor(...) @ sun` / `moon = Rotor(...) @ earth`
- [ ] 动画：实时渲染行星系统运动
- [ ] 支持任意层级嵌套

### 5.3 机械结构

- [ ] 齿轮系统：多个 Rotor 以有理频率比耦合
- [ ] 连杆机构：Motion Tree + 约束求解
- [ ] 万花筒：反射群 + Rotor 组合

**里程碑：用 5 行代码画出一个带动画的"行星系统"**

---

## 阶段六：CPR 语言原型

> 目标：设计 CPR 的 DSL（领域特定语言）语法。
> 预计工期：2-3 周

### 6.1 语法设计

- [ ] 定义 CPR 文法（BNF）
- [ ] 核心关键字：`rotor`, `trace`, `compose`, `lift`, `project`
- [ ] 运算符：`+`（叠加）、`*`（组合）、`@`（附着）
- [ ] 查询：`closed?`, `period()`, `frequency()`, `explain`

### 6.2 解释器

- [ ] 用 Python 实现 CPR 解释器（或 AST 转换器）
- [ ] `cpr.run("r1 = rotor(3, 1); r2 = rotor(1, 7); trace(r1 + r2)")`
- [ ] 输出：图形 + 数学表达式 + 频率分析

### 6.3 Geometry ↔ Program 双向翻译

- [ ] `cpr.compile(shape)` → SVG/曲线 → CPR 程序
- [ ] `cpr.decompile(program)` → CPR 程序 → 数学公式
- [ ] `cpr.optimize(program, epsilon)` → 最小 Rotor 数逼近

**里程碑：输入 SVG → 输出 CPR 程序 → 修改程序 → 输出新图形**

---

## 阶段七：音频与跨模态（可选但有趣）

> 目标：实现 Rotor → Sound 的映射。
> 预计工期：1 周

### 7.1 基础音频

- [ ] `rotor_to_audio(composition, duration, f0)` → 生成 WAV
- [ ] 立体声：x(t) → Left, y(t) → Right
- [ ] 频率映射：对数映射（音乐友好）

### 7.2 高级调制

- [ ] 曲率 → 滤波器截止频率
- [ ] 挠率 → 颤音深度
- [ ] 弧长变化率 → 振幅包络

### 7.3 3D 音频

- [ ] Rotor3D → 空间音频（ambisonics 或双耳渲染）
- [ ] 5D Rotor → 五通道音频

**里程碑：画出睡莲的同时"听到"睡莲**

---

## 优先级总结

```
紧急且重要                    重要不紧急
┌─────────────────┐          ┌─────────────────┐
│ 阶段 0: Rotor   │          │ 阶段 3: GA 扩展  │
│   内核          │          │ 阶段 5: 运动树   │
│ 阶段 1: 3D      │          │ 阶段 6: CPR 语言 │
│   Rotor         │          │ 阶段 7: 音频     │
└─────────────────┘          └─────────────────┘
紧急不太重要                    不紧急不重要
┌─────────────────┐          ┌─────────────────┐
│ 阶段 4: Hopf    │          │ （暂无）         │
│   demo (已有代码)│          │                 │
└─────────────────┘          └─────────────────┘
```

---

## 建议的第一步

**今天就做：阶段 0.1 — 实现 `Rotor2D` 类。**

理由：
1. 它是所有后续工作的基础
2. 数学最简单（复数加法）
3. 立刻能看到视觉效果（画出外摆线）
4. 验证"Rotor 组合生成一切"的核心假设

```python
# 目标代码（阶段 0 完成后）
from cprdspy.rotor import Rotor2D, trace

r1 = Rotor2D(radius=3, frequency=1)
r2 = Rotor2D(radius=1, frequency=7)
curve = trace(r1 + r2, t_end=2*pi, n=2000)
curve.plot()  # 一条 7 瓣外摆线
```

---

## 技术决策记录

| 决策 | 选择 | 理由 |
|------|------|------|
| 2D Rotor 底层 | 复数 | 最简单，性能够用 |
| 3D Rotor 底层 | 四元数 / 球面坐标双接口 | 用户看球面坐标，内部用四元数 |
| GA 扩展 | 可选依赖 `clifford` | 不强制安装，核心功能不依赖 |
| 可视化 | matplotlib + plotly 双后端 | 静态图 + 交互图都覆盖 |
| 音频 | numpy 直接生成 WAV | 零额外依赖 |
| DSL | Python 内嵌（先不做独立语言） | 降低门槛，快速迭代 |

---

*Created: 2026-10-29*
*Based on: cprdspy docs analysis and discussion*

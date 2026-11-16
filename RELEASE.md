# cprdspy v0.3.0 Release Notes

## 🎉 首个完整版本发布

**cprdspy** 是一个基于 Matplotlib 和 Plotly 的 Python 几何图形可视化工具包，提供圆形、弧线、螺旋线、花朵、波形、星形、点阵和线条等丰富的几何图形绘制功能。

---

## ✨ 新特性

### 📐 Matplotlib 8大绘图模块（50+ 函数）
- **Flowers 花朵** — 经典多瓣花、椭圆花瓣、嵌套层叠花
- **Circles 圆形** — 圆、椭圆、同心圆（等差/等比）、通过圆心和点画圆
- **Arcs 弧线** — 角度弧、点定位弧、椭圆弧、可旋转弧 `arc_rotate`
- **Spirals 螺旋线** — 对数螺线、n边形螺线、马蹄莲 `calla`
- **Waves 波形** — 等差/等比波形、波形叠加
- **Stars 星形** — 单层/多层旋转星形
- **Dots 点阵** — 点集容器（支持 `+` 拼接）、椭圆/超椭圆点阵
- **Lines 线条** — 正多边形、全连接图、梅塔特隆立方体、水晶立方体

### 🌐 Plotly 交互式可视化
- 基于 Plotly 的交互式版本，支持缩放、平移、悬停提示
- 3D 椭球体绘制（`ellipsoid`）

### 🧊 3D 可视化 & Blender 支持
- 椭球体生成与颜色修复
- 球面、椭球面数学建模
- Blender 集成脚本（花朵、花瓣、椭球体）
- 完整的数学文档（CPR数学、椭球数学）

### 📊 Dash Dashboard
- 基于 Dash 的 Web 交互仪表板
- 支持花朵和波形模块的可视化展示

### 🎨 全局配置系统
- 主题切换（`set_theme`）
- 自定义线条宽度、透明度、网格等样式

### 🟨 JavaScript 可视化库（CPR_js1）
- Arcs、Circles、Flowers、Spirals、Waves 的 JS 版本
- 模块化设计，支持浏览器端直接使用

---

## 📦 安装

```bash
pip install cprdspy
```

或从源码安装：

```bash
git clone https://github.com/lbylzk8/cprdspy.git
cd cprdspy
pip install -e .
```

---

## 🚀 快速开始

```python
# Matplotlib 绘图
from cprdspy import flowers_mpl, arc_rotate_mpl, logSpiral_mpl
flowers_mpl(R=1, r=1, n=4, color="#e74c3c")

# Plotly 交互式绘图
from cprdspy.CPR_plotly import flowers
flowers(R=1, r=1, n=4, color="#e74c3c")

# 全局配置
from cprdspy import set_theme, config
set_theme("dark")
```

---

## 🔧 依赖

- Python ≥ 3.13
- matplotlib ≥ 3.10.7
- plotly ≥ 6.3.1
- numpy ≥ 2.3.4
- dash ≥ 3.2.0
- ipykernel ≥ 7.1.0

---

## 📝 更新日志

- **a4b817e** — 添加3D功能、完善文档、更新配置
- **8e759fe** — 更新Blender椭球功能和数学文档
- **9313799** — 修复椭球颜色显示问题
- **455dc0c** — 添加新的3D模型和示例
- **c1896d1** — 修复 `CPR_OT_add_ellipsoid` 操作符和面板功能
- **2c30375** — 添加3D功能、完善文档、更新版本到 v0.2.4
- **abaed36** — 首次提交

---

## 🔗 链接

- GitHub: [https://github.com/lbylzk8/cprdspy](https://github.com/lbylzk8/cprdspy)
- Issues: [https://github.com/lbylzk8/cprdspy/issues](https://github.com/lbylzk8/cprdspy/issues)
- PyPI: [https://pypi.org/project/cprdspy](https://pypi.org/project/cprdspy)

---

**License:** MIT | **Author:** lbylzk8 | **Version:** 0.3.0

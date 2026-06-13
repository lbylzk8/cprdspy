# CPR_js1 - CPR 图形库 JavaScript 版本

这个模块提供了使用 SVG 绘制各种几何图形的功能，是 CPR_matplotlib 项目的 JavaScript 版本。

## 目录结构

```
CPR_js1/
├── index.js                 # 主模块导出
├── package.json             # npm 包配置
├── test.html                # 测试页面
├── Circles/
│   ├── circle.js            # 圆形、椭圆、同心圆
│   └── index.js             # 模块导出
├── Arcs/
│   ├── arc.js               # 圆弧、椭圆弧
│   └── index.js
├── Flowers/
│   ├── flower.js            # 花朵图案
│   └── index.js
├── Spirals/
│   ├── spiral.js            # 螺旋线
│   └── index.js
└── Waves/
    ├── waves.js             # 波形图案
    └── index.js
```

## 安装

```bash
# 本地使用（ES Module）
import { circle, flower, ... } from './CPR_js1/index.js';

# 或通过 npm
npm install ./cprdspy/cprdspy/CPR_js1
```

## 使用示例

### 浏览器中使用

```html
<script type="module">
    import { circle, flower, renderSVG } from './CPR_js1/index.js';
    
    // 绘制圆形
    const circlePath = circle({ radius: 2, color: "#00ff00" });
    
    // 绘制花朵
    const flowerPaths = flower({ R: 2, r: 2, n: 4, N: 8, color: "#ff66cc" });
    
    // 渲染到 HTML
    renderSVG('myCanvas', [...flowerPaths], {
        viewBox: "-3 -3 6 6",
        bg: "#10101a",
        width: "600",
        height: "600"
    });
</script>
```

### Node.js 中使用

```javascript
import { circle, ellipse, pathsToSVG, createSVG } from './CPR_js1/index.js';

// 生成 SVG 字符串
const svg = createSVG("-3 -3 6 6", "#10101a") + 
            pathsToSVG([circle({ radius: 1 })]) + 
            "</svg>";

// 保存到文件
import fs from 'fs';
fs.writeFileSync('output.svg', svg);
```

## API 文档

### Circles 模块

| 函数 | 说明 |
|------|------|
| `circle(options)` | 绘制圆形 |
| `circleP(center, point, color)` | 通过圆心和圆上一点绘制圆 |
| `ellipse(options)` | 绘制椭圆 |
| `concentricCircles(options)` | 绘制同心圆 |
| `concentricEllipses(options)` | 绘制同心椭圆 |

### Arcs 模块

| 函数 | 说明 |
|------|------|
| `arc(options)` | 通过角度绘制圆弧 |
| `arcPoint(options)` | 通过两点绘制圆弧 |
| `arcInverse(options)` | 反向圆弧 |
| `ovalArc(options)` | 绘制椭圆弧 |

### Flowers 模块

| 函数 | 说明 |
|------|------|
| `flowerPetal(options)` | 绘制单片花瓣 |
| `flower(options)` | 绘制单层花 |
| `flowers(options)` | 绘制多层花 |
| `ovalPetal(options)` | 绘制椭圆花瓣 |
| `ovalFlower(options)` | 绘制椭圆花 |

### Spirals 模块

| 函数 | 说明 |
|------|------|
| `logSpiral(options)` | 绘制对数螺线 |
| `nSpiral(options)` | 绘制 n 瓣螺旋 |
| `nSpiralRotate(options)` | 绘制旋转螺旋 |
| `callaPetal(options)` | 绘制马蹄莲花瓣 |

### Waves 模块

| 函数 | 说明 |
|------|------|
| `wave(options)` | 绘制波形 |
| `waveAri(options)` | 绘制等差波形 |
| `waveGeo(options)` | 绘制等比波形 |
| `waveWave(options)` | 绘制嵌套波形 |

## 通用参数

所有函数都接受 `options` 对象，常用参数包括：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `color` | string | "#0f0" | 颜色（十六进制或 CSS 颜色名） |
| `alpha` | number | 1 | 透明度 (0-1) |
| `center` | Array | [0, 0] | 中心坐标 |
| `points` | number | 1000 | 采样点数 |
| `lineWidth` | number | 1 | 线宽 |

## 测试

在浏览器中打开 `test.html` 查看各模块的测试效果：

```bash
npx serve .
# 然后访问 http://localhost:3000/test.html
```

## 与 Python 版本对比

| 特性 | CPR_matplotlib | CPR_js1 |
|------|----------------|---------|
| 渲染方式 | Matplotlib | SVG |
| 输出格式 | PNG/SVG/PDF | SVG |
| 交互性 | 低 | 高（可 DOM 操作） |
| 运行环境 | Python | 浏览器/Node.js |

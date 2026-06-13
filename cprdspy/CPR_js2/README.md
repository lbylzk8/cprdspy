# CPR_js2 - Plotly.js 版本

CPR 图形库的 JavaScript + Plotly.js 实现。

## 目录结构

```
CPR_js2/
├── Circles/          # 圆形和椭圆
│   └── circle.js
├── Arcs/             # 圆弧和椭圆弧
│   └── arc.js
├── Flowers/          # 花朵图案
│   └── flower.js
├── Spirals/          # 螺旋线
│   └── spiral.js
├── Waves/            # 波浪图案
│   └── waves.js
├── index.js          # 主模块入口
├── test.html         # 测试页面
├── package.json      # npm 配置
└── README.md         # 本文件
```

## 模块说明

### Circles (圆形)
- `circle()` - 绘制圆形
- `circleP()` - 通过圆心和圆上一点绘制圆
- `ellipse()` - 绘制椭圆
- `concentricCircles()` - 绘制同心圆
- `concentricEllipses()` - 绘制同心椭圆

### Arcs (圆弧)
- `arc()` - 通过角度绘制圆弧
- `arcPoint()` - 通过两点绘制圆弧
- `ovalArc()` - 绘制椭圆弧
- `arcDot()` - 获取圆弧坐标

### Flowers (花朵)
- `flowerPetal()` - 绘制单片花瓣
- `flower()` - 绘制单层花
- `flowers()` - 绘制多层花
- `ovalPetal()` - 绘制椭圆花瓣
- `ovalFlower()` - 绘制椭圆花

### Spirals (螺旋)
- `logSpiral()` - 绘制对数螺线
- `logSpiralOut()` - 外向对数螺线
- `logSpiralIn()` - 内向对数螺线
- `nSpiral()` - 绘制 n 瓣螺旋
- `nSpiralRotate()` - 旋转螺旋
- `callaPetal()` - 马蹄莲花瓣
- `callaByPetal()` - 多个马蹄莲花瓣

### Waves (波浪)
- `wave()` - 绘制波浪
- `waveAri()` - 等差波浪
- `waveGeo()` - 等比波浪
- `waveWave()` - 嵌套波浪

## 使用方法

### 方式 1: 使用测试页面
直接打开 `test.html` 文件查看示例（需要 HTTP 服务器）。

### 方式 2: 在项目中导入

```javascript
import {
    circle,
    flower,
    logSpiral,
    wave
} from './CPR_js2/index.js';

// 使用示例
const circleTrace = circle({ radius: 1, color: '#00ff88', center: [0, 0] });
const flowerTraces = flower({ R: 1, r: 0.5, n: 4, N: 12, color: '#00ff88' });

// 添加到 Plotly 图表
Plotly.newPlot('myDiv', [circleTrace, ...flowerTraces]);
```

## 运行测试

```bash
# 安装依赖
npm install

# 使用 Python 启动 HTTP 服务器
python -m http.server 8000

# 或使用 Node.js 的 http-server
npx http-server -p 8000

# 然后在浏览器中打开 http://localhost:8000/cprdspy/cprdspy/CPR_js2/test.html
```

## 与 matplotlib 版本的对应关系

| CPR_matplotlib | CPR_js2 |
|----------------|---------|
| circle() | circle() |
| ellipse() | ellipse() |
| concentric_circles() | concentricCircles() |
| arc() | arc() |
| flower_petal() | flowerPetal() |
| flower() | flower() |
| oval_flower() | ovalFlower() |
| log_spiral() | logSpiral() |
| n_spiral() | nSpiral() |
| wave() | wave() |
| wave_ari() | waveAri() |
| wave_geo() | waveGeo() |

## 特性

- 使用 Plotly.js 的 scattergl 渲染模式，性能优异
- 支持自定义颜色、透明度、线宽等样式
- 所有函数返回 Plotly 轨迹对象，可直接用于 Plotly.newPlot()
- ES 模块结构，便于按需导入

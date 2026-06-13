/**
 * CPR 图形库 - JavaScript 版本
 *
 * 这个模块提供了使用 SVG 绘制各种几何图形的功能，包括：
 * - 圆形 (Circles)
 * - 弧线 (Arcs)
 * - 螺旋线 (Spirals)
 * - 花朵 (Flowers)
 * - 波形 (Waves)
 */

// Circles 模块
export {
    circle,
    circleP,
    ellipse,
    concentricCircles,
    concentricEllipses,
} from "./Circles/circle.js";

// Arcs 模块
export {
    arcPoint,
    arcPointInverse,
    arc,
    arcInverse,
    arcDot,
    arcDotInverse,
    ovalArc,
} from "./Arcs/arc.js";

// Flowers 模块
export {
    rotatePoint,
    flowerPetal,
    flower,
    flowers,
    ovalPetal,
    ovalFlower,
    ovalFlowerA,
} from "./Flowers/flower.js";

// Spirals 模块
export {
    logSpiral,
    logSpiralOut,
    logSpiralIn,
    logSpiralInOut,
    nSpiral,
    nSpiralRotate,
    nSpiralRotateOut,
    nSpiralRotateIn,
    callaPetal,
    callaByPetal,
} from "./Spirals/spiral.js";

// Waves 模块
export {
    waveAri,
    waveGeo,
    wave,
    waveWave,
} from "./Waves/waves.js";

/**
 * 创建 SVG 元素的辅助函数
 * @param {string} viewBox - SVG 视图框
 * @param {string} bg - 背景颜色
 * @returns {string} SVG 开始标签
 */
export function createSVG(viewBox = "0 0 100 100", bg = "white") {
    return `<svg viewBox="${viewBox}" xmlns="http://www.w3.org/2000/svg" style="background:${bg};">`;
}

/**
 * 将路径数据转换为 SVG 元素
 * @param {Array} paths - 路径数据数组
 * @returns {string} SVG 路径元素字符串
 */
export function pathsToSVG(paths) {
    let svg = "";
    for (const path of paths) {
        if (path.type === "center") {
            svg += `<circle cx="${path.cx}" cy="${path.cy}" r="${path.r}" fill="${path.fill}"/>`;
        } else if (path.d) {
            svg += `<path d="${path.d}" fill="${path.fill || "none"}" stroke="${path.stroke}" stroke-width="${path["stroke-width"]}" stroke-opacity="${path["stroke-opacity"]}"/>`;
        }
    }
    return svg;
}

/**
 * 渲染 SVG 到 HTML 元素
 * @param {string} elementId - 目标元素 ID
 * @param {Array} paths - 路径数据数组
 * @param {Object} options - 配置选项
 */
export function renderSVG(elementId, paths, options = {}) {
    const {
        viewBox = "-5 -5 10 10",
        bg = "#10101a",
        width = "600",
        height = "600",
    } = options;

    const svg = `${createSVG(viewBox, bg)}${pathsToSVG(paths)}</svg>`;
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = svg;
        element.querySelector("svg").setAttribute("width", width);
        element.querySelector("svg").setAttribute("height", height);
    }
    return svg;
}

/**
 * CPR 图形库 - JavaScript 版本 (Plotly.js)
 * Circles 模块 - 圆形和椭圆相关函数
 */

/**
 * 绘制圆形
 * @param {Object} options - 配置选项
 * @returns {Object} Plotly 轨迹对象
 */
function circle({
    radius = 1,
    color = "#0F0",
    alpha = 1,
    center = [0, 0],
    points = 100,
    lineWidth = 1,
    label = null,
    name = null,
} = {}) {
    const angle = Array.from({ length: points + 1 }, (_, i) => (2 * Math.PI * i) / points);
    const x = angle.map(a => center[0] + radius * Math.cos(a));
    const y = angle.map(a => center[1] + radius * Math.sin(a));

    return {
        type: "scattergl",
        mode: "lines",
        x: x,
        y: y,
        line: { color: color, width: lineWidth },
        opacity: alpha,
        name: name || label,
        hoverinfo: "none",
    };
}

/**
 * 通过圆心和圆上一点绘制圆
 */
function circleP(center, point, color = "b") {
    const dx = point[0] - center[0];
    const dy = point[1] - center[1];
    const radius = Math.sqrt(dx * dx + dy * dy);
    return circle({ radius, color, center });
}

/**
 * 绘制椭圆
 */
function ellipse({
    a = 2,
    b = 1,
    rotation = 0,
    color = "#0f0",
    alpha = 1,
    center = [0, 0],
    points = 1000,
    lineWidth = 1,
    label = null,
} = {}) {
    const angleRad = (rotation * Math.PI) / 180;
    const theta = Array.from({ length: points + 1 }, (_, i) => (2 * Math.PI * i) / points);

    const x = theta.map(t =>
        a * Math.cos(t) * Math.cos(angleRad) - b * Math.sin(t) * Math.sin(angleRad) + center[0]
    );
    const y = theta.map(t =>
        a * Math.cos(t) * Math.sin(angleRad) + b * Math.sin(t) * Math.cos(angleRad) + center[1]
    );

    return {
        type: "scattergl",
        mode: "lines",
        x: x,
        y: y,
        line: { color: color, width: lineWidth },
        opacity: alpha,
        name: label,
        hoverinfo: "none",
    };
}

/**
 * 绘制同心圆
 */
function concentricCircles({
    center = [0, 0],
    n = 3,
    radius = 1,
    param = 0.5,
    mode = "arithmetic",
    direction = "both",
    color = "#0F0",
    alpha = 1,
    points = 200,
    lineWidth = 1,
    showCenter = true,
} = {}) {
    const traces = [];

    if (showCenter) {
        traces.push({
            type: "scattergl",
            mode: "markers",
            x: [center[0]],
            y: [center[1]],
            marker: { color: color, size: 6 },
            showlegend: false,
            hoverinfo: "none",
        });
    }

    const radii = [];
    const d = parseFloat(param);
    const q = parseFloat(param);

    if (mode.toLowerCase().startsWith("a")) {
        if (direction === "both") {
            for (let i = 1; i <= n; i++) {
                radii.push(radius + i * d);
                radii.push(radius - i * d);
            }
        } else if (direction === "out") {
            for (let i = 1; i <= n; i++) radii.push(radius + i * d);
        } else if (direction === "in") {
            for (let i = 1; i <= n; i++) radii.push(radius - i * d);
        }
    } else if (mode.toLowerCase().startsWith("g")) {
        if (q === 0) throw new Error("ratio (param) must be non-zero for geometric mode");
        if (direction === "both") {
            for (let i = 1; i <= n; i++) {
                radii.push(radius * Math.pow(q, i));
                radii.push(radius / Math.pow(q, i));
            }
        } else if (direction === "out") {
            for (let i = 1; i <= n; i++) radii.push(radius * Math.pow(q, i));
        } else if (direction === "in") {
            for (let i = 1; i <= n; i++) radii.push(radius / Math.pow(q, i));
        }
    }

    radii.push(radius);
    const uniqueRadii = [...new Set(radii)].filter(r => r > 0).sort((a, b) => a - b);

    for (const r of uniqueRadii) {
        const angle = Array.from({ length: points + 1 }, (_, i) => (2 * Math.PI * i) / points);
        const x = angle.map(a => center[0] + r * Math.cos(a));
        const y = angle.map(a => center[1] + r * Math.sin(a));

        traces.push({
            type: "scattergl",
            mode: "lines",
            x: x,
            y: y,
            line: { color: color, width: lineWidth },
            opacity: alpha,
            showlegend: false,
            hoverinfo: "none",
        });
    }

    return traces;
}

/**
 * 绘制同心椭圆
 */
function concentricEllipses({
    center = [0, 0],
    n = 3,
    a = 2,
    b = 1,
    param = 0.5,
    mode = "arithmetic",
    direction = "both",
    rotation = 0,
    color = "#0F0",
    alpha = 1,
    points = 200,
    lineWidth = 1,
    showCenter = true,
} = {}) {
    const traces = [];

    if (showCenter) {
        traces.push({
            type: "scattergl",
            mode: "markers",
            x: [center[0]],
            y: [center[1]],
            marker: { color: color, size: 6 },
            showlegend: false,
            hoverinfo: "none",
        });
    }

    const ellipses = [];
    const d = parseFloat(param);
    const q = parseFloat(param);

    if (mode.toLowerCase().startsWith("a")) {
        if (direction === "both") {
            for (let i = 1; i <= n; i++) {
                ellipses.push([a + i * d, b + i * d]);
                ellipses.push([a - i * d, b - i * d]);
            }
        } else if (direction === "out") {
            for (let i = 1; i <= n; i++) ellipses.push([a + i * d, b + i * d]);
        } else if (direction === "in") {
            for (let i = 1; i <= n; i++) ellipses.push([a - i * d, b - i * d]);
        }
    } else if (mode.toLowerCase().startsWith("g")) {
        if (q === 0) throw new Error("ratio (param) must be non-zero for geometric mode");
        if (direction === "both") {
            for (let i = 1; i <= n; i++) {
                ellipses.push([a * Math.pow(q, i), b * Math.pow(q, i)]);
                ellipses.push([a / Math.pow(q, i), b / Math.pow(q, i)]);
            }
        } else if (direction === "out") {
            for (let i = 1; i <= n; i++) ellipses.push([a * Math.pow(q, i), b * Math.pow(q, i)]);
        } else if (direction === "in") {
            for (let i = 1; i <= n; i++) ellipses.push([a / Math.pow(q, i), b / Math.pow(q, i)]);
        }
    }

    ellipses.push([a, b]);
    const uniqueMap = new Map();
    for (const [aa, bb] of ellipses) {
        if (aa > 0 && bb > 0) {
            uniqueMap.set(`${aa.toFixed(12)},${bb.toFixed(12)}`, [aa, bb]);
        }
    }
    const sortedEllipses = [...uniqueMap.values()].sort(([a1, b1], [a2, b2]) => a1 * b1 - a2 * b2);
    const angleRad = (rotation * Math.PI) / 180;

    for (const [aa, bb] of sortedEllipses) {
        const theta = Array.from({ length: points + 1 }, (_, i) => (2 * Math.PI * i) / points);
        const x = theta.map(t =>
            aa * Math.cos(t) * Math.cos(angleRad) - bb * Math.sin(t) * Math.sin(angleRad) + center[0]
        );
        const y = theta.map(t =>
            aa * Math.cos(t) * Math.sin(angleRad) + bb * Math.sin(t) * Math.cos(angleRad) + center[1]
        );

        traces.push({
            type: "scattergl",
            mode: "lines",
            x: x,
            y: y,
            line: { color: color, width: lineWidth },
            opacity: alpha,
            showlegend: false,
            hoverinfo: "none",
        });
    }

    return traces;
}

export { circle, circleP, ellipse, concentricCircles, concentricEllipses };

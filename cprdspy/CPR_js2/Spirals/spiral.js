/**
 * CPR 图形库 - JavaScript 版本 (Plotly.js)
 * Spirals 模块 - 螺旋线相关函数
 */

/**
 * 绘制对数螺线
 */
function logSpiral({
    n = 4,
    a = 1,
    b = 1,
    cyc = 0.5,
    color = "b",
    theta = 0,
    rotation = 0,
    direction = "both",
    alpha = 1,
    lineWidth = 1,
} = {}) {
    if (!["both", "in", "out"].includes(direction)) {
        throw new Error("direction must be 'both', 'in' or 'out'");
    }

    let tStart, tEnd;
    if (direction === "both") {
        tStart = -cyc * 2 * Math.PI;
        tEnd = cyc * 2 * Math.PI;
    } else if (direction === "out") {
        tStart = 0;
        tEnd = cyc * 2 * Math.PI;
    } else {
        tStart = 0;
        tEnd = -cyc * 2 * Math.PI;
    }

    const points = 1000;
    const t = Array.from({ length: points + 1 }, (_, i) => tStart + ((tEnd - tStart) * i) / points);
    const r = t.map(t => Math.pow(Math.cos(Math.PI / n), (-n * t) / Math.PI));
    const ang = t.map(t => t + theta + rotation);
    const x = r.map((r, i) => a * r * Math.cos(ang[i]));
    const y = r.map((r, i) => b * r * Math.sin(ang[i]));

    return {
        type: "scattergl",
        mode: "lines",
        x: x,
        y: y,
        line: { color: color, width: lineWidth },
        opacity: alpha,
        hoverinfo: "none",
    };
}

/**
 * 绘制 n 瓣螺旋
 */
function nSpiral({
    n = 4,
    N = 4,
    cyc = 0.5,
    color = "b",
    theta = 0,
    rotation = 0,
    lineWidth = 1,
} = {}) {
    const traces = [];

    for (let i = 0; i < N; i++) {
        const t1 = logSpiral({
            n, a: 1, b: 1, cyc, color,
            theta: theta + (i * 2 * Math.PI) / N,
            rotation, direction: "both", lineWidth,
        });

        const t2 = logSpiral({
            n, a: -1, b: 1, cyc, color,
            theta: -theta + (i * 2 * Math.PI) / N,
            rotation: -rotation, direction: "both", lineWidth,
        });

        traces.push(t1, t2);
    }

    return traces;
}

/**
 * 双向对数螺线
 */
function logSpiralInOut({ n, a, b, cyc, color = "b", theta = 0 } = {}) {
    const points = 1000;
    const tStart = -cyc * 2 * Math.PI;
    const tEnd = cyc * 2 * Math.PI;
    const t = Array.from({ length: points + 1 }, (_, i) => tStart + ((tEnd - tStart) * i) / points);
    const r = t.map(t => Math.pow(Math.cos(Math.PI / n), (-n * t) / Math.PI));
    const x = r.map((r, i) => a * r * Math.cos(t[i] + theta));
    const y = r.map((r, i) => b * r * Math.sin(t[i] + theta));

    return {
        type: "scattergl",
        mode: "lines",
        x: x,
        y: y,
        line: { color: color },
        hoverinfo: "none",
    };
}

/**
 * 外向对数螺线
 */
function logSpiralOut({ n, a, b, cyc, color = "b", theta = 0 } = {}) {
    const points = 100;
    const t = Array.from({ length: points + 1 }, (_, i) => (cyc * 2 * Math.PI * i) / points);
    const r = t.map(t => Math.pow(Math.cos(Math.PI / n), (-n * t) / Math.PI));
    const x = r.map((r, i) => a * r * Math.cos(t[i] + theta));
    const y = r.map((r, i) => b * r * Math.sin(t[i] + theta));

    return {
        type: "scattergl",
        mode: "lines",
        x: x,
        y: y,
        line: { color: color },
        hoverinfo: "none",
    };
}

/**
 * 内向对数螺线
 */
function logSpiralIn({ n, a, b, cyc, color = "b", theta = 0 } = {}) {
    const points = 100;
    const t = Array.from({ length: points + 1 }, (_, i) => (-cyc * 2 * Math.PI * i) / points);
    const r = t.map(t => Math.pow(Math.cos(Math.PI / n), (-n * t) / Math.PI));
    const x = r.map((r, i) => a * r * Math.cos(t[i] + theta));
    const y = r.map((r, i) => b * r * Math.sin(t[i] + theta));

    return {
        type: "scattergl",
        mode: "lines",
        x: x,
        y: y,
        line: { color: color },
        hoverinfo: "none",
    };
}

/**
 * 绘制 n 个螺旋
 */
function nSpiralRotate({ n, cyc, color, alpha = 0, theta = 0 } = {}) {
    const traces = [];

    for (let i = 0; i < n; i++) {
        const t1 = logSpiral({
            n, a: 1, b: 1, cyc, color,
            theta: alpha + theta + (i * 2 * Math.PI) / n,
            lineWidth: 1,
        });

        const t2 = logSpiral({
            n, a: -1, b: 1, cyc, color,
            theta: alpha - theta + (i * 2 * Math.PI) / n,
            lineWidth: 1,
        });

        traces.push(t1, t2);
    }

    return traces;
}

/**
 * 旋转外向螺旋
 */
function nSpiralRotateOut({ n, cyc, color, theta = 0 } = {}) {
    const traces = [];

    for (let i = 0; i < n; i++) {
        const t1 = logSpiralOut({ n, a: 1, b: 1, cyc, color, theta: theta + (i * 2 * Math.PI) / n });
        const t2 = logSpiralOut({ n, a: -1, b: 1, cyc, color, theta: -theta + (i * 2 * Math.PI) / n });
        traces.push(t1, t2);
    }

    return traces;
}

/**
 * 旋转内向螺旋
 */
function nSpiralRotateIn({ n, cyc, color, theta = 0 } = {}) {
    const traces = [];

    for (let i = 0; i < n; i++) {
        const t1 = logSpiralIn({ n, a: 1, b: 1, cyc, color, theta: theta + (i * 2 * Math.PI) / n });
        const t2 = logSpiralIn({ n, a: -1, b: 1, cyc, color, theta: -theta + (i * 2 * Math.PI) / n });
        traces.push(t1, t2);
    }

    return traces;
}

/**
 * 马蹄莲花瓣
 */
function callaPetal({ n, cyc, theta, color } = {}) {
    const t1 = logSpiral({ n, a: 1, b: 1, cyc: cyc * 1.25, color, theta, lineWidth: 1 });
    const t2 = logSpiral({ n, a: -1, b: 1, cyc: cyc * 1.25, color, theta: -theta, lineWidth: 1 });
    return [t1, t2];
}

/**
 * 多个马蹄莲花瓣
 */
function callaByPetal({ n, cyc, N, theta, colors } = {}) {
    const traces = [];

    for (let i = 0; i < N; i++) {
        const petalColor = colors[i % colors.length];
        const petals = callaPetal({
            n, cyc,
            theta: theta + (i * 2 * Math.PI) / N,
            color: petalColor,
        });
        traces.push(...petals);
    }

    return traces;
}

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
};

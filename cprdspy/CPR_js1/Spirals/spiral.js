/**
 * CPR 图形库 - JavaScript 版本
 * Spirals 模块 - 螺旋线相关函数
 */

/**
 * 绘制对数螺线
 * @param {Object} options - 配置选项
 * @param {number} options.n - 花瓣/对称数
 * @param {number} options.a - x 方向缩放
 * @param {number} options.b - y 方向缩放
 * @param {number} options.cyc - 周期数
 * @param {string} options.color - 颜色
 * @param {number} options.theta - 相位偏移
 * @param {number} options.rotation - 旋转角度
 * @param {string} options.direction - "both", "in", "out"
 * @param {number} options.alpha - 透明度
 * @param {number} options.lineWidth - 线宽
 * @returns {Object} 螺线路径数据
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
    const pathData = [];

    for (let i = 0; i <= points; i++) {
        const t = tStart + ((tEnd - tStart) * i) / points;
        const r = Math.pow(Math.cos(Math.PI / n), (-n * t) / Math.PI);
        const ang = t + theta + rotation;
        const x = a * r * Math.cos(ang);
        const y = b * r * Math.sin(ang);

        if (i === 0) {
            pathData.push(`M ${x} ${y}`);
        } else {
            pathData.push(`L ${x} ${y}`);
        }
    }

    return {
        type: "logSpiral",
        d: pathData.join(" "),
        fill: "none",
        stroke: color,
        "stroke-width": lineWidth,
        "stroke-opacity": alpha,
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
    const paths = [];

    for (let i = 0; i < N; i++) {
        const t1 = logSpiral({
            n,
            a: 1,
            b: 1,
            cyc,
            color,
            theta: theta + (i * 2 * Math.PI) / N,
            rotation,
            direction: "both",
            lineWidth,
        });

        const t2 = logSpiral({
            n,
            a: -1,
            b: 1,
            cyc,
            color,
            theta: -theta + (i * 2 * Math.PI) / N,
            rotation: -rotation,
            direction: "both",
            lineWidth,
        });

        paths.push(t1, t2);
    }

    return paths;
}

/**
 * 双向对数螺线
 */
function logSpiralInOut({
    n,
    a,
    b,
    cyc,
    color = "b",
    theta = 0,
} = {}) {
    const points = 1000;
    const tStart = -cyc * 2 * Math.PI;
    const tEnd = cyc * 2 * Math.PI;
    const pathData = [];

    for (let i = 0; i <= points; i++) {
        const t = tStart + ((tEnd - tStart) * i) / points;
        const r = Math.pow(Math.cos(Math.PI / n), (-n * t) / Math.PI);
        const x = a * r * Math.cos(t + theta);
        const y = b * r * Math.sin(t + theta);

        if (i === 0) {
            pathData.push(`M ${x} ${y}`);
        } else {
            pathData.push(`L ${x} ${y}`);
        }
    }

    return {
        type: "logSpiral",
        d: pathData.join(" "),
        fill: "none",
        stroke: color,
    };
}

/**
 * 外向对数螺线
 */
function logSpiralOut({
    n,
    a,
    b,
    cyc,
    color = "b",
    theta = 0,
} = {}) {
    const points = 100;
    const pathData = [];

    for (let i = 0; i <= points; i++) {
        const t = (cyc * 2 * Math.PI * i) / points;
        const r = Math.pow(Math.cos(Math.PI / n), (-n * t) / Math.PI);
        const x = a * r * Math.cos(t + theta);
        const y = b * r * Math.sin(t + theta);

        if (i === 0) {
            pathData.push(`M ${x} ${y}`);
        } else {
            pathData.push(`L ${x} ${y}`);
        }
    }

    return {
        type: "logSpiral",
        d: pathData.join(" "),
        fill: "none",
        stroke: color,
    };
}

/**
 * 内向对数螺线
 */
function logSpiralIn({
    n,
    a,
    b,
    cyc,
    color = "b",
    theta = 0,
} = {}) {
    const points = 100;
    const pathData = [];

    for (let i = 0; i <= points; i++) {
        const t = (-cyc * 2 * Math.PI * i) / points;
        const r = Math.pow(Math.cos(Math.PI / n), (-n * t) / Math.PI);
        const x = a * r * Math.cos(t + theta);
        const y = b * r * Math.sin(t + theta);

        if (i === 0) {
            pathData.push(`M ${x} ${y}`);
        } else {
            pathData.push(`L ${x} ${y}`);
        }
    }

    return {
        type: "logSpiral",
        d: pathData.join(" "),
        fill: "none",
        stroke: color,
    };
}

/**
 * 绘制 n 个螺旋
 */
function nSpiralRotate({
    n,
    cyc,
    color,
    alpha = 0,
    theta = 0,
} = {}) {
    const paths = [];

    for (let i = 0; i < n; i++) {
        const t1 = logSpiral({
            n,
            a: 1,
            b: 1,
            cyc,
            color,
            theta: alpha + theta + (i * 2 * Math.PI) / n,
            lineWidth: 1,
        });

        const t2 = logSpiral({
            n,
            a: -1,
            b: 1,
            cyc,
            color,
            theta: alpha - theta + (i * 2 * Math.PI) / n,
            lineWidth: 1,
        });

        paths.push(t1, t2);
    }

    return paths;
}

/**
 * 旋转外向螺旋
 */
function nSpiralRotateOut({
    n,
    cyc,
    color,
    theta = 0,
} = {}) {
    const paths = [];

    for (let i = 0; i < n; i++) {
        const t1 = logSpiralOut({
            n,
            a: 1,
            b: 1,
            cyc,
            color,
            theta: theta + (i * 2 * Math.PI) / n,
        });

        const t2 = logSpiralOut({
            n,
            a: -1,
            b: 1,
            cyc,
            color,
            theta: -theta + (i * 2 * Math.PI) / n,
        });

        paths.push(t1, t2);
    }

    return paths;
}

/**
 * 旋转内向螺旋
 */
function nSpiralRotateIn({
    n,
    cyc,
    color,
    theta = 0,
} = {}) {
    const paths = [];

    for (let i = 0; i < n; i++) {
        const t1 = logSpiralIn({
            n,
            a: 1,
            b: 1,
            cyc,
            color,
            theta: theta + (i * 2 * Math.PI) / n,
        });

        const t2 = logSpiralIn({
            n,
            a: -1,
            b: 1,
            cyc,
            color,
            theta: -theta + (i * 2 * Math.PI) / n,
        });

        paths.push(t1, t2);
    }

    return paths;
}

/**
 * 马蹄莲花瓣
 */
function callaPetal({
    n,
    cyc,
    theta,
    color,
} = {}) {
    const t1 = logSpiral({
        n,
        a: 1,
        b: 1,
        cyc: cyc * 1.25,
        color,
        theta,
        lineWidth: 1,
    });

    const t2 = logSpiral({
        n,
        a: -1,
        b: 1,
        cyc: cyc * 1.25,
        color,
        theta: -theta,
        lineWidth: 1,
    });

    return [t1, t2];
}

/**
 * 多个马蹄莲花瓣
 */
function callaByPetal({
    n,
    cyc,
    N,
    theta,
    colors,
} = {}) {
    const paths = [];

    for (let i = 0; i < N; i++) {
        const petalColor = colors[i % colors.length];
        const petals = callaPetal({
            n,
            cyc,
            theta: theta + (i * 2 * Math.PI) / N,
            color: petalColor,
        });
        paths.push(...petals);
    }

    return paths;
}

// 导出模块
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

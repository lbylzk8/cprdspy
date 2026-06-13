/**
 * CPR 图形库 - JavaScript 版本
 * Circles 模块 - 圆形和椭圆相关函数
 */

/**
 * 绘制圆形
 * @param {Object} options - 配置选项
 * @param {number} options.radius - 半径，默认 1
 * @param {string} options.color - 颜色，默认 "#0F0"
 * @param {number} options.alpha - 透明度，默认 1
 * @param {Array} options.center - 圆心坐标 [x, y]，默认 [0, 0]
 * @param {number} options.points - 点数，默认 100
 * @param {number} options.lineWidth - 线宽，默认 1
 * @param {string} options.label - 标签
 * @returns {Object} 圆形路径数据
 */
function circle({
    radius = 1,
    color = "#0F0",
    alpha = 1,
    center = [0, 0],
    points = 100,
    lineWidth = 1,
    label = null,
} = {}) {
    const pathData = [];
    for (let i = 0; i <= points; i++) {
        const angle = (2 * Math.PI * i) / points;
        const x = center[0] + radius * Math.cos(angle);
        const y = center[1] + radius * Math.sin(angle);
        if (i === 0) {
            pathData.push(`M ${x} ${y}`);
        } else {
            pathData.push(`L ${x} ${y}`);
        }
    }
    pathData.push("Z"); // 闭合路径

    return {
        type: "circle",
        d: pathData.join(" "),
        fill: "none",
        stroke: color,
        "stroke-width": lineWidth,
        "stroke-opacity": alpha,
        label: label,
    };
}

/**
 * 通过圆心和圆上一点绘制圆
 * @param {Array} center - 圆心坐标
 * @param {Array} point - 圆上一点
 * @param {string} color - 颜色
 * @returns {Object} 圆形路径数据
 */
function circleP(center, point, color = "b") {
    const dx = point[0] - center[0];
    const dy = point[1] - center[1];
    const radius = Math.sqrt(dx * dx + dy * dy);
    return circle({ radius, color, center });
}

/**
 * 绘制椭圆
 * @param {Object} options - 配置选项
 * @param {number} options.a - 半长轴，默认 2
 * @param {number} options.b - 半短轴，默认 1
 * @param {number} options.rotation - 旋转角度（度），默认 0
 * @param {string} options.color - 颜色
 * @param {number} options.alpha - 透明度
 * @param {Array} options.center - 中心坐标
 * @param {number} options.points - 点数
 * @param {number} options.lineWidth - 线宽
 * @param {string} options.label - 标签
 * @returns {Object} 椭圆路径数据
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
    const pathData = [];

    for (let i = 0; i <= points; i++) {
        const theta = (2 * Math.PI * i) / points;
        const x =
            a * Math.cos(theta) * Math.cos(angleRad) -
            b * Math.sin(theta) * Math.sin(angleRad) +
            center[0];
        const y =
            a * Math.cos(theta) * Math.sin(angleRad) +
            b * Math.sin(theta) * Math.cos(angleRad) +
            center[1];
        if (i === 0) {
            pathData.push(`M ${x} ${y}`);
        } else {
            pathData.push(`L ${x} ${y}`);
        }
    }
    pathData.push("Z");

    return {
        type: "ellipse",
        d: pathData.join(" "),
        fill: "none",
        stroke: color,
        "stroke-width": lineWidth,
        "stroke-opacity": alpha,
        label: label,
    };
}

/**
 * 绘制同心圆
 * @param {Object} options - 配置选项
 * @param {Array} options.center - 圆心坐标
 * @param {number} options.n - 每侧圈数
 * @param {number} options.radius - 基准半径
 * @param {number} options.param - 公差（等差）或公比（等比）
 * @param {string} options.mode - "arithmetic" 或 "geometric"
 * @param {string} options.direction - "both", "out", "in"
 * @param {string} options.color - 颜色
 * @param {number} options.alpha - 透明度
 * @param {number} options.points - 点数
 * @param {number} options.lineWidth - 线宽
 * @param {boolean} options.showCenter - 是否显示圆心
 * @returns {Array} 圆形路径数据数组
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
    const paths = [];

    // 添加圆心标记
    if (showCenter) {
        paths.push({
            type: "center",
            cx: center[0],
            cy: center[1],
            fill: color,
            r: 3,
        });
    }

    const radii = [];
    const d = parseFloat(param);
    const q = parseFloat(param);

    if (mode.toLowerCase().startsWith("a")) {
        // 等差数列
        if (direction === "both") {
            for (let i = 1; i <= n; i++) {
                radii.push(radius + i * d);
                radii.push(radius - i * d);
            }
        } else if (direction === "out") {
            for (let i = 1; i <= n; i++) {
                radii.push(radius + i * d);
            }
        } else if (direction === "in") {
            for (let i = 1; i <= n; i++) {
                radii.push(radius - i * d);
            }
        }
    } else if (mode.toLowerCase().startsWith("g")) {
        // 等比数列
        if (q === 0) {
            throw new Error("ratio (param) must be non-zero for geometric mode");
        }
        if (direction === "both") {
            for (let i = 1; i <= n; i++) {
                radii.push(radius * Math.pow(q, i));
                radii.push(radius / Math.pow(q, i));
            }
        } else if (direction === "out") {
            for (let i = 1; i <= n; i++) {
                radii.push(radius * Math.pow(q, i));
            }
        } else if (direction === "in") {
            for (let i = 1; i <= n; i++) {
                radii.push(radius / Math.pow(q, i));
            }
        }
    }

    // 过滤正半径并添加基准半径
    radii.push(radius);
    const uniqueRadii = [...new Set(radii)].filter((r) => r > 0).sort((a, b) => a - b);

    for (const r of uniqueRadii) {
        paths.push(
            circle({
                radius: r,
                color: color,
                alpha: alpha,
                center: center,
                points: points,
                lineWidth: lineWidth,
            })
        );
    }

    return paths;
}

/**
 * 绘制同心椭圆
 * @param {Object} options - 配置选项
 * @param {Array} options.center - 椭圆中心
 * @param {number} options.n - 每侧椭圆数量
 * @param {number} options.a - 基准半长轴
 * @param {number} options.b - 基准半短轴
 * @param {number} options.param - 公差或公比
 * @param {string} options.mode - "arithmetic" 或 "geometric"
 * @param {string} options.direction - "both", "out", "in"
 * @param {number} options.rotation - 旋转角度（度）
 * @param {string} options.color - 颜色
 * @param {number} options.alpha - 透明度
 * @param {number} options.points - 点数
 * @param {number} options.lineWidth - 线宽
 * @param {boolean} options.showCenter - 是否显示中心
 * @returns {Array} 椭圆路径数据数组
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
    const paths = [];

    if (showCenter) {
        paths.push({
            type: "center",
            cx: center[0],
            cy: center[1],
            fill: color,
            r: 3,
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
            for (let i = 1; i <= n; i++) {
                ellipses.push([a + i * d, b + i * d]);
            }
        } else if (direction === "in") {
            for (let i = 1; i <= n; i++) {
                ellipses.push([a - i * d, b - i * d]);
            }
        }
    } else if (mode.toLowerCase().startsWith("g")) {
        if (q === 0) {
            throw new Error("ratio (param) must be non-zero for geometric mode");
        }
        if (direction === "both") {
            for (let i = 1; i <= n; i++) {
                ellipses.push([a * Math.pow(q, i), b * Math.pow(q, i)]);
                ellipses.push([a / Math.pow(q, i), b / Math.pow(q, i)]);
            }
        } else if (direction === "out") {
            for (let i = 1; i <= n; i++) {
                ellipses.push([a * Math.pow(q, i), b * Math.pow(q, i)]);
            }
        } else if (direction === "in") {
            for (let i = 1; i <= n; i++) {
                ellipses.push([a / Math.pow(q, i), b / Math.pow(q, i)]);
            }
        }
    }

    ellipses.push([a, b]);

    // 去重并排序
    const uniqueMap = new Map();
    for (const [aa, bb] of ellipses) {
        if (aa > 0 && bb > 0) {
            const key = `${aa.toFixed(12)},${bb.toFixed(12)}`;
            uniqueMap.set(key, [aa, bb]);
        }
    }

    const sortedEllipses = [...uniqueMap.values()].sort(
        ([a1, b1], [a2, b2]) => a1 * b1 - a2 * b2
    );

    for (const [aa, bb] of sortedEllipses) {
        paths.push(
            ellipse({
                a: aa,
                b: bb,
                rotation: rotation,
                color: color,
                alpha: alpha,
                center: center,
                points: points,
                lineWidth: lineWidth,
            })
        );
    }

    return paths;
}

// 导出模块
export { circle, circleP, ellipse, concentricCircles, concentricEllipses };

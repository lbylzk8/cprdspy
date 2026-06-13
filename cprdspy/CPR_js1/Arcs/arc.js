/**
 * CPR 图形库 - JavaScript 版本
 * Arcs 模块 - 圆弧和椭圆弧相关函数
 */

/**
 * 通过两点绘制圆弧
 * @param {Object} options - 配置选项
 * @param {Array} options.center - 圆心坐标
 * @param {Array} options.point1 - 起点
 * @param {Array} options.point2 - 终点
 * @param {string} options.color - 颜色
 * @param {number} options.alpha - 透明度
 * @param {number} options.points - 点数
 * @param {number} options.lineWidth - 线宽
 * @param {string} options.label - 标签
 * @param {string} options.direction - "ccw" 或 "cw"
 * @returns {Object} 圆弧路径数据
 */
function arcPoint({
    center = [0, 0],
    point1 = [1, 0],
    point2 = [-1, 0],
    color = "#0f0",
    alpha = 1,
    points = 1000,
    lineWidth = 1,
    label = null,
    direction = "ccw",
} = {}) {
    const v1 = [point1[0] - center[0], point1[1] - center[1]];
    const v2 = [point2[0] - center[0], point2[1] - center[1]];

    const r1 = Math.sqrt(v1[0] * v1[0] + v1[1] * v1[1]);
    const r2 = Math.sqrt(v2[0] * v2[0] + v2[1] * v2[1]);

    if (r1 === 0 || r2 === 0) {
        throw new Error("point1/point2 不应与 center 重合");
    }
    if (Math.abs(r1 - r2) > 1e-6) {
        console.warn(`Warning: radii differ (r1=${r1}, r2=${r2}); using r1 for arc`);
    }
    const r = r1;

    let theta1 = Math.atan2(v1[1], v1[0]) % (2 * Math.PI);
    let theta2 = Math.atan2(v2[1], v2[0]) % (2 * Math.PI);
    if (theta1 < 0) theta1 += 2 * Math.PI;
    if (theta2 < 0) theta2 += 2 * Math.PI;

    if (direction === "ccw") {
        if (theta2 <= theta1) {
            theta2 += 2 * Math.PI;
        }
    } else {
        if (theta1 <= theta2) {
            theta1 += 2 * Math.PI;
        }
    }

    const pathData = [];
    for (let i = 0; i <= points; i++) {
        const t = theta1 + ((theta2 - theta1) * i) / points;
        const x = center[0] + r * Math.cos(t);
        const y = center[1] + r * Math.sin(t);
        if (i === 0) {
            pathData.push(`M ${x} ${y}`);
        } else {
            pathData.push(`L ${x} ${y}`);
        }
    }

    return {
        type: "arc",
        d: pathData.join(" "),
        fill: "none",
        stroke: color,
        "stroke-width": lineWidth,
        "stroke-opacity": alpha,
        label: label,
    };
}

/**
 * 反向圆弧（顺时针）
 */
function arcPointInverse({
    center = [0, 0],
    point1 = [1, 0],
    point2 = [-1, 0],
    color = "#0f0",
    alpha = 1,
    points = 1000,
    lineWidth = 1,
    label = null,
} = {}) {
    return arcPoint({
        center,
        point1,
        point2,
        color,
        alpha,
        points,
        lineWidth,
        label,
        direction: "cw",
    });
}

/**
 * 通过角度绘制圆弧
 * @param {Object} options - 配置选项
 * @param {number} options.r - 半径
 * @param {number} options.angle1 - 起始角度
 * @param {number} options.angle2 - 结束角度
 * @param {number} options.rotation - 旋转角度
 * @param {string} options.color - 颜色
 * @param {number} options.alpha - 透明度
 * @param {Array} options.center - 圆心坐标
 * @param {number} options.points - 点数
 * @param {number} options.lineWidth - 线宽
 * @param {string} options.label - 标签
 * @param {boolean} options.useDegree - 是否使用角度制
 * @param {string} options.direction - "ccw" 或 "cw"
 * @returns {Object} 圆弧路径数据
 */
function arc({
    r = 1,
    angle1 = 45,
    angle2 = 135,
    rotation = 0,
    color = "#0f0",
    alpha = 1,
    center = [0, 0],
    points = 1000,
    lineWidth = 1,
    label = null,
    useDegree = true,
    direction = "ccw",
} = {}) {
    let theta1, theta2, rot;

    if (useDegree) {
        theta1 = (angle1 * Math.PI) / 180;
        theta2 = (angle2 * Math.PI) / 180;
        rot = (rotation * Math.PI) / 180;
    } else {
        theta1 = angle1;
        theta2 = angle2;
        rot = rotation;
    }

    if (direction === "ccw") {
        if (theta2 <= theta1) {
            theta2 += 2 * Math.PI;
        }
    } else {
        if (theta1 <= theta2) {
            theta1 += 2 * Math.PI;
        }
    }

    const cosRot = Math.cos(rot);
    const sinRot = Math.sin(rot);

    const pathData = [];
    for (let i = 0; i <= points; i++) {
        const theta = theta1 + ((theta2 - theta1) * i) / points;
        const x = center[0] + r * (Math.cos(theta) * cosRot - Math.sin(theta) * sinRot);
        const y = center[1] + r * (Math.sin(theta) * cosRot + Math.cos(theta) * sinRot);
        if (i === 0) {
            pathData.push(`M ${x} ${y}`);
        } else {
            pathData.push(`L ${x} ${y}`);
        }
    }

    return {
        type: "arc",
        d: pathData.join(" "),
        fill: "none",
        stroke: color,
        "stroke-width": lineWidth,
        "stroke-opacity": alpha,
        label: label,
    };
}

/**
 * 反向圆弧
 */
function arcInverse({
    r = 1,
    angle1 = 45,
    angle2 = 135,
    rotation = 0,
    color = "#0f0",
    alpha = 1,
    center = [0, 0],
    points = 1000,
    lineWidth = 1,
    label = null,
    useDegree = true,
} = {}) {
    return arc({
        r,
        angle1,
        angle2,
        rotation,
        color,
        alpha,
        center,
        points,
        lineWidth,
        label,
        useDegree,
        direction: "cw",
    });
}

/**
 * 获取圆弧坐标（不绘制）
 */
function arcDot({
    r = 1,
    angle1 = 45,
    angle2 = 135,
    rotation = 0,
    center = [0, 0],
    points = 1000,
    useDegree = true,
} = {}) {
    let theta1, theta2, rot;

    if (useDegree) {
        theta1 = (angle1 * Math.PI) / 180;
        theta2 = (angle2 * Math.PI) / 180;
        rot = (rotation * Math.PI) / 180;
    } else {
        theta1 = angle1;
        theta2 = angle2;
        rot = rotation;
    }

    const cosRot = Math.cos(rot);
    const sinRot = Math.sin(rot);

    const xCoords = [];
    const yCoords = [];
    for (let i = 0; i <= points; i++) {
        const theta = theta1 + ((theta2 - theta1) * i) / points;
        const x = center[0] + r * (Math.cos(theta) * cosRot - Math.sin(theta) * sinRot);
        const y = center[1] + r * (Math.sin(theta) * cosRot + Math.cos(theta) * sinRot);
        xCoords.push(x);
        yCoords.push(y);
    }

    return { x: xCoords, y: yCoords };
}

/**
 * 反向圆弧坐标
 */
function arcDotInverse(options = {}) {
    return arcDot({ ...options, direction: "cw" });
}

/**
 * 绘制椭圆弧
 * @param {Object} options - 配置选项
 * @param {number} options.a - 长轴
 * @param {number} options.b - 短轴
 * @param {number} options.angle1 - 起始角度
 * @param {number} options.angle2 - 结束角度
 * @param {number} options.angle - 旋转角度
 * @param {string} options.color - 颜色
 * @param {number} options.alpha - 透明度
 * @param {Array} options.center - 中心坐标
 * @param {number} options.points - 点数
 * @param {number} options.lineWidth - 线宽
 * @param {string} options.label - 标签
 * @param {boolean} options.useDegree - 是否使用角度制
 * @returns {Object} 椭圆弧路径数据
 */
function ovalArc({
    a = 2,
    b = 1,
    angle1 = 45,
    angle2 = 135,
    angle = 0,
    color = "#0f0",
    alpha = 1,
    center = [0, 0],
    points = 1000,
    lineWidth = 1,
    label = null,
    useDegree = true,
} = {}) {
    let angle1Rad, angle2Rad, angleRad;

    if (useDegree) {
        angle1Rad = (angle1 * Math.PI) / 180;
        angle2Rad = (angle2 * Math.PI) / 180;
        angleRad = (angle * Math.PI) / 180;
    } else {
        angle1Rad = angle1;
        angle2Rad = angle2;
        angleRad = angle;
    }

    const pathData = [];
    for (let i = 0; i <= points; i++) {
        const theta = angle1Rad + ((angle2Rad - angle1Rad) * i) / points;
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

    return {
        type: "ovalArc",
        d: pathData.join(" "),
        fill: "none",
        stroke: color,
        "stroke-width": lineWidth,
        "stroke-opacity": alpha,
        label: label,
    };
}

// 导出模块
export {
    arcPoint,
    arcPointInverse,
    arc,
    arcInverse,
    arcDot,
    arcDotInverse,
    ovalArc,
};

/**
 * CPR 图形库 - JavaScript 版本 (Plotly.js)
 * Arcs 模块 - 圆弧和椭圆弧相关函数
 */

/**
 * 通过两点绘制圆弧
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

    if (r1 === 0 || r2 === 0) throw new Error("point1/point2 不应与 center 重合");
    if (Math.abs(r1 - r2) > 1e-6) console.warn(`Warning: radii differ (r1=${r1}, r2=${r2}); using r1`);

    let theta1 = Math.atan2(v1[1], v1[0]) % (2 * Math.PI);
    let theta2 = Math.atan2(v2[1], v2[0]) % (2 * Math.PI);
    if (theta1 < 0) theta1 += 2 * Math.PI;
    if (theta2 < 0) theta2 += 2 * Math.PI;

    if (direction === "ccw") {
        if (theta2 <= theta1) theta2 += 2 * Math.PI;
    } else {
        if (theta1 <= theta2) theta1 += 2 * Math.PI;
    }

    const theta = Array.from({ length: points + 1 }, (_, i) => theta1 + ((theta2 - theta1) * i) / points);
    const x = theta.map(t => center[0] + r1 * Math.cos(t));
    const y = theta.map(t => center[1] + r1 * Math.sin(t));

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
    return arcPoint({ center, point1, point2, color, alpha, points, lineWidth, label, direction: "cw" });
}

/**
 * 通过角度绘制圆弧
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
        if (theta2 <= theta1) theta2 += 2 * Math.PI;
    } else {
        if (theta1 <= theta2) theta1 += 2 * Math.PI;
    }

    const cosRot = Math.cos(rot);
    const sinRot = Math.sin(rot);

    const theta = Array.from({ length: points + 1 }, (_, i) => theta1 + ((theta2 - theta1) * i) / points);
    const x = theta.map(t => center[0] + r * (Math.cos(t) * cosRot - Math.sin(t) * sinRot));
    const y = theta.map(t => center[1] + r * (Math.sin(t) * cosRot + Math.cos(t) * sinRot));

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
    return arc({ r, angle1, angle2, rotation, color, alpha, center, points, lineWidth, label, useDegree, direction: "cw" });
}

/**
 * 获取圆弧坐标
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

    const theta = Array.from({ length: points + 1 }, (_, i) => theta1 + ((theta2 - theta1) * i) / points);
    const x = theta.map(t => center[0] + r * (Math.cos(t) * cosRot - Math.sin(t) * sinRot));
    const y = theta.map(t => center[1] + r * (Math.sin(t) * cosRot + Math.cos(t) * sinRot));

    return { x, y };
}

/**
 * 反向圆弧坐标
 */
function arcDotInverse(options = {}) {
    return arcDot({ ...options, direction: "cw" });
}

/**
 * 绘制椭圆弧
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

    const theta = Array.from({ length: points + 1 }, (_, i) => angle1Rad + ((angle2Rad - angle1Rad) * i) / points);
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

export { arcPoint, arcPointInverse, arc, arcInverse, arcDot, arcDotInverse, ovalArc };

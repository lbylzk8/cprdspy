/**
 * CPR 图形库 - JavaScript 版本
 * Flowers 模块 - 花朵图案相关函数
 */

import { arc } from "../Arcs/arc.js";
import { ovalArc } from "../Arcs/arc.js";

/**
 * 旋转点
 * @param {Array} point - 点坐标 [x, y]
 * @param {number} theta - 旋转角度（弧度）
 * @returns {Array} 旋转后的坐标
 */
function rotatePoint(point, theta) {
    const [x, y] = point;
    return [
        x * Math.cos(theta) - y * Math.sin(theta),
        x * Math.sin(theta) + y * Math.cos(theta),
    ];
}

/**
 * 绘制单片花瓣
 * @param {Object} options - 配置选项
 * @param {number} options.R - 基圆半径
 * @param {number} options.r - 圆弧半径
 * @param {number} options.n - 花瓣数
 * @param {number} options.rotation - 旋转角度
 * @param {string} options.color - 颜色
 * @param {number} options.alpha - 透明度
 * @param {Array} options.center - 中心坐标
 * @param {number} options.points - 点数
 * @param {number} options.lineWidth - 线宽
 * @param {string} options.label - 标签
 * @param {boolean} options.useDegree - 是否使用角度制
 * @param {string} options.direction - "ccw" 或 "cw"
 * @returns {Array} 两段圆弧路径数据
 */
function flowerPetal({
    R = 1,
    r = 1,
    n = 4,
    rotation = 0,
    color = "#0f0",
    alpha = 1,
    center = [0, 0],
    points = 1000,
    lineWidth = 1,
    label = null,
    useDegree = false,
    direction = "ccw",
} = {}) {
    const angle = (2 * Math.PI) / n;
    const a = R * Math.sin(Math.PI / n);

    let beta;
    if (r > 0) {
        beta = Math.acos(Math.min(1, Math.max(-1, a / r)));
    } else {
        beta = 0;
    }

    const thetaArc = Math.PI / 2 - Math.PI / n + Math.acos(Math.min(1, Math.max(-1, a / r)));

    const rotationRad = useDegree ? (rotation * Math.PI) / 180 : rotation;

    const center1Theta = rotationRad + angle / 2;
    const center2Theta = rotationRad - angle / 2;

    const center1 = [
        Math.cos(center1Theta) * R + center[0],
        Math.sin(center1Theta) * R + center[1],
    ];
    const center2 = [
        Math.cos(center2Theta) * R + center[0],
        Math.sin(center2Theta) * R + center[1],
    ];

    let theta1BaseRad, theta2BaseRad, theta3BaseRad, theta4BaseRad;

    if (Math.abs(r - a) < 1e-12) {
        theta1BaseRad = Math.PI + angle / 2;
        theta2BaseRad = Math.PI + angle / 2 + thetaArc;
        theta3BaseRad = Math.PI / 2;
        theta4BaseRad = Math.PI / 2 + thetaArc;
    } else if (r > a) {
        theta1BaseRad = Math.PI + angle / 2;
        theta2BaseRad = Math.PI + angle / 2 + thetaArc;
        theta3BaseRad = Math.PI / 2 - beta;
        theta4BaseRad = Math.PI / 2 - beta + thetaArc;
    } else {
        console.warn(`r=${r}, a=${a}`);
        console.warn(`r<a，不能形成花瓣。最小需要 r > ${a.toFixed(3)}`);
        return null;
    }

    let theta1, theta2, theta3, theta4, rotationForArc;

    if (useDegree) {
        theta1 = (theta1BaseRad * 180) / Math.PI;
        theta2 = (theta2BaseRad * 180) / Math.PI;
        theta3 = (theta3BaseRad * 180) / Math.PI;
        theta4 = (theta4BaseRad * 180) / Math.PI;
        rotationForArc = rotation;
    } else {
        theta1 = theta1BaseRad;
        theta2 = theta2BaseRad;
        theta3 = theta3BaseRad;
        theta4 = theta4BaseRad;
        rotationForArc = rotationRad;
    }

    const arc1 = arc({
        r: r,
        angle1: theta1,
        angle2: theta2,
        rotation: rotationForArc,
        color: color,
        alpha: alpha,
        center: center1,
        points: points,
        lineWidth: lineWidth,
        label: label,
        useDegree: useDegree,
        direction: direction,
    });

    const arc2 = arc({
        r: r,
        angle1: theta3,
        angle2: theta4,
        rotation: rotationForArc,
        color: color,
        alpha: alpha,
        center: center2,
        points: points,
        lineWidth: lineWidth,
        label: label,
        useDegree: useDegree,
        direction: direction,
    });

    return [arc1, arc2];
}

/**
 * 绘制单层花
 * @param {Object} options - 配置选项
 * @param {number} options.R - 基圆半径
 * @param {number} options.r - 圆弧半径
 * @param {number} options.n - 每瓣圆弧数
 * @param {number} options.N - 花瓣数量
 * @param {number} options.rotation - 旋转角度
 * @param {string} options.color - 颜色
 * @param {number} options.alpha - 透明度
 * @param {Array} options.center - 中心坐标
 * @param {number} options.points - 点数
 * @param {number} options.lineWidth - 线宽
 * @param {string} options.label - 标签
 * @param {boolean} options.useDegree - 是否使用角度制
 * @param {string} options.direction - "ccw" 或 "cw"
 * @returns {Array} 所有圆弧路径数据
 */
function flower({
    R = 1,
    r = 1,
    n = 4,
    N = 12,
    rotation = 0,
    color = "#0f0",
    alpha = 1,
    center = [0, 0],
    points = 1000,
    lineWidth = 1,
    label = null,
    useDegree = false,
    direction = "ccw",
} = {}) {
    const paths = [];

    for (let i = 0; i < N; i++) {
        const petalRot = useDegree
            ? rotation + (i * 360) / N + 90
            : (i * 2 * Math.PI) / N + Math.PI / 2;

        const petals = flowerPetal({
            R,
            r,
            n,
            rotation: petalRot,
            color,
            alpha,
            center,
            points,
            lineWidth,
            label,
            useDegree,
            direction,
        });

        if (petals) {
            paths.push(...petals);
        }
    }

    return paths;
}

/**
 * 绘制多层花
 * @param {Object} options - 配置选项
 * @param {number} options.R - 基圆半径
 * @param {number} options.r - 圆弧半径
 * @param {number} options.n - 每瓣圆弧数
 * @param {number} options.ratio - 比例因子
 * @param {number} options.M - 层数
 * @param {number} options.N - 每层花瓣数
 * @param {string} options.color - 颜色
 * @param {number} options.alpha - 透明度
 * @param {number} options.theta - 初始角度
 * @param {Array} options.center - 中心坐标
 * @param {number} options.points - 点数
 * @param {number} options.lineWidth - 线宽
 * @param {boolean} options.useDegree - 是否使用角度制
 * @param {string} options.direction - "ccw" 或 "cw"
 * @returns {Array} 所有圆弧路径数据
 */
function flowers({
    R = 1,
    r = 1,
    n = 4,
    ratio = Math.sqrt(2),
    M = 3,
    N = 12,
    color = "b",
    alpha = 1,
    theta = 0,
    center = [0, 0],
    points = 1000,
    lineWidth = 1,
    useDegree = false,
    direction = "ccw",
} = {}) {
    const paths = [];

    for (let j = 1; j <= M; j++) {
        for (let i = 0; i < N; i++) {
            const petalRot =
                (2 * i * Math.PI) / N + ((j - 1) * Math.PI) / N + theta + Math.PI / 2;

            const petals = flowerPetal({
                R: R * Math.pow(ratio, j - 1),
                r: r * Math.pow(ratio, j - 1),
                n,
                rotation: petalRot,
                color,
                alpha,
                center,
                points,
                lineWidth,
                useDegree,
                direction,
            });

            if (petals) {
                paths.push(...petals);
            }
        }
    }

    return paths;
}

/**
 * 绘制椭圆花瓣
 * @param {Object} options - 配置选项
 * @param {number} options.a - 长轴
 * @param {number} options.b - 短轴
 * @param {number} options.d - 垂直距离
 * @param {number} options.rotation - 旋转角度
 * @param {boolean} options.rotByCenter - 是否绕中心旋转
 * @param {string} options.color - 颜色
 * @param {number} options.alpha - 透明度
 * @param {Array} options.center - 中心坐标
 * @param {number} options.points - 点数
 * @param {number} options.lineWidth - 线宽
 * @param {string} options.label - 标签
 * @param {boolean} options.useDegree - 是否使用角度制
 * @returns {Array} 两段椭圆弧路径数据
 */
function ovalPetal({
    a = 2,
    b = 1,
    d = 0.5,
    rotation = 0,
    rotByCenter = true,
    color = "#0f0",
    alpha = 1,
    center = [0, 0],
    points = 1000,
    lineWidth = 1,
    label = null,
    useDegree = true,
} = {}) {
    const x0 = (b / (2 * a)) * Math.sqrt(4 * a * a - d * d) / (d / 2);
    const beta = Math.atan(x0);

    let betaB1 = Math.PI / 2 - beta;
    let betaE1 = Math.PI / 2 + beta;
    let betaB2 = 3 * Math.PI / 2 - beta;
    let betaE2 = 3 * Math.PI / 2 + beta;

    let rotationRad = useDegree ? (rotation * Math.PI) / 180 : rotation;

    if (useDegree) {
        betaB1 = (betaB1 * 180) / Math.PI;
        betaE1 = (betaE1 * 180) / Math.PI;
        betaB2 = (betaB2 * 180) / Math.PI;
        betaE2 = (betaE2 * 180) / Math.PI;
    }

    const center1 = [center[0], center[1] - d / 2];
    const center2 = [center[0], center[1] + d / 2];

    let center1Rot, center2Rot;
    if (rotByCenter) {
        center1Rot = rotatePoint(center1, rotationRad);
        center2Rot = rotatePoint(center2, rotationRad);
    } else {
        center1Rot = rotatePoint([a, center[1] - d / 2], rotationRad);
        center2Rot = rotatePoint([a, center[1] + d / 2], rotationRad);
    }

    const arc1 = ovalArc({
        a,
        b,
        angle1: betaB1,
        angle2: betaE1,
        angle: rotation,
        color,
        alpha,
        center: center1Rot,
        points,
        lineWidth,
        label,
        useDegree,
    });

    const arc2 = ovalArc({
        a,
        b,
        angle1: betaB2,
        angle2: betaE2,
        angle: rotation,
        color,
        alpha,
        center: center2Rot,
        points,
        lineWidth,
        label,
        useDegree,
    });

    return [arc1, arc2];
}

/**
 * 绘制椭圆花
 * @param {Object} options - 配置选项
 * @param {number} options.a - 长轴
 * @param {number} options.b - 短轴
 * @param {number} options.d - 垂直距离
 * @param {number} options.n - 花瓣数
 * @param {number} options.rotation - 旋转角度
 * @param {string} options.color - 颜色
 * @param {number} options.alpha - 透明度
 * @param {Array} options.center - 中心坐标
 * @param {number} options.points - 点数
 * @returns {Array} 所有椭圆弧路径数据
 */
function ovalFlower({
    a = 2,
    b = 1,
    d = 0.1,
    n = 12,
    rotation = 0,
    color = "#0f0",
    alpha = 1,
    center = [0, 0],
    points = 1000,
} = {}) {
    const paths = [];

    for (let i = 0; i < n; i++) {
        const petals = ovalPetal({
            a,
            b,
            d,
            rotation: rotation + (i * 2 * Math.PI) / n,
            rotByCenter: true,
            color,
            alpha,
            center,
            points,
            useDegree: false,
        });

        if (petals) {
            paths.push(...petals);
        }
    }

    return paths;
}

/**
 * 绘制椭圆花（方式 a）
 */
function ovalFlowerA({
    a = 2,
    b = 1,
    d = 0.1,
    n = 12,
    rotation = 0,
    color = "#0f0",
    alpha = 1,
    center = [0, 0],
    points = 1000,
} = {}) {
    const paths = [];

    for (let i = 0; i < n; i++) {
        const petals = ovalPetal({
            a,
            b,
            d,
            rotation: rotation + (i * 2 * Math.PI) / n,
            rotByCenter: false,
            color,
            alpha,
            center,
            points,
            useDegree: false,
        });

        if (petals) {
            paths.push(...petals);
        }
    }

    return paths;
}

// 导出模块
export {
    rotatePoint,
    flowerPetal,
    flower,
    flowers,
    ovalPetal,
    ovalFlower,
    ovalFlowerA,
};

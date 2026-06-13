/**
 * CPR 图形库 - JavaScript 版本
 * Waves 模块 - 波形图案相关函数
 */

import { concentricCircles } from "../Circles/circle.js";

/**
 * 绘制等差波形
 * @param {Object} options - 配置选项
 * @param {number} options.A - 振幅（等差公差）
 * @param {number} options.F - 频率（圈数）
 * @param {number} options.P - 相位数
 * @param {number} options.rotation - 旋转角度
 * @param {string} options.direction - "both", "out", "in"
 * @param {string} options.color - 颜色
 * @param {number} options.alpha - 透明度
 * @param {number} options.R - 基准半径
 * @param {Array} options.center - 中心坐标
 * @param {number} options.points - 点数
 * @param {number} options.lineWidth - 线宽
 * @param {boolean} options.showCenter - 是否显示中心
 * @returns {Array} 所有圆形路径数据
 */
function waveAri({
    A = 1,
    F = 3,
    P = 12,
    rotation = 0,
    direction = "both",
    color = "#0f0",
    alpha = 1,
    R = 1,
    center = [0, 0],
    points = 1000,
    lineWidth = 1,
    showCenter = true,
} = {}) {
    const paths = [];

    for (let i = 0; i <= P; i++) {
        const circleCenter = [
            center[0] + Math.cos((i * 2 * Math.PI) / P + Math.PI / 2 + rotation),
            center[1] + Math.sin((i * 2 * Math.PI) / P + Math.PI / 2 + rotation),
        ];

        const circles = concentricCircles({
            center: circleCenter,
            n: F,
            radius: R,
            param: A,
            mode: "arithmetic",
            direction: direction,
            color: color,
            alpha: alpha,
            points: points,
            lineWidth: lineWidth,
            showCenter: showCenter,
        });

        paths.push(...circles);
    }

    return paths;
}

/**
 * 绘制等比波形
 * @param {Object} options - 配置选项
 * @param {number} options.A - 振幅（等比公比）
 * @param {number} options.F - 频率（圈数）
 * @param {number} options.P - 相位数
 * @param {number} options.rotation - 旋转角度
 * @param {string} options.direction - "both", "out", "in"
 * @param {string} options.color - 颜色
 * @param {number} options.alpha - 透明度
 * @param {number} options.R - 基准半径
 * @param {Array} options.center - 中心坐标
 * @param {number} options.points - 点数
 * @param {number} options.lineWidth - 线宽
 * @param {boolean} options.showCenter - 是否显示中心
 * @returns {Array} 所有圆形路径数据
 */
function waveGeo({
    A = 1,
    F = 3,
    P = 12,
    rotation = 0,
    direction = "both",
    color = "#0f0",
    alpha = 1,
    R = 1,
    center = [0, 0],
    points = 1000,
    lineWidth = 1,
    showCenter = true,
} = {}) {
    const paths = [];

    for (let i = 0; i <= P; i++) {
        const circleCenter = [
            center[0] + Math.cos((i * 2 * Math.PI) / P + Math.PI / 2 + rotation),
            center[1] + Math.sin((i * 2 * Math.PI) / P + Math.PI / 2 + rotation),
        ];

        const circles = concentricCircles({
            center: circleCenter,
            n: F,
            radius: R,
            param: A,
            mode: "geometric",
            direction: direction,
            color: color,
            alpha: alpha,
            points: points,
            lineWidth: lineWidth,
            showCenter: showCenter,
        });

        paths.push(...circles);
    }

    return paths;
}

/**
 * 绘制波形（通用）
 * @param {Object} options - 配置选项
 * @param {number} options.A - 振幅
 * @param {number} options.F - 频率
 * @param {number} options.P - 相位数
 * @param {number} options.rotation - 旋转角度
 * @param {string} options.mode - "arithmetic" 或 "geometric"
 * @param {string} options.direction - "both", "out", "in"
 * @param {string} options.color - 颜色
 * @param {number} options.alpha - 透明度
 * @param {number} options.R - 基准半径
 * @param {Array} options.center - 中心坐标
 * @param {number} options.points - 点数
 * @param {number} options.lineWidth - 线宽
 * @param {boolean} options.showCenter - 是否显示中心
 * @returns {Array} 所有圆形路径数据
 */
function wave({
    A = 1,
    F = 3,
    P = 12,
    rotation = 0,
    mode = "geometric",
    direction = "both",
    color = "#0f0",
    alpha = 1,
    R = 1,
    center = [0, 0],
    points = 1000,
    lineWidth = 1,
    showCenter = true,
} = {}) {
    const paths = [];

    for (let i = 0; i <= P; i++) {
        const circleCenter = [
            center[0] + Math.cos((i * 2 * Math.PI) / P + Math.PI / 2 + rotation),
            center[1] + Math.sin((i * 2 * Math.PI) / P + Math.PI / 2 + rotation),
        ];

        const circles = concentricCircles({
            center: circleCenter,
            n: F,
            radius: R,
            param: A,
            mode: mode,
            direction: direction,
            color: color,
            alpha: alpha,
            points: points,
            lineWidth: lineWidth,
            showCenter: showCenter,
        });

        paths.push(...circles);
    }

    return paths;
}

/**
 * 绘制嵌套波形
 * @param {Object} options - 配置选项
 * @param {number} options.A - 振幅
 * @param {number} options.F - 频率
 * @param {number} options.P - 相位数
 * @param {number} options.rotation - 旋转角度
 * @param {string} options.mode - "arithmetic" 或 "geometric"
 * @param {string} options.direction - "both", "out", "in"
 * @param {string} options.color - 颜色
 * @param {number} options.alpha - 透明度
 * @param {number} options.R - 基准半径
 * @param {Array} options.center - 中心坐标
 * @param {number} options.points - 点数
 * @param {number} options.lineWidth - 线宽
 * @param {boolean} options.showCenter - 是否显示中心
 * @returns {Array} 所有圆形路径数据
 */
function waveWave({
    A = 1,
    F = 3,
    P = 12,
    rotation = 0,
    mode = "geometric",
    direction = "both",
    color = "#0f0",
    alpha = 1,
    R = 1,
    center = [0, 0],
    points = 1000,
    lineWidth = 1,
    showCenter = true,
} = {}) {
    const paths = [];

    for (let i = 0; i <= P; i++) {
        const waveCenter = [
            center[0] + Math.cos((i * 2 * Math.PI) / P + Math.PI / 2 + rotation),
            center[1] + Math.sin((i * 2 * Math.PI) / P + Math.PI / 2 + rotation),
        ];

        const wavePaths = wave({
            A: A,
            F: F,
            P: P,
            rotation: rotation,
            mode: mode,
            direction: direction,
            color: color,
            alpha: alpha,
            R: R,
            center: waveCenter,
            points: points,
            lineWidth: lineWidth,
            showCenter: showCenter,
        });

        paths.push(...wavePaths);
    }

    return paths;
}

// 导出模块
export { waveAri, waveGeo, wave, waveWave };

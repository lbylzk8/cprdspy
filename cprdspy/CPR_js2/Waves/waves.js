/**
 * CPR 图形库 - JavaScript 版本 (Plotly.js)
 * Waves 模块 - 波浪图案相关函数
 */

import { concentricCircles } from "../Circles/circle.js";

/**
 * 绘制等差波浪
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
    const traces = [];

    for (let i = 0; i <= P; i++) {
        const newCenter = [
            center[0] + Math.cos((i * 2 * Math.PI) / P + Math.PI / 2 + rotation),
            center[1] + Math.sin((i * 2 * Math.PI) / P + Math.PI / 2 + rotation),
        ];

        const circleTraces = concentricCircles({
            center: newCenter,
            n: F,
            radius: R,
            param: A,
            mode: "arithmetic",
            direction,
            color,
            alpha,
            points,
            lineWidth,
            showCenter,
        });

        traces.push(...circleTraces);
    }

    return traces;
}

/**
 * 绘制等比波浪
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
    const traces = [];

    for (let i = 0; i <= P; i++) {
        const newCenter = [
            center[0] + Math.cos((i * 2 * Math.PI) / P + Math.PI / 2 + rotation),
            center[1] + Math.sin((i * 2 * Math.PI) / P + Math.PI / 2 + rotation),
        ];

        const circleTraces = concentricCircles({
            center: newCenter,
            n: F,
            radius: R,
            param: A,
            mode: "geometric",
            direction,
            color,
            alpha,
            points,
            lineWidth,
            showCenter,
        });

        traces.push(...circleTraces);
    }

    return traces;
}

/**
 * 绘制波浪
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
    const traces = [];

    for (let i = 0; i <= P; i++) {
        const newCenter = [
            center[0] + Math.cos((i * 2 * Math.PI) / P + Math.PI / 2 + rotation),
            center[1] + Math.sin((i * 2 * Math.PI) / P + Math.PI / 2 + rotation),
        ];

        const circleTraces = concentricCircles({
            center: newCenter,
            n: F,
            radius: R,
            param: A,
            mode,
            direction,
            color,
            alpha,
            points,
            lineWidth,
            showCenter,
        });

        traces.push(...circleTraces);
    }

    return traces;
}

/**
 * 绘制嵌套波浪
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
    const traces = [];

    for (let i = 0; i <= P; i++) {
        const newCenter = [
            center[0] + Math.cos((i * 2 * Math.PI) / P + Math.PI / 2 + rotation),
            center[1] + Math.sin((i * 2 * Math.PI) / P + Math.PI / 2 + rotation),
        ];

        const waveTraces = wave({
            A,
            F,
            P,
            rotation,
            mode,
            direction,
            color,
            alpha,
            R,
            center: newCenter,
            points,
            lineWidth,
            showCenter,
        });

        traces.push(...waveTraces);
    }

    return traces;
}

export { waveAri, waveGeo, wave, waveWave };

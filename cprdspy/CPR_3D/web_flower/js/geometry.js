// 几何内核 —— geometry.py 的逐行 JS 镜像。
//
// 为什么两边都要实现一遍？
//   * Python 端负责离线出规范（flower_spec.py）与参考几何（build_assets.py --ref），
//     可以直接和已经验证过的 blender_ellipsoid.py / ellipsoid_flower.py 对齐；
//   * 浏览器端必须自己算，滑条才能实时响应（不能每动一下就回服务端）；
//   * tests/test_parity_js.py 会把两端逐点比对，谁改了公式立刻红。
//
// 曲面公式（θ = π/2 − π/n，v = θ·t^curl）：
//   P(u,t) = ( a·cos u·sin v + x_d,  c·(cos v − cos θ),  −b·sin u·sin v )
//   x_d = a·sin θ,  y_d = c·cos θ
// 也就是「椭球冠 → 绕 X 转 −90° → 平移让边缘弧落在 y=0」。

import { DEG, eulerRzRyRx, halfTurn, matS, matT, matRz, mul } from "./math4.js";

/** numpy.linspace 的等价实现（端点精确，最后一个值直接赋值） */
export function linspace(start, stop, n) {
  const out = new Float64Array(n);
  if (n === 1) {
    out[0] = start;
    return out;
  }
  const step = (stop - start) / (n - 1);
  for (let k = 0; k < n; k++) out[k] = start + k * step;
  out[n - 1] = stop;
  return out;
}

// --------------------------------------------------------------------------
// 规范里的派生量（flower_spec.py: Generator.theta/x_d/y_d, Symmetry.step, Stack.resolve）
// --------------------------------------------------------------------------

export const SQRT8 = Math.sqrt(8);

export function thetaOf(n) {
  return Math.PI / 2 - Math.PI / n;
}

export function layerTable(spec) {
  const { symmetry, stack } = spec;
  const N = symmetry.N;
  if (stack.table && stack.table.length) {
    return stack.table.map((r) => [r[0], r[1], r[2], r[3], r.length > 4 ? r[4] : 0]);
  }
  const phase = stack.phase === null || stack.phase === undefined ? 180 / N : stack.phase;
  const [s0, s1] = stack.scale_range;
  const m = Math.max(1, stack.M - 1);
  const rows = [];
  for (let j = 0; j < stack.M; j++) {
    const t = j / m;
    const rx = stack.cup[0] + (stack.cup[1] - stack.cup[0]) * t;
    const scale = s0 * Math.pow(s1 / s0, t);
    rows.push([rx, stack.droop * j, ((j + 1) % 2) * phase, scale, stack.lift * t]);
  }
  return rows;
}

export function stepOf(spec) {
  return 360 / spec.symmetry.N + spec.symmetry.twist;
}

export function instanceCount(spec) {
  return 2 * spec.symmetry.N * layerTable(spec).length;
}

// --------------------------------------------------------------------------
// 生成元：一片花瓣的右半
// --------------------------------------------------------------------------

/**
 * @returns {{positions: Float32Array, normals: Float32Array, indices: Uint32Array,
 *            vertexCount: number, triangleCount: number}}
 */
export function buildPetal(g) {
  const th = thetaOf(g.n);
  const xD = g.a * Math.sin(th);
  const nu = Math.max(2, Math.round(g.nu));
  const nv = Math.max(2, Math.round(g.nv));
  const curl = g.curl;
  const cosTh = Math.cos(th);

  const U = linspace(0, Math.PI, nu);
  const T = linspace(0, 1, nv);

  const nVerts = nu * nv;
  const positions = new Float32Array(nVerts * 3);
  const normals = new Float32Array(nVerts * 3);

  for (let i = 0; i < nv; i++) {
    const t = T[i];
    const v = th * Math.pow(t, curl);
    const sv = Math.sin(v);
    const cv = Math.cos(v);
    // t=0 处 v' 的解析值：curl>1 → 0，curl=1 → θ，curl<1 → ∞（但法向极限仍是 (0,1,0)）
    const vprime = t > 0 ? th * curl * Math.pow(t, curl - 1) : 0;
    const rhoP = cv * vprime;
    const hP = -sv * vprime;

    for (let j = 0; j < nu; j++) {
      const u = U[j];
      const cu = Math.cos(u);
      const su = Math.sin(u);
      const o = (i * nu + j) * 3;

      positions[o] = g.a * cu * sv + xD;
      positions[o + 1] = g.c * (cv - cosTh);
      positions[o + 2] = -g.b * su * sv;

      // nrm = cross(pt, pu)，与三角形绕序同向 = 花瓣外侧
      const ptx = g.a * cu * rhoP;
      const pty = g.c * hP;
      const ptz = -g.b * su * rhoP;
      const pux = -g.a * su * sv;
      const puz = -g.b * cu * sv;
      let nx = pty * puz - ptz * 0;
      let ny = ptz * pux - ptx * puz;
      let nz = ptx * 0 - pty * pux;

      if (i === 0) {
        // 北极：所有 u 收缩到同一点，切平面水平，外法向极限 (0, 1, 0)
        nx = 0;
        ny = 1;
        nz = 0;
      }
      const len = Math.hypot(nx, ny, nz);
      if (len > 1e-12) {
        nx /= len;
        ny /= len;
        nz /= len;
      }
      if (i === 0) {
        nx = 0;
        ny = 1;
        nz = 0;
      }
      normals[o] = nx;
      normals[o + 1] = ny;
      normals[o + 2] = nz;
    }
  }

  // 索引：四边形 A=(i,j) B=(i,j+1) C=(i+1,j+1) D=(i+1,j) → (A,C,B) 与 (A,D,C)；
  // 首行（i=0）的 (A,C,B) 两点重合，直接跳过，避免零面积三角形。
  const quads = (nv - 1) * (nu - 1);
  const indices = new Uint32Array(3 * (2 * quads - (nu - 1)));
  let w = 0;
  for (let i = 0; i < nv - 1; i++) {
    for (let j = 0; j < nu - 1; j++) {
      const A = i * nu + j;
      const B = A + 1;
      const C = A + nu + 1;
      const D = A + nu;
      if (i > 0) {
        indices[w++] = A;
        indices[w++] = C;
        indices[w++] = B;
      }
      indices[w++] = A;
      indices[w++] = D;
      indices[w++] = C;
    }
  }

  return { positions, normals, indices, vertexCount: nVerts, triangleCount: w / 3 };
}

// --------------------------------------------------------------------------
// 对称群 + 层栈 → 实例矩阵（顺序：层 j → 瓣 i → 半片 R/L）
// --------------------------------------------------------------------------

/** @returns {Float64Array[]} K 个行主序 4×4 矩阵
 *
 *  乘法顺序（关键，别改回去）：
 *      m = T(lift) · Rz(phase + i·step) · Ry(ry) · Rx(rx) · S(scale)
 *  阵列旋转必须最外层（等价于 Blender 的 rotation_euler=(rx, ry, i*30+phase)）。
 *  写成 base · Rz(i·step) 会让「整层」先摆成圈、再被整体掰一次，得到歪掉的斜环。
 */
export function buildInstances(spec) {
  const g = spec.generator;
  const N = Math.max(1, Math.round(spec.symmetry.N));
  const step = stepOf(spec);
  const H = halfTurn(g.a * Math.sin(thetaOf(g.n)));
  const out = [];
  for (const [rx, ry, phase, scale, lift] of layerTable(spec)) {
    for (let i = 0; i < N; i++) {
      const m = mul(
        matT(0, 0, lift),
        mul(eulerRzRyRx(rx, ry, phase + i * step), matS(scale)),
      );
      out.push(m);
      out.push(mul(m, H));
    }
  }
  return out;
}

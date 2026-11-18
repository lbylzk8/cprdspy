// 4×4 矩阵小工具 —— geometry.py 里同名函数的逐行镜像。
//
// 约定（两边必须一致，由 tests/test_parity_js.py 锁定）：
//   * 逻辑上是「行主序 16 元数组」+「列向量」：p' = M @ p，平移在第 4 列（下标 3,7,11,15）；
//   * 交给 three.js 时才转成列主序（toColumnMajor / writeInstances）；
//   * 角度一律用「度」传入，内部转弧度；欧拉顺序 R = Rz(rz) @ Ry(ry) @ Rx(rx)。

export const DEG = Math.PI / 180;

export function identity() {
  const m = new Float64Array(16);
  m[0] = m[5] = m[10] = m[15] = 1;
  return m;
}

/** C = A @ B（行主序） */
export function mul(A, B) {
  const C = new Float64Array(16);
  for (let r = 0; r < 4; r++) {
    for (let c = 0; c < 4; c++) {
      C[r * 4 + c] =
        A[r * 4] * B[c] +
        A[r * 4 + 1] * B[4 + c] +
        A[r * 4 + 2] * B[8 + c] +
        A[r * 4 + 3] * B[12 + c];
    }
  }
  return C;
}

/** p' = M @ (x,y,z,1)，只回前三分量 */
export function apply(M, x, y, z) {
  return [
    M[0] * x + M[1] * y + M[2] * z + M[3],
    M[4] * x + M[5] * y + M[6] * z + M[7],
    M[8] * x + M[9] * y + M[10] * z + M[11],
  ];
}

export function matT(x, y, z) {
  const m = identity();
  m[3] = x;
  m[7] = y;
  m[11] = z;
  return m;
}

/** 各向同性缩放（保持 det>0，法向变换才不会翻面） */
export function matS(s) {
  const m = new Float64Array(16);
  m[0] = m[5] = m[10] = s;
  m[15] = 1;
  return m;
}

export function matRz(deg) {
  const a = deg * DEG;
  const c = Math.cos(a);
  const s = Math.sin(a);
  return new Float64Array([c, -s, 0, 0, s, c, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]);
}

export function matRy(deg) {
  const a = deg * DEG;
  const c = Math.cos(a);
  const s = Math.sin(a);
  return new Float64Array([c, 0, s, 0, 0, 1, 0, 0, -s, 0, c, 0, 0, 0, 0, 1]);
}

export function matRx(deg) {
  const a = deg * DEG;
  const c = Math.cos(a);
  const s = Math.sin(a);
  return new Float64Array([1, 0, 0, 0, 0, c, -s, 0, 0, s, c, 0, 0, 0, 0, 1]);
}

export function eulerRzRyRx(rx, ry, rz) {
  return mul(mul(matRz(rz), matRy(ry)), matRx(rx));
}

/** 左半 = 右半绕直线 {x=x_d, y=0}（沿 Z）转 180°：(x,y,z) → (2x_d−x, −y, z) */
export function halfTurn(xD) {
  const m = identity();
  m[0] = -1;
  m[5] = -1;
  m[3] = 2 * xD;
  return m;
}

/** 行主序 → three.js 需要的列主序 */
export function toColumnMajor(M, out = new Float32Array(16), offset = 0) {
  for (let c = 0; c < 4; c++) {
    for (let r = 0; r < 4; r++) out[offset + c * 4 + r] = M[r * 4 + c];
  }
  return out;
}

/**
 * 把 K 个行主序矩阵连续写进 three.js 的 instanceMatrix.array（列主序、每实例 16 个 float）。
 * 与 geometry.column_major() 产出完全相同的字节序。
 */
export function writeInstances(mats, target) {
  for (let k = 0; k < mats.length; k++) toColumnMajor(mats[k], target, k * 16);
  return target;
}

export function det3(M) {
  const a = M[0], b = M[1], c = M[2];
  const d = M[4], e = M[5], f = M[6];
  const g = M[8], h = M[9], i = M[10];
  return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g);
}

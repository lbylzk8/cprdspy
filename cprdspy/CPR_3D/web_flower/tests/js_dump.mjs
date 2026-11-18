// 把 JS 侧的几何输出成 JSON，交给 tests/test_parity_js.py 和 Python 逐点比对。
//
// 只 import geometry.js / math4.js —— 这两个文件必须保持「无浏览器、无 three.js 依赖」，
// 否则这条一致性测试就跑不起来（也正是这个约束逼着数学和渲染分层的）。
//
//   node tests/js_dump.mjs                 # 全部预设，写到 stdout
//   node tests/js_dump.mjs ROSE LOTUS      # 指定预设

import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { buildInstances, buildPetal, layerTable, stepOf, thetaOf } from "../js/geometry.js";
import { toColumnMajor } from "../js/math4.js";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.dirname(HERE);

const data = JSON.parse(readFileSync(path.join(ROOT, "assets", "presets.json"), "utf8"));
const wanted = process.argv.slice(2).length ? process.argv.slice(2) : data.order;

const out = {};
for (const name of wanted) {
  const spec = data.presets[name];
  if (!spec) throw new Error(`presets.json 里没有 ${name}`);
  const petal = buildPetal(spec.generator);
  const mats = buildInstances(spec);
  const col = new Float32Array(mats.length * 16);
  mats.forEach((m, k) => toColumnMajor(m, col, k * 16));

  out[name] = {
    theta: thetaOf(spec.generator.n),
    step: stepOf(spec),
    layers: layerTable(spec),
    positions: Array.from(petal.positions),
    normals: Array.from(petal.normals),
    indices: Array.from(petal.indices),
    counts: {
      vertices: petal.vertexCount,
      triangles: petal.triangleCount,
      instances: mats.length,
    },
    matrices: mats.map((m) => Array.from(m)), // 行主序 float64
    colMajor: Array.from(col), // three.js 实际吃的那份 float32
  };
}

process.stdout.write(JSON.stringify(out));

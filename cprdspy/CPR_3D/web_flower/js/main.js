// 入口：取预设 → 建场景 → 建面板 → 把三者接起来。
// 这个文件刻意不含任何花朵知识，只做转发和状态管理。

import { FlowerScene } from "./scene.js";
import { Panel } from "./panel.js";

const $ = (sel) => document.querySelector(sel);

function fail(msg, detail) {
  const box = $("#boot");
  box.classList.remove("hidden");
  box.textContent = "";
  box.appendChild(Object.assign(document.createElement("strong"), { textContent: `启动失败：${msg}` }));
  if (detail) {
    const pre = document.createElement("pre");
    pre.textContent = String(detail);
    box.appendChild(pre);
  }
  console.error(msg, detail);
}

async function loadPresets() {
  const res = await fetch("assets/presets.json", { cache: "no-store" });
  if (!res.ok) throw new Error(`assets/presets.json -> HTTP ${res.status}`);
  const data = await res.json();
  if (!data.presets || !Array.isArray(data.order) || !data.order.length) {
    throw new Error("presets.json 结构不对（缺 presets / order）");
  }
  return data;
}

function jitter(spec) {
  const r = (lo, hi) => lo + Math.random() * (hi - lo);
  const g = spec.generator;
  g.a = r(1.2, 3.0);
  g.b = r(0.15, 1.2);
  g.c = r(0.8, 3.0);
  g.n = Math.round(r(3, 9));
  g.curl = r(0.6, 2.0);
  spec.symmetry.N = Math.round(r(5, 20));
  spec.symmetry.twist = r(-12, 12);
  spec.stack.M = Math.round(r(2, 7));
  spec.stack.cup = [r(-10, 35), r(10, 60)];
  spec.stack.droop = r(-32, 4);
  spec.stack.scale_range = [r(1.2, 3.0), r(0.6, 1.2)];
  spec.stack.lift = r(0, 1.2);
  spec.stack.table = null; // 显式层表会锁死配方滑条，随机变体一定要清掉
  spec.name = "RANDOM";
  return spec;
}

async function main() {
  const data = await loadPresets();
  const clone = (name) => structuredClone(data.presets[name]);

  const scene = new FlowerScene($("#stage"));
  const hash = decodeURIComponent(location.hash.replace(/^#/, ""));
  let currentName = data.order.includes(hash) ? hash : data.order[0];
  let spec = clone(currentName);
  let lastRadius = 0;

  // ---------------------------------------------------------------- 应用

  /** @param {boolean} refit 是否重新取景（只在换预设/尺度突变时为 true） */
  function apply({ refit = false } = {}) {
    scene.setSpec(spec);
    const r = scene.radius; // setSpec 里由实例包围球算出的精确尺寸
    if (refit || Math.abs(r - lastRadius) > 0.25 * Math.max(r, lastRadius)) {
      scene.frameCamera();
      lastRadius = r;
    }
  }

  function usePreset(name) {
    currentName = name;
    spec = clone(name);
    panel.setSpec(spec);
    apply({ refit: true });
    mark(name);
    history.replaceState(null, "", `#${name}`);
  }

  // ---------------------------------------------------------------- 面板

  const panel = new Panel($("#panel"), spec, () => apply());
  panel.mountDerived($("#derived"));
  panel.onExport = (kind) => {
    if (kind === "glb") scene.exportGLB().catch((e) => fail("GLB 导出失败", e));
    else if (kind === "png") scene.exportPNG();
    else scene.exportSpec();
  };
  panel.onLoad = (raw) => {
    spec = raw;
    currentName = spec.name || "CUSTOM";
    panel.setSpec(spec);
    apply({ refit: true });
    mark(null);
  };
  panel.onView = (v) => {
    if (v.autoRotate !== undefined) scene.setAutoRotate(v.autoRotate);
    if (v.grid !== undefined) scene.setGrid(v.grid);
    if (v.env !== undefined) scene.setEnv(v.env);
    if (v.frame) {
      lastRadius = 0;
      apply({ refit: true });
    }
  };

  // ---------------------------------------------------------------- 预设条

  const buttons = new Map();
  const bar = $("#presets");
  for (const name of data.order) {
    const b = document.createElement("button");
    b.className = "preset";
    b.textContent = name;
    b.title = `按 ${data.order.indexOf(name) + 1} 号键`;
    b.addEventListener("click", () => usePreset(name));
    bar.appendChild(b);
    buttons.set(name, b);
  }
  const dice = document.createElement("button");
  dice.className = "preset alt";
  dice.textContent = "随机变体";
  dice.addEventListener("click", () => {
    spec = jitter(structuredClone(spec));
    currentName = "RANDOM";
    panel.setSpec(spec);
    apply({ refit: true });
    mark(null);
  });
  bar.appendChild(dice);
  buttons.set(null, dice);

  function mark(name) {
    for (const [k, b] of buttons) b.classList.toggle("on", k === name);
  }

  // ---------------------------------------------------------------- 其它

  scene.onStats = (st) => {
    $("#stats").textContent =
      `${st.instances} 实例 · ${(st.triangles / 1000).toFixed(0)}k 三角面 · ` +
      `花瓣网格只传 1 份（${st.vertices} 顶点）· 重建 ${st.ms.toFixed(1)} ms · ${st.fps} fps` +
      (st.truncated ? "（实例数已截断）" : "");
  };

  window.addEventListener("keydown", (e) => {
    // 焦点在控件里时不抢键；e.target 也可能是 window/document（合成事件、无焦点时）
    if (e.target?.matches?.("input, textarea, select, [contenteditable]")) return;
    const k = e.key.toLowerCase();
    if (k === "r") {
      scene.setAutoRotate(!scene.controls.autoRotate);
    } else if (k === "g") {
      scene.setGrid(!scene.ground.visible);
    } else if (k === "f") {
      lastRadius = 0;
      apply({ refit: true });
    } else if (/^[1-9]$/.test(k)) {
      const name = data.order[Number(k) - 1];
      if (name) usePreset(name);
    }
  });

  $("#share").addEventListener("click", async () => {
    const url = new URL(location.href);
    url.hash = `#${encodeURIComponent(currentName)}`;
    try {
      await navigator.clipboard.writeText(url.toString());
      $("#share").textContent = "已复制链接";
    } catch {
      prompt("复制这个链接：", url.toString());
    }
    setTimeout(() => ($("#share").textContent = "复制链接"), 1600);
  });

  mark(currentName);
  apply({ refit: true });
  $("#boot").classList.add("hidden");

  // 控制台可直接 __flower.scene / __flower.spec 折腾；自动化检查也靠它强制渲染一帧
  window.__flower = { scene, panel, apply, usePreset, get spec() { return spec; } };
}

main().catch((e) =>
  fail(
    "先导出资产，再用本地服务器打开页面。",
    [
      "cd web_flower",
      "python build_assets.py     # 生成 assets/presets.json",
      "python serve.py            # 打开 http://127.0.0.1:8080/",
      "",
      "ES 模块不能从 file:// 直接加载，必须走 HTTP。",
      "",
      String(e && e.stack ? e.stack : e),
    ].join("\n"),
  ),
);

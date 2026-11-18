// 控制面板：把 spec 的字段变成滑条，改完就回调重画。
// 面板不碰几何，几何不碰 DOM —— 两边只通过 spec 这个纯对象通信。

import { layerTable, stepOf, thetaOf } from "./geometry.js";

/** path → 值 */
function get(obj, path) {
  return path.split(".").reduce((o, k) => (o === undefined || o === null ? o : o[k]), obj);
}
function set(obj, path, value) {
  const keys = path.split(".");
  let o = obj;
  for (let i = 0; i < keys.length - 1; i++) o = o[keys[i]];
  o[keys[keys.length - 1]] = value;
}

export const PALETTES = {
  玫瑰: {
    color_outer: ["#ffd1e8", "#ffb3d9", "#ff8fc4", "#f76fae", "#e04f97"],
    color_inner: ["#ffc2b3", "#ff9f87", "#f77f68", "#e0644f", "#c4493a"],
  },
  睡莲: {
    color_outer: ["#cfefff", "#a8e0ff", "#7fcdf2", "#59b6e3", "#3d97c9"],
    color_inner: ["#eafcff", "#c2f2ff", "#9ae8ff", "#6fdcf5", "#48c4e8"],
  },
  龙舌兰: {
    color_outer: ["#d8f5c8", "#b7e8a4", "#93d981", "#6fc763", "#4fb048", "#33963a"],
    color_inner: ["#eef7c9", "#dcef9f", "#cbe276", "#b5d252", "#9bbf36", "#7da826"],
  },
  暮光: {
    color_outer: ["#ffe9b0", "#ffc978", "#f79a5c", "#d96a63", "#a8467c"],
    color_inner: ["#fff5d6", "#ffdfa1", "#ffb877", "#e88a72", "#b95f8b"],
  },
  水墨: {
    color_outer: ["#f2f4f7", "#d7dde6", "#b3bdcc", "#8b98ad", "#63708a"],
    color_inner: ["#e8ecf2", "#c2ccd9", "#98a6ba", "#6e7d94", "#4a586e"],
  },
};

const SCHEMA = [
  {
    group: "生成元 · 一片花瓣",
    hint: "θ = π/2 − π/n 是「n 瓣刚好铺满平面」的临界半角，整朵花的比例感都来自它。",
    items: [
      { path: "generator.a", label: "瓣长 a", min: 0.4, max: 4, step: 0.02 },
      { path: "generator.b", label: "瓣厚 b", min: 0.05, max: 2, step: 0.02 },
      { path: "generator.c", label: "鼓起 c", min: 0.2, max: 4, step: 0.02 },
      { path: "generator.n", label: "铺满数 n", min: 3, max: 12, step: 1, int: true },
      { path: "generator.curl", label: "卷度 curl", min: 0.4, max: 3, step: 0.02 },
      { path: "generator.nu", label: "网格 nu", min: 6, max: 160, step: 2, int: true },
      { path: "generator.nv", label: "网格 nv", min: 3, max: 80, step: 1, int: true },
    ],
  },
  {
    group: "对称群 · 排成一圈",
    hint: "第 i 瓣绕花轴转 i·(360/N + twist)。twist≠0 就成旋涡，代价是不再闭合。",
    items: [
      { path: "symmetry.N", label: "每层瓣数 N", min: 1, max: 24, step: 1, int: true },
      { path: "symmetry.twist", label: "扭角 twist°", min: -25, max: 25, step: 0.5 },
    ],
  },
  {
    group: "层栈 · 一层层叠起来",
    hint: "配方：scale 几何衰减、rx 线性（杯口）、ry 线性（下垂）、奇偶层错开 180/N。",
    items: [
      { path: "stack.M", label: "层数 M", min: 1, max: 9, step: 1, int: true },
      { path: "stack.cup.0", label: "杯角起 rx₀", min: -60, max: 80, step: 1 },
      { path: "stack.cup.1", label: "杯角止 rx₁", min: -60, max: 80, step: 1 },
      { path: "stack.droop", label: "下垂 ry/层", min: -45, max: 20, step: 0.5 },
      { path: "stack.phase", label: "错列角 phase°", min: 0, max: 60, step: 0.5, allowAuto: true },
      { path: "stack.scale_range.0", label: "外层缩放 s₀", min: 0.4, max: 4, step: 0.02 },
      { path: "stack.scale_range.1", label: "内层缩放 s₁", min: 0.2, max: 4, step: 0.02 },
      { path: "stack.lift", label: "内层抬升 lift", min: -1, max: 3, step: 0.02 },
    ],
  },
  {
    group: "样式",
    items: [{ path: "style.opacity", label: "透明度", min: 0.15, max: 1, step: 0.01 }],
  },
];

export class Panel {
  /**
   * @param {HTMLElement} root     挂载点
   * @param {object}      spec     会被就地修改的规范对象
   * @param {(spec:object, meta:object)=>void} onChange
   */
  constructor(root, spec, onChange) {
    this.root = root;
    this.spec = spec;
    this.onChange = onChange;
    this.controls = new Map();
    this.render();
  }

  emit(meta = {}) {
    this.updateDerived();
    this.onChange(this.spec, meta);
  }

  render() {
    this.root.textContent = "";
    for (const section of SCHEMA) this.root.appendChild(this.#section(section));
    this.root.appendChild(this.#styleSection());
    this.root.appendChild(this.#viewSection());
    this.root.appendChild(this.#ioSection());
    this.sync();
  }

  #section({ group, hint, items }) {
    const box = el("section", "grp");
    box.appendChild(el("h3", null, group));
    if (hint) box.appendChild(el("p", "hint", hint));
    for (const item of items) box.appendChild(this.#slider(item));
    return box;
  }

  #slider(item) {
    const row = el("div", "row");
    const label = el("label", null, item.label);
    const input = document.createElement("input");
    input.type = "range";
    input.min = item.min;
    input.max = item.max;
    input.step = item.step;
    const out = el("span", "val");

    const read = () => {
      const raw = get(this.spec, item.path);
      return raw === null || raw === undefined ? null : Number(raw);
    };
    const show = (v) => (out.textContent = v === null ? "自动" : fmt(v, item.int));

    input.addEventListener("input", () => {
      const v = item.int ? Math.round(Number(input.value)) : Number(input.value);
      set(this.spec, item.path, v);
      if (item.path.startsWith("stack.") || item.path === "generator.n") this.#applyVisibility();
      show(v);
      this.emit({ path: item.path });
    });

    if (item.allowAuto) {
      const auto = document.createElement("button");
      auto.className = "mini";
      auto.textContent = "自动";
      auto.title = "错列角 = 180/N，奇偶层交替";
      auto.addEventListener("click", () => {
        set(this.spec, item.path, null);
        this.sync();
        this.emit({ path: item.path });
      });
      label.appendChild(auto);
    }

    row.append(label, input, out);
    this.controls.set(item.path, { input, show, read, item });
    return row;
  }

  // ---- 配色 / 线框 -------------------------------------------------------

  #styleSection() {
    const box = el("section", "grp");
    box.appendChild(el("h3", null, "配色"));

    const sel = document.createElement("select");
    for (const name of Object.keys(PALETTES)) {
      const o = document.createElement("option");
      o.value = name;
      o.textContent = name;
      sel.appendChild(o);
    }
    sel.addEventListener("change", () => {
      Object.assign(this.spec.style, PALETTES[sel.value]);
      this.emit({ path: "style" });
    });

    const wire = document.createElement("input");
    wire.type = "checkbox";
    wire.checked = !!this.spec.style.wireframe;
    wire.addEventListener("change", () => {
      this.spec.style.wireframe = wire.checked;
      this.emit({ path: "style.wireframe" });
    });
    this.wire = wire;

    const flip = document.createElement("button");
    flip.className = "mini";
    flip.textContent = "内外互换";
    flip.addEventListener("click", () => {
      const a = this.spec.style.color_outer;
      this.spec.style.color_outer = this.spec.style.color_inner;
      this.spec.style.color_inner = a;
      this.emit({ path: "style" });
    });

    box.append(row("色板", sel), row("线框", wire), row("", flip));
    return box;
  }

  // ---- 视图 --------------------------------------------------------------

  #viewSection() {
    const box = el("section", "grp");
    box.appendChild(el("h3", null, "视图"));

    const rotate = document.createElement("input");
    rotate.type = "checkbox";
    rotate.addEventListener("change", () => this.onView({ autoRotate: rotate.checked }));

    const grid = document.createElement("input");
    grid.type = "checkbox";
    grid.checked = true;
    grid.addEventListener("change", () => this.onView({ grid: grid.checked }));

    const env = document.createElement("select");
    for (const [v, t] of [["dark", "深色"], ["studio", "浅色棚拍"], ["black", "纯黑"]]) {
      const o = document.createElement("option");
      o.value = v;
      o.textContent = t;
      env.appendChild(o);
    }
    env.addEventListener("change", () => this.onView({ env: env.value }));

    const frame = document.createElement("button");
    frame.className = "mini";
    frame.textContent = "重置视角";
    frame.addEventListener("click", () => this.onView({ frame: true }));

    box.append(row("自动旋转", rotate), row("极坐标网格", grid), row("背景", env), row("", frame));
    this.onView = () => {};
    return box;
  }

  // ---- 导入 / 导出 -------------------------------------------------------

  #ioSection() {
    const box = el("section", "grp");
    box.appendChild(el("h3", null, "导入 / 导出"));

    this.ta = document.createElement("textarea");
    this.ta.rows = 6;
    this.ta.spellcheck = false;
    this.ta.value = JSON.stringify(this.spec, null, 2);

    const show = document.createElement("button");
    show.className = "mini";
    show.textContent = "把当前 spec 写入文本框";
    show.addEventListener("click", () => {
      this.ta.value = JSON.stringify(this.spec, null, 2);
    });

    const load = document.createElement("button");
    load.className = "mini";
    load.textContent = "读取文本框并应用";
    load.addEventListener("click", () => {
      try {
        const parsed = JSON.parse(this.ta.value);
        this.onLoad(parsed);
      } catch (err) {
        this.ta.classList.add("bad");
        setTimeout(() => this.ta.classList.remove("bad"), 900);
        console.error("spec JSON 解析失败", err);
      }
    });
    this.onLoad = () => {};

    const mk = (text, fn) => {
      const b = document.createElement("button");
      b.className = "mini";
      b.textContent = text;
      b.addEventListener("click", fn);
      return b;
    };
    this.exportBtns = [
      mk("下载 GLB", () => this.onExport && this.onExport("glb")),
      mk("下载 PNG", () => this.onExport && this.onExport("png")),
      mk("下载 spec.json", () => this.onExport && this.onExport("json")),
    ];
    this.onExport = null;

    box.append(row("", show), this.ta, row("", load), row("", ...this.exportBtns));
    return box;
  }

  // ------------------------------------------------------------------ 状态

  /** 显式层表 (stack.table) 存在时，配方滑条无效 —— 直接灰掉，免得用户以为坏了 */
  #applyVisibility() {
    const locked = !!(this.spec.stack.table && this.spec.stack.table.length);
    for (const path of ["stack.M", "stack.cup.0", "stack.cup.1", "stack.droop", "stack.phase",
      "stack.scale_range.0", "stack.scale_range.1", "stack.lift"]) {
      const c = this.controls.get(path);
      if (!c) continue;
      c.input.disabled = locked;
      c.input.parentElement.classList.toggle("locked", locked);
    }
  }

  updateDerived() {
    if (!this.derived) return;
    const g = this.spec.generator;
    const rows = layerTable(this.spec);
    const th = (thetaOf(g.n) * 180) / Math.PI;
    this.derived.textContent =
      `θ = ${th.toFixed(1)}°   步进 = ${stepOf(this.spec).toFixed(2)}°   ` +
      `层数 = ${rows.length}   实例 K = 2·${this.spec.symmetry.N}·${rows.length} = ${2 * this.spec.symmetry.N * rows.length}`;
  }

  /** spec 被整体替换（换预设 / 导入 JSON）后重新同步所有控件 */
  sync() {
    for (const { input, show, read } of this.controls.values()) {
      const v = read();
      if (v === null) {
        show(null);
        input.value = input.min;
      } else {
        input.value = String(v);
        show(v);
      }
    }
    if (this.wire) this.wire.checked = !!this.spec.style.wireframe;
    this.#applyVisibility();
    this.updateDerived();
  }

  setSpec(spec) {
    this.spec = spec;
    this.sync();
    this.ta.value = JSON.stringify(spec, null, 2);
  }

  mountDerived(node) {
    this.derived = node;
    this.updateDerived();
  }
}

// ---------------------------------------------------------------- 小工具

function el(tag, cls, text) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text !== undefined) n.textContent = text;
  return n;
}

function row(labelText, ...nodes) {
  const r = el("div", "row");
  r.appendChild(el("label", null, labelText));
  for (const n of nodes) r.appendChild(n);
  return r;
}

function fmt(v, isInt) {
  if (isInt) return String(Math.round(v));
  return Math.abs(v) >= 100 ? v.toFixed(0) : v.toFixed(2);
}

// three.js 场景层：只负责「把 spec 画出来 + 交互 + 导出」，不含任何花朵数学。
//
// 性能要点（对应 blender_ellipsoid.py 的教训）：
//   * 花瓣网格只上传 GPU 一次（1 个 BufferGeometry），整朵花 = 1 个 InstancedMesh
//     + K 个实例矩阵 + K 个实例颜色。K = 2·N·M，默认 120。
//   * 原来 Blender 里 120 个物体 × 各自 1 万顶点 = 120 万顶点；这里 2048 顶点 + 120 矩阵。

import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFExporter } from "three/addons/exporters/GLTFExporter.js";

import { buildInstances, buildPetal } from "./geometry.js";
import { toColumnMajor, writeInstances } from "./math4.js";

const MAX_INSTANCES = 4096;

function hexPerLayer(list, j) {
  if (!list || !list.length) return "#ffffff";
  return list[Math.min(j, list.length - 1)];
}

export class FlowerScene {
  // 私有字段必须先声明再用（node --check / V8 都会直接 SyntaxError）
  #resizeObserver;
  #raf = 0;

  constructor(container) {
    this.container = container;

    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 0.98;
    container.appendChild(this.renderer.domElement);

    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color("#12151c");
    this.scene.fog = new THREE.Fog("#12151c", 18, 60);

    // 花轴是 Z，所以把 up 立到 Z 上，OrbitControls 的旋转才符合直觉
    this.camera = new THREE.PerspectiveCamera(42, 1, 0.05, 500);
    this.camera.up.set(0, 0, 1);
    this.camera.position.set(9, -9, 6);

    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.08;
    this.controls.autoRotateSpeed = 0.9;
    this.controls.target.set(0, 0, 1.6);

    this.#addLights();
    this.#addGround();

    this.geometry = null;
    this.mesh = null;
    this.spec = null;
    this.radius = 4;
    this.center = new THREE.Vector3(0, 0, 1.2);
    this.envMode = "dark";
    this.stats = { instances: 0, triangles: 0, vertices: 0, ms: 0 };

    // 计帧用 performance.now()，不引入 THREE.Clock（r187 已废弃）
    this.frames = 0;
    this.fpsAt = performance.now();
    this.fps = 0;

    this.#resizeObserver = new ResizeObserver(() => this.resize());
    this.#resizeObserver.observe(container);
    this.resize(); // 统一走一处带 1px 保底的尺寸计算

    this.#loop();
  }

  #addLights() {
    // 灯光强度是调过的：ACES + 过强的 key 会把 #ffd1e8 这类浅粉吹成近白，
    // 花瓣的分层色就没了。宁可略暗一点保住饱和度。
    this.scene.add(new THREE.HemisphereLight("#dfe9ff", "#2a2118", 0.95));

    const key = new THREE.DirectionalLight("#fff2e0", 1.6);
    key.position.set(6, -8, 12);
    this.scene.add(key);

    const rim = new THREE.DirectionalLight("#8fc4ff", 0.85);
    rim.position.set(-9, 7, -4);
    this.scene.add(rim);

    const fill = new THREE.DirectionalLight("#ffd0e8", 0.4);
    fill.position.set(0, 10, 3);
    this.scene.add(fill);
  }

  #addGround() {
    this.ground = new THREE.Group();
    const polar = new THREE.PolarGridHelper(7, 12, 6, 96, "#33405c", "#242c3d");
    polar.rotation.x = Math.PI / 2; // PolarGridHelper 默认躺在 XZ，搬到 XY（花轴 Z）
    this.ground.add(polar);
    this.scene.add(this.ground);
  }

  // ---------------------------------------------------------------- 构建

  /** @param {object} spec 完整花型规范（presets.json 里的一个条目，或面板改过的副本） */
  setSpec(spec) {
    const t0 = performance.now();
    this.spec = spec;

    const petal = buildPetal(spec.generator);
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute("position", new THREE.BufferAttribute(petal.positions, 3));
    geometry.setAttribute("normal", new THREE.BufferAttribute(petal.normals, 3));
    geometry.setIndex(new THREE.BufferAttribute(petal.indices, 1));
    if (this.geometry) this.geometry.dispose();
    this.geometry = geometry;

    const mats = buildInstances(spec);
    const K = mats.length;
    const truncated = K > MAX_INSTANCES;
    const count = Math.min(K, MAX_INSTANCES);

    if (!this.mesh) this.#createMesh();
    this.mesh.geometry = this.geometry;
    this.mesh.count = count;

    const target = this.mesh.instanceMatrix.array;
    writeInstances(mats.slice(0, count), target);
    this.mesh.instanceMatrix.needsUpdate = true;

    const color = new THREE.Color();
    const per = 2 * spec.symmetry.N;
    for (let k = 0; k < count; k++) {
      const j = Math.floor(k / per);
      const half = k % 2; // 0=右半(外侧色) 1=左半(内侧色)
      const hex = half === 0
        ? hexPerLayer(spec.style.color_outer, j)
        : hexPerLayer(spec.style.color_inner, j);
      this.mesh.setColorAt(k, color.set(hex));
    }
    if (this.mesh.instanceColor) this.mesh.instanceColor.needsUpdate = true;

    // 精确包围球：three 会按 count 逐个实例变换几何包围球再求并集，
    // 比任何「按参数估」的半径都靠谱 —— 相机取景和地板网格都用它。
    this.mesh.computeBoundingSphere();
    this.center = this.mesh.boundingSphere.center.clone();
    this.radius = Math.max(0.4, this.mesh.boundingSphere.radius);

    const st = spec.style;
    this.mesh.material.opacity = st.opacity;
    this.mesh.material.wireframe = !!st.wireframe;
    this.mesh.material.transparent = st.opacity < 0.999;
    this.mesh.material.depthWrite = st.opacity > 0.6;
    this.mesh.material.needsUpdate = true;

    this.ground.scale.setScalar(Math.max(0.3, this.radius / 4.5));

    this.stats = {
      instances: count,
      triangles: petal.triangleCount * count,
      vertices: petal.vertexCount,
      ms: performance.now() - t0,
      truncated,
    };
    if (truncated) console.warn(`web_flower: 实例数 ${K} 超过上限 ${MAX_INSTANCES}，已截断`);
    // 立刻回一次数：静态截图/无 rAF 的环境里也要能看到规模，而不是等下一帧
    if (this.onStats) this.onStats({ ...this.stats, fps: this.fps });
  }

  #createMesh() {
    const material = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      roughness: 0.52,
      metalness: 0.02,
      side: THREE.DoubleSide, // 花瓣是单面壳体，背面也得亮
      transparent: true,
      opacity: 0.92,
    });
    this.mesh = new THREE.InstancedMesh(this.geometry, material, MAX_INSTANCES);
    this.mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    this.mesh.frustumCulled = false;
    this.scene.add(this.mesh);
  }

  // ---------------------------------------------------------------- 视图

  frameCamera() {
    const r = this.radius;
    const c = this.center;
    const d = r * 2.45;
    this.camera.position.set(c.x + d * 0.62, c.y - d * 0.62, c.z + d * 0.52);
    this.controls.target.set(c.x, c.y, c.z);
    this.camera.near = Math.max(0.01, r / 150);
    this.camera.far = r * 80;
    this.camera.updateProjectionMatrix();
    this.controls.update();
    this.setEnv(this.envMode ?? "dark"); // 雾的距离跟着花的尺寸走
  }

  resize() {
    const w = this.container.clientWidth || 1;
    const h = this.container.clientHeight || 1;
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(w, h);
  }

  setAutoRotate(on) {
    this.controls.autoRotate = !!on;
  }

  setGrid(on) {
    this.ground.visible = !!on;
  }

  setEnv(mode) {
    this.envMode = mode;
    const bg = { dark: "#12151c", studio: "#e9ecf2", black: "#000000" }[mode] || "#12151c";
    this.scene.background = new THREE.Color(bg);
    this.scene.fog.color = new THREE.Color(bg);
    const r = this.radius;
    const light = mode === "studio";
    this.scene.fog.near = r * (light ? 2.4 : 1.7);
    this.scene.fog.far = r * (light ? 14 : 9);
  }

  #loop() {
    this.#raf = requestAnimationFrame(() => this.#loop());
    this.controls.update();
    this.renderer.render(this.scene, this.camera);

    this.frames++;
    const now = performance.now();
    if (now - this.fpsAt > 500) {
      this.fps = Math.round((this.frames * 1000) / (now - this.fpsAt));
      this.frames = 0;
      this.fpsAt = now;
      if (this.onStats) this.onStats({ ...this.stats, fps: this.fps });
    }
  }

  // ---------------------------------------------------------------- 导出

  /** 把 InstancedMesh 摊平成「共享几何 + K 个节点」再导出，GLTFExporter 不支持实例化 */
  #flatten() {
    const group = new THREE.Group();
    const mats = buildInstances(this.spec).slice(0, this.mesh.count);
    const cache = new Map();
    const per = 2 * this.spec.symmetry.N;
    mats.forEach((M, k) => {
      const j = Math.floor(k / per);
      const half = k % 2;
      const hex = half === 0
        ? hexPerLayer(this.spec.style.color_outer, j)
        : hexPerLayer(this.spec.style.color_inner, j);
      if (!cache.has(hex)) {
        cache.set(hex, new THREE.MeshStandardMaterial({
          color: new THREE.Color(hex),
          roughness: 0.52,
          metalness: 0.02,
          side: THREE.DoubleSide,
          transparent: this.spec.style.opacity < 0.999,
          opacity: this.spec.style.opacity,
        }));
      }
      const mesh = new THREE.Mesh(this.geometry, cache.get(hex));
      mesh.matrixAutoUpdate = false;
      mesh.matrix.fromArray(toColumnMajor(M, new Float64Array(16))); // 导出保精度：列主序 float64
      mesh.matrixWorldNeedsUpdate = true;
      group.add(mesh);
    });
    group.userData.materials = [...cache.values()]; // 交给 exportGLB 用完就释放
    return group;
  }

  async exportGLB() {
    const group = this.#flatten();
    group.updateMatrixWorld(true);
    try {
      const exporter = new GLTFExporter();
      const buffer = await exporter.parseAsync(group, { binary: true, onlyVisible: false });
      download(new Blob([buffer], { type: "model/gltf-binary" }), `${this.spec.name}.glb`);
    } finally {
      for (const m of group.userData.materials) m.dispose();
    }
  }

  exportPNG() {
    // WebGL 默认不保留绘制缓冲：异步的 toBlob 回调时缓冲区可能已被清成空白图。
    // 同步的 readPixels 读的就是当前 framebuffer，不依赖 preserveDrawingBuffer（那玩意有性能代价）。
    this.renderer.render(this.scene, this.camera);
    const gl = this.renderer.getContext();
    const W = gl.drawingBufferWidth;
    const H = gl.drawingBufferHeight;
    const px = new Uint8Array(W * H * 4);
    gl.readPixels(0, 0, W, H, gl.RGBA, gl.UNSIGNED_BYTE, px);

    const canvas = document.createElement("canvas");
    canvas.width = W;
    canvas.height = H;
    const ctx = canvas.getContext("2d");
    const img = ctx.createImageData(W, H);
    for (let y = 0; y < H; y++) {
      const src = (H - 1 - y) * W * 4; // readPixels 从左下角开始，DOM 从左上角
      img.data.set(px.subarray(src, src + W * 4), y * W * 4);
    }
    ctx.putImageData(img, 0, 0);
    canvas.toBlob((blob) => download(blob, `${this.spec.name}.png`), "image/png");
  }

  exportSpec() {
    download(
      new Blob([JSON.stringify(this.spec, null, 2)], { type: "application/json" }),
      `${this.spec.name}.json`,
    );
  }

  dispose() {
    cancelAnimationFrame(this.#raf);
    this.#resizeObserver.disconnect();
    this.mesh?.material.dispose();
    this.mesh?.dispose();
    this.geometry?.dispose();
    this.controls.dispose();
    this.renderer.dispose();
  }
}

function download(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 4000);
}

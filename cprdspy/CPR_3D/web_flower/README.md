# web_flower —— 参数化花瓣/花朵建模库（Python 规范 + three.js 网页端）

从 [`blender_ellipsoid.py`](../blender_ellipsoid.py) 里那朵手写 5 层 ×12 瓣的椭球花出发，
把它的**几何规律抽成一份数据**，然后：

- **Python** 负责定义花型（`flower_spec.py`）、算参考几何（`geometry.py`）、导出资产（`build_assets.py`）；
- **浏览器** 用 three.js 把同一份数据实时画出来，滑条随便拖（`js/`）；
- 两端各有一份公式实现，由 `tests/test_parity_js.py` 逐点锁死，防止漂移。

```
花 = ⋃_层  T_层 · ⋃_i  [ Rz(phase_层 + i·step) · Ry(ry) · Rx(rx) · S(scale) ] · 花瓣
花瓣 = 右半椭球冠 ∪ (右半绕竖直线转 180°)
step = 360°/N + twist
```

> **乘法顺序不能反。** 阵列旋转 `Rz(phase + i·step)` 必须是最外层（等价于 Blender 的
> `rotation_euler_deg=(rx, ry, i*30 + phase)`）。若写成 `Rz(phase)·Ry·Rx·S·Rz(i·step)`，
> 杯角/下垂角就变成"先把整圈摆好、再整体掰一次"，每一层会退化成一个**歪掉的斜环**——
> 内层 droop 最大所以歪得最凶，看上去正是"最上层那层花是斜的"。
> `test_each_layer_is_a_centered_ring` 与 `test_instances_match_ellipsoid_flower_place` 守着这条。


---

## 30 秒跑起来

```bash
cd cprdspy/CPR_3D/web_flower

python build_assets.py          # 生成 assets/presets.json（改了 flower_spec.py 后要重跑）
python serve.py                 # → http://127.0.0.1:8080/
python run_tests.py             # 16 项性质测试 + Python↔JS 一致性 + 前端静态检查
```

依赖：Python 3 + numpy（仓库本来就有）、Node（只为跑一致性测试，缺了会自动 SKIP）。
**前端零构建**：three.js 走 CDN importmap，没有 `node_modules`、没有打包步骤。

> 必须用 HTTP 打开。`file://` 下浏览器拒绝加载 ES 模块，`serve.py` 顺手解决了
> Windows 把 `.js` 报成 `text/plain` 和缓存旧文件这两个坑。

---

## 文件

| 文件 | 职责 |
| --- | --- |
| `flower_spec.py` | **唯一真源**。`Generator / Symmetry / Stack / Style / FlowerSpec` 五个 dataclass + 6 个预设。纯数据，无依赖 |
| `geometry.py` | numpy 参考实现：`build_petal`（右半网格）、`build_instances`（K 个 4×4 矩阵）、`to_obj` |
| `build_assets.py` | 离线导出：`assets/presets.json`（前端用）、`assets/ref/*.json`（测试用）、`assets/obj/*.obj`（进 Blender 用） |
| `serve.py` | 本地静态服务器：正确 MIME + no-cache |
| `js/math4.js` | 4×4 矩阵小工具（`geometry.py` 同名函数的镜像） |
| `js/geometry.js` | 花瓣网格 + 实例矩阵（**不碰 DOM、不 import three**，所以能在 node 里跑） |
| `js/scene.js` | three.js 场景：`InstancedMesh`、灯光、取景、GLB/PNG 导出 |
| `js/panel.js` | 参数面板：把 spec 字段变成滑条 |
| `js/main.js` | 入口，只做转发和状态管理 |
| `tests/` | 性质测试、`node` 几何转储、Python↔JS 逐点一致性 |
| `run_tests.py` | 一键自检（不依赖 pytest） |

分层的硬约束：`js/geometry.js` 和 `js/math4.js` **只依赖 ECMAScript 标准库**。
这条约束不是洁癖——它是让"节点上跑一遍 JS、和 Python 对一遍数"成为可能的唯一原因。

---

## 范式：三层抽象，缺一不可

| 层 | 管什么 | 字段 | 换了会怎样 |
| --- | --- | --- | --- |
| 生成元 `Generator` | 一片花瓣长什么样 | `a b c n curl nu nv` | 瓣形：圆鼓 / 尖硬 / 卷边 |
| 对称群 `Symmetry` | 怎么排成一圈 | `N twist` | 瓣数；`twist≠0` 变旋涡 |
| 层栈 `Stack` | 怎么一层层叠起来 | `M cup droop phase scale_range lift` | 花型：玫瑰 / 郁金香 / 龙舌兰 |

三个关键点：

1. **临界角 θ = π/2 − π/n**。`n` 瓣的椭球冠刚好铺满平面时的半角就是这个值 ——
   这和 2D 圆弧花 [`CPR_matplotlib/Flowers/flower.py`](../../CPR_matplotlib/Flowers/flower.py)
   里的 `theta_arc = π/2 − π/n + arccos(a/r)` 是同一个角。2D 花和 3D 花是**一个范式实例化两次**。
2. **左半 = 右半绕直线 {x=x_d, y=0} 转 180°**，即 `(x,y,z) → (2x_d−x, −y, z)`。
   这个映射的行列式是 **+1**（是旋转，不是镜像），所以它可以当成一个**实例矩阵**而不是一份新网格。
   于是整朵花 = **1 个几何体 + 2·N·M 个矩阵**。这是全库最重要的一条简化。
3. **层栈可以是闭式配方**，不必手调。原 Blender demo 手写的 L0..L4 满足：
   `scale = s₀·(s₁/s₀)^(j/(M−1))`、`ry = droop·j`、`rx` 线性、`phase = (j+1)%2 · 180/N`。
   测试 `test_recipe_reproduces_blender_demo` 把这条量化了：**ry 和 phase 逐点精确相等**，
   scale 最大偏差 0.18，rx 最大偏差 7.5°。

### curl：一个免费的手感旋钮

`v = θ·t^curl` 是子午线重参数化。`curl=1` 就是标准椭球冠；`>1` 脊部变平、边缘变陡；`<1` 反过来。
它不动任何端点约束（`ρ(0)=0`、`ρ(1)=sinθ`、`h(0)=1`、`h(1)=cosθ`），所以花瓣照样拼得拢——
由 `test_curl_changes_shape_but_keeps_endpoints` 守住。

---

## 预设

| 名字 | n | N | M | 实例 K | 特点 |
| --- | --- | --- | --- | --- | --- |
| `ROSE` | 4 | 12 | 5 | 120 | 闭式配方版 |
| `ROSE_TABLE` | 4 | 12 | 5 | 120 | Blender demo 的手写层表（回归锚点，面板滑条会锁死） |
| `LOTUS` | 6 | 16 | 4 | 128 | 平铺宽瓣，`curl=0.75` |
| `TULIP` | 5 | 6 | 3 | 36 | 少瓣高杯，内层立起来 |
| `AGAVE` | 8 | 12 | 6 | 144 | 硬直尖瓣 + 6° 扭角 |
| `SPIRAL` | 5 | 13 | 5 | 130 | 11° 扭角旋涡 |

---

## 在 Python 里直接用

```python
from flower_spec import preset, Stack, Symmetry
from geometry import build_petal, build_instances, to_obj

spec = preset("LOTUS")
spec.symmetry = Symmetry(N=20, twist=-4)     # 换对称群
spec.stack = Stack(M=6, cup=(5, 30), droop=-8)  # 换层栈

petal = build_petal(spec.generator)          # positions/normals/indices，只算右半
mats = build_instances(spec)                 # (2·N·M, 4, 4)，列向量约定 p' = M @ p
print(to_obj(spec, "lotus.obj"))             # 拖进 Blender 对照
```

导一份给浏览器：

```bash
python build_assets.py --ref --obj      # assets/presets.json + assets/ref/ + assets/obj/
```

---

## 验证过什么

| 检查 | 结果 |
| --- | --- |
| `build_petal` vs 已对过 Blender 的 [`ellipsoid_flower.py`](../ellipsoid_flower.py) | 右半 **4.44e-16**，左半（经半周矩阵）**4.44e-16** |
| Python ↔ JS（6 个预设，逐点） | positions / normals / 索引 / colMajor 字节序 **完全相等**；实例矩阵 ≤ **2.7e-15** |
| 顶点法向 | 处处单位长（`min|n| = 1.0`），与三角形绕序同向（`min dot = 0.96`） |
| 退化三角形 | 0 个（北极行只保留有效三角形） |
| 实例矩阵 | 全部 `det > 0`（纯旋转 × 各向同性缩放，不会翻面） |
| 实例矩阵 vs `ellipsoid_flower.place(tilt=(rx, ry, phase+i·step))` | 逐点 **< 1e-12**，乘法顺序的护栏 |
| 每层是否为同心正环（各瓣极点同高同半径、相邻瓣严格差一个 `Rz(step)`） | 6 个预设全部通过 |
| 几何性质 | 边缘弧精确落在 `y=0`；北极整行收缩为一点；JSON 往返无损 |
| 浏览器实测（无头 Chromium + WebGL） | 6 预设渲染覆盖率 25–31%，`glGetError()=0`，控制台零报错；换预设/拖滑条/导入 JSON/快捷键全通 |
| GLB 导出 | `ROSE.glb` 127,632 字节，magic `glTF` version 2 |
| PNG 导出 | 57,994 字节，像素内容非空（走 `readPixels` 而非异步 `toBlob`，避开绘制缓冲被清） |
| HTTP 服务 | `text/javascript` / `application/json` / `no-store` 全部正确 |

### 为什么不用 Blender 那种建模方式

`blender_ellipsoid.py` 的原 demo 里，120 个花瓣是 **120 个各自独立的 mesh**：
实测 **4.41 s、120 份网格数据、1,200,000 个存储顶点**。
改成"共享网格 + 链接副本"是 **0.06 s、2 份网格、20,000 顶点**（快 73×、省 60× 内存），世界坐标不变。

网页端走的是同一条路的极限形态：**1 份花瓣网格（2048 顶点）+ 120 个实例矩阵**，
GPU 内存里约 2 万顶点而不是 120 万。实测整朵花重建 **6 ms**（含上传网格），
拖滑条时 0.8 ms。

---

## 已知边界

- **只建模花瓣，没有花蕊/茎/叶**。生成元只有 `ellipsoid_cap` 一种；加新瓣形是加一个 `kind` 分支，不是改范式。
- 左半靠矩阵而不是镜像 —— 这是**优点**（能实例化），意味着花瓣内部结构左右同手性，做真实植物的"内外侧不同色"需要另加一套 UV 或分组材质。
- 实例上限 `MAX_INSTANCES = 4096`（约 `N=24, M=85`），超了会在状态栏提示并截断。
- 透明度靠 `depthWrite` 开关权衡，多层半叠时排序仍会有轻微瑕疵；要完美透射得走 OIT，超出范围。
- 无头浏览器能验证渲染管线和数据，**验证不了真机上的观感**。视觉效果请自己开页面看。
- `n < 3`（θ 为负）在数学上是退化花，面板已挡住，但手改 JSON 能绕过去 —— 不崩，只是看不见。

## 相关文件

- 上游分析：[`../blender_ellipsoid.py`](../blender_ellipsoid.py)（原始 Blender 版，本库没改它）
- 无 Blender 快速版：[`../ellipsoid_flower.py`](../ellipsoid_flower.py)（plotly/matplotlib，本库的数值参考基准）
- 2D 同源：[`../../CPR_matplotlib/Flowers/flower.py`](../../CPR_matplotlib/Flowers/flower.py)

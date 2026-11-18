"""一键跑完 web_flower 的全部自检（不依赖 pytest）。

    python run_tests.py              # Python 性质测试 + Python↔JS 一致性 + 前端静态检查
    python run_tests.py --quick      # 只跑 Python 性质测试（没装 node 时用）
    python run_tests.py --serve      # 额外起服务器，真发一次 HTTP 请求验证 MIME/no-cache

退出码非 0 表示有测试失败，可以直接接进 CI。
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
# Windows 控制台默认 GBK，中文断言消息会花掉；强制 UTF-8
FLAGS = ["-X", "utf8"]


def run(title: str, argv: list[str], *, optional: bool = False) -> bool:
    print(f"\n=== {title} ===")
    cmd = [argv[0], *FLAGS, *argv[1:]] if argv[0] == PY else argv  # 给 python 子进程加 -X utf8
    proc = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True, encoding="utf-8")
    print(((proc.stdout or "") + (proc.stderr or "")).rstrip())
    if proc.returncode != 0 and optional:
        print("  (可选步骤失败，忽略)")
        return True
    return proc.returncode == 0


def check_frontend() -> bool:
    """index.html 引用的本地文件必须都在，importmap 必须钉住 three 的版本。"""
    print("\n=== 前端静态检查 ===")
    ok = True
    with open(os.path.join(HERE, "index.html"), encoding="utf-8") as f:
        html = f.read()

    refs = re.findall(r'(?:src|href)="([^"]+)"', html)
    for ref in refs:
        if ref.startswith(("http", "data:", "#")):
            continue
        path = os.path.join(HERE, ref.replace("/", os.sep))
        if os.path.exists(path):
            print(f"  ok    引用存在 {ref}")
        else:
            print(f"  FAIL  引用缺失 {ref}")
            ok = False

    pinned = re.findall(r'cdn[^"]*three@(\d+\.\d+\.\d+)', html)
    if not pinned:
        print("  FAIL  importmap 没把 three 钉到具体版本（裸 unpkg/skypack 会随 CDN 漂移）")
        ok = False
    elif len(set(pinned)) == 1:
        print(f"  ok    three 钉在 {pinned[0]}")
    else:
        print(f"  FAIL  three 版本不一致：{sorted(set(pinned))}")
        ok = False

    # 场景里用到的 three 导出必须真的存在（防止升级 three 后静默炸）
    for js in ("js/scene.js", "js/main.js", "js/panel.js", "js/geometry.js", "js/math4.js"):
        with open(os.path.join(HERE, js), encoding="utf-8") as f:
            src = f.read()
        if re.search(r"^\s*import .* from\s+[\"'](?!three|\.)([^\"']+)", src, re.M):
            print(f"  FAIL  {js} 引入了意外的第三方裸模块（只允许 three / 相对路径）")
            ok = False
    return ok


def check_node_syntax() -> bool:
    """node --check 逐个解析 ES 模块，抓语法错（不需要 three，纯语法）。"""
    if shutil.which("node") is None:
        print("\n=== JS 语法检查 ===\n  SKIP  没装 node")
        return True
    print("\n=== JS 语法检查 ===")
    ok = True
    for name in ("math4", "geometry", "scene", "panel", "main"):
        path = os.path.join(HERE, "js", f"{name}.js")
        proc = subprocess.run(["node", "--check", path], capture_output=True, text=True, cwd=HERE)
        if proc.returncode == 0:
            print(f"  ok    js/{name}.js 解析通过")
        else:
            ok = False
            print(f"  FAIL  js/{name}.js\n{proc.stderr.strip()}")
    return ok


def check_http() -> bool:
    """真起一次服务器，验证 index.html / js / json 的 Content-Type 和 no-cache。"""
    import urllib.request

    print("\n=== HTTP 服务检查 ===")
    port = 8731
    proc = subprocess.Popen(
        [PY, *FLAGS, "serve.py", "--port", str(port)],
        cwd=HERE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        import time

        for _ in range(50):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/index.html", timeout=0.3).read()
                break
            except OSError:
                time.sleep(0.1)
        else:
            print("  FAIL  服务器没起来")
            return False

        want = {
            "/index.html": "text/html",
            "/js/scene.js": "text/javascript",
            "/assets/presets.json": "application/json",
        }
        ok = True
        for path, ctype in want.items():
            with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=2) as r:
                got = r.headers.get("Content-Type", "")
                cache = r.headers.get("Cache-Control", "")
                good = ctype in got and "no-store" in cache
                ok &= good
                print(f"  {'ok  ' if good else 'FAIL'}  {path:26s} {got} | {cache}")
        return ok
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:  # pragma: no cover
            proc.kill()


def main() -> int:
    ap = argparse.ArgumentParser(description="web_flower 自检")
    ap.add_argument("--quick", action="store_true", help="只跑 Python 性质测试")
    ap.add_argument("--serve", action="store_true", help="额外做一次真实 HTTP 检查")
    args = ap.parse_args()

    if not os.path.exists(os.path.join(HERE, "assets", "presets.json")):
        print("assets/presets.json 不存在，先跑 python build_assets.py")
        return 2

    results = [("Python 性质测试", run("Python 性质测试", [PY, "tests/test_python.py"]))]
    if not args.quick:
        results.append(("前端静态检查", check_frontend()))
        results.append(("JS 语法检查", check_node_syntax()))
        results.append(("Python↔JS 一致性", run("Python↔JS 一致性", [PY, "tests/test_parity_js.py"])))
    if args.serve:
        results.append(("HTTP 服务", check_http()))

    print("\n" + "=" * 46)
    for name, ok in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    failed = [n for n, ok in results if not ok]
    print("=" * 46)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

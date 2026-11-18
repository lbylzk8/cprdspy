"""web_flower 的本地静态服务器（ES 模块不能用 file:// 打开，必须走 HTTP）。

    python serve.py                # http://127.0.0.1:8080/
    python serve.py --port 9000 --open

为什么不用 `python -m http.server`：
  1. Windows 的注册表常常把 .js 报成 text/plain 或 application/octet-stream，
     浏览器会以「严格 MIME」拒绝执行模块；
  2. 默认没有 no-cache —— 改了 js/*.js 刷新却拿到旧文件，是最难查的一类假 bug；
  3. 没有 .wasm / .map 之类扩展名的处理。
"""

from __future__ import annotations

import argparse
import functools
import http.server
import os
import socketserver
import webbrowser

HERE = os.path.dirname(os.path.abspath(__file__))

MIME = {
    ".html": "text/html; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".mjs": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".wasm": "application/wasm",
    ".map": "application/json; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".obj": "text/plain; charset=utf-8",
    ".glb": "model/gltf-binary",
}


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**MIME, "": "application/octet-stream"}

    def end_headers(self) -> None:  # noqa: D102
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def log_message(self, fmt: str, *args) -> None:  # 只打有意义的行
        if "404" in str(args):
            super().log_message(fmt, *args)


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main() -> int:
    ap = argparse.ArgumentParser(description="web_flower 本地服务器")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--dir", default=HERE, help="站点根目录（默认 web_flower/）")
    ap.add_argument("--open", action="store_true", help="启动后打开浏览器")
    args = ap.parse_args()

    handler = functools.partial(Handler, directory=os.path.abspath(args.dir))
    url = f"http://{args.host}:{args.port}/index.html"
    with Server((args.host, args.port), handler) as httpd:
        print(f"root  : {os.path.abspath(args.dir)}")
        print(f"open  : {url}")
        print("Ctrl-C 停止")
        if args.open:
            webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

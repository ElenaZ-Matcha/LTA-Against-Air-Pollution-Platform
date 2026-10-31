"""Local server for the platform: serves week11/ (like `python -m http.server --directory ..`)
and accepts exports, so DXF / JSON / PNG land in 01-Platform/exports/ even where the browser
cannot download (the Claude app's preview pane).

    python serve_platform.py [port]        -> http://localhost:8765/01-Platform/LTA-Against%20Air%20Pollution%20Platform.html

POST /__save?name=<file name>  body = file bytes  -> {"path": "..."}
GET  /__ping                                       -> {"ok": true}
Bound to 127.0.0.1 only; names are reduced to a safe base name.
"""
import json
import re
import socket
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "exports"
MAX = 60 * 1024 * 1024


class Handler(SimpleHTTPRequestHandler):
    def _json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if urlparse(self.path).path == "/__ping":
            return self._json(200, {"ok": True, "dir": str(OUT)})
        return super().do_GET()

    def do_POST(self):
        u = urlparse(self.path)
        if u.path != "/__save":
            return self._json(404, {"error": "not found"})
        name = (parse_qs(u.query).get("name") or [""])[0]
        name = re.sub(r"[^A-Za-z0-9._ -]", "_", Path(name).name).strip(" .")[:150]
        n = int(self.headers.get("Content-Length") or 0)
        if not name or n <= 0 or n > MAX:
            return self._json(400, {"error": "bad name or size"})
        OUT.mkdir(exist_ok=True)
        p = OUT / name
        p.write_bytes(self.rfile.read(n))
        print(f"saved {p} ({n} bytes)")
        return self._json(200, {"path": str(p.relative_to(ROOT.parent))})


class Server6(ThreadingHTTPServer):
    address_family = socket.AF_INET6


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    h = partial(Handler, directory=str(ROOT))
    # loopback only, IPv4 and IPv6 (browsers resolve localhost to either)
    srv = ThreadingHTTPServer(("127.0.0.1", port), h)
    try:
        threading.Thread(target=Server6(("::1", port), h).serve_forever, daemon=True).start()
    except OSError:
        pass
    print(f"serving {ROOT} on http://localhost:{port} · exports -> {OUT}", flush=True)
    srv.serve_forever()

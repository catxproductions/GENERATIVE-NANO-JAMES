"""
GENERATIVE-NANO-JAMES HTTP Backend Server.
Serves static frontend (index.html) and JSON REST API.
Operates using Python standard libraries + NumPy.

Run:
    python backend.py
Then access: http://localhost:8000
"""

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from nano_ultra_james import VERSION, NanoUltraJames

ROOT = os.path.dirname(os.path.abspath(__file__))
WEIGHTS_FILE = os.path.join(ROOT, "weights.json")

brain = NanoUltraJames(WEIGHTS_FILE)
lock = threading.Lock()

class Handler(BaseHTTPRequestHandler):
    def reply(self, data, code=200, ctype="application/json"):
        body = data if isinstance(data, bytes) else json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/", "/index.html"):
            with open(os.path.join(ROOT, "index.html"), "rb") as f:
                return self.reply(f.read(), ctype="text/html; charset=utf-8")
        if path == "/api/state":
            with lock:
                return self.reply(brain.state())
        self.reply({"error": "not found"}, 404)

    def do_POST(self):
        path = self.path.split("?")[0]
        try:
            size = min(int(self.headers.get("Content-Length") or 0), 10_000)
            payload = json.loads(self.rfile.read(size) or b"{}")
        except ValueError:
            return self.reply({"error": "request body must be valid JSON"}, 400)

        if path == "/api/chat":
            message = str(payload.get("message", "")).strip()[:500]
            if not message:
                return self.reply({"error": "message is empty"}, 400)
            with lock:
                return self.reply(brain.chat(message))

        if path == "/api/reset":
            with lock:
                brain.reset()
                return self.reply(brain.state())

        self.reply({"error": "not found"}, 404)

    def log_message(self, fmt, *args):
        pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"{VERSION} running on http://localhost:{port} (Ctrl+C to stop & save weights.json)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        with lock:
            brain.save()
        server.server_close()
        print("System weights safely saved to weights.json. Server shut down.")

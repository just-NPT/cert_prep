"""Local server for quiz.html: serves this folder and saves finished attempts to results/.

Run: python serve.py [port]    then open http://localhost:8000/quiz.html

POST /api/results  saves one attempt (JSON) as results/<YYYYMMDD-HHMMSS>_<exam>_<mode>.json
GET  /api/results  lists saved attempts (summary fields only), newest first
Saved files are also served as plain files under /results/.
"""
import glob, json, os, re, sys
from datetime import datetime
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
SUMMARY = ("exam", "mode", "score", "total", "pct", "pass", "startedAt", "finishedAt", "durationMs")
MAX_BODY = 20 * 1024 * 1024


def slug(s):
    return re.sub(r"[^A-Za-z0-9-]+", "-", str(s)).strip("-")[:40] or "x"


def save_result(attempt):
    os.makedirs(RESULTS, exist_ok=True)
    base = f"{datetime.now():%Y%m%d-%H%M%S}_{slug(attempt.get('exam'))}_{slug(attempt.get('mode'))}"
    name, n = base + ".json", 1
    while os.path.exists(os.path.join(RESULTS, name)):
        n += 1
        name = f"{base}-{n}.json"
    with open(os.path.join(RESULTS, name), "x", encoding="utf-8") as f:
        json.dump(attempt, f, ensure_ascii=False, indent=1)
    return name


def list_results():
    rows = []
    for p in sorted(glob.glob(os.path.join(RESULTS, "*.json")), reverse=True):
        try:
            with open(p, encoding="utf-8") as f:
                a = json.load(f)
            rows.append({"file": os.path.basename(p), **{k: a.get(k) for k in SUMMARY}})
        except (OSError, ValueError):
            pass
    return rows


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.split("?")[0] == "/api/results":
            return self.send_json(200, list_results())
        super().do_GET()

    def do_POST(self):
        if self.path.split("?")[0] != "/api/results":
            return self.send_json(404, {"error": "not found"})
        try:
            n = int(self.headers.get("Content-Length") or 0)
            if not 0 < n <= MAX_BODY:
                raise ValueError
            attempt = json.loads(self.rfile.read(n))
            if not isinstance(attempt, dict) or not isinstance(attempt.get("questions"), list):
                raise ValueError
        except ValueError:
            return self.send_json(400, {"error": "expected an attempt JSON object with a questions list"})
        self.send_json(201, {"file": save_result(attempt)})

    def send_json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def make_server(port):
    return ThreadingHTTPServer(("127.0.0.1", port), partial(Handler, directory=HERE))


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    httpd = make_server(port)
    print(f"Quiz: http://localhost:{port}/quiz.html   (attempts saved to {RESULTS})")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

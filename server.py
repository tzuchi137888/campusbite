"""Run with python server.py; localhost only, no packages or API keys required."""
import copy
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from engine import DurationModel, recommend, validate_options

ROOT = Path(__file__).resolve().parent
MODEL = DurationModel(ROOT / "data" / "synthetic_meals.csv")


def table(tid, capacity, party=0, elapsed=0):
    return {"id": tid, "capacity": capacity, "party": party, "elapsed": elapsed}


DEFAULT = [
    {"id": "rice", "name": "Campus Rice Kitchen", "meal": "rice", "outbound_m": 400,
     "return_m": 560, "cleanup": 2, "queue": [2, 1],
     "tables": [table("A1", 2, 2, 18), table("A2", 2, 1, 7),
                table("A3", 4, 3, 13), table("A4", 4, 4, 20), table("A5", 6, 4, 4)]},
    {"id": "noodles", "name": "Corner Noodle House", "meal": "noodles", "outbound_m": 640,
     "return_m": 480, "cleanup": 2, "queue": [],
     "tables": [table("B1", 2), table("B2", 2, 2, 15),
                table("B3", 4, 4, 22), table("B4", 4), table("B5", 6, 5, 10)]},
    {"id": "cafe", "name": "Garden Cafe", "meal": "cafe", "outbound_m": 240,
     "return_m": 320, "cleanup": 3, "queue": [3, 2, 1, 4],
     "tables": [table("C1", 2, 2, 8), table("C2", 2, 1, 10),
                table("C3", 4, 3, 15), table("C4", 4, 4, 20), table("C5", 6, 5, 12)]},
]
STATE = copy.deepcopy(DEFAULT)
LOCK = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, content, content_type="application/json; charset=utf-8"):
        body = json.dumps(content, ensure_ascii=False).encode() if isinstance(content, (dict, list)) else content
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        route = urlsplit(self.path).path
        if route == "/api/state":
            with LOCK:
                state = copy.deepcopy(STATE)
            self.reply(200, {"restaurants": state, "source": "synthetic demo snapshot"})
        elif route == "/api/health":
            self.reply(200, {"ok": True, "model": "empirical conditional duration", "rows": len(MODEL.rows)})
        elif route in ("/", "/index.html", "/app.js", "/style.css"):
            name = "index.html" if route == "/" else route[1:]
            mime = {"html": "text/html", "js": "text/javascript", "css": "text/css"}[name.rsplit(".", 1)[1]]
            self.reply(200, (ROOT / "static" / name).read_bytes(), mime + "; charset=utf-8")
        else:
            self.reply(404, {"error": "Not found"})

    def do_POST(self):
        global STATE
        # Prevent another website from modifying this local demo via a browser.
        origin = self.headers.get("Origin")
        if origin and origin not in ("http://127.0.0.1:8000", "http://localhost:8000"):
            self.reply(403, {"error": "Cross-origin request rejected"})
            return
        try:
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                raise ValueError("Send application/json.")
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 10000:
                raise ValueError("Invalid request size.")
            raw = json.loads(self.rfile.read(length))
            if not isinstance(raw, dict):
                raise ValueError("Expected a JSON object.")
            route = urlsplit(self.path).path
            if route == "/api/recommend":
                options = validate_options(raw)
                with LOCK:
                    state = copy.deepcopy(STATE)
                results = [recommend(r, options, MODEL) for r in state]
                results.sort(key=lambda r: (r["scenarios"]["cautious"] or {}).get("total", float("inf")))
                self.reply(200, {"restaurants": results, "options": options})
            elif route == "/api/reset":
                with LOCK:
                    STATE = copy.deepcopy(DEFAULT)
                self.reply(200, {"ok": True})
            elif route == "/api/update":
                with LOCK:
                    target = next((r for r in STATE if r["id"] == raw.get("restaurant")), None)
                    if target is None:
                        raise ValueError("Unknown restaurant.")
                    if "queue" in raw:
                        queue = raw["queue"]
                        if not isinstance(queue, list) or len(queue) > 30 or any(type(n) is not int or not 1 <= n <= 6 for n in queue):
                            raise ValueError("Queue: at most 30 groups, each with 1 to 6 people.")
                        target["queue"] = queue
                    else:
                        item = next((t for t in target["tables"] if t["id"] == raw.get("table")), None)
                        if item is None:
                            raise ValueError("Unknown table.")
                        party, elapsed = raw.get("party"), raw.get("elapsed")
                        if type(party) is not int or not 0 <= party <= item["capacity"]:
                            raise ValueError("Group exceeds table capacity.")
                        if type(elapsed) is not int or not 0 <= elapsed <= 180:
                            raise ValueError("Elapsed time must be 0 to 180 minutes.")
                        item.update(party=party, elapsed=elapsed if party else 0)
                self.reply(200, {"ok": True})
            else:
                self.reply(404, {"error": "Not found"})
        except (ValueError, KeyError, TypeError) as error:
            self.reply(400, {"error": str(error)})


if __name__ == "__main__":
    print("CampusBite demo: http://127.0.0.1:8000\nSynthetic snapshot; Ctrl+C to stop.")
    try:
        ThreadingHTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")

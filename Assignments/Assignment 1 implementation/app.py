"""University Student Records API - standard-library implementation.
Runs on Python 3.11+ without third-party packages; container-ready via Dockerfile.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from datetime import datetime, timezone
import json, os, time, threading, resource

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5000"))
STARTED = time.time()
REQUESTS = 0
LOCK = threading.Lock()
STUDENTS = [
    {"id": 1, "register_number": "192511001", "name": "Aarav Kumar", "department": "CSE", "year": 3},
    {"id": 2, "register_number": "192511002", "name": "Meera Sharma", "department": "CSE", "year": 3},
    {"id": 3, "register_number": "192511003", "name": "Rohan Patel", "department": "IT", "year": 2},
    {"id": 4, "register_number": "192511004", "name": "Ananya Das", "department": "ECE", "year": 4},
]

class Handler(BaseHTTPRequestHandler):
    server_version = "UniversityCloudPOC/1.0"

    def send_json(self, status, payload):
        body = json.dumps(payload, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        global REQUESTS
        with LOCK:
            REQUESTS += 1
        path = urlparse(self.path).path
        if path == "/":
            html = DASHBOARD.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
        elif path == "/health":
            self.send_json(200, {"status": "healthy", "service": "University Student Records API", "timestamp": datetime.now(timezone.utc).isoformat()})
        elif path == "/api/students":
            self.send_json(200, {"count": len(STUDENTS), "students": STUDENTS})
        elif path.startswith("/api/students/"):
            try:
                student_id = int(path.rsplit("/", 1)[1])
            except ValueError:
                return self.send_json(400, {"error": "Student ID must be an integer"})
            student = next((s for s in STUDENTS if s["id"] == student_id), None)
            if student is None:
                return self.send_json(404, {"error": "Student not found", "student_id": student_id})
            self.send_json(200, student)
        elif path == "/metrics":
            usage = resource.getrusage(resource.RUSAGE_SELF)
            self.send_json(200, {
                "process_id": os.getpid(),
                "uptime_seconds": round(time.time() - STARTED, 2),
                "requests_served": REQUESTS,
                "max_resident_memory_mb": round(usage.ru_maxrss / (1024 if os.name != "darwin" else 1024*1024), 2),
                "cpu_time_seconds": round(usage.ru_utime + usage.ru_stime, 4),
                "resource_limit_note": "Local process metrics; use docker stats after container deployment for container-level CPU and memory usage."
            })
        else:
            self.send_json(404, {"error": "Endpoint not found", "path": path})

    def log_message(self, fmt, *args):
        print("[%s] %s - %s" % (datetime.now().strftime("%H:%M:%S"), self.address_string(), fmt % args), flush=True)

DASHBOARD = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>University Cloud POC</title><style>
*{box-sizing:border-box}body{margin:0;background:#f3f6fb;color:#17243a;font:15px/1.5 Arial,sans-serif}.wrap{max-width:1050px;margin:38px auto;padding:0 22px}.hero{background:linear-gradient(120deg,#102a56,#1767a9);color:white;border-radius:18px;padding:30px 34px;box-shadow:0 12px 30px #102a5620}.tag{font-size:12px;letter-spacing:1.5px;text-transform:uppercase;color:#b9d8f5}.hero h1{margin:8px 0;font-size:30px}.hero p{margin:0;color:#dcecff}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:20px 0}.card{background:white;border:1px solid #e1e8f2;border-radius:14px;padding:18px;box-shadow:0 5px 16px #17243a08}.muted{color:#62728a;font-size:13px}.value{font-size:24px;font-weight:700;margin-top:5px}.ok{color:#118454}.section{margin-top:22px}.section h2{font-size:18px}.table{width:100%;border-collapse:collapse;background:white;border-radius:12px;overflow:hidden}.table th,.table td{text-align:left;padding:12px;border-bottom:1px solid #e8edf4}.table th{background:#edf3fa;color:#42536b}.pill{background:#e5f7ee;color:#087747;border-radius:20px;padding:4px 10px;font-size:12px;font-weight:bold}pre{background:#111d31;color:#d8e9ff;padding:15px;border-radius:10px;overflow:auto;font-size:12px}.foot{margin:20px 0;color:#718096;font-size:12px}@media(max-width:700px){.grid{grid-template-columns:1fr}.hero h1{font-size:24px}}</style></head><body><div class="wrap"><header class="hero"><div class="tag">Cloud Computing · Containerization Proof of Concept</div><h1>University Student Records API</h1><p>Live service dashboard · API validation · resource monitoring</p></header><div class="grid"><div class="card"><div class="muted">Service status</div><div class="value ok" id="status">Checking…</div></div><div class="card"><div class="muted">Student records</div><div class="value" id="count">—</div></div><div class="card"><div class="muted">Requests served</div><div class="value" id="requests">—</div></div></div><section class="section"><h2>Student records</h2><table class="table"><thead><tr><th>ID</th><th>Register number</th><th>Name</th><th>Department</th><th>Year</th></tr></thead><tbody id="students"><tr><td colspan="5">Loading…</td></tr></tbody></table></section><section class="section"><h2>Live resource monitor</h2><div class="card"><div class="muted">Process metrics from /metrics</div><pre id="metrics">Loading…</pre></div></section><section class="section"><h2>Available API endpoints</h2><div class="card"><p><b>GET /health</b> — service health check</p><p><b>GET /api/students</b> — list student records</p><p><b>GET /api/students/1</b> — retrieve one student</p><p><b>GET /api/students/999</b> — expected HTTP 404 failure case</p><p><b>GET /metrics</b> — process resource information</p></div></section><p class="foot">Academic proof of concept using sample data only. No real student information is stored.</p></div><script>
async function load(){const h=await fetch('/health');const health=await h.json();document.getElementById('status').innerHTML='<span class="pill">'+health.status.toUpperCase()+'</span>';const r=await fetch('/api/students');const data=await r.json();document.getElementById('count').textContent=data.count;document.getElementById('students').innerHTML=data.students.map(s=>`<tr><td>${s.id}</td><td>${s.register_number}</td><td>${s.name}</td><td>${s.department}</td><td>${s.year}</td></tr>`).join('');const m=await fetch('/metrics');const md=await m.json();document.getElementById('requests').textContent=md.requests_served;document.getElementById('metrics').textContent=JSON.stringify(md,null,2)}load();</script></body></html>'''

if __name__ == "__main__":
    print(f"Starting University Student Records API on http://{HOST}:{PORT}", flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()

#!/usr/bin/env python3
"""Local demonstrator for the CO3 Cloud Collaboration assignment.
This is a locally hosted prototype, not a production cloud deployment."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
import json, sqlite3, os, secrets
from http import cookies

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, 'placement_demo.db')
HOST, PORT = '127.0.0.1', 8000
SESSIONS = {}


def connect():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with connect() as c:
        c.execute('''CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY, title TEXT NOT NULL, company TEXT NOT NULL,
            location TEXT NOT NULL, status TEXT NOT NULL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL,
            owner TEXT NOT NULL, status TEXT NOT NULL, updated_by TEXT NOT NULL)''')
        if c.execute('SELECT COUNT(*) FROM opportunities').fetchone()[0] == 0:
            c.executemany('INSERT INTO opportunities(title,company,location,status) VALUES(?,?,?,?)', [
                ('Graduate Cloud Support Engineer','Northstar Systems','Remote - India','Open'),
                ('Junior Platform Engineer','BluePeak Technologies','Chennai, India','Open'),
                ('Technical Support Associate','Vertex Cloud','Remote - APAC','Open')])
        if c.execute('SELECT COUNT(*) FROM tasks').fetchone()[0] == 0:
            c.executemany('INSERT INTO tasks(title,owner,status,updated_by) VALUES(?,?,?,?)', [
                ('Review placement eligibility','Student A','In Progress','System'),
                ('Upload updated resume','Student B','Pending','System'),
                ('Confirm interview schedule','Placement Officer','Pending','System')])

HTML = r'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>CampusConnect | Cloud Placement Coordination</title>
<style>
:root{--navy:#163b61;--blue:#2b6595;--pale:#eaf2f8;--ink:#26384a;--muted:#61758a;--line:#d7e1eb;--green:#287a58;--teal:#2f7f86;--purple:#76579a;--orange:#b77928}*{box-sizing:border-box}body{margin:0;background:#f4f7fa;color:var(--ink);font:15px/1.55 Arial,Helvetica,sans-serif}.top{background:var(--navy);color:white;padding:20px max(22px,calc((100% - 1120px)/2));display:flex;justify-content:space-between;align-items:center;gap:16px}.brand{font-size:21px;font-weight:700}.sub{font-size:12px;color:#dce8f3}.wrap{max-width:1120px;margin:26px auto;padding:0 20px}.intro{background:white;border:1px solid var(--line);border-radius:12px;padding:22px;margin-bottom:18px}.intro h1{margin:0 0 5px;color:var(--navy);font-size:25px}.muted{color:var(--muted)}.toolbar{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin-top:14px}.toolbar label{font-weight:600}.toolbar select, input,button{font:inherit;border:1px solid var(--line);border-radius:7px;padding:9px 11px;background:white;color:var(--ink)}button{background:var(--blue);border-color:var(--blue);color:white;font-weight:600;cursor:pointer}button.secondary{background:white;color:var(--blue)}.grid{display:grid;grid-template-columns:1.15fr .85fr;gap:18px}.panel{background:white;border:1px solid var(--line);border-radius:10px;padding:20px;margin-bottom:18px;box-shadow:0 1px 2px rgba(22,59,97,.05)}.panel h2{font-size:18px;color:var(--navy);margin:0 0 13px}.card{border:1px solid #d5e1eb;border-left:5px solid var(--blue);border-radius:8px;padding:13px;margin:10px 0;background:#f8fbfe}.card:nth-child(2){border-left-color:var(--teal);background:#f5fbfa}.card:nth-child(3){border-left-color:var(--purple);background:#faf8fd}.card strong{display:block;color:#1d3854}.tag{display:inline-block;background:#e8f3ed;color:var(--green);border-radius:4px;padding:2px 9px;font-size:12px;margin-top:5px}.task:nth-child(2){border-left:3px solid #76579a;padding-left:10px}.task:nth-child(3){border-left:3px solid #b77928;padding-left:10px}.row{display:flex;justify-content:space-between;align-items:center;gap:12px}.task{padding:11px 0;border-bottom:1px solid var(--line)}.task:last-child{border:0}.task small{display:block;color:var(--muted)}.status{font-size:12px;background:var(--pale);padding:3px 8px;border-radius:12px;white-space:nowrap}.notice{padding:10px 12px;background:#eaf2f8;border-left:4px solid var(--blue);border-radius:4px;margin-top:12px;font-size:13px}.api{background:#edf3f8;color:#24425e;border:1px solid #d7e1eb;border-radius:6px;padding:13px;font:12px/1.5 Consolas,monospace;overflow-wrap:anywhere}.footer{text-align:center;color:var(--muted);font-size:12px;padding:16px}.hidden{display:none}@media(max-width:760px){.grid{grid-template-columns:1fr}.top{align-items:flex-start;flex-direction:column}.intro h1{font-size:22px}}
</style></head><body><header class="top"><div><div class="brand">CampusConnect</div><div class="sub">Cloud-Based College Placement Coordination Prototype</div></div><div class="sub">CO3 · Cloud access · REST API · Collaboration</div></header>
<main class="wrap"><section class="intro"><h1>Placement Coordination Workspace</h1><div class="muted">A centralized workspace for placement opportunities, student tasks and authorized status updates.</div><div class="toolbar"><label for="role">Demonstration user</label><select id="role"><option value="student_a">Student A</option><option value="student_b">Student B</option><option value="faculty">Placement Officer</option><option value="recruiter">Recruiter</option></select><button id="login">Apply role</button><span id="loginState" class="muted">Current access: Student A</span></div><div class="notice">Prototype environment: locally hosted for assignment demonstration. A production deployment would use managed identity, HTTPS termination, cloud database and object storage.</div></section>
<div class="grid"><div><section class="panel"><h2>Open Placement Opportunities</h2><div id="opportunities">Loading records…</div></section><section class="panel"><h2>Shared Team Tasks</h2><div id="tasks">Loading tasks…</div><div class="toolbar"><input id="taskTitle" placeholder="New shared task" aria-label="New shared task"><button id="addTask">Add task</button></div><div id="taskMessage" class="muted"></div></section></div>
<div><section class="panel"><h2>Cloud Access and API Status</h2><div class="row"><span>Application service</span><span class="tag" id="health">Checking</span></div><p class="muted">The browser retrieves data from REST endpoints rather than embedding database records in the page.</p><div class="api">GET /api/health<br>GET /api/opportunities<br>GET /api/tasks<br>POST /api/tasks</div></section><section class="panel"><h2>Access Control</h2><p class="muted">Students can view opportunities and shared tasks. Only the Placement Officer role can create or update shared task records in this demonstration.</p><div class="api" id="accessInfo">Role: student_a<br>Permission: read</div><button class="secondary" id="checkAccess">Test restricted endpoint</button><div id="accessResult" class="muted" style="margin-top:8px"></div></section><section class="panel"><h2>Implementation Notes</h2><ul class="muted"><li>SQLite stores prototype records.</li><li>Cookie-backed demonstration sessions identify roles.</li><li>REST endpoints return JSON.</li><li>Responsive layout supports desktop and mobile browsers.</li></ul></section></div></div><div class="footer">CampusConnect · CO3 implementation prototype · Not a production placement service</div></main>
<script>
let currentRole='student_a';
async function api(path,opts={}){const r=await fetch(path,{...opts,headers:{'Content-Type':'application/json',...(opts.headers||{})}});let d={};try{d=await r.json()}catch(e){}return {ok:r.ok,status:r.status,data:d}}
async function load(){let h=await api('/api/health');document.getElementById('health').textContent=h.ok?'Available':'Unavailable';let o=await api('/api/opportunities');document.getElementById('opportunities').innerHTML=o.data.items.map(x=>`<div class="card"><strong>${x.title}</strong><span>${x.company} · ${x.location}</span><br><span class="tag">${x.status}</span></div>`).join('');let t=await api('/api/tasks');document.getElementById('tasks').innerHTML=t.data.items.map(x=>`<div class="task"><div class="row"><strong>${x.title}</strong><span class="status">${x.status}</span></div><small>Owner: ${x.owner} · Last updated by: ${x.updated_by}</small></div>`).join('');document.getElementById('accessInfo').innerHTML=`Role: ${currentRole}<br>Permission: ${currentRole==='faculty'?'read/write':'read only'}`}
document.getElementById('login').onclick=async()=>{currentRole=document.getElementById('role').value;let r=await api('/api/login',{method:'POST',body:JSON.stringify({role:currentRole})});document.getElementById('loginState').textContent='Current access: '+r.data.role;load()};
document.getElementById('addTask').onclick=async()=>{let title=document.getElementById('taskTitle').value.trim();if(!title)return;let r=await api('/api/tasks',{method:'POST',body:JSON.stringify({title,owner:currentRole==='faculty'?'Placement Officer':currentRole})});document.getElementById('taskMessage').textContent=r.ok?'Task saved to shared workspace.':(r.data.error||'Request failed') ;document.getElementById('taskTitle').value='';load()};
document.getElementById('checkAccess').onclick=async()=>{let r=await api('/api/admin');document.getElementById('accessResult').textContent=r.ok?'Authorized: '+r.data.message:`HTTP ${r.status}: ${r.data.error}`};load();
</script></body></html>'''

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_): pass
    def send_json(self, status, data, extra=None):
        body=json.dumps(data).encode(); self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(body))); self.send_header('Cache-Control','no-store')
        if extra:
            for k,v in extra.items(): self.send_header(k,v)
        self.end_headers(); self.wfile.write(body)
    def body(self):
        n=int(self.headers.get('Content-Length','0')); return json.loads(self.rfile.read(n) or b'{}')
    def role(self):
        raw=self.headers.get('Cookie','')
        c=cookies.SimpleCookie();
        try: c.load(raw); sid=c['cc_session'].value
        except Exception: return 'anonymous'
        return SESSIONS.get(sid,'anonymous')
    def do_GET(self):
        p=urlparse(self.path).path
        if p=='/':
            b=HTML.encode(); self.send_response(200); self.send_header('Content-Type','text/html; charset=utf-8'); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b); return
        if p=='/api/health': return self.send_json(200,{'status':'ok','service':'campusconnect-local-prototype'})
        if p=='/api/opportunities':
            with connect() as c: rows=[dict(x) for x in c.execute('SELECT * FROM opportunities ORDER BY id')]
            return self.send_json(200,{'count':len(rows),'items':rows})
        if p=='/api/tasks':
            with connect() as c: rows=[dict(x) for x in c.execute('SELECT * FROM tasks ORDER BY id DESC')]
            return self.send_json(200,{'count':len(rows),'items':rows})
        if p=='/api/admin':
            if self.role()!='faculty': return self.send_json(403,{'error':'Forbidden: Placement Officer role required'})
            return self.send_json(200,{'message':'Placement Officer access granted'})
        return self.send_json(404,{'error':'Not found'})
    def do_POST(self):
        p=urlparse(self.path).path
        try: data=self.body()
        except Exception: return self.send_json(400,{'error':'Invalid JSON body'})
        if p=='/api/login':
            role=data.get('role','')
            if role not in {'student_a','student_b','faculty','recruiter'}: return self.send_json(400,{'error':'Unknown role'})
            sid=secrets.token_urlsafe(18); SESSIONS[sid]=role
            return self.send_json(200,{'role':role},{'Set-Cookie':f'cc_session={sid}; HttpOnly; SameSite=Strict; Path=/'})
        if p=='/api/tasks':
            role=self.role()
            if role!='faculty': return self.send_json(403,{'error':'Forbidden: only Placement Officer can create shared tasks'})
            title=str(data.get('title','')).strip()
            if not title or len(title)>120: return self.send_json(400,{'error':'Task title must contain 1 to 120 characters'})
            with connect() as c:
                cur=c.execute('INSERT INTO tasks(title,owner,status,updated_by) VALUES(?,?,?,?)',(title,'Placement Officer','Pending','Placement Officer')); tid=cur.lastrowid
            return self.send_json(201,{'message':'Task created','id':tid,'title':title})
        return self.send_json(404,{'error':'Not found'})

if __name__=='__main__':
    init_db(); print(f'CampusConnect running at http://{HOST}:{PORT}'); ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()

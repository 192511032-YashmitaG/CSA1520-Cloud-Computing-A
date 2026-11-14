import json, unittest, urllib.request, urllib.error, subprocess, time, os, sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
class CampusConnectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proc=subprocess.Popen([sys.executable,os.path.join(ROOT,'app','server.py')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        for _ in range(40):
            try:
                urllib.request.urlopen('http://127.0.0.1:8000/api/health',timeout=.2); break
            except Exception: time.sleep(.15)
    @classmethod
    def tearDownClass(cls): cls.proc.terminate(); cls.proc.wait(timeout=5)
    def request(self,path,method='GET',data=None,cookie=None):
        headers={}
        if data is not None: headers['Content-Type']='application/json'
        if cookie: headers['Cookie']=cookie
        req=urllib.request.Request('http://127.0.0.1:8000'+path,data=json.dumps(data).encode() if data is not None else None,headers=headers,method=method)
        try:
            with urllib.request.urlopen(req) as r: return r.status,json.loads(r.read()),r.headers
        except urllib.error.HTTPError as e: return e.code,json.loads(e.read()),e.headers
    def test_01_health_endpoint(self):
        s,d,_=self.request('/api/health'); self.assertEqual(s,200); self.assertEqual(d['status'],'ok')
    def test_02_opportunities_request(self):
        s,d,_=self.request('/api/opportunities'); self.assertEqual(s,200); self.assertGreaterEqual(d['count'],2)
    def test_03_tasks_request(self):
        s,d,_=self.request('/api/tasks'); self.assertEqual(s,200); self.assertGreaterEqual(d['count'],1)
    def test_04_role_login(self):
        s,d,h=self.request('/api/login','POST',{'role':'faculty'}); self.assertEqual(s,200); self.assertEqual(d['role'],'faculty'); self.assertIn('cc_session',h['Set-Cookie'])
    def test_05_restricted_endpoint_denies_anonymous(self):
        s,d,_=self.request('/api/admin'); self.assertEqual(s,403); self.assertIn('Forbidden',d['error'])
    def test_06_restricted_endpoint_allows_faculty(self):
        _,_,h=self.request('/api/login','POST',{'role':'faculty'}); cookie=h['Set-Cookie'].split(';')[0]
        s,d,_=self.request('/api/admin',cookie=cookie); self.assertEqual(s,200); self.assertIn('granted',d['message'])
    def test_07_task_creation_denies_student(self):
        _,_,h=self.request('/api/login','POST',{'role':'student_a'}); cookie=h['Set-Cookie'].split(';')[0]
        s,d,_=self.request('/api/tasks','POST',{'title':'Test task'},cookie); self.assertEqual(s,403)
    def test_08_task_creation_allows_faculty(self):
        _,_,h=self.request('/api/login','POST',{'role':'faculty'}); cookie=h['Set-Cookie'].split(';')[0]
        s,d,_=self.request('/api/tasks','POST',{'title':'Verify CO3 prototype'},cookie); self.assertEqual(s,201); self.assertEqual(d['title'],'Verify CO3 prototype')
if __name__=='__main__': unittest.main(verbosity=2)

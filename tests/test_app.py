import os
os.environ["DATABASE_URL"] = "sqlite:///./data/test_tickets.db"
from fastapi.testclient import TestClient
from app.main import app
from app.db import init_db, get_conn

init_db()
with get_conn() as conn:
    conn.execute("DELETE FROM flow_runs")
    conn.execute("DELETE FROM email_logs")
    conn.execute("DELETE FROM tickets")

client = TestClient(app)

def test_health():
    r=client.get('/health'); assert r.status_code==200; assert r.json()['status']=='ok'

def test_metadata_dependency():
    r=client.get('/api/dependencies/Network'); assert r.status_code==200; assert r.json()['subcategories']==['Wi-Fi']

def test_wifi_ticket_classification():
    r=client.post('/api/tickets',json={"caller_name":"Anu","caller_email":"anu@example.edu","short_description":"WiFi not working in library","description":"Cannot connect"})
    assert r.status_code==201
    data=r.json(); assert data['ticket']['category']=='Network'; assert data['ticket']['subcategory']=='Wi-Fi'; assert data['email_status']=='queued'

def test_projector_ticket_classification():
    r=client.post('/api/tickets',json={"caller_name":"Meena","caller_email":"meena@example.edu","short_description":"Projector not turning on","description":"No display"})
    assert r.status_code==201
    assert r.json()['ticket']['category']=='Hardware'
    assert r.json()['ticket']['subcategory']=='Projector'

def test_password_ticket_classification():
    r=client.post('/api/tickets',json={"caller_name":"Rani","caller_email":"rani@example.edu","short_description":"Forgot password for portal","description":"Cannot login"})
    assert r.status_code==201
    assert r.json()['classification']['category']=='Access'

def test_slow_ticket_classification_and_history():
    r=client.post('/api/tickets',json={"caller_name":"Sara","caller_email":"sara@example.edu","short_description":"Computer is slow and hanging","description":"Applications freeze"})
    assert r.status_code==201
    tid=r.json()['ticket']['id']
    h=client.get(f'/api/tickets/{tid}/history'); assert h.status_code==200; assert len(h.json())>=3

def test_unmatched_ticket():
    r=client.post('/api/tickets',json={"caller_name":"Dev","caller_email":"dev@example.edu","short_description":"Library printer jam","description":"Paper is stuck"})
    assert r.status_code==201; assert r.json()['ticket']['category'] is None

def test_dashboard():
    r=client.get('/api/dashboard'); assert r.status_code==200; assert r.json()['total']>=5

def test_update_ticket():
    tid=client.get('/api/tickets').json()[0]['id']
    r=client.patch(f'/api/tickets/{tid}',json={'state':'In progress'}); assert r.status_code==200; assert r.json()['state']=='In progress'

def test_ai_fallback():
    r=client.post('/api/ai/classify',json={'short_description':'WiFi issue','description':''}); assert r.status_code==200; assert r.json()['provider'] in ('local-fallback','gemini')

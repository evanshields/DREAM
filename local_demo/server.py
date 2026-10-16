"""Loopback-only synthetic acceptance app. Never imports production main.py."""
from pathlib import Path
import os
import re
import socket
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'frontend' / 'local-demo-dist'
for name in list(os.environ):
    if name.startswith('DREAM_') or any(s in name.upper() for s in ('API_KEY', 'AUTH_TOKEN', 'OAUTH', 'JWT_SECRET')):
        os.environ.pop(name, None)
os.environ.update(DREAM_ALLOW_STUBS='1', DREAM_USE_KIMI='0', DREAM_JOBS_SYNC='0')
_connect = socket.socket.connect
def loopback_connect(self, address):
    if self.family in (socket.AF_INET, socket.AF_INET6) and address[0] not in ('127.0.0.1', '::1', 'localhost'):
        raise RuntimeError('Local demo blocks outbound connections')
    return _connect(self, address)
socket.socket.connect = loopback_connect
sys.path.insert(0, str(ROOT / 'backend'))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from auth_dep import require_auth
from store import SQLiteDealStore
from jobs.job_store import SQLiteJobStore
from jobs.analysts import StubAnalysts, StubEFBAnalysts
from jobs import queue
import routers.jobs as jobs_router
import routers.deals as deals_router
import routers.recalc as recalc_router

ds, js = SQLiteDealStore(':memory:'), SQLiteJobStore(':memory:')
class DemoAnalysts:
    def run_all(self, deal_docs=None, intake_summary=None, critical_inputs=None):
        # A visible cancellation window, followed by the existing real worker logic.
        time.sleep(2)
        factory = StubEFBAnalysts if (intake_summary or {}).get('routing') == 'EFB' else StubAnalysts
        return factory().run_all(deal_docs, intake_summary, critical_inputs)
for module in (jobs_router, deals_router):
    module.get_deal_store = lambda: ds
    module.get_job_store = lambda: js
jobs_router.get_analysts = DemoAnalysts
app = FastAPI(title='DREAM local synthetic fixture', docs_url=None, redoc_url=None, openapi_url=None)
app.dependency_overrides[require_auth] = lambda: {'email': 'analyst@example.invalid', 'name': 'Local fixture'}
app.include_router(jobs_router.router)
app.include_router(deals_router.router)
app.include_router(recalc_router.router)

@app.middleware('http')
async def fixture_boundary(request: Request, call_next):
    if (not request.client or request.client.host not in ('127.0.0.1', '::1', 'testclient') or
        request.headers.get('host') not in ('127.0.0.1:8769', 'testserver') or
        request.headers.get('origin') not in (None, 'http://127.0.0.1:8769', 'http://testserver')):
        return JSONResponse({'detail': 'Local fixture origin required'}, status_code=403)
    path, method = request.url.path, request.method
    if path.startswith('/api'):
        allowed = ((method == 'GET' and (path == '/api/me' or path == '/api/deals' or
                    re.fullmatch(r'/api/(jobs|deals)/[^/]+(/audit)?', path))) or
                   (method == 'POST' and (path in ('/api/jobs', '/api/recalc') or
                    re.fullmatch(r'/api/jobs/[^/]+/(answer|cancel)', path))))
        if not allowed:
            return JSONResponse({'detail': 'Unavailable in local fixture: no providers, CRM, uploads, exports or approval mutations'}, status_code=403)
    response = await call_next(request)
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; font-src 'self'; frame-src 'none'; object-src 'none'"
    response.headers['Cache-Control'] = 'no-store'
    return response

@app.get('/api/me')
def fixture_user():
    return {'email': 'analyst@example.invalid', 'name': 'Local fixture', 'picture': None}

BANNER = '<aside style="background:#fff3cd;color:#332600;padding:12px;position:sticky;top:0;z-index:9999">LOCAL SYNTHETIC FIXTURE — fixed analyst data; financial oracle unverified. No real CRM, providers, uploads, exports or CP-1 approval. Data disappears when stopped. <a href="/__demo__/">Sample instructions</a></aside>'
LANDING = '''<!doctype html><html><head><title>DREAM local sample</title></head><body style="font:18px system-ui;max-width:850px;margin:40px auto">''' + BANNER + '''<h1>DREAM local sample</h1><p>This uses the actual isolated app job runner, engine adapter and UI with fixed synthetic analyst slices. It does not prove live extraction or the complete Mono/MCP/CRM workflow.</p><ol><li>Open the app. Choose ACQ; enter purchase price 55000000, hold 7 years and exit cap 6%. Leave documents empty. Submit and observe the human review stop.</li><li>Submit with missing inputs to see questions; supply the requested answers to resume. While the fixed in-process sample is running, cancel it and observe its actual cancelled status. This tests a cooperative phase flag only: it does not interrupt arbitrary blocking work or prove descendant cleanup. A separate Windows MCP Dispatcher test left an owned grandchild alive after cancellation; Our two full Linux Dispatcher descendant cases remain unrun; the current MCP owner has separate passing Linux process-group helper coverage. Cancellation while paused remains a known backend gap; the UI disables that action.</li><li>Choose EFB with stabilized NOI 4448271.31 for the fixed EFB sample. All analyst values are predetermined, regardless of uploaded text or assumptions.</li><li>Inspect the separate bridge fixture to see read-only status and denied, expired, cross-workspace and Hermes-unavailable cases. It uses invented fixture identities, never real CRM credentials.</li></ol><button id="enter">Open isolated app</button> <a href="/samples/bridge.html">Open bridge fixture</a><p>Stop with Ctrl+C. Refresh retains data only until this process stops. The public fixture marker below is not a JWT or OAuth credential.</p><script>document.getElementById('enter').onclick=()=>{localStorage.setItem('dream_token','LOCAL_FIXTURE_ONLY');location.assign('/underwrite')}</script></body></html>'''

@app.get('/__demo__/')
def landing():
    return HTMLResponse(LANDING)

@app.get('/{path:path}')
def frontend(path: str):
    if path.startswith('api/'):
        return JSONResponse({'detail': 'Unknown local fixture endpoint'}, status_code=404)
    target = (DIST / path).resolve()
    if not target.is_relative_to(DIST.resolve()):
        return JSONResponse({'detail': 'Invalid static path'}, status_code=404)
    if target.is_file() and target.suffix != '.html':
        return FileResponse(target)
    html = target if target.is_file() else DIST / 'index.html'
    if not html.is_file():
        return JSONResponse({'detail': 'Build local-demo-dist first'}, status_code=503)
    content = html.read_text(encoding='utf-8')
    content = re.sub(r'<script\b[^>]*src="https?://[^>]+>.*?</script>', '', content, flags=re.S)
    content = re.sub(r'<link\b[^>]*href="https?://[^>]+>', '', content, flags=re.S)
    return HTMLResponse(content.replace('<body>', '<body>' + BANNER))

if __name__ == '__main__':
    import uvicorn
    try:
        uvicorn.run(app, host='127.0.0.1', port=8769, log_level='warning')
    finally:
        queue.shutdown(wait=True)

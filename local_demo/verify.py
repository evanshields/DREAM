"""Repeatable local partial-beta acceptance. Existing dependencies only."""
import json
from pathlib import Path
import time
from fastapi.testclient import TestClient
import server

checks = []
def check(name, condition):
    assert condition, name
    checks.append({'name': name, 'result': 'passed'})

def wait(client, job_id, target):
    deadline = time.monotonic() + 12
    while time.monotonic() < deadline:
        view = client.get('/api/jobs/' + job_id).json()
        if view['status'] == target:
            return view
        if view['status'] == 'failed':
            raise AssertionError(view)
        time.sleep(.03)
    raise AssertionError(view)

with TestClient(server.app) as client:
    check('Foreign Host and Origin rejected', client.get('/api/me',headers={'Host':'foreign.invalid'}).status_code == 403 and client.get('/api/me',headers={'Origin':'https://foreign.invalid'}).status_code == 403)
    home = client.get('/__demo__/')
    check('Clear fixture instructions and fixture-only identity', 'financial oracle unverified' in home.text and client.get('/api/me').json()['email'].endswith('@example.invalid'))
    page = client.get('/underwrite')
    check('Static app, local banner, remote scripts removed and CSP blocks external transport', page.status_code == 200 and 'LOCAL SYNTHETIC FIXTURE' in page.text and 'https://accounts.google.com' not in page.text and "connect-src 'self'" in page.headers['content-security-policy'])
    bridge = client.get('/samples/bridge.html')
    check('Separate compiled bridge fixture available', bridge.status_code == 200 and 'DREAM bridge fixture' in bridge.text)
    check('Inherited remote VITE_API_BASE absent from static bundle', not any('invalid.example.invalid' in p.read_text(encoding='utf-8') for p in server.DIST.rglob('*.js')))
    check('Providers/CRM/uploads/export/CP1 writes blocked', all(client.post(path,json={}).status_code == 403 for path in ['/api/underwrite/v2','/api/extract','/api/chat','/api/deals/fake/archive','/api/deals/fake/approve','/api/export']))
    ready = {'routing':'ACQ','deal_name':'Synthetic ACQ','critical_inputs':{'purchase_price':55000000,'hold_years':7,'exit_cap':.06}}
    body = {'intake_summary':ready,'idempotency_key':'repeatable-local-acq'}
    first = client.post('/api/jobs',json=body).json()
    replay = client.post('/api/jobs',json=body).json()
    final = wait(client,first['job_id'],'awaiting_cp1')
    check('Actual async ACQ runner, idempotent replay and CP1 stop', first['job_id'] == replay['job_id'] and first['deal_id'] == replay['deal_id'] and final['status'] == 'awaiting_cp1')
    check('Deal cold reload and audit retained in fixture process', client.get('/api/deals/'+first['deal_id']).status_code == 200 and client.get('/api/deals/'+first['deal_id']+'/audit').status_code == 200)
    efb = client.post('/api/jobs',json={'intake_summary':{'routing':'EFB','deal_name':'Synthetic EFB','critical_inputs':{'stabilized_noi':4448271.31}},'idempotency_key':'repeatable-local-efb'}).json()
    efb_final = wait(client,efb['job_id'],'awaiting_cp1')
    check('Fixed EFB runner reaches CP1 without ACQ metrics', 'bond_amount' in efb_final['headline_metrics'] and 'irr' not in efb_final['headline_metrics'])
    paused = client.post('/api/jobs',json={'intake_summary':{'routing':'ACQ'},'idempotency_key':'repeatable-local-questions'}).json()
    paused = wait(client,paused['job_id'],'awaiting_input')
    check('Missing input pauses before analysis', paused['status'] == 'awaiting_input')
    values = {'purchase_price':55000000,'hold_years':7,'exit_cap':.06}
    for question in paused['open_questions']:
        if question.get('blocking'):
            answer = values[question['field'].split('.')[-1]]
            response = client.post('/api/jobs/'+paused['job_id']+'/answer',json={'question_id':question['id'],'answer':answer})
            assert response.status_code == 200,response.text
    check('Human answers resume to CP1', wait(client,paused['job_id'],'awaiting_cp1')['status'] == 'awaiting_cp1')
    cancelled = client.post('/api/jobs',json={'intake_summary':ready,'idempotency_key':'repeatable-local-cancel'}).json()
    ack = client.post('/api/jobs/'+cancelled['job_id']+'/cancel').json()
    check('Cancellation acknowledgement followed by actual worker cancellation', ack['cancel_requested'] and wait(client,cancelled['job_id'],'cancelled')['status'] == 'cancelled')
    inputs = dict(bridge_loan=1000000,bridge_rate=.08,bridge_io_years=2,refi_loan=1200000,refi_rate=.06,refi_io_years=3,refi_amort_years=30,refi_year=2,total_equity=600000,noi_series=[150000,160000,170000,180000,190000],exit_cap=.06,sale_year=4,years=5,servicing_spread=0,debt_service=[100000]*5)
    result = client.post('/api/recalc',json=inputs)
    check('Explicit annual debt service reaches real deterministic recalc', result.status_code == 200 and result.json()['headline_metrics']['cash_flows'][1] == 50000)
    inputs['debt_service'] = [100000]*4
    check('Partial annual payment schedule fails closed', client.post('/api/recalc',json=inputs).status_code == 422)
server.queue.shutdown(wait=True)
receipt = {'scope':'Composed de824ba + corrected cancellationv2 + corrected bridgev2 + explicit debt adapter; actual async runner with in-memory stores and fixed analyst fixtures', 'checks':checks,
 'not_run':['Browser interaction/races','Live identity/link/Hermes','Real extraction/providers','Mono/C2 integrated workbook/document','Native Linux dispatcher lifecycle','Financial exact oracle','Production deployment'],
 'known_failures':['Paused cancellation acknowledged but backend never transitions until worker exists; UI disables paused cancellation','Historical Esplanade 0.2251 exact target differs from unchanged engine 0.22212539391032182']}
(Path(__file__).parent/'verification.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps(receipt,indent=2))

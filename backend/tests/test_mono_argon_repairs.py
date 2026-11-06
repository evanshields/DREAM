"""Argon hold repairs (Nov 4): typed numbers, quarantine latch, staged revision cleanup, ledger history.

The pinned calculator package (`tools.*`) is not part of this repo, so these tests install tiny
stand-ins for the few calculator helpers the revision code imports. They carry no financial math.
"""
import hashlib
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
from fastapi import HTTPException

import engine_boundary
from mono import provider as provider_module
from mono.config import canonical_hash, digest
from mono.provider import wait_for_bridge
from mono.revisions import RevisionBuilder, normalize, write_new
from mono.service import MonoService
from store.mono_deal_store import MonoDealStore


# ---------------------------------------------------------------- calculator stand-ins

@pytest.fixture
def calculator(monkeypatch):
    """Install minimal `tools.*` modules the revision code imports, then remove them."""
    def module(name, **attrs):
        mod = ModuleType(name)
        mod.__dict__.update(attrs)
        monkeypatch.setitem(sys.modules, name, mod)
        return mod

    def safe_file(root, relative, must_exist=True):
        path = Path(root) / relative
        if must_exist and not path.is_file():
            raise ValueError('Missing registered file')
        return path

    state = SimpleNamespace(mapping=[], code='code-sha')
    module('tools')
    module('tools.deal_file')
    module('tools.deal_file.readiness', _text_id=lambda field_id: False)
    module('tools.deal_file.core', load_map=lambda path: state.mapping, validate=lambda doc: [])
    module('tools.mono_calc')
    module('tools.mono_calc.adapters', safe_scalar=lambda value: True)
    module('tools.mono_calc.contracts', safe_file=safe_file,
           read_json=lambda path: json.loads(Path(path).read_text(encoding='utf-8')),
           identifier=lambda value: value)
    module('tools.mono_calc.executor', code_identity=lambda: state.code)
    return state


# ---------------------------------------------------------------- finding 1: typed numbers

NUMBER_ENTRY = {'id': 'purchase_price', 'unit': '$'}
COUNT_ENTRY = {'id': 'unit_count', 'unit': 'count'}


@pytest.mark.parametrize('typed,expected', [
    ('$1,250,000', 1250000.0), ('-$1,250,000', -1250000.0), ('$-1,250,000', -1250000.0),
    ('$ 1,250,000', 1250000.0), ('+$5', 5.0), ('1250000.25', 1250000.25),
])
def test_currency_text_accepts_a_sign_before_or_after_the_dollar_sign(calculator, typed, expected):
    assert normalize(NUMBER_ENTRY, typed, '$') == expected


@pytest.mark.parametrize('typed', ['-$-5', '$$5', '--5', '$', '-$', 'NaN', 'inf', '-Infinity', '1e999999999', '5%', 'abc', '1,2,x'])
def test_malformed_or_non_finite_number_text_is_rejected(calculator, typed):
    with pytest.raises(ValueError):
        normalize(NUMBER_ENTRY, typed, '$')


def test_whole_number_units_keep_exact_integers_beyond_binary_float_precision(calculator):
    typed = '9007199254740993'  # 2**53 + 1: a binary float would silently store ...992
    result = normalize(COUNT_ENTRY, typed, 'count')
    assert result == 9007199254740993
    assert isinstance(result, int)
    assert normalize(COUNT_ENTRY, '12.0', 'count') == 12
    assert normalize(COUNT_ENTRY, '1,200', 'count') == 1200


def test_whole_number_units_still_reject_fractions(calculator):
    with pytest.raises(ValueError):
        normalize(COUNT_ENTRY, '2.5', 'count')


def test_number_parsing_runs_through_the_engine_boundary(calculator, monkeypatch):
    seen = []
    real = engine_boundary.parse_mono_number
    monkeypatch.setattr(engine_boundary, 'parse_mono_number', lambda *a, **k: seen.append(a) or real(*a, **k))
    assert normalize(NUMBER_ENTRY, '$10', '$') == 10.0
    assert seen and seen[0][0] == '$10'


def test_currency_text_is_rejected_for_a_non_currency_unit(calculator):
    with pytest.raises(ValueError):
        normalize({'id': 'x', 'unit': 'months'}, '$12', 'months')


# ---------------------------------------------------------------- finding 2: quarantine latch

class SlowProcess:
    pid = 4242

    def __init__(self, exits_after_polls):
        self.polls_left = exits_after_polls
        self.exited = False

    def poll(self):
        if self.polls_left <= 0:
            self.exited = True
            return 0
        self.polls_left -= 1
        return None


def test_latch_quarantine_treats_an_existing_latch_as_already_latched(tmp_path):
    path = tmp_path / 'dispatcher-quarantine.json'
    provider_module.latch_quarantine(path, {'job_id': 'first'})
    provider_module.latch_quarantine(path, {'job_id': 'second'})  # must not raise FileExistsError
    assert json.loads(path.read_text(encoding='utf-8'))['job_id'] == 'first'


def test_a_failing_quarantine_callback_never_ends_the_wait_while_the_bridge_is_alive(tmp_path):
    clock = [0]
    process = SlowProcess(exits_after_polls=40)

    def boom(reason):
        raise FileExistsError('latch already present')

    def advance(_):
        clock[0] += 1

    with pytest.raises(FileExistsError):
        wait_for_bridge(process, tmp_path, lambda: False, boom, timeout=2, cancel_grace=1,
                        clock=lambda: clock[0], sleep=advance)
    # The error is reported only after the owned child process has really exited.
    assert process.exited is True


# ---------------------------------------------------------------- staged revision fixtures

DEAL = 'fixture-deal'
EVAN = {'issuer': 'dream-app', 'subject': 'evan-subject'}


def make_world(tmp_path, calculator, prior_records=()):
    data_root = tmp_path / 'data'
    config = SimpleNamespace(
        data_root=data_root, evan_principals=(EVAN['issuer'] + '|' + EVAN['subject'],),
        map_sha256='map', template_sha256='tpl', expected_code_sha256='code-sha',
        map_path=tmp_path / 'map.json', verify_pins=lambda code_hash=None: None,
        permits=lambda deal_id, actor: True)
    calculator.mapping = [{'id': 'purchase_price', 'unit': '$', 'label': 'Purchase price'}]
    builder = RevisionBuilder(config)
    source = tmp_path / 'registered'
    (source / 'model-inputs').mkdir(parents=True)
    (source / 'evidence.txt').write_text('evidence', encoding='utf-8')
    doc = {'slug': DEAL, 'name': 'Fixture', 'history': [], 'updated': 'x',
           'assumptions': [{'id': 'purchase_price', 'label': 'Purchase price', 'value': 100.0, 'unit': '$',
                            'source': {'type': 'default', 'detail': 'seed'}}]}
    bundle = {'deal_id': DEAL, 'claims': {}, 'groups': {},
              'sources': [{'id': 'evidence', 'path': 'evidence.txt', 'format': 'text',
                           'sha256': hashlib.sha256(b'evidence').hexdigest()}]}
    (source / 'model-inputs/deal-file.json').write_text(json.dumps(doc), encoding='utf-8')
    (source / 'model-inputs/source-bundle.json').write_text(json.dumps(bundle), encoding='utf-8')
    registration = {'root': str(source)}
    if prior_records:
        ledger_path = tmp_path / 'registered-ledger.json'
        ledger_path.write_text(json.dumps({'format': 'dream-trusted-rulings-v2', 'records': list(prior_records)}), encoding='utf-8')
        registration['trusted_rulings'] = {'path': str(ledger_path), 'sha256': digest(ledger_path)}
    record = builder.initial(DEAL, registration)
    return config, builder, record


def prior(decision_id, assumption='purchase_price'):
    return {'decision_id': decision_id, 'deal_id': DEAL, 'assumption_id': assumption, 'value': 1.0, 'reason': 'seed',
            'provenance': {'type': 'authenticated_decision'}}


def edit(builder, record, request_id='req-1', entered='$250'):
    return builder.edit(record, 'purchase_price', entered, '$', 'Because', EVAN, request_id)


# ---------------------------------------------------------------- finding 4: ledger history

def test_a_new_decision_supersedes_the_latest_prior_record_not_the_oldest(tmp_path, calculator):
    config, builder, record = make_world(tmp_path, calculator,
        prior_records=[prior('decision-old'), prior('decision-new'), prior('decision-other', 'other_field')])
    revised, event = edit(builder, record)
    assert event['supersedes'] == 'decision-new'
    ledger = json.loads(Path(revised['trusted_rulings']['path']).read_text(encoding='utf-8'))
    ids = [r['decision_id'] for r in ledger['records']]
    # Existing behavior stays: one active record per assumption, other fields untouched.
    assert ids == ['decision-other', event['decision_id']]


def test_first_decision_for_an_assumption_supersedes_nothing(tmp_path, calculator):
    config, builder, record = make_world(tmp_path, calculator)
    revised, event = edit(builder, record)
    assert event['supersedes'] is None


# ---------------------------------------------------------------- finding 3: orphan staging

def tree(root):
    return sorted(p.name for p in Path(root).iterdir()) if Path(root).exists() else []


def service_for(config, builder, record, tmp_path):
    store = MonoDealStore(tmp_path / 'mono.sqlite')
    store.register(DEAL, record)
    service = object.__new__(MonoService)
    service.config, service.builder, service.store, service.provider = config, builder, store, None
    return service, store


def body(key='key-1'):
    return {'field_id': 'purchase_price', 'entered_value': '$250', 'unit': '$', 'reason': 'Because',
            'idempotency_key': key, 'expected_revision': 1, 'expected_deal_sha256': None}


def test_losing_a_concurrent_edit_race_removes_the_staged_revision_and_ledger(tmp_path, calculator, monkeypatch):
    config, builder, record = make_world(tmp_path, calculator, prior_records=[prior('decision-old')])
    service, store = service_for(config, builder, record, tmp_path)
    request = dict(body(), expected_deal_sha256=record['identity']['deal_sha256'])
    before_revisions, before_trusted = tree(config.data_root / 'revisions'), tree(config.data_root / 'trusted')
    staged = []
    real_edit = builder.edit

    def racing_edit(*args):
        ours = real_edit(*args)
        staged.append(ours[0])
        rival, rival_event = real_edit(*args)
        store.commit_revision(DEAL, 1, rival, rival_event, 'rival-key', 'rival-digest')
        return ours

    monkeypatch.setattr(builder, 'edit', racing_edit)
    with pytest.raises(HTTPException) as caught:
        service.edit(DEAL, request, EVAN)
    assert caught.value.status_code == 409
    ours = staged[0]
    assert not Path(ours['root']).exists()
    assert not Path(ours['trusted_rulings']['path']).exists()
    # The rival's published revision and ledger are untouched.
    published = store.current(DEAL)
    assert Path(published['root']).is_dir()
    assert Path(published['trusted_rulings']['path']).is_file()
    assert len(tree(config.data_root / 'revisions')) == len(before_revisions) + 1
    assert len(tree(config.data_root / 'trusted')) == len(before_trusted) + 1


def test_an_idempotent_replay_race_discards_the_duplicate_staging(tmp_path, calculator, monkeypatch):
    config, builder, record = make_world(tmp_path, calculator)
    service, store = service_for(config, builder, record, tmp_path)
    request = dict(body('same-key'), expected_deal_sha256=record['identity']['deal_sha256'])
    digest_value = canonical_hash({'request': request, 'actor': EVAN})
    staged, winners = [], []
    real_edit = builder.edit

    def racing_edit(*args):
        ours = real_edit(*args)
        staged.append(ours[0])
        theirs = real_edit(*args)
        winners.append(store.commit_revision(DEAL, 1, theirs[0], theirs[1], 'same-key', digest_value))
        return ours

    monkeypatch.setattr(builder, 'edit', racing_edit)
    monkeypatch.setattr(service, '_operation_view', lambda deal_id, actor, kind, event, replayed: {'replayed': replayed, 'event': event})
    result = service.edit(DEAL, request, EVAN)
    assert not Path(staged[0]['root']).exists()
    assert Path(winners[0]['root']).is_dir()
    assert result['replayed'] is True


def test_a_successful_edit_keeps_its_staged_files(tmp_path, calculator, monkeypatch):
    config, builder, record = make_world(tmp_path, calculator)
    service, store = service_for(config, builder, record, tmp_path)
    request = dict(body('ok-key'), expected_deal_sha256=record['identity']['deal_sha256'])
    monkeypatch.setattr(service, '_operation_view', lambda deal_id, actor, kind, event, replayed: {'replayed': replayed})
    assert service.edit(DEAL, request, EVAN) == {'replayed': False}
    published = store.current(DEAL)
    assert published['revision'] == 2
    assert Path(published['root']).is_dir()
    assert Path(published['trusted_rulings']['path']).is_file()


def test_discard_refuses_paths_outside_the_server_owned_folders(tmp_path, calculator):
    config, builder, record = make_world(tmp_path, calculator)
    victim = tmp_path / 'victim'
    victim.mkdir()
    (victim / 'keep.txt').write_text('keep', encoding='utf-8')
    builder.discard({'root': str(victim), 'trusted_rulings': {'path': str(victim / 'keep.txt')}})
    assert (victim / 'keep.txt').exists()

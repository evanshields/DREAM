"""Mono requires verified identity and an explicit existing deal association."""
from pathlib import Path
import secrets

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
import pytest

from app_jwt import mint_token
from mono.config import MonoConfig, actor_dependency


@pytest.fixture
def configured(monkeypatch, tmp_path):
    monkeypatch.delenv('GOOGLE_CLIENT_ID', raising=False)
    monkeypatch.setenv('AUTH_JWT_SECRET', secrets.token_urlsafe(48))
    import auth_dep
    monkeypatch.setattr(auth_dep, 'ALLOWED_EMAILS', set())
    config = MonoConfig(tmp_path, Path('unused-runtime'), 'a'*64, tmp_path/'template', 'b'*64,
                        tmp_path/'map', 'c'*64, tmp_path/'data',
                        {'fixture': {'principals': ['dream-app|engineering-test']}})
    app = FastAPI()
    dep = actor_dependency(config)

    @app.get('/{deal_id}')
    def who(deal_id: str, actor=Depends(dep)):
        return actor

    return TestClient(app)


def test_mono_identity_comes_from_verified_token(configured):
    token = mint_token('engineering-test', 'fixture@example.test')
    response = configured.get('/fixture', headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 200
    assert response.json() == {'issuer': 'dream-app', 'subject': 'engineering-test',
                               'auth_method': 'app_jwt', 'email': 'fixture@example.test'}


def test_signed_in_user_without_deal_association_is_rejected(configured):
    token = mint_token('unassociated-test', 'fixture@example.test')
    assert configured.get('/fixture', headers={'Authorization': 'Bearer ' + token}).status_code == 403


def test_local_development_evan_stub_cannot_attest_a_human(configured, monkeypatch):
    monkeypatch.delenv('AUTH_JWT_SECRET')
    assert configured.get('/fixture').status_code == 403


def test_missing_or_altered_credentials_fail(configured):
    assert configured.get('/fixture').status_code == 401
    token = mint_token('engineering-test', 'fixture@example.test')
    head, payload, signature = token.split('.')
    altered = head + '.' + payload + '.' + ('A' if signature[0] != 'A' else 'B') + signature[1:]
    assert configured.get('/fixture', headers={'Authorization': 'Bearer ' + altered}).status_code == 401


def test_unregistered_deal_has_no_mono_access(configured):
    token = mint_token('engineering-test', 'fixture@example.test')
    assert configured.get('/not-registered', headers={'Authorization': 'Bearer ' + token}).status_code == 404

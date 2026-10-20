"""Server-owned registration, package pins and authenticated deal associations."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys

from fastapi import Depends, HTTPException
from auth_dep import require_auth, auth_enabled


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class MonoConfig:
    calculator_root: Path
    calculator_python: Path
    expected_code_sha256: str
    template: Path
    template_sha256: str
    map_path: Path
    map_sha256: str
    data_root: Path
    registrations: dict
    capabilities: dict | None = None
    evan_principals: tuple = ()

    def load_calculator(self):
        root = self.calculator_root.resolve(strict=True)
        if root.is_symlink() or root.is_junction() or not (root / 'tools/mono_calc/executor.py').is_file():
            raise ValueError('Invalid pinned calculator package')
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        import tools.mono_calc.executor as executor
        if Path(executor.REPO).resolve() != root:
            raise ValueError('A different calculator package is already loaded')
        self.verify_pins(executor.code_identity())
        return executor

    def verify_pins(self, code_hash=None):
        if digest(self.template) != self.template_sha256 or digest(self.map_path) != self.map_sha256:
            raise ValueError('Configured Mono template or map identity changed')
        if code_hash is not None and code_hash != self.expected_code_sha256:
            raise ValueError('Configured calculator code identity changed')
        if not self.calculator_python.is_file():
            raise ValueError('Configured calculator runtime is unavailable')

    def permits(self, deal_id, actor):
        principal = actor['issuer'] + '|' + actor['subject']
        return principal in self.registrations.get(deal_id, {}).get('principals', [])


def actor_dependency(config):
    def actor(deal_id: str, user=Depends(require_auth)):
        if config is None or deal_id not in config.registrations:
            raise HTTPException(404, 'Mono is not registered for this deal')
        if not auth_enabled() or not user or user.get('local_dev'):
            raise HTTPException(403, 'Mono requires a verified signed-in identity')
        if user.get('auth') == 'app':
            identity = {'issuer': 'dream-app', 'subject': user.get('sub'), 'auth_method': 'app_jwt', 'email': user.get('email')}
        elif user.get('iss') in ('accounts.google.com', 'https://accounts.google.com'):
            identity = {'issuer': user['iss'], 'subject': user.get('sub'), 'auth_method': 'google_oidc',
                        'email': user.get('email') if user.get('email_verified') is True else None}
        else:
            raise HTTPException(403, 'Verified identity method is unavailable')
        if not isinstance(identity['subject'], str) or not identity['subject'] or not config.permits(deal_id, identity):
            raise HTTPException(403, 'This identity is not associated with this Mono deal')
        return identity
    return actor


def load_config(path):
    raw = json.loads(Path(path).read_text(encoding='utf-8'))
    required = {'calculator_root', 'calculator_python', 'expected_code_sha256', 'template', 'template_sha256',
                'map_path', 'map_sha256', 'data_root', 'registrations'}
    if set(raw) - required - {'capabilities', 'evan_principals'} or not required <= set(raw):
        raise ValueError('Invalid server-owned Mono configuration')
    for key in ('calculator_root', 'calculator_python', 'template', 'map_path', 'data_root'):
        raw[key] = Path(raw[key]).absolute()
    config = MonoConfig(**raw)
    config.load_calculator()
    return config

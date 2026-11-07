"""Opt-in private Mono registration. Existing deployments stay unconfigured."""
import os

from .config import load_config
from .service import MonoService


def configured_service():
    path = os.environ.get('DREAM_MONO_CONFIG', '').strip()
    return MonoService(load_config(path)) if path else None

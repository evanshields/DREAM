"""One owned native job in the configured COM-capable Python runtime."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import time


def main():
    directory = Path(sys.argv[1]).resolve(strict=True)
    envelope = json.loads((directory / 'envelope.json').read_text(encoding='utf-8'))
    sys.path.insert(0, envelope['calculator_root'])
    from tools.mono_calc.__main__ import registry_from_file
    from tools.mono_calc.executor import calculate, code_identity
    from tools.mono_calc.jobs import JobStore
    from tools.mono_calc.native import write_json_new
    if code_identity() != envelope['expected_code_sha256']:
        raise ValueError('Pinned calculator package changed before dispatch')
    registry = registry_from_file(directory / 'registry.json')
    context = None
    if envelope.get('trusted_comps_context') is not None:
        from tools.mono_calc.comps_admission import TrustedCompsContext
        context = TrustedCompsContext(**envelope['trusted_comps_context'])
    store = JobStore(registry, lambda req, cancellation: calculate(req, registry, cancellation=cancellation, trusted_context=context))
    try:
        job = store.submit(envelope['request'])
        write_json_new(directory / 'submitted.json', job)
        cancelled = False
        while True:
            if (directory / 'cancel-requested').exists() and not cancelled:
                store.cancel(job['job_id'])
                cancelled = True
            result = store.result(job['job_id'])
            if result['state'] not in ('queued', 'running'):
                write_json_new(directory / 'terminal.json', result)
                break
            time.sleep(0.2)
    finally:
        store.close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

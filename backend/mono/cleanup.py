"""Validate positive cleanup independently of a native job's terminal state."""
from pathlib import PureWindowsPath

POLICY = 'mono-calculator-cleanup-v1'


def verified_cleanup(native):
    if not isinstance(native, dict) or native.get('cleanup_verified') is not True:
        return False
    record = native.get('cleanup')
    if not isinstance(record, dict) or record.get('policy') != POLICY or record.get('verified') is not True:
        return False
    observation = record.get('observation')
    if not isinstance(observation, dict):
        return False
    if record.get('native_launched') is False:
        return (native.get('state') in ('cancelled', 'failed', 'blocked', 'stale')
                and record.get('state') == 'not_launched'
                and record.get('native_worker') is None and record.get('excel_owner') is None
                and observation.get('method') == 'executor_control_flow'
                and observation.get('native_worker_exited') is None
                and observation.get('owned_excel_present') is None)
    owner, worker = record.get('excel_owner'), record.get('native_worker')
    return (record.get('native_launched') is True and record.get('state') == 'verified_exit'
            and isinstance(owner, dict) and owner.get('new_process') is True
            and type(owner.get('pid')) is int and owner['pid'] > 0
            and isinstance(owner.get('created'), str) and bool(owner['created'])
            and isinstance(owner.get('image'), str) and PureWindowsPath(owner['image']).name.lower() == 'excel.exe'
            and isinstance(worker, dict) and type(worker.get('pid')) is int and worker['pid'] > 0
            and type(worker.get('returncode')) is int
            and observation.get('method') == 'identified_process_exit'
            and observation.get('native_worker_exited') is True
            and observation.get('owned_excel_present') is False)

"""Every calculator terminal outcome needs its explicit cleanup contract."""
import copy

import pytest

from mono.cleanup import verified_cleanup
from mono.verification import validate_evidence
from test_mono_result_evidence import receipt


@pytest.mark.parametrize('attack', ['missing', 'null', 'flag_only', 'version', 'unverified',
    'still_present', 'worker_alive', 'boolean_pid', 'boolean_exit', 'unowned', 'missing_owner'])
def test_cleanup_cannot_be_inferred_from_completed_calculation(receipt, attack):
    native, record, package = receipt
    if attack == 'missing':
        native.pop('cleanup')
    elif attack == 'null':
        native['cleanup'] = None
    elif attack == 'flag_only':
        native['cleanup']['verified'] = False
    elif attack == 'version':
        native['cleanup']['policy'] = 'unsupported'
    elif attack == 'unverified':
        native['cleanup']['state'] = 'unverified'
    elif attack == 'still_present':
        native['cleanup']['observation']['owned_excel_present'] = True
    elif attack == 'worker_alive':
        native['cleanup']['native_worker']['returncode'] = None
    elif attack == 'boolean_pid':
        native['cleanup']['excel_owner']['pid'] = True
    elif attack == 'boolean_exit':
        native['cleanup']['native_worker']['returncode'] = False
    elif attack == 'unowned':
        native['cleanup']['excel_owner']['new_process'] = False
    elif attack == 'missing_owner':
        native['cleanup']['excel_owner'] = None
    assert not verified_cleanup(native)
    with pytest.raises(ValueError, match='positive native cleanup'):
        validate_evidence(native, record, package)


@pytest.mark.parametrize('state', ['cancelled', 'blocked', 'failed', 'stale', 'complete'])
def test_only_prelaunch_terminal_failure_can_use_no_native_cleanup(state):
    native = {'state': state, 'cleanup_verified': True, 'cleanup': {
        'policy': 'mono-calculator-cleanup-v1', 'state': 'not_launched', 'verified': True,
        'native_launched': False, 'native_worker': None, 'excel_owner': None,
        'observation': {'method': 'executor_control_flow', 'native_worker_exited': None,
                        'owned_excel_present': None}}}
    assert verified_cleanup(native) is (state != 'complete')

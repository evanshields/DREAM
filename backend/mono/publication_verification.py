"""Independently derive completed documents from their frozen request plan."""
from pathlib import Path
from tempfile import TemporaryDirectory

from .config import canonical_hash,digest
from .publication_files import verify_package,output_file


def verify_planned_package(config,job,root):
    from tools.mono_calc.contracts import read_json
    from tools.mono_publish.contracts import artifact_path
    from tools.mono_publish.evidence import compare_native_evidence
    from tools.mono_publish.native_projection import normalized_identity
    from tools.mono_publish.source_plan import compile_source_plan,plan_identity
    root=Path(root).resolve(strict=True)
    request_root=root.parent/'request-sources'
    plan=read_json(request_root/'source-plan.json')
    if plan_identity(plan)!=job['identity']['source_plan_sha256']:
        raise ValueError('Frozen publication source plan changed')
    if digest(job['_native_receipt'])!=job['_native_receipt_sha256']:
        raise ValueError('Original native calculation receipt changed')
    projection=read_json(output_file(root,'projection.json'))
    release=job['identity']['release']
    expected=normalized_identity(release['result_identity'],job['deal_id'],job['revision'])
    if any(projection['identity'].get(key)!=value for key,value in expected.items()):
        raise ValueError('Compiled document belongs to another calculation')
    receipt=verify_package(root,identity=projection['identity'],projection_sha256=canonical_hash(projection))
    if receipt.get('cleanup_verified') is not True:
        raise ValueError('Publication cleanup has not been verified')
    source_root=root/'sources'
    source=projection['artifacts'][plan['extraction_artifact_id']]
    extracted=artifact_path(source_root,source['path'])
    reopened=read_json(receipt['workbook_verification']['path'])
    if reopened.get('receipt_sha256')!=job['_native_receipt_sha256']:
        raise ValueError('Workbook proof uses another native calculation receipt')
    compare_native_evidence(projection,source_root,reopened)
    base=config.data_root.resolve(strict=True)
    with TemporaryDirectory(prefix='dream-publication-verify-',dir=base) as temporary:
        scratch=Path(temporary).resolve(strict=True)
        if not scratch.is_relative_to(base):
            raise ValueError('Private verification directory escapes the configured data root')
        compiled=compile_source_plan(plan,request_root/'artifacts',extracted,scratch/'compiled',
            expected_native_identity=expected,expected_extraction_sha256=source['sha256'],
            renderer_sha256=job['identity']['renderer_sha256'],created_at=job['created_at'],
            comps_event_id=release['comps_event_id'],go_event_id=release['go_event_id'],final=True)
        if canonical_hash(compiled)!=receipt['projection_sha256']:
            raise ValueError('Published documents do not match the frozen source plan')
    return receipt

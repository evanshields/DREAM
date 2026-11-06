"""Counterexamples for the app boundary, using synthetic package bytes only."""
import copy
import json
from zipfile import ZipFile

import pytest

from mono.config import canonical_hash, digest
from mono.publication_files import (PublicationFilesError, verify_package,
                                    output_file, download_entry)


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding='utf-8')


def fixture(root):
    root.mkdir()
    files, deliverables = [], {}

    def entry(path, role, content):
        target = root/path
        target.parent.mkdir(parents=True, exist_ok=True)
        if content is not None:
            target.write_bytes(content)
        record = {'path':path, 'sha256':digest(target), 'role':role, 'media_type':'synthetic/test'}
        files.append(record)
        return record

    for kind in ('memo', 'onepager', 'deck'):
        source = kind+'/source.'+('pptx' if kind == 'deck' else 'html')
        if kind == 'deck':
            (root/kind).mkdir()
            with ZipFile(root/source, 'x') as archive:
                archive.writestr('[Content_Types].xml', '<Types/>')
                archive.writestr('ppt/presentation.xml', '<presentation/>')
        source_entry = entry(source, 'editable_source', None if kind == 'deck' else b'SYNTHETIC HTML')
        pdf_entry = entry(kind+'/source.pdf', 'pdf', b'%PDF-1.4\nSYNTHETIC TEST ONLY')
        deliverables[kind] = {'files':[source_entry, pdf_entry], 'validation':{'status':'passed'}}
    workbook = entry('mono.xlsx', 'underwriting_record', b'SYNTHETIC TEST, NOT A WORKBOOK')
    deliverables['workbook'] = {'files':[workbook], 'validation':{'status':'passed'}}
    identity = {key:'a'*64 for key in ('deal_sha256', 'bundle_sha256', 'source_sha256',
        'ledger_sha256', 'map_sha256', 'template_sha256', 'calculator_sha256')}
    identity.update(deal_id='synthetic-test', revision=1, result_id='synthetic-result',
                    workbook_sha256=workbook['sha256'])
    projection = {'identity':identity, 'synthetic_boundary_only':True}
    save(root/'projection.json', projection)
    entry('projection.json', 'private_audit', None)
    save(root/'verification.json', {'policy':'mono-publication-extraction-v1',
        'identity':identity, 'all_sheet_errors':{'synthetic-sheet':0}})
    proof = entry('verification.json', 'private_audit', None)
    record = {'state':'complete', 'preview':False, 'cleanup_verified':True, 'validation':{'passed':True}, 'identity':identity,
        'projection_sha256':canonical_hash(projection), 'deliverables':deliverables, 'files':files,
        'audience':'internal_underwriting_package', 'external_distribution_authorized':False, 'artifact_root':'sources',
        'workbook_verification':{'path':str(root/'verification.json'), 'sha256':proof['sha256']}}
    repack(root, record)
    return record


def repack(root, record):
    save(root/'manifest.json', {'schema_version':'mono-publication-package-v1',
        **{key:record[key] for key in ('identity', 'projection_sha256', 'deliverables', 'files',
            'audience', 'external_distribution_authorized', 'preview', 'artifact_root')}})
    record['manifest'] = {'path':'manifest.json', 'sha256':digest(root/'manifest.json'),
                          'role':'manifest', 'media_type':'application/json'}
    with ZipFile(root/'package.zip', 'w') as archive:
        for entry in [*record['files'], record['manifest']]:
            archive.write(root/entry['path'], entry['path'])
    record['archive'] = {'path':'package.zip', 'sha256':digest(root/'package.zip'),
                         'role':'internal_package', 'media_type':'application/zip'}
    save(root/'package.json', record)


def verify(root, record):
    return verify_package(root, identity=record['identity'], projection_sha256=record['projection_sha256'])


def test_complete_synthetic_package_and_controlled_download_choices(tmp_path):
    root = tmp_path/'package'
    record = fixture(root)
    actual = verify(root, record)
    assert actual == record
    assert download_entry(actual, 'package', 'archive')['path'] == 'package.zip'
    assert download_entry(actual, 'workbook', 'workbook')['path'] == 'mono.xlsx'
    assert download_entry(actual, 'deck', 'editable')['path'].endswith('.pptx')
    assert download_entry(actual, 'memo', 'pdf')['path'].endswith('.pdf')


@pytest.mark.parametrize('relative', ['../outside', '/absolute', 'C:/secret', 'a\\b',
                                    'a/../b', './mono.xlsx', 'a//b', ''])
def test_paths_must_stay_inside_the_package(tmp_path, relative):
    with pytest.raises((PublicationFilesError, OSError)):
        output_file(tmp_path, relative)


@pytest.mark.parametrize('change', ['preview', 'state', 'identity', 'partial', 'duplicate',
                                  'output', 'archive', 'projection', 'proof'])
def test_incomplete_or_changed_packages_cannot_be_used(tmp_path, change):
    root = tmp_path/'package'
    record = fixture(root)
    expected = copy.deepcopy(record)
    if change == 'preview':
        record['preview'] = True
    elif change == 'state':
        record['state'] = 'cancelled'
    elif change == 'identity':
        record['identity']['revision'] = 2
    elif change == 'partial':
        record['deliverables'].pop('deck')
    elif change == 'duplicate':
        record['files'].append(copy.deepcopy(record['files'][0]))
    elif change == 'output':
        (root/'memo/source.pdf').write_bytes(b'changed')
    elif change == 'archive':
        with ZipFile(root/'package.zip', 'a') as archive:
            archive.writestr('extra.txt', 'changed')
        record['archive']['sha256'] = digest(root/'package.zip')
    elif change == 'projection':
        record['projection_sha256'] = '0'*64
    else:
        record['workbook_verification']['sha256'] = '0'*64
    save(root/'package.json', record)
    with pytest.raises(PublicationFilesError):
        verify(root, expected)


def test_repacked_archive_cannot_hide_a_failed_native_reopen_proof(tmp_path):
    root = tmp_path/'package'
    record = fixture(root)
    proof = json.loads((root/'verification.json').read_text())
    proof['all_sheet_errors']['synthetic-sheet'] = 1
    save(root/'verification.json', proof)
    new_hash = digest(root/'verification.json')
    next(entry for entry in record['files'] if entry['path'] == 'verification.json')['sha256'] = new_hash
    record['workbook_verification']['sha256'] = new_hash
    repack(root, record)
    with pytest.raises(PublicationFilesError, match='Reopened workbook'):
        verify(root, record)


def test_exact_source_bytes_must_be_present_in_the_private_archive(tmp_path):
    root = tmp_path/'package'
    record = fixture(root)
    projection = json.loads((root/'projection.json').read_text())
    source = root/'sources/evidence.json'
    source.parent.mkdir()
    save(source, {'synthetic_source_only':True})
    projection['artifacts'] = {'source':{'path':'evidence.json','sha256':digest(source),
        'media_type':'application/json','role':'reference'}}
    save(root/'projection.json',projection)
    next(entry for entry in record['files'] if entry['path']=='projection.json')['sha256']=digest(root/'projection.json')
    record['projection_sha256']=canonical_hash(projection)
    repack(root,record)
    with pytest.raises(PublicationFilesError,match='source evidence'):
        verify(root,record)
    record['files'].append({'path':'sources/evidence.json','sha256':digest(source),
        'media_type':'application/json','role':'private_evidence'})
    repack(root,record)
    assert verify(root,record)['state']=='complete'


@pytest.mark.parametrize('deliverable,variant', [('private_audit', 'editable'), ('../memo', 'pdf'),
    ('workbook', 'pdf'), ('deck', 'workbook'), ('memo', 'private_audit'), ('package', 'editable')])
def test_download_choices_cannot_select_audit_files_or_paths(tmp_path, deliverable, variant):
    record = fixture(tmp_path/'package')
    with pytest.raises(PublicationFilesError):
        download_entry(record, deliverable, variant)

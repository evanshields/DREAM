"""Independently verify a renderer's complete private package before use."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
from zipfile import ZipFile, BadZipFile

from .config import canonical_hash, digest


class PublicationFilesError(ValueError):
    pass


def output_file(root, relative):
    """Only receipt-listed regular files strictly below this job's directory."""
    if (not isinstance(relative, str) or not relative or '\\' in relative or ':' in relative
            or relative.startswith('/') or any(part in ('', '.', '..') for part in relative.split('/'))):
        raise PublicationFilesError('Publication file path is invalid')
    root = Path(root).resolve(strict=True)
    path = root.joinpath(*PurePosixPath(relative).parts).resolve(strict=True)
    if not path.is_relative_to(root) or not path.is_file():
        raise PublicationFilesError('Publication file is unavailable')
    return path


def _entry(root, entry):
    if (not isinstance(entry, dict) or not {'path', 'sha256', 'role', 'media_type'} <= set(entry)
            or not isinstance(entry['sha256'], str) or len(entry['sha256']) != 64
            or any(char not in '0123456789abcdef' for char in entry['sha256'])):
        raise PublicationFilesError('Publication file receipt is incomplete')
    path = output_file(root, entry['path'])
    if digest(path) != entry['sha256']:
        raise PublicationFilesError('Publication file changed after verification')
    return path


def verify_package(root, *, identity, projection_sha256):
    """Return a verified immutable receipt, never accepting previews as final."""
    root = Path(root).resolve(strict=True)
    try:
        record = json.loads(output_file(root, 'package.json').read_text(encoding='utf-8'))
        if (record.get('state') != 'complete' or record.get('preview') is not False
                or record.get('validation', {}).get('passed') is not True
                or record.get('identity') != identity
                or record.get('projection_sha256') != projection_sha256
                or record.get('audience') != 'internal_underwriting_package'
                or record.get('artifact_root') != 'sources'
                or record.get('external_distribution_authorized') is not False
                or set(record.get('deliverables', {})) != {'memo', 'onepager', 'deck', 'workbook'}):
            raise PublicationFilesError('Publication is incomplete or has a different source identity')
        files = record.get('files')
        if not isinstance(files, list) or not files:
            raise PublicationFilesError('Publication file inventory is missing')
        for entry in files:
            _entry(root, entry)
        by_path = {entry['path']:entry for entry in files}
        if len(by_path) != len(files):
            raise PublicationFilesError('Publication contains duplicate file paths')
        for kind, deliverable in record['deliverables'].items():
            entries = deliverable.get('files', [])
            if (deliverable.get('validation', {}).get('status') != 'passed' or not entries
                    or any(entry != by_path.get(entry.get('path')) for entry in entries)):
                raise PublicationFilesError('Required deliverable files are missing or inconsistent')
            roles = {entry['role'] for entry in entries}
            if kind == 'workbook':
                if (len(entries) != 1 or entries[0]['role'] != 'underwriting_record'
                        or entries[0]['sha256'] != identity['workbook_sha256']
                        or not entries[0]['path'].endswith('.xlsx')):
                    raise PublicationFilesError('Workbook export differs from the verified calculation')
            elif not {'editable_source', 'pdf'} <= roles:
                raise PublicationFilesError('Editable document and PDF are required')
            elif kind == 'deck' and not any(entry['role'] == 'editable_source'
                    and entry['path'].endswith('.pptx') for entry in entries):
                raise PublicationFilesError('Editable PowerPoint is required')
            for entry in entries:
                path = output_file(root, entry['path'])
                if entry['role'] == 'pdf' and not path.read_bytes().startswith(b'%PDF-'):
                    raise PublicationFilesError('Required PDF has invalid content')
                if path.suffix.lower() == '.pptx':
                    with ZipFile(path) as deck:
                        if not {'[Content_Types].xml', 'ppt/presentation.xml'} <= set(deck.namelist()):
                            raise PublicationFilesError('PowerPoint source is incomplete')
        manifest_path = _entry(root, record['manifest'])
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        if (manifest.get('schema_version') != 'mono-publication-package-v1'
                or any(manifest.get(key) != record.get(key) for key in
                    ('identity', 'projection_sha256', 'deliverables', 'files', 'audience',
                     'external_distribution_authorized', 'preview', 'artifact_root'))):
            raise PublicationFilesError('Archive manifest differs from the verified publication')
        archive_path = _entry(root, record['archive'])
        archive_entries = [*files, record['manifest']]
        with ZipFile(archive_path) as archive:
            names = archive.namelist()
            if (len(names) != len(archive_entries)
                    or set(names) != {entry['path'] for entry in archive_entries}):
                raise PublicationFilesError('Archive inventory differs from the package')
            for entry in archive_entries:
                if hashlib.sha256(archive.read(entry['path'])).hexdigest() != entry['sha256']:
                    raise PublicationFilesError('Archive bytes differ from the verified files')
        projection_path = output_file(root, 'projection.json')
        projection = json.loads(projection_path.read_text(encoding='utf-8'))
        if 'projection.json' not in by_path or canonical_hash(projection) != projection_sha256:
            raise PublicationFilesError('Saved projection differs from the publication plan')
        for artifact in projection.get('artifacts', {}).values():
            entry = by_path.get('sources/'+artifact['path'])
            if (entry is None or entry['sha256'] != artifact['sha256']
                    or entry['media_type'] != artifact['media_type'] or entry['role'] != 'private_evidence'):
                raise PublicationFilesError('Publication source evidence is absent from the archive')
        verification = record['workbook_verification']
        proof_path = Path(verification['path']).resolve(strict=True)
        if not proof_path.is_relative_to(root):
            raise PublicationFilesError('Workbook verification escapes its package')
        proof_entry = by_path.get(proof_path.relative_to(root).as_posix())
        if proof_entry is None or verification.get('sha256') != proof_entry['sha256']:
            raise PublicationFilesError('Workbook verification is absent from the package')
        proof = json.loads(proof_path.read_text(encoding='utf-8'))
        fields = {'deal_id', 'revision', 'result_id', 'deal_sha256', 'bundle_sha256', 'source_sha256',
                  'ledger_sha256', 'map_sha256', 'template_sha256', 'calculator_sha256', 'workbook_sha256'}
        if (proof.get('policy') != 'mono-publication-extraction-v1'
                or not fields <= set(proof.get('identity', {}))
                or any(identity.get(key) != value for key, value in proof['identity'].items())
                or not proof.get('all_sheet_errors')
                or any(type(value) not in (int, float) or value != 0
                       for value in proof['all_sheet_errors'].values())):
            raise PublicationFilesError('Reopened workbook proof did not pass')
        return record
    except PublicationFilesError:
        raise
    except (OSError, ValueError, KeyError, TypeError, BadZipFile) as error:
        raise PublicationFilesError('Publication package verification failed') from error


def download_entry(record, deliverable, variant):
    """Resolve controlled download choices, never a caller-supplied file path."""
    if deliverable == 'package' and variant == 'archive':
        return record['archive']
    if deliverable not in {'memo', 'onepager', 'deck', 'workbook'}:
        raise PublicationFilesError('Unknown publication download')
    role = {'pdf':'pdf', 'editable':'editable_source', 'workbook':'underwriting_record'}.get(variant)
    if role is None or (deliverable == 'workbook') != (variant == 'workbook'):
        raise PublicationFilesError('Unknown publication download format')
    matches = [entry for entry in record['deliverables'][deliverable]['files'] if entry['role'] == role]
    if len(matches) != 1:
        raise PublicationFilesError('Requested publication file is unavailable')
    return matches[0]

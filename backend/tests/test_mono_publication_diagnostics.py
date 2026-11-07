"""A failed publication tells the operator why when the reason is one of the app's own curated messages.

Any other error (a path error from the operating system, a parser message, an unexpected bug) keeps the
generic private message, because those can carry file paths or source text.
"""
import queue
from threading import Event
from types import SimpleNamespace

import pytest

import mono.publication as publication_module
from mono.publication_files import PublicationFilesError
from store.mono_deal_store import MonoConflict
from test_mono_publication_provider import inputs, isolate_financial_context_for_dispatcher_tests  # noqa: F401
from test_mono_publish_store import ready, publication  # noqa: F401

GENERIC = 'publication verification failed. Sources remain private.'


def failed_job(ready, tmp_path, error):
    """Queue one publication, make its worker raise `error`, and return the stored job."""
    store, config, builder, _, _ = inputs(ready, tmp_path)
    job = publication(store)
    job['identity']['release'] = store.snapshot('fixture')
    store.claim('fixture', job, 'diagnostic-key', 'request')
    provider = publication_module.PublicationProvider.__new__(publication_module.PublicationProvider)
    provider.config, provider.store, provider.builder = config, store, builder
    provider._closed, provider._queue, provider._active_job = Event(), queue.Queue(), None
    provider._lease = SimpleNamespace(close=lambda: None)

    def run(deal_id, job_id):
        raise error

    provider._run = run
    provider._queue.put(('fixture', job['job_id']))
    provider._queue.put(None)
    provider._work()
    return store.job('fixture', job['job_id'])


@pytest.mark.parametrize('error', [PublicationFilesError('Required PDF has invalid content'),
                                   MonoConflict('Publication reviews changed before rendering')])
def test_curated_failure_message_reaches_the_operator(ready, tmp_path, error):
    job = failed_job(ready, tmp_path, error)
    assert job['state'] == 'failed' and job['package'] is None
    assert job['diagnostics'] == [type(error).__name__ + ': ' + str(error)]


@pytest.mark.parametrize('error', [
    ValueError("'C:/Users/private/sources/rent-roll.xlsx' is not in the subpath of 'C:/data/jobs/job-1'"),
    FileNotFoundError(2, 'No such file or directory', 'C:/Users/private/sources/evidence.pdf'),
    KeyError('C:/Users/private/sources/evidence.pdf'),
    RuntimeError('unexpected token near seller name Example Holdings LLC')])
def test_other_failures_keep_the_generic_private_message(ready, tmp_path, error):
    job = failed_job(ready, tmp_path, error)
    assert job['state'] == 'failed' and job['package'] is None
    assert job['diagnostics'] == [type(error).__name__ + ': ' + GENERIC]
    assert 'private/sources' not in job['diagnostics'][0] and 'Example Holdings' not in job['diagnostics'][0]

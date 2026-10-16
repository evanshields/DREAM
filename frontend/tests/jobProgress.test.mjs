import test from 'node:test';
import assert from 'node:assert/strict';
import { isCancellationPending, isKnownJobStatus, shouldPollJob, runDestination, requestJobCancellation, mergeJobView } from '../src/lib/jobProgress.ts';

const job = (status, cancel_requested = false) => ({ job_id: 'sample-run', status, cancel_requested });

test('cancel acknowledgement stays visible and polling until cancellation is observed', async () => {
  let current = job('analyzing');
  let finishRequest;
  const response = new Promise(resolve => { finishRequest = resolve; });
  const request = requestJobCancellation('sample-run', id => {
    assert.equal(id, 'sample-run');
    return response;
  }, view => { current = view; });
  assert.equal(current.cancel_requested, false);
  finishRequest(job('analyzing', true));
  await request;
  assert.equal(runDestination(current), 'running');
  assert.equal(shouldPollJob(current), true);
  assert.equal(isCancellationPending(current), true);
  current = job('cancelled', true);
  assert.equal(runDestination(current), 'intake');
  assert.equal(shouldPollJob(current), false);
});

test('failed or lost cancellation request preserves the known server state', async () => {
  const current = job('analyzing');
  let applied = 0;
  await assert.rejects(requestJobCancellation('sample-run', async () => {
    throw new Error('Connection lost');
  }, () => { applied += 1; }), /Connection lost/);
  assert.equal(applied, 0);
  assert.equal(runDestination(current), 'running');
  assert.equal(shouldPollJob(current), true);
});

test('completion racing cancellation goes to human review, not fabricated cancellation', async () => {
  let current = job('analyzing');
  await requestJobCancellation('sample-run', async () => job('completed'), view => { current = view; });
  assert.equal(runDestination(current), 'review');
  assert.equal(shouldPollJob(current), false);
  assert.equal(isCancellationPending(current), false);
});

test('a cancel flag cannot hide paused inputs or the CP-1 human stop', () => {
  for (const status of ['awaiting_input', 'awaiting_cp1']) {
    assert.equal(shouldPollJob(job(status, true)), false);
    assert.equal(isCancellationPending(job(status, true)), false);
  }
  assert.equal(runDestination(job('awaiting_input', true)), 'questions');
  assert.equal(runDestination(job('awaiting_cp1', true)), 'review');
  assert.equal(runDestination(job('awaiting_input')), 'questions');
  assert.equal(runDestination(job('awaiting_cp1')), 'review');
  assert.equal(shouldPollJob(job('awaiting_cp1')), false);
});

test('late responses cannot regress cancellation acknowledgement or a terminal outcome', () => {
  const acknowledged = job('analyzing', true);
  assert.equal(mergeJobView(acknowledged, job('analyzing')).cancel_requested, true);
  for (const status of ['awaiting_cp1', 'completed', 'failed', 'cancelled']) {
    const finished = job(status);
    assert.equal(mergeJobView(finished, acknowledged), finished);
  }
  const other = { ...acknowledged, job_id: 'old-run' };
  assert.equal(mergeJobView(acknowledged, other), acknowledged);
});

test('failure while cancellation is pending is an actual failure, not cancellation', () => {
  assert.equal(runDestination(job('failed', true)), 'failed');
  assert.equal(shouldPollJob(job('failed', true)), false);
  assert.equal(isCancellationPending(job('failed', true)), false);
});

test('all active API statuses continue polling', () => {
  for (const status of ['submitted', 'routing', 'analyzing', 'synthesizing']) {
    assert.equal(runDestination(job(status)), 'running');
    assert.equal(shouldPollJob(job(status)), true);
  }
});

test('aborted cancellation passes the signal and suppresses a late response', async () => {
  const controller = new AbortController();
  let resolve;
  let applied = 0;
  const response = new Promise(done => { resolve = done; });
  const request = requestJobCancellation('sample-run', (_id, signal) => {
    assert.equal(signal, controller.signal);
    return response;
  }, () => { applied += 1; }, controller.signal);
  controller.abort();
  resolve(job('completed'));
  await request;
  assert.equal(applied, 0);
});

test('executing phases cannot regress, while an actual paused-to-running resume is accepted', () => {
  const analyzing = job('analyzing');
  assert.equal(mergeJobView(analyzing, job('routing')), analyzing);
  const resumed = mergeJobView(job('awaiting_input'), job('routing'));
  assert.equal(resumed.status, 'routing');
  assert.equal(runDestination(resumed), 'running');
});

test('unknown server status keeps an unconfirmed run visible instead of returning to intake', () => {
  const unknown = job('future_status');
  assert.equal(isKnownJobStatus(unknown), false);
  assert.equal(runDestination(unknown), 'running');
  assert.equal(shouldPollJob(unknown), true);
});

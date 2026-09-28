import { test, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { request } from './api.js';

const originalFetch = globalThis.fetch;
afterEach(() => { globalThis.fetch = originalFetch; });

test('submits edited resume and unwraps the API response', async () => {
  const body = { resume_text: 'Edited resume', structured_resume: { name: 'Example' }, jd: 'React' };
  globalThis.fetch = async (url, options) => {
    assert.equal(url, '/api/v1/assistant/analyze');
    assert.equal(options.method, 'POST');
    assert.deepEqual(JSON.parse(options.body), body);
    return Response.json({ success: true, data: { analysis_id: '123' } });
  };
  assert.deepEqual(await request('/assistant/analyze', { body }), { analysis_id: '123' });
});

test('file uploads leave the multipart boundary to the browser', async () => {
  const body = new FormData();
  body.append('file', new Blob(['resume']), 'resume.txt');
  globalThis.fetch = async (_, options) => {
    assert.equal(options.body, body);
    assert.equal(options.headers['Content-Type'], undefined);
    return Response.json({ success: true, data: { text: 'resume' } });
  };
  assert.deepEqual(await request('/upload/resume', { body }), { text: 'resume' });
});

test('reports application errors even with a successful HTTP status', async () => {
  globalThis.fetch = async () => Response.json({ success: false, message: '没有可用的简历' });
  await assert.rejects(request('/match/match', { body: {} }), /没有可用的简历/);
});

test('exposes FastAPI validation errors', async () => {
  globalThis.fetch = async () => Response.json({ detail: [{ loc: ['body', 'jd'], msg: 'Field required' }] }, { status: 422 });
  await assert.rejects(request('/match/match'), /body.jd: Field required/);
});

test('handles unavailable proxy and network failures', async () => {
  globalThis.fetch = async () => new Response('Bad Gateway', { status: 502 });
  await assert.rejects(request('/resume/version/list'), /502/);
  globalThis.fetch = async () => { throw new TypeError('Failed to fetch'); };
  await assert.rejects(request('/resume/version/list'), /无法连接服务/);
});

test('downloads binary reports and preserves JSON errors for failed downloads', async () => {
  globalThis.fetch = async () => new Response('%PDF-1.7', { headers: { 'Content-Type': 'application/pdf' } });
  assert.equal(await (await request('/assistant/report/pdf/123', { binary: true })).text(), '%PDF-1.7');
  globalThis.fetch = async () => Response.json({ detail: 'analysis_id not found' }, { status: 404 });
  await assert.rejects(request('/assistant/report/pdf/123', { binary: true }), /analysis_id not found/);
});

test('aborts slow requests with a useful message', async () => {
  globalThis.fetch = async (_, options) => new Promise((resolve, reject) => {
    options.signal.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')));
  });
  await assert.rejects(request('/assistant/analyze', { body: {}, timeout: 5 }), /请求超时/);
});

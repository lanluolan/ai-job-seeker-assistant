export async function request(path, { body, binary = false, timeout = 180000, ...options } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeout);
  try {
    const multipart = body instanceof FormData;
    const response = await fetch(`/api/v1${path}`, {
      ...options,
      method: options.method || (body !== undefined ? 'POST' : 'GET'),
      headers: { ...(body !== undefined && !multipart ? { 'Content-Type': 'application/json' } : {}), ...options.headers },
      body: body === undefined ? undefined : multipart ? body : JSON.stringify(body),
      signal: controller.signal,
    });
    if (response.ok && binary) return await response.blob();
    const result = await response.json().catch(() => null);
    if (!response.ok || !result || result.success === false) {
      const detail = result?.detail;
      const message = Array.isArray(detail) ? detail.map(item => `${item.loc?.join('.')}: ${item.msg}`).join('；') : detail;
      throw new Error(message || result?.message || `请求失败（${response.status}），请检查后端服务。`);
    }
    return result.data;
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('请求超时，请稍后重试。');
    if (error instanceof TypeError) throw new Error('无法连接服务，请检查网络和后端是否启动。');
    throw error;
  } finally {
    clearTimeout(timer);
  }
}

export function download(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

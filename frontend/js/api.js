export function getToken() {
  return localStorage.getItem('knowbase_token') || '';
}

export function setAuth(token, username) {
  localStorage.setItem('knowbase_token', token);
  localStorage.setItem('knowbase_user', username || '');
}

export function clearAuth() {
  localStorage.removeItem('knowbase_token');
  localStorage.removeItem('knowbase_user');
}

export function requireAuth() {
  if (!getToken()) {
    window.location.href = '/login.html';
    return false;
  }
  return true;
}

export async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  if (options.body && !(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }
  const res = await fetch(path, { ...options, headers });
  const text = await res.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { raw: text };
  }
  if (!res.ok) {
    const msg = data?.error || data?.message || res.statusText;
    throw new Error(msg);
  }
  return data;
}

// ===== API 基礎設定 =====
const API_BASE = '/api';

function getToken() {
  return localStorage.getItem('access_token');
}

function makeEventUuid() {
  if (globalThis.crypto && typeof globalThis.crypto.randomUUID === 'function') {
    return globalThis.crypto.randomUUID();
  }
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, char => {
    const value = Math.floor(Math.random() * 16);
    return (char === 'x' ? value : (value & 0x3) | 0x8).toString(16);
  });
}

// ===== 研究事件基礎（②③④）=====
// 分頁識別：同一分頁固定、不同分頁不同，讓事件可區分來源分頁
function getTabUuid() {
  try {
    let id = sessionStorage.getItem('tab_uuid');
    if (!id) {
      id = makeEventUuid();
      sessionStorage.setItem('tab_uuid', id);
    }
    return id;
  } catch (e) {
    return null;
  }
}

// 每筆事件附上「裝置實際操作時間＋分頁」；伺服器另記 received_at 供時鐘差分析
function eventStamp() {
  return { client_occurred_at: new Date().toISOString(), tab_uuid: getTabUuid() };
}

// 本地事件佇列：先落地 localStorage、送達才移除；後端以 event_uuid 去重，重送安全
const EVENT_QUEUE_KEY = 'al_event_queue_v1';
const EVENT_QUEUE_MAX = 500;

function loadEventQueue() {
  try {
    return JSON.parse(localStorage.getItem(EVENT_QUEUE_KEY) || '[]');
  } catch (e) {
    return [];
  }
}

function saveEventQueue(queue) {
  try {
    localStorage.setItem(EVENT_QUEUE_KEY, JSON.stringify(queue.slice(-EVENT_QUEUE_MAX)));
  } catch (e) { /* storage 滿了就放棄最舊的 */ }
}

async function flushEventQueue() {
  const token = localStorage.getItem('access_token');
  if (!token) return;
  const queue = loadEventQueue();
  if (!queue.length) return;
  const batch = queue.slice(0, 100);
  try {
    const res = await fetch(`${API_BASE}/learning/events/`, {
      method: 'POST',
      keepalive: true,
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify(batch),
    });
    if (res && res.ok) {
      const sent = new Set(batch.map(item => item.event_uuid));
      const remaining = loadEventQueue().filter(item => !sent.has(item.event_uuid));
      saveEventQueue(remaining);
      if (remaining.length) flushEventQueue();
    }
  } catch (e) { /* 網路失敗：佇列保留，下次載頁或下筆事件時補送 */ }
}

// 開頁補送上次殘留；關頁前盡力送出
flushEventQueue();
window.addEventListener('pagehide', () => flushEventQueue());

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  })[char]);
}

// admin 預覽學生功能：若當前頁面 URL 帶 preview_as，所有 API 自動附加
// （搭配後端 PreviewAsJWTAuthentication，admin 身分自動拿取該學生資料）
function getPreviewAs() {
  try {
    const p = new URLSearchParams(window.location.search).get('preview_as');
    return p || null;
  } catch (e) {
    return null;
  }
}

function withPreviewAs(endpoint) {
  const previewAs = getPreviewAs();
  if (!previewAs) return endpoint;
  const sep = endpoint.includes('?') ? '&' : '?';
  return `${endpoint}${sep}preview_as=${encodeURIComponent(previewAs)}`;
}

async function apiFetch(endpoint, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const url = `${API_BASE}${withPreviewAs(endpoint)}`;
  const res = await fetch(url, { ...options, headers });

  if (res.status === 401) {
    // Token 過期，嘗試 refresh
    const refreshed = await refreshToken();
    if (refreshed) {
      headers['Authorization'] = `Bearer ${getToken()}`;
      return fetch(url, { ...options, headers });
    } else {
      localStorage.clear();
      window.location.href = '/login.html';
      return;
    }
  }

  return res;
}

async function refreshToken() {
  const refresh = localStorage.getItem('refresh_token');
  if (!refresh) return false;
  const res = await fetch(`${API_BASE}/token/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh }),
  });
  if (res.ok) {
    const data = await res.json();
    localStorage.setItem('access_token', data.access);
    return true;
  }
  return false;
}

// ===== Auth API =====
const AuthAPI = {
  async login(username, password) {
    const res = await fetch(`${API_BASE}/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    if (res.ok) {
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
    }
    return { ok: res.ok, data };
  },

  async getProfile() {
    const res = await apiFetch('/auth/profile/');
    return res && res.ok ? await res.json() : null;
  },

  async changePassword(payload) {
    const res = await apiFetch('/auth/change-password/', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    if (!res) return { ok: false, data: null };
    let data = null;
    try {
      data = await res.json();
    } catch (e) {
      data = null;
    }
    return { ok: res && res.ok, data };
  },

  async logout() {
    try { await apiFetch('/auth/logout/', { method: 'POST' }); } catch (e) {}
    localStorage.clear();
    window.location.href = '/login.html';
  },
};

// ===== Courses API =====
const CoursesAPI = {
  async list() {
    const res = await fetch(`${API_BASE}/courses/`);
    return res.ok ? await res.json() : [];
  },

  async detail(id) {
    const res = await fetch(`${API_BASE}/courses/${id}/`);
    return res.ok ? await res.json() : null;
  },
};

// ===== Learning API =====
const LearningAPI = {
  async getProgress() {
    const res = await apiFetch('/learning/progress/');
    return res && res.ok ? await res.json() : { results: [] };
  },

  async getRecommendations() {
    const res = await apiFetch('/learning/recommendations/');
    return res && res.ok ? await res.json() : { results: [] };
  },

  // 單元開放開關（老師／管理員）
  async getUnitReleases() {
    const res = await apiFetch('/learning/unit-release/');
    return res && res.ok ? await res.json() : [];
  },

  async setUnitRelease(unitNumber, isOpen) {
    const res = await apiFetch('/learning/unit-release/', {
      method: 'POST',
      body: JSON.stringify({ unit_number: unitNumber, is_open: isOpen }),
    });
    return { ok: Boolean(res && res.ok), data: res ? await res.json().catch(() => null) : null };
  },

  // 記錄推薦卡點擊（RQ-04 推薦接受度埋點）。keepalive 確保導頁時仍送達
  clickRecommendation(id) {
    if (!id) return;
    const token = localStorage.getItem('access_token');
    return fetch(`${API_BASE}/learning/recommendations/${id}/click/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      body: JSON.stringify(eventStamp()),
      keepalive: true,
    }).catch(() => {});
  },

  impressionRecommendation(id) {
    if (!id) return;
    return apiFetch(`/learning/recommendations/${id}/impression/`, {
      method: 'POST', body: JSON.stringify(eventStamp()),
    }).catch(() => {});
  },

  dismissRecommendation(id) {
    if (!id) return;
    return apiFetch(`/learning/recommendations/${id}/dismiss/`, {
      method: 'POST', body: JSON.stringify(eventStamp()),
    }).catch(() => {});
  },

  // 記錄教材瀏覽 / 線上時數（RQ-05 投入度埋點）。seconds 省略或 0 = 計一次瀏覽
  recordActivity(lessonId, seconds = 0) {
    if (!lessonId) return;
    const body = JSON.stringify({
      lesson_id: lessonId, seconds, page_url: location.href,
      referrer: document.referrer,
      client_timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      app_version: 'research-events-v1', content_version: 'v1',
      ...eventStamp(),
    });
    const token = localStorage.getItem('access_token');
    // keepalive 確保 pagehide 時仍能送達（Authorization header 需自帶，故不用 sendBeacon）
    return fetch(`${API_BASE}/learning/activity/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      body,
      keepalive: true,
    }).catch(() => {});
  },

  // 使用時段心跳（RQ-05 使用時間/次數）。後端僅對學生帳號計入。
  heartbeat() {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    return fetch(`${API_BASE}/learning/heartbeat/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      keepalive: true,
    }).catch(() => {});
  },

  // 事件先進本地佇列再批次上傳（④ 可靠送達：失敗保留、下次補送、UUID 去重）
  recordEvent(eventType, extra = {}) {
    if (!localStorage.getItem('access_token')) return;
    const queue = loadEventQueue();
    queue.push({
      event_uuid: makeEventUuid(), event_type: eventType, page_url: location.href,
      referrer: document.referrer,
      client_timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      app_version: 'research-events-v1', ...eventStamp(), ...extra,
    });
    saveEventQueue(queue);
    return flushEventQueue();
  },

  startAttempt(quizId) {
    return apiFetch('/assessments/start/', {
      method: 'POST', body: JSON.stringify({ quiz_id: Number(quizId), ...eventStamp() }),
    });
  },

  recordQuestionInteraction(payload) {
    return apiFetch('/assessments/interaction/', {
      method: 'POST', body: JSON.stringify({ ...eventStamp(), ...payload }),
    }).catch(() => {});
  },

  abandonAttempt(attemptId) {
    if (!attemptId) return;
    const token = localStorage.getItem('access_token');
    return fetch(`${API_BASE}/assessments/attempts/${attemptId}/abandon/`, {
      method: 'POST', keepalive: true,
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify(eventStamp()),
    }).catch(() => {});
  },
};

// ===== 報表 API（學生個人成長報表）=====
const ReportAPI = {
  async myReport() {
    const res = await apiFetch('/auth/my-report/');
    return res && res.ok ? await res.json() : null;
  },
};

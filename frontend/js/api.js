// ===== API 基礎設定 =====
const API_BASE = '/api';

function getToken() {
  return localStorage.getItem('access_token');
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

  async register(payload) {
    const res = await fetch(`${API_BASE}/auth/register/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    return { ok: res.ok, data: await res.json() };
  },

  async getProfile() {
    const res = await apiFetch('/auth/profile/');
    return res.ok ? await res.json() : null;
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

  logout() {
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

  async enroll(courseId) {
    const res = await apiFetch('/courses/enroll/', {
      method: 'POST',
      body: JSON.stringify({ course: courseId }),
    });
    return { ok: res.ok, data: await res.json() };
  },

  async myCourses() {
    const res = await apiFetch('/courses/my/');
    return res && res.ok ? await res.json() : { results: [] };
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

  async getPerformance() {
    const res = await apiFetch('/learning/performance/');
    return res && res.ok ? await res.json() : { results: [] };
  },

  // 記錄推薦卡點擊（RQ-04 推薦接受度埋點）。keepalive 確保導頁時仍送達
  clickRecommendation(id) {
    if (!id) return;
    const token = localStorage.getItem('access_token');
    return fetch(`${API_BASE}/learning/recommendations/${id}/click/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      keepalive: true,
    }).catch(() => {});
  },

  // 記錄教材瀏覽 / 線上時數（RQ-05 投入度埋點）。seconds 省略或 0 = 計一次瀏覽
  recordActivity(lessonId, seconds = 0) {
    if (!lessonId) return;
    const body = JSON.stringify({ lesson_id: lessonId, seconds });
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
};

// ===== 報表 API（學生個人成長報表）=====
const ReportAPI = {
  async myReport() {
    const res = await apiFetch('/auth/my-report/');
    return res && res.ok ? await res.json() : null;
  },
};

// ===== 問卷成績 API（管理端）=====
const SurveyAPI = {
  async scales() {
    const res = await apiFetch('/surveys/scales/');
    return res && res.ok ? await res.json() : [];
  },
  async grid(scaleKey, phase) {
    const res = await apiFetch(`/surveys/scores/?scale=${encodeURIComponent(scaleKey)}&phase=${phase}`);
    return res && res.ok ? await res.json() : null;
  },
  async saveBatch(scaleKey, phase, scores) {
    const res = await apiFetch('/surveys/scores/batch/', {
      method: 'POST',
      body: JSON.stringify({ scale: scaleKey, phase, scores }),
    });
    return { ok: res && res.ok, data: res && res.ok ? await res.json() : null };
  },
  async importCsv(csvText) {
    const res = await apiFetch('/surveys/scores/import/', {
      method: 'POST',
      body: JSON.stringify({ csv: csvText }),
    });
    return { ok: res && res.ok, data: res ? await res.json().catch(() => null) : null };
  },
};

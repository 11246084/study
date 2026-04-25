// ===== API 基礎設定 =====
const API_BASE = '/api';

function getToken() {
  return localStorage.getItem('access_token');
}

async function apiFetch(endpoint, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const res = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });

  if (res.status === 401) {
    // Token 過期，嘗試 refresh
    const refreshed = await refreshToken();
    if (refreshed) {
      headers['Authorization'] = `Bearer ${getToken()}`;
      return fetch(`${API_BASE}${endpoint}`, { ...options, headers });
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
};

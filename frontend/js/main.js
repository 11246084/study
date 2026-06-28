// ===== Utility =====
function showToast(message, type = 'success') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

function isLoggedIn() {
  return !!localStorage.getItem('access_token');
}

// ===== Navbar 動態 =====
function initNavbar() {
  const loggedIn = isLoggedIn();
  const navLinks = document.querySelector('.navbar-links');
  const navRight = document.getElementById('nav-right');

  // 清空所有導覽連結
  if (navLinks) navLinks.innerHTML = '';

  // 右側只有登出或登入
  if (navRight) {
    if (loggedIn) {
      navRight.innerHTML = `
        <button class="btn-nav solid" onclick="AuthAPI.logout()">登出</button>
      `;
    } else {
      navRight.innerHTML = `
        <a href="/login.html" class="btn-nav outline">登入</a>
        <a href="/register.html" class="btn-nav solid">註冊</a>
      `;
    }
  }
}

// ===== 全站 footer：整個系統累計登入次數 =====
async function renderSystemFooter() {
  // 登入 / 註冊頁不顯示 footer
  if (/\/(login|register)\.html$/.test(window.location.pathname)) return;
  // iframe 內嵌頁（admin-shell 載入）不重複顯示，footer 由外層 shell 呈現
  const params = new URLSearchParams(window.location.search);
  if (params.get('embedded') === '1') return;
  if (document.getElementById('system-footer')) return;

  const footer = document.createElement('footer');
  footer.id = 'system-footer';
  footer.style.cssText =
    'margin-top:0;height:50px;padding:2px 16px;box-sizing:border-box;' +
    'border-top:1px solid var(--color-border,#e4e1da);display:flex;flex-direction:column;' +
    'align-items:center;justify-content:center;text-align:center;color:#8a8a8a;font-size:.75rem;line-height:1.35;';
  footer.innerHTML =
    '<div>AdaptLearn · 程式設計適性學習輔助系統</div>' +
    '<div>系統累計登入 <b id="sf-logins" style="color:#555">—</b> 次</div>';
  document.body.appendChild(footer);

  try {
    const res = await fetch('/api/auth/stats/');
    if (res.ok) {
      const data = await res.json();
      const el = document.getElementById('sf-logins');
      if (el) el.textContent = Number(data.total_logins).toLocaleString('zh-TW');
    }
  } catch (e) { /* 靜默失敗，footer 仍顯示 */ }
}

document.addEventListener('DOMContentLoaded', () => {
  initNavbar();
  renderSystemFooter();
});

// ===== 使用時段心跳（RQ-05 使用時間/次數）=====
// 登入後每 2 分鐘送一次心跳，後端據此切分「使用時段」。
// 跳過管理端預覽 / iframe 內嵌情境，避免汙染學生研究資料。
(function startHeartbeat() {
  const params = new URLSearchParams(window.location.search);
  const isAdminContext = params.has('preview_as') || params.get('embedded') === '1' || params.get('admin_mode') === '1';
  if (isAdminContext || !isLoggedIn() || typeof LearningAPI === 'undefined') return;

  const ping = () => { if (!document.hidden) LearningAPI.heartbeat(); };
  ping(); // 進站立即記一次
  setInterval(ping, 120000);
  document.addEventListener('visibilitychange', () => { if (!document.hidden) ping(); });
})();

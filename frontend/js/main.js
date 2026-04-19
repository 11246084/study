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

document.addEventListener('DOMContentLoaded', initNavbar);

/**
 * Blood Reach BD — Login Page JavaScript
 * Handles: role selection, form validation, password toggle,
 *           animated background, JWT-ready submit flow
 */

'use strict';

/* ── DOM References ────────────────────────────────────── */
const bgParticles = document.getElementById('bgParticles');
const floatingDrops = document.getElementById('floatingDrops');
const roleTabs = document.querySelectorAll('.role-tab');
const loginForm = document.getElementById('loginForm');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const togglePwdBtn = document.getElementById('togglePassword');
const eyeIcon = document.getElementById('eyeIcon');
const submitBtn = document.getElementById('submitBtn');
const btnText = document.getElementById('btnText');
const btnLoader = document.getElementById('btnLoader');
const btnArrow = submitBtn.querySelector('.btn-arrow');
const alertBanner = document.getElementById('alertBanner');
const alertIcon = document.getElementById('alertIcon');
const alertMsg = document.getElementById('alertMsg');
const emailError = document.getElementById('emailError');
const passwordError = document.getElementById('passwordError');
const groupEmail = document.getElementById('groupEmail');
const groupPassword = document.getElementById('groupPassword');
const rememberMe = document.getElementById('rememberMe');

/* ── State ─────────────────────────────────────────────── */
let selectedRole = 'DONOR';
let isSubmitting = false;

/* ── Animated Background ───────────────────────────────── */
(function createBackground() {
  // Floating particles
  for (let i = 0; i < 14; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    const size = 60 + Math.random() * 120;
    p.style.cssText = `
      width:${size}px; height:${size}px;
      left:${Math.random() * 100}%;
      top:${Math.random() * 100}%;
      --dur:${10 + Math.random() * 14}s;
      --delay:${-Math.random() * 12}s;
      --opacity:${0.15 + Math.random() * 0.3};
    `;
    bgParticles.appendChild(p);
  }

  // Floating blood drop SVGs
  const dropSVG = (size, x, y, dur, delay) => {
    const el = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    el.setAttribute('viewBox', '0 0 60 80');
    el.setAttribute('width', size);
    el.setAttribute('height', size * 1.33);
    el.classList.add('drop-float');
    el.style.cssText = `position:absolute;left:${x}%;top:${y}%;--dur:${dur}s;--delay:${delay}s;`;
    el.innerHTML = `<path d="M30 2 C30 2 4 32 4 50 C4 65.46 15.54 77 30 77 C44.46 77 56 65.46 56 50 C56 32 30 2 30 2Z" fill="#E53935"/>`;
    floatingDrops.appendChild(el);
  };

  const drops = [
    [90, 5, 15, 20, 0],
    [50, 92, 60, 25, -5],
    [70, 12, 75, 18, -3],
    [40, 80, 10, 22, -8],
    [110, 50, 40, 30, -2],
    [60, 30, 85, 17, -6],
  ];

  drops.forEach(([sz, x, y, dur, delay]) => dropSVG(sz, x, y, dur, delay));
})();

/* ── Role Switching Helper ─────────────────────────────── */
function setRole(role) {
  selectedRole = role;
  roleTabs.forEach(t => {
    const isCurrent = t.dataset.role === role;
    t.classList.toggle('active', isCurrent);
    t.setAttribute('aria-pressed', isCurrent ? 'true' : 'false');
  });
}

/* ── Role Tab Selection ────────────────────────────────── */
roleTabs.forEach(tab => {
  tab.addEventListener('click', () => {
    setRole(tab.dataset.role);

    // Animate the tab
    tab.style.transform = 'scale(0.95)';
    requestAnimationFrame(() => {
      tab.style.transform = '';
      tab.style.transition = 'transform 0.15s ease';
    });
  });
});

/* ── Check URL Parameters (e.g. ?role=seeker&emergency=1) ─ */
(function checkUrlParams() {
  const urlParams = new URLSearchParams(window.location.search);
  const roleParam = (urlParams.get('role') || '').toUpperCase();
  const isEmergency = urlParams.get('emergency') === '1' || urlParams.get('emergency') === 'true' || urlParams.get('urgent') === '1';

  if (roleParam === 'SEEKER' || isEmergency) {
    setRole('SEEKER');
  } else if (roleParam === 'ADMIN' || roleParam === 'SUPERADMIN') {
    setRole('SUPERADMIN');
  } else if (roleParam === 'DONOR') {
    setRole('DONOR');
  }

  // If emergency request mode, display emergency alert banner and update register link
  if (isEmergency) {
    const emergencyAlertBanner = document.getElementById('emergencyAlertBanner');
    if (emergencyAlertBanner) {
      emergencyAlertBanner.hidden = false;
    }
    const registerLink = document.getElementById('registerLink');
    if (registerLink) {
      registerLink.href = 'register.html?role=seeker&emergency=1';
    }
  }
})();

/* ── Password Visibility Toggle ────────────────────────── */
const EYE_OPEN = `
  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
  <circle cx="12" cy="12" r="3"/>
`;
const EYE_CLOSED = `
  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
  <line x1="1" y1="1" x2="23" y2="23"/>
`;

togglePwdBtn.addEventListener('click', () => {
  const isHidden = passwordInput.type === 'password';
  passwordInput.type = isHidden ? 'text' : 'password';
  eyeIcon.innerHTML = isHidden ? EYE_CLOSED : EYE_OPEN;
  togglePwdBtn.setAttribute('aria-label', isHidden ? 'Hide password' : 'Show password');
});

/* ── Validation Helpers ────────────────────────────────── */
function validateEmail(value) {
  if (!value.trim()) return 'Email address is required.';
  const isEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
  const isPhone = /^\+?[0-9]{7,15}$/.test(value);
  if (!isEmail && !isPhone) return 'Enter a valid email address or mobile number.';
  return '';
}

function validatePassword(value) {
  if (!value) return 'Password is required.';
  if (value.length < 6) return 'Password must be at least 6 characters.';
  return '';
}

function setFieldError(groupEl, errorEl, inputEl, msg) {
  errorEl.textContent = msg;
  if (msg) {
    groupEl.classList.add('has-error');
    inputEl.setAttribute('aria-invalid', 'true');
  } else {
    groupEl.classList.remove('has-error');
    inputEl.removeAttribute('aria-invalid');
  }
}

function clearFieldErrors() {
  setFieldError(groupEmail, emailError, emailInput, '');
  setFieldError(groupPassword, passwordError, passwordInput, '');
  hideAlert();
}

/* ── Alert Banner ─────────────────────────────────────── */
function showAlert(type, msg) {
  alertBanner.hidden = false;
  alertBanner.className = `alert-banner ${type}`;
  alertIcon.textContent = type === 'error' ? '⚠️' : '✅';
  alertMsg.textContent = msg;
}

function hideAlert() {
  alertBanner.hidden = true;
  alertBanner.className = 'alert-banner';
}

/* ── Loading State ─────────────────────────────────────── */
function setLoading(loading) {
  isSubmitting = loading;
  submitBtn.disabled = loading;
  btnText.hidden = loading;
  btnArrow.hidden = loading;
  btnLoader.hidden = !loading;
}

/* ── Form Submit ───────────────────────────────────────── */
loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  if (isSubmitting) return;

  clearFieldErrors();

  const email = emailInput.value.trim();
  const password = passwordInput.value;

  const emailErr = validateEmail(email);
  const passErr = validatePassword(password);

  if (emailErr) setFieldError(groupEmail, emailError, emailInput, emailErr);
  if (passErr) setFieldError(groupPassword, passwordError, passwordInput, passErr);

  if (emailErr || passErr) return;

  setLoading(true);

  try {
    const payload = {
      email,
      password,
      role: selectedRole,
    };

    // ── API Call (FastAPI backend) ──
    const API_BASE = (window.location.port === '8000' && window.location.protocol !== 'file:') ? '' : 'http://localhost:8000';
    const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      let message = 'Invalid credentials. Please try again.';
      if (typeof data?.detail === 'string') {
        message = data.detail;
      } else if (Array.isArray(data?.detail)) {
        message = data.detail.map(d => d.msg || d.message || JSON.stringify(d)).join('; ');
      } else if (data?.message) {
        message = data.message;
      }
      showAlert('error', message);
      setLoading(false);
      return;
    }

    // Store JWT token
    const storage = rememberMe.checked ? localStorage : sessionStorage;
    storage.setItem('bloodreach_access_token', data.access_token);
    storage.setItem('bloodreach_user_role', data.role || selectedRole);
    storage.setItem('bloodreach_user_name', data.full_name || data.name || '');

    showAlert('success', `Welcome back! Redirecting to your dashboard...`);

    // Redirect after short delay
    setTimeout(() => {
      const dashboardMap = {
        DONOR: 'dashboard-donor.html',
        SEEKER: 'dashboard-seeker.html',
        HOSPITAL_ADMIN: 'dashboard-hospital.html',
        SUPERADMIN: 'dashboard-admin.html',
      };
      const isEmergency = new URLSearchParams(window.location.search).get('emergency') === '1'
        || new URLSearchParams(window.location.search).get('emergency') === 'true'
        || new URLSearchParams(window.location.search).get('urgent') === '1';

      const userRole = data.role || selectedRole;
      if (userRole === 'SEEKER' && isEmergency) {
        window.location.href = 'dashboard-seeker.html?emergency=1';
      } else {
        window.location.href = dashboardMap[userRole] || 'index.html';
      }
    }, 1400);

  } catch (err) {
    // Network / server unreachable — always reset loading state
    const isNetworkError = err instanceof TypeError;
    if (isNetworkError) {
      showAlert('error', 'Cannot connect to server. Please ensure the backend is running on port 8000.');
    } else {
      showAlert('error', 'An unexpected error occurred. Please try again.');
    }
    setLoading(false); // ✅ সবসময় loading বন্ধ হবে
  }
});

/* ── Real-time Field Validation (on blur) ─────────────── */
emailInput.addEventListener('blur', () => {
  const err = validateEmail(emailInput.value);
  setFieldError(groupEmail, emailError, emailInput, err);
});

passwordInput.addEventListener('blur', () => {
  const err = validatePassword(passwordInput.value);
  setFieldError(groupPassword, passwordError, passwordInput, err);
});

emailInput.addEventListener('input', () => {
  if (groupEmail.classList.contains('has-error') && validateEmail(emailInput.value) === '') {
    setFieldError(groupEmail, emailError, emailInput, '');
  }
});

passwordInput.addEventListener('input', () => {
  if (groupPassword.classList.contains('has-error') && validatePassword(passwordInput.value) === '') {
    setFieldError(groupPassword, passwordError, passwordInput, '');
  }
});

/* ── Pre-fill from Storage (Remember Me) ──────────────── */
(function prefill() {
  const storedEmail = localStorage.getItem('bloodreach_remembered_email');
  if (storedEmail) {
    emailInput.value = storedEmail;
    rememberMe.checked = true;
  }
})();

rememberMe.addEventListener('change', () => {
  if (rememberMe.checked && emailInput.value.trim()) {
    localStorage.setItem('bloodreach_remembered_email', emailInput.value.trim());
  } else {
    localStorage.removeItem('bloodreach_remembered_email');
  }
});

/* ── Already Logged In? Redirect ──────────────────────── */
(function checkExistingSession() {
  const token = localStorage.getItem('bloodreach_access_token')
    || sessionStorage.getItem('bloodreach_access_token');
  const role = localStorage.getItem('bloodreach_user_role')
    || sessionStorage.getItem('bloodreach_user_role');

  if (token && role) {
    const dashboardMap = {
      DONOR: 'dashboard-donor.html',
      SEEKER: 'dashboard-seeker.html',
      HOSPITAL_ADMIN: 'dashboard-hospital.html',
      SUPERADMIN: 'dashboard-admin.html',
    };
    // Silently redirect if a valid session exists
    // window.location.href = dashboardMap[role] || 'index.html';
    // NOTE: Commented out to allow testing the login page directly.
    // Uncomment when backend is connected.
  }
})();

/* ── Keyboard Shortcut: Enter on Role Tab ────────────── */
roleTabs.forEach(tab => {
  tab.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      tab.click();
    }
  });
});

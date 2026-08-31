/**
 * Blood Reach BD — Login Page JavaScript
 * Handles: role selection, authentication form validation, FastAPI login endpoint integration,
 *           fast timeout resolution, and instant Demo session fallback on Vercel & offline.
 */

'use strict';

/* ── Dynamic API Base (Auto-detects localhost, LAN/WiFi IP, or Vercel serverless API) ── */
function getApiBase() {
  if (typeof window === 'undefined') return '';
  if (window.API_BASE !== undefined && window.API_BASE !== null) return window.API_BASE;
  if (window.location.protocol === 'file:') return 'http://localhost:8000';
  const hostname = window.location.hostname || 'localhost';
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return window.location.port === '8000' ? '' : 'http://localhost:8000';
  }
  // On Vercel / Cloud deployments, serverless API endpoints are served directly on the same domain
  return '';
}

/* ── DOM References ────────────────────────────────────── */
const bgParticles = document.getElementById('bgParticles');
const floatingDrops = document.getElementById('floatingDrops');
const roleTabs = document.querySelectorAll('.role-tab');
const loginForm = document.getElementById('loginForm');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const togglePwdBtn = document.getElementById('togglePassword');
const eyeIcon = document.getElementById('passwordEyeIcon');
const rememberMe = document.getElementById('rememberMe');
const submitBtn = document.getElementById('submitBtn');
const btnText = document.getElementById('btnText');
const btnLoader = document.getElementById('btnLoader');
const btnArrow = submitBtn ? submitBtn.querySelector('.btn-arrow') : null;
const alertBanner = document.getElementById('alertBanner');
const alertIcon = document.getElementById('alertIcon');
const alertMsg = document.getElementById('alertMsg');
const emailError = document.getElementById('emailError');
const passwordError = document.getElementById('passwordError');
const groupEmail = document.getElementById('groupEmail');
const groupPassword = document.getElementById('groupPassword');

/* ── State ─────────────────────────────────────────────── */
let selectedRole = 'DONOR';
let isSubmitting = false;

/* ── Animated Background ───────────────────────────────── */
(function createBackground() {
  if (bgParticles) {
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
  }

  if (floatingDrops) {
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
  }
})();

/* ── Role Switching Helper ─────────────────────────────── */
function setRole(role) {
  let normalized = (role || 'DONOR').toUpperCase();
  if (normalized === 'ADMIN') normalized = 'SUPERADMIN';
  if (normalized === 'HOSPITAL') normalized = 'HOSPITAL_ADMIN';

  selectedRole = normalized;
  roleTabs.forEach(t => {
    const tabRole = (t.dataset.role || '').toUpperCase();
    const isCurrent = tabRole === normalized || (tabRole === 'SUPERADMIN' && normalized === 'ADMIN') || (tabRole === 'HOSPITAL_ADMIN' && normalized === 'HOSPITAL');
    t.classList.toggle('active', isCurrent);
    t.setAttribute('aria-pressed', isCurrent ? 'true' : 'false');
  });

  const emergencyBanner = document.getElementById('emergencyAlertBanner');
  const titleEl = document.getElementById('formTitle');
  if (normalized !== 'SEEKER') {
    if (emergencyBanner) emergencyBanner.hidden = true;
    if (titleEl) titleEl.textContent = 'Welcome Back';
  }

  const roleDescMap = {
    DONOR: 'Access donor requests, update availability status, and track donation impact.',
    SEEKER: 'Post urgent blood requests, track nearby matches, and connect with donors.',
    HOSPITAL_ADMIN: 'Manage hospital blood stock inventory and emergency hospital requests.',
    SUPERADMIN: 'Platform verification, dispute resolution, and national blood network overview.'
  };

  const roleDescEl = document.getElementById('roleDesc');
  if (roleDescEl && roleDescMap[selectedRole]) {
    roleDescEl.textContent = roleDescMap[selectedRole];
  }
}

/* ── Role Tab Selection ────────────────────────────────── */
roleTabs.forEach(tab => {
  tab.addEventListener('click', () => {
    setRole(tab.dataset.role);

    // Animate tab
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
  } else if (roleParam === 'HOSPITAL' || roleParam === 'HOSPITAL_ADMIN') {
    setRole('HOSPITAL_ADMIN');
  } else if (roleParam === 'ADMIN' || roleParam === 'SUPERADMIN') {
    setRole('SUPERADMIN');
  } else if (roleParam === 'DONOR') {
    setRole('DONOR');
  }

  if (isEmergency) {
    const emergencyBanner = document.getElementById('emergencyAlertBanner');
    if (emergencyBanner) emergencyBanner.hidden = false;
    const titleEl = document.getElementById('formTitle');
    if (titleEl) titleEl.innerHTML = '🚨 Emergency Seeker Login';
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

if (togglePwdBtn && passwordInput && eyeIcon) {
  togglePwdBtn.addEventListener('click', () => {
    const isHidden = passwordInput.type === 'password';
    passwordInput.type = isHidden ? 'text' : 'password';
    eyeIcon.innerHTML = isHidden ? EYE_CLOSED : EYE_OPEN;
    togglePwdBtn.setAttribute('aria-label', isHidden ? 'Hide password' : 'Show password');
  });
}

/* ── Validation Helpers ────────────────────────────────── */
function validateEmail(value) {
  if (!value || !value.trim()) return 'Email address or Mobile number is required.';
  const isEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
  const isPhone = /^\+?[0-9]{7,15}$/.test(value.replace(/[\s\-\(\)]/g, ''));
  if (!isEmail && !isPhone) return 'Enter a valid email address or mobile number.';
  return '';
}

function validatePassword(value) {
  if (!value) return 'Password is required.';
  if (value.length < 4) return 'Password must be at least 4 characters.';
  return '';
}

function setFieldError(groupEl, errorEl, inputEl, msg) {
  if (!groupEl || !errorEl || !inputEl) return;
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
  if (!alertBanner) return;
  alertBanner.hidden = false;
  alertBanner.className = `alert-banner ${type}`;
  if (alertIcon) alertIcon.textContent = type === 'error' ? '⚠️' : '✅';
  if (alertMsg) alertMsg.textContent = msg;
}

function hideAlert() {
  if (!alertBanner) return;
  alertBanner.hidden = true;
  alertBanner.className = 'alert-banner';
}

/* ── Loading State ─────────────────────────────────────── */
function setLoading(loading) {
  isSubmitting = loading;
  if (submitBtn) submitBtn.disabled = loading;
  if (btnText) btnText.hidden = loading;
  if (btnArrow) btnArrow.hidden = loading;
  if (btnLoader) btnLoader.hidden = !loading;
}

/* ── Helper: Authenticate & Save Session ───────────────── */
async function authenticateAndSaveSession(identifier, role, password, serverToken) {
  if (window.CloudSync && typeof window.CloudSync.fetchCloudData === 'function') {
    await window.CloudSync.fetchCloudData();
  }

  // The role chosen on the login screen must strictly take precedence
  const effectiveRole = (role || selectedRole || 'DONOR').toUpperCase();

  let matchedUser = null;
  try {
    const usersList = JSON.parse(localStorage.getItem('bloodreach_users_db') || '[]');
    const cleanId = identifier.replace(/[\s\-\(\)]/g, '').toLowerCase();
    matchedUser = usersList.find(u => 
      (u.email && u.email.toLowerCase() === cleanId) ||
      (u.phone && u.phone.replace(/[\s\-\(\)]/g, '') === cleanId)
    );
  } catch (e) {}

  const activeUser = matchedUser ? { ...matchedUser } : {
    id: 'usr_' + Date.now(),
    full_name: identifier.includes('@') ? identifier.split('@')[0] : identifier,
    name: identifier.includes('@') ? identifier.split('@')[0] : identifier,
    phone: identifier.startsWith('01') ? identifier : '',
    email: identifier.includes('@') ? identifier : `${identifier}@bloodreach.local`,
    district: 'Dhaka',
    division: 'Dhaka',
    blood_group: 'O+'
  };

  activeUser.role = effectiveRole;

  if (effectiveRole === 'DONOR') {
    if (!activeUser.donor_profile) {
      activeUser.donor_profile = {
        blood_group: activeUser.blood_group || 'O+',
        is_available: true,
        district: typeof activeUser.district === 'object' ? activeUser.district?.name : (activeUser.district || 'Dhaka'),
        division: typeof activeUser.division === 'object' ? activeUser.division?.name : (activeUser.division || 'Dhaka'),
        total_donations: 0
      };
    }
  }

  // Save/update in local users registry
  try {
    const usersList = JSON.parse(localStorage.getItem('bloodreach_users_db') || '[]');
    const cleanId = identifier.replace(/[\s\-\(\)]/g, '').toLowerCase();
    const idx = usersList.findIndex(u => 
      (u.email && u.email.toLowerCase() === cleanId) ||
      (u.phone && u.phone.replace(/[\s\-\(\)]/g, '') === cleanId)
    );
    if (idx >= 0) {
      usersList[idx] = { ...usersList[idx], ...activeUser };
    } else {
      usersList.push(activeUser);
    }
    localStorage.setItem('bloodreach_users_db', JSON.stringify(usersList));
  } catch (e) {}

  const storage = rememberMe && rememberMe.checked ? localStorage : sessionStorage;
  storage.setItem('bloodreach_access_token', serverToken || ('token_' + Date.now()));
  storage.setItem('bloodreach_user_role', effectiveRole);
  storage.setItem('bloodreach_user_name', activeUser.full_name || activeUser.name);
  storage.setItem('bloodreach_user_phone', activeUser.phone || '');
  storage.setItem('bloodreach_user_email', activeUser.email || '');
  if (activeUser.district) storage.setItem('bloodreach_user_district', typeof activeUser.district === 'object' ? activeUser.district.name : activeUser.district);
  if (activeUser.division) storage.setItem('bloodreach_user_division', typeof activeUser.division === 'object' ? activeUser.division.name : activeUser.division);
  if (activeUser.blood_group) storage.setItem('bloodreach_user_blood_group', activeUser.blood_group);
  storage.setItem('bloodreach_current_user', JSON.stringify(activeUser));

  if (window.CloudSync && typeof window.CloudSync.saveUser === 'function') {
    window.CloudSync.saveUser(activeUser);
  }

  showAlert('success', `Welcome back, ${activeUser.full_name || activeUser.name}! Redirecting to ${effectiveRole} Dashboard...`);

  setTimeout(() => {
    const dashboardMap = {
      DONOR: 'dashboard-donor.html',
      SEEKER: 'dashboard-seeker.html',
      HOSPITAL_ADMIN: 'dashboard-hospital.html',
      HOSPITAL: 'dashboard-hospital.html',
      SUPERADMIN: 'dashboard-admin.html',
      ADMIN: 'dashboard-admin.html',
    };

    const targetUrl = dashboardMap[effectiveRole] || (effectiveRole === 'DONOR' ? 'dashboard-donor.html' : 'dashboard-seeker.html');
    window.location.href = targetUrl;
  }, 600);
}

/* ── Form Submit ───────────────────────────────────────── */
if (loginForm) {
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (isSubmitting) return;

    clearFieldErrors();

    const email = emailInput ? emailInput.value.trim() : '';
    const password = passwordInput ? passwordInput.value : '';

    const emailErr = validateEmail(email);
    const passErr = validatePassword(password);

    if (emailErr) setFieldError(groupEmail, emailError, emailInput, emailErr);
    if (passErr) setFieldError(groupPassword, passwordError, passwordInput, passErr);

    if (emailErr || passErr) return;

    setLoading(true);

    const API_BASE = getApiBase();

    if (!API_BASE) {
      authenticateAndSaveSession(email, selectedRole, password);
      return;
    }

    try {
      const payload = {
        email,
        password,
        role: selectedRole,
      };

      // Abort controller to prevent infinite spinner if backend is unresponsive
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);

      const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: controller.signal
      });

      clearTimeout(timeoutId);
      const data = await response.json();

      if (!response.ok) {
        let message = 'Invalid credentials. Please check your username and password.';
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

      authenticateAndSaveSession(email, data.role || selectedRole, password, data.access_token);

    } catch (err) {
      authenticateAndSaveSession(email, selectedRole, password);
    }
  });
}

/* ── Real-time Field Validation (on blur) ─────────────── */
if (emailInput) {
  emailInput.addEventListener('blur', () => {
    const err = validateEmail(emailInput.value);
    setFieldError(groupEmail, emailError, emailInput, err);
  });
}

/**
 * Blood Reach BD — Registration Page JavaScript
 * Handles: role selection, 64-district dynamic location selector, form validation,
 *           phone & email normalization, and resilient FastAPI submit flow.
 */

'use strict';

/* ── Dynamic API Base (Auto-detects localhost, LAN/WiFi IP, or relative port) ── */
function getApiBase() {
  if (typeof window === 'undefined') return 'http://localhost:8000';
  if (window.location.protocol === 'file:') return 'http://localhost:8000';
  if (window.location.port === '8000') return '';
  const protocol = window.location.protocol || 'http:';
  const hostname = window.location.hostname || 'localhost';
  return `${protocol}//${hostname}:8000`;
}

/* ── Location Data (8 Divisions & 64 Districts) ──────── */
const locationData = {
  "Dhaka": ["Dhaka", "Faridpur", "Gazipur", "Gopalganj", "Kishoreganj", "Madaripur", "Manikganj", "Munshiganj", "Narayanganj", "Narsingdi", "Rajbari", "Shariatpur", "Tangail"],
  "Chattogram": ["Bandarban", "Brahmanbaria", "Chandpur", "Chattogram", "Comilla", "Cox's Bazar", "Feni", "Khagrachhari", "Lakshmipur", "Noakhali", "Rangamati"],
  "Rajshahi": ["Bogura", "Chapainawabganj", "Joypurhat", "Naogaon", "Natore", "Pabna", "Rajshahi", "Sirajganj"],
  "Khulna": ["Bagerhat", "Chuadanga", "Jashore", "Jhenaidah", "Khulna", "Kushtia", "Magura", "Meherpur", "Narail", "Satkhira"],
  "Barishal": ["Barguna", "Barishal", "Bhola", "Jhalokati", "Patuakhali", "Pirojpur"],
  "Sylhet": ["Habiganj", "Moulvibazar", "Sunamganj", "Sylhet"],
  "Rangpur": ["Dinajpur", "Gaibandha", "Kurigram", "Lalmonirhat", "Nilphamari", "Panchagarh", "Rangpur", "Thakurgaon"],
  "Mymensingh": ["Jamalpur", "Mymensingh", "Netrokona", "Sherpur"]
};

/* ── DOM References ────────────────────────────────────── */
const bgParticles = document.getElementById('bgParticles');
const floatingDrops = document.getElementById('floatingDrops');
const roleTabs = document.querySelectorAll('.role-tab');
const registerForm = document.getElementById('registerForm');
const nameInput = document.getElementById('name');
const phoneInput = document.getElementById('phone');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const confirmPwdInput = document.getElementById('confirmPassword');
const togglePasswordBtn = document.getElementById('togglePassword');
const toggleConfirmPasswordBtn = document.getElementById('toggleConfirmPassword');
const passwordEyeIcon = document.getElementById('passwordEyeIcon');
const confirmPasswordEyeIcon = document.getElementById('confirmPasswordEyeIcon');
const bloodGroupSelect = document.getElementById('bloodGroup');
const divisionSelect = document.getElementById('division');
const districtSelect = document.getElementById('district');
const donorDetailsPanel = document.getElementById('donorDetailsPanel');
const submitBtn = document.getElementById('submitBtn');
const btnText = document.getElementById('btnText');
const btnLoader = document.getElementById('btnLoader');
const btnArrow = submitBtn ? submitBtn.querySelector('.btn-arrow') : null;
const alertBanner = document.getElementById('alertBanner');
const alertIcon = document.getElementById('alertIcon');
const alertMsg = document.getElementById('alertMsg');

const nameError = document.getElementById('nameError');
const phoneError = document.getElementById('phoneError');
const emailError = document.getElementById('emailError');
const passwordError = document.getElementById('passwordError');
const confirmPasswordError = document.getElementById('confirmPasswordError');
const bloodGroupError = document.getElementById('bloodGroupError');
const divisionError = document.getElementById('divisionError');
const districtError = document.getElementById('districtError');

const groupName = document.getElementById('groupName');
const groupPhone = document.getElementById('groupPhone');
const groupEmail = document.getElementById('groupEmail');
const groupPassword = document.getElementById('groupPassword');
const groupConfirmPassword = document.getElementById('groupConfirmPassword');
const groupBloodGroup = document.getElementById('groupBloodGroup');
const groupDivision = document.getElementById('groupDivision');
const groupDistrict = document.getElementById('groupDistrict');

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

/* ── Location Dropdown Helpers ─────────────────────────── */
function initLocationDropdowns() {
  if (!divisionSelect || !districtSelect) return;

  // Populate divisions
  divisionSelect.innerHTML = '<option value="">Select Division</option>';
  Object.keys(locationData).sort().forEach(div => {
    const opt = document.createElement('option');
    opt.value = div;
    opt.textContent = div;
    divisionSelect.appendChild(opt);
  });

  // Handle division select change
  divisionSelect.addEventListener('change', () => {
    const div = divisionSelect.value;
    if (!div) {
      districtSelect.innerHTML = '<option value="">Select Division first</option>';
      districtSelect.disabled = true;
      return;
    }

    districtSelect.innerHTML = '<option value="">Select District</option>';
    const districts = locationData[div] || [];
    [...districts].sort().forEach(dist => {
      const opt = document.createElement('option');
      opt.value = dist;
      opt.textContent = dist;
      districtSelect.appendChild(opt);
    });
    districtSelect.disabled = false;
  });
}
initLocationDropdowns();

/* ── Password Visibility Toggle ────────────────────────── */
const EYE_OPEN = `
  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
  <circle cx="12" cy="12" r="3"/>
`;
const EYE_CLOSED = `
  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
  <line x1="1" y1="1" x2="23" y2="23"/>
`;

function setupPasswordToggle(input, button, icon) {
  if (!input || !button || !icon) return;
  button.addEventListener('click', () => {
    const isHidden = input.type === 'password';
    input.type = isHidden ? 'text' : 'password';
    icon.innerHTML = isHidden ? EYE_CLOSED : EYE_OPEN;
    button.setAttribute('aria-label', isHidden ? 'Hide password' : 'Show password');
  });
}

setupPasswordToggle(passwordInput, togglePasswordBtn, passwordEyeIcon);
setupPasswordToggle(confirmPwdInput, toggleConfirmPasswordBtn, confirmPasswordEyeIcon);

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

  const roleBenefitIcon = document.getElementById('roleBenefitIcon');
  const roleBenefitText = document.getElementById('roleBenefitText');

  // Show/hide donor fields panel and update benefit description
  if (selectedRole === 'DONOR') {
    if (donorDetailsPanel) donorDetailsPanel.style.display = 'block';
    if (roleBenefitIcon) roleBenefitIcon.textContent = '🩸';
    if (roleBenefitText) roleBenefitText.textContent = 'Register as a voluntary donor to save lives in your district and receive urgent blood alerts.';
  } else if (selectedRole === 'SEEKER') {
    if (donorDetailsPanel) donorDetailsPanel.style.display = 'none';
    clearDonorErrors();
    if (roleBenefitIcon) roleBenefitIcon.textContent = '🔍';
    if (roleBenefitText) roleBenefitText.textContent = 'Register as a seeker to create urgent blood requests and find matching donors nearby instantly.';
  } else if (selectedRole === 'HOSPITAL_ADMIN' || selectedRole === 'HOSPITAL') {
    if (donorDetailsPanel) donorDetailsPanel.style.display = 'none';
    clearDonorErrors();
    if (roleBenefitIcon) roleBenefitIcon.textContent = '🏥';
    if (roleBenefitText) roleBenefitText.textContent = 'Register hospital administration account to manage blood stock inventory and emergency transfusions.';
  } else {
    if (donorDetailsPanel) donorDetailsPanel.style.display = 'none';
    clearDonorErrors();
    if (roleBenefitIcon) roleBenefitIcon.textContent = '🛡️';
    if (roleBenefitText) roleBenefitText.textContent = 'Register administrative account to verify emergency requests and oversee platform operations.';
  }
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
  } else if (roleParam === 'HOSPITAL' || roleParam === 'HOSPITAL_ADMIN') {
    setRole('HOSPITAL_ADMIN');
  } else if (roleParam === 'ADMIN' || roleParam === 'SUPERADMIN') {
    setRole('SUPERADMIN');
  } else if (roleParam === 'DONOR') {
    setRole('DONOR');
  }

  // If emergency request mode, display emergency alert banner and update titles
  if (isEmergency) {
    const emergencyAlertBanner = document.getElementById('emergencyAlertBanner');
    if (emergencyAlertBanner) {
      emergencyAlertBanner.hidden = false;
    }
    const formTitle = document.getElementById('formTitle');
    if (formTitle) {
      formTitle.innerHTML = '🚨 Emergency Seeker Sign Up';
    }
    const cardSubtitle = document.querySelector('.card-subtitle');
    if (cardSubtitle) {
      cardSubtitle.textContent = 'Create seeker account to immediately post urgent blood request';
    }
    if (btnText) {
      btnText.textContent = 'Sign Up & Request Blood';
    }
    const loginLink = document.getElementById('loginLink');
    if (loginLink) {
      loginLink.href = 'login.html?role=seeker&emergency=1';
    }
  }
})();

/* ── Validation Helpers ────────────────────────────────── */
function sanitizePhone(value) {
  return (value || '').replace(/[\s\-\(\)]/g, '');
}

function validateName(value) {
  if (!value.trim()) return 'Full name is required.';
  if (value.trim().length < 2) return 'Name must be at least 2 characters.';
  return '';
}

function validateEmail(value) {
  if (!value || !value.trim()) return ''; // Optional
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim())) return 'Please enter a valid email address.';
  return '';
}

function validatePhone(value) {
  const clean = sanitizePhone(value);
  if (!clean) return 'Mobile number is required.';
  if (!/^\+?[0-9]{7,15}$/.test(clean)) return 'Enter a valid mobile number (e.g. 01711223344).';
  return '';
}

function validatePassword(value) {
  if (!value) return 'Password is required.';
  if (value.length < 6) return 'Password must be at least 6 characters.';
  return '';
}

function validateConfirmPassword(value, password) {
  if (!value) return 'Confirm password is required.';
  if (value !== password) return 'Passwords do not match.';
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

function clearDonorErrors() {
  setFieldError(groupBloodGroup, bloodGroupError, bloodGroupSelect, '');
  setFieldError(groupDivision, divisionError, divisionSelect, '');
  setFieldError(groupDistrict, districtError, districtSelect, '');
}

function clearFieldErrors() {
  setFieldError(groupName, nameError, nameInput, '');
  setFieldError(groupPhone, phoneError, phoneInput, '');
  setFieldError(groupEmail, emailError, emailInput, '');
  setFieldError(groupPassword, passwordError, passwordInput, '');
  setFieldError(groupConfirmPassword, confirmPasswordError, confirmPwdInput, '');
  clearDonorErrors();
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

/* ── Form Submit ───────────────────────────────────────── */
if (registerForm) {
  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (isSubmitting) return;

    clearFieldErrors();

    const name = nameInput ? nameInput.value.trim() : '';
    const rawPhone = phoneInput ? phoneInput.value.trim() : '';
    const phone = sanitizePhone(rawPhone);
    const email = emailInput ? emailInput.value.trim() : '';
    const password = passwordInput ? passwordInput.value : '';
    const confirmPassword = confirmPwdInput ? confirmPwdInput.value : '';

    // Validation
    const nameErr = validateName(name);
    const phoneErr = validatePhone(phone);
    const emailErr = validateEmail(email);
    const passErr = validatePassword(password);
    const confPassErr = validateConfirmPassword(confirmPassword, password);

    let bloodGroupErr = '';
    let divisionErr = '';
    let districtErr = '';

    if (selectedRole === 'DONOR') {
      if (!bloodGroupSelect || !bloodGroupSelect.value) bloodGroupErr = 'Blood group is required for donors.';
      if (!divisionSelect || !divisionSelect.value) divisionErr = 'Division is required for donors.';
      if (!districtSelect || !districtSelect.value) districtErr = 'District is required for donors.';
    }

    // Display errors if any
    if (nameErr) setFieldError(groupName, nameError, nameInput, nameErr);
    if (phoneErr) setFieldError(groupPhone, phoneError, phoneInput, phoneErr);
    if (emailErr) setFieldError(groupEmail, emailError, emailInput, emailErr);
    if (passErr) setFieldError(groupPassword, passwordError, passwordInput, passErr);
    if (confPassErr) setFieldError(groupConfirmPassword, confirmPasswordError, confirmPwdInput, confPassErr);

    if (selectedRole === 'DONOR') {
      if (bloodGroupErr) setFieldError(groupBloodGroup, bloodGroupError, bloodGroupSelect, bloodGroupErr);
      if (divisionErr) setFieldError(groupDivision, divisionError, divisionSelect, divisionErr);
      if (districtErr) setFieldError(groupDistrict, districtError, districtSelect, districtErr);
    }

    if (nameErr || phoneErr || emailErr || passErr || confPassErr || bloodGroupErr || divisionErr || districtErr) {
      return;
    }

    setLoading(true);

    try {
      const payload = {
        full_name: name,
        name: name,
        phone: phone,
        email: email || `${phone}@bloodreach.local`,
        password: password,
        role: selectedRole,
        blood_group: selectedRole === 'DONOR' ? bloodGroupSelect.value : null,
        division: selectedRole === 'DONOR' ? divisionSelect.value : null,
        district: selectedRole === 'DONOR' ? districtSelect.value : null
      };

      // ── API Call to FastAPI Registration Endpoint ──
      const API_BASE = getApiBase();
      const response = await fetch(`${API_BASE}/api/v1/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (!response.ok) {
        let message = 'Registration failed. Please try again.';
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

      // If access token returned, auto log the user in
      if (data.access_token) {
        localStorage.setItem('bloodreach_access_token', data.access_token);
        localStorage.setItem('bloodreach_user_role', data.role || selectedRole);
        localStorage.setItem('bloodreach_user_name', data.full_name || data.name || name);
        if (selectedRole === 'DONOR' && districtSelect && districtSelect.value) {
          localStorage.setItem('bloodreach_user_district', districtSelect.value);
        }
      }

      const isEmergency = new URLSearchParams(window.location.search).get('emergency') === '1'
        || new URLSearchParams(window.location.search).get('emergency') === 'true'
        || new URLSearchParams(window.location.search).get('urgent') === '1';

      if (selectedRole === 'SEEKER') {
        showAlert('success', 'Account created successfully! Redirecting to Seeker Request Console...');
        setTimeout(() => {
          window.location.href = isEmergency ? 'dashboard-seeker.html?emergency=1' : 'dashboard-seeker.html';
        }, 1200);
      } else if (selectedRole === 'DONOR') {
        showAlert('success', 'Donor account created successfully! Redirecting to Donor Console...');
        setTimeout(() => {
          window.location.href = 'dashboard-donor.html';
        }, 1200);
      } else if (selectedRole === 'HOSPITAL_ADMIN' || selectedRole === 'HOSPITAL') {
        showAlert('success', 'Hospital account created successfully! Redirecting to Hospital Portal...');
        setTimeout(() => {
          window.location.href = 'dashboard-hospital.html';
        }, 1200);
      } else {
        showAlert('success', 'Admin account created successfully! Redirecting to Admin Console...');
        setTimeout(() => {
          window.location.href = 'dashboard-admin.html';
        }, 1200);
      }

    } catch (err) {
      // If network / server is offline (e.g. static preview on Vercel or localhost before backend start)
      const isNetworkError = err instanceof TypeError || !navigator.onLine || (err.message && err.message.includes('fetch'));
      if (isNetworkError) {
        // Fallback demo session so offline or static preview works seamlessly
        localStorage.setItem('bloodreach_access_token', 'demo-token-' + Date.now());
        localStorage.setItem('bloodreach_user_role', selectedRole);
        localStorage.setItem('bloodreach_user_name', name);
        if (selectedRole === 'DONOR' && districtSelect && districtSelect.value) {
          localStorage.setItem('bloodreach_user_district', districtSelect.value);
        }

        showAlert('success', `⚡ Demo Mode: Account created locally! Redirecting to ${selectedRole} dashboard...`);
        setTimeout(() => {
          const dashboardMap = {
            DONOR: 'dashboard-donor.html',
            SEEKER: (new URLSearchParams(window.location.search).get('emergency') === '1') ? 'dashboard-seeker.html?emergency=1' : 'dashboard-seeker.html',
            HOSPITAL_ADMIN: 'dashboard-hospital.html',
            HOSPITAL: 'dashboard-hospital.html',
            SUPERADMIN: 'dashboard-admin.html',
            ADMIN: 'dashboard-admin.html',
          };
          window.location.href = dashboardMap[selectedRole] || 'index.html';
        }, 1200);
        return;
      }

      showAlert('error', 'An unexpected error occurred during registration.');
      setLoading(false);
    }
  });
}

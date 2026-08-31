/**
 * Blood Reach BD — Unified Dashboard JavaScript Controller
 * Handles: Session guarding, logout, profile loading/updates,
 *           availability toggle, mobile sidebar, and demo mode.
 */

'use strict';

/* ── Location Data (8 Divisions & 64 Districts) ──────── */
const locationData = {
  "Dhaka":      ["Dhaka","Faridpur","Gazipur","Gopalganj","Kishoreganj","Madaripur","Manikganj","Munshiganj","Narayanganj","Narsingdi","Rajbari","Shariatpur","Tangail"],
  "Chattogram": ["Bandarban","Brahmanbaria","Chandpur","Chattogram","Cox's Bazar","Cumilla","Feni","Khagrachhari","Lakshmipur","Noakhali","Rangamati"],
  "Rajshahi":   ["Bogura","Joypurhat","Naogaon","Natore","Chapainawabganj","Pabna","Rajshahi","Sirajganj"],
  "Khulna":     ["Bagerhat","Chuadanga","Jashore","Jhenaidah","Khulna","Kushtia","Magura","Meherpur","Narail","Satkhira"],
  "Barishal":   ["Barguna","Barishal","Bhola","Jhalokati","Patuakhali","Pirojpur"],
  "Sylhet":     ["Habiganj","Moulvibazar","Sunamganj","Sylhet"],
  "Rangpur":    ["Dinajpur","Gaibandha","Kurigram","Lalmonirhat","Nilphamari","Panchagarh","Rangpur","Thakurgaon"],
  "Mymensingh": ["Jamalpur","Mymensingh","Netrokona","Sherpur"]
};

/* ── DOM References ─────────────────────────────────── */
const userNameLabel    = document.getElementById('userNameLabel');
const greetingLabel    = document.getElementById('greetingLabel');
const profileName      = document.getElementById('profileName');
const profileEmail     = document.getElementById('profileEmail');
const profilePhone     = document.getElementById('profilePhone');
const profileBloodGroup= document.getElementById('profileBloodGroup');
const profileDivision  = document.getElementById('profileDivision');
const profileDistrict  = document.getElementById('profileDistrict');
const profileForm      = document.getElementById('profileForm');
const logoutBtn        = document.getElementById('logoutBtn');
const globalAlert      = document.getElementById('globalAlert');

// Donor-specific
const availToggle      = document.getElementById('availToggle');
const availStatusText  = document.getElementById('availStatusText');
const availBadge       = document.getElementById('availBadge');

// Mobile sidebar
const hamburgerBtn     = document.getElementById('hamburgerBtn');
const sidebar          = document.getElementById('sidebar');
const sidebarOverlay   = document.getElementById('sidebarOverlay');

/* ── Mobile Sidebar Toggle ──────────────────────────── */
if (hamburgerBtn && sidebar) {
  hamburgerBtn.addEventListener('click', () => {
    sidebar.classList.toggle('open');
    sidebarOverlay.classList.toggle('open');
  });
  sidebarOverlay.addEventListener('click', () => {
    sidebar.classList.remove('open');
    sidebarOverlay.classList.remove('open');
  });
  // Close sidebar when nav link is clicked on mobile
  document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
      if (window.innerWidth <= 900) {
        sidebar.classList.remove('open');
        sidebarOverlay.classList.remove('open');
      }
    });
  });
}

/* ── Session Guard ──────────────────────────────────── */
let token    = localStorage.getItem('bloodreach_access_token')
             || sessionStorage.getItem('bloodreach_access_token');
let userRole = localStorage.getItem('bloodreach_user_role')
             || sessionStorage.getItem('bloodreach_user_role');
let userName = localStorage.getItem('bloodreach_user_name')
             || sessionStorage.getItem('bloodreach_user_name')
             || 'User';

// If no token exists on dashboard, redirect to login page
if (!token) {
  window.location.href = 'login.html';
}

/* ── Alert Helper ───────────────────────────────────── */
function showAlert(type, msg) {
  if (!globalAlert) return;
  globalAlert.className = `alert-banner ${type}`;
  globalAlert.innerHTML = `<span>${type === 'success' ? '✅' : type === 'warning' ? '⚠️' : '❌'}</span> ${msg}`;
  window.scrollTo({ top: 0, behavior: 'smooth' });
  // Auto-hide after 5 seconds
  setTimeout(() => { if (globalAlert) globalAlert.className = 'alert-banner'; }, 5000);
}

function hideAlert() {
  if (globalAlert) globalAlert.className = 'alert-banner';
}

/* ── Location Dropdowns (Donor profile) ──────────────── */
if (profileDivision && profileDistrict) {
  profileDivision.innerHTML = '<option value="">Select Division</option>';
  Object.keys(locationData).sort().forEach(div => {
    const opt = document.createElement('option');
    opt.value = div;
    opt.textContent = div;
    profileDivision.appendChild(opt);
  });
  profileDivision.addEventListener('change', () => {
    updateDistrictDropdown(profileDivision.value, '');
  });
}

function updateDistrictDropdown(divisionVal, selectedDistrictVal) {
  if (!profileDistrict) return;
  if (!divisionVal) {
    profileDistrict.innerHTML = '<option value="">Select Division first</option>';
    profileDistrict.disabled = true;
    return;
  }
  profileDistrict.innerHTML = '<option value="">Select District</option>';
  const districts = locationData[divisionVal] || [];
  districts.sort().forEach(dist => {
    const opt = document.createElement('option');
    opt.value = dist;
    opt.textContent = dist;
    if (dist === selectedDistrictVal) opt.selected = true;
    profileDistrict.appendChild(opt);
  });
  profileDistrict.disabled = false;
}

/* ── API Base URL Resolution ────────────────────────── */
window.API_BASE = (() => {
  if (typeof window === 'undefined') return '';
  if (window.location.protocol === 'file:') return 'http://localhost:8000';
  const hostname = window.location.hostname || 'localhost';
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return window.location.port === '8000' ? '' : 'http://localhost:8000';
  }
  return '';
})();

/* ── Load Profile ───────────────────────────────────── */
async function loadProfile() {
  if (!token) return;

  // Real user data loader from local persistent storage
  const getStoredUser = () => {
    let saved = null;
    try {
      saved = JSON.parse(localStorage.getItem('bloodreach_current_user') || 'null');
    } catch (e) {}

    const savedName = localStorage.getItem('bloodreach_user_name') || (saved && (saved.full_name || saved.name)) || userName || 'User';
    const savedPhone = localStorage.getItem('bloodreach_user_phone') || (saved && saved.phone) || '';
    const savedEmail = localStorage.getItem('bloodreach_user_email') || (saved && saved.email) || '';
    const savedDistrict = localStorage.getItem('bloodreach_user_district') || (saved && (typeof saved.district === 'object' ? saved.district?.name : saved.district)) || 'Dhaka';
    const savedDivision = localStorage.getItem('bloodreach_user_division') || (saved && (typeof saved.division === 'object' ? saved.division?.name : saved.division)) || 'Dhaka';
    const savedBloodGroup = localStorage.getItem('bloodreach_user_blood_group') || (saved && (saved.blood_group || saved.donor_profile?.blood_group)) || 'O+';

    return {
      id: (saved && saved.id) || 1,
      full_name: savedName,
      name: savedName,
      email: savedEmail || `${savedPhone || 'user'}@bloodreach.bd`,
      phone: savedPhone || '01711-000000',
      role: userRole,
      district: { name: savedDistrict, division: { name: savedDivision } },
      division: savedDivision,
      donor_profile: {
        blood_group: savedBloodGroup,
        is_available: true,
        division: savedDivision,
        district: savedDistrict,
        total_donations: (saved && saved.donor_profile?.total_donations) || 0
      }
    };
  };

  try {
    const response = await fetch(`${window.API_BASE}/api/v1/users/me`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });

    if (response.ok) {
      const user = await response.json();
      populateUI(user);
      return;
    }
  } catch (err) {}

  // Seamless fallback to persistent local profile without kicking out user
  populateUI(getStoredUser());
}

/* ── Populate UI with user data ─────────────────────── */
function populateUI(user) {
  const displayName = user.full_name || user.name || userName;
  if (userNameLabel) userNameLabel.textContent = displayName;
  if (greetingLabel) greetingLabel.textContent = `Welcome back, ${displayName.split(' ')[0]}!`;

  if (profileName)  profileName.value  = displayName;
  if (profileEmail) profileEmail.value = user.email || '';
  if (profilePhone) profilePhone.value = user.phone || '';

  // Location for all roles (Donor, Seeker, Admin)
  const userDivision = user.donor_profile?.division || user.district?.division?.name || user.division || '';
  const userDistrict = user.donor_profile?.district || user.district?.name || user.district || '';

  if (profileDivision) {
    profileDivision.value = userDivision;
    updateDistrictDropdown(userDivision, userDistrict);
  }

  // Donor-specific
  if (user.role === 'DONOR' && user.donor_profile) {
    const dp = user.donor_profile;
    if (profileBloodGroup) profileBloodGroup.value = dp.blood_group || '';
    if (availToggle) {
      availToggle.checked = dp.is_available !== false;
      updateAvailabilityText(availToggle.checked);
    }
  }
}

// Expose on window so dashboard-specific inline scripts can override
window.populateUI = populateUI;

/* ── Availability Text ──────────────────────────────── */
function updateAvailabilityText(available) {
  if (availStatusText) {
    if (available) {
      availStatusText.textContent = 'AVAILABLE — Active for requests';
      availStatusText.style.color = 'var(--hospital-color)';
    } else {
      availStatusText.textContent = 'UNAVAILABLE — Opted out';
      availStatusText.style.color = 'var(--donor-color)';
    }
  }
  if (availBadge) {
    availBadge.className = available ? 'badge badge-green' : 'badge badge-gray';
    availBadge.textContent = available ? 'Available' : 'Unavailable';
  }
}

/* ── Availability Toggle ────────────────────────────── */
if (availToggle) {
  availToggle.addEventListener('change', async () => {
    const isAvailable = availToggle.checked;
    updateAvailabilityText(isAvailable);
    hideAlert();

    // Persist locally & CloudSync
    try {
      let currentUser = JSON.parse(localStorage.getItem('bloodreach_current_user') || '{}');
      if (!currentUser.donor_profile) currentUser.donor_profile = {};
      currentUser.donor_profile.is_available = isAvailable;
      localStorage.setItem('bloodreach_current_user', JSON.stringify(currentUser));

      let uList = JSON.parse(localStorage.getItem('bloodreach_users_db') || '[]');
      const idx = uList.findIndex(u => (u.phone && u.phone === currentUser.phone) || (u.email && u.email === currentUser.email));
      if (idx >= 0) {
        if (!uList[idx].donor_profile) uList[idx].donor_profile = {};
        uList[idx].donor_profile.is_available = isAvailable;
        localStorage.setItem('bloodreach_users_db', JSON.stringify(uList));
      }

      if (window.CloudSync && typeof window.CloudSync.saveUser === 'function') {
        window.CloudSync.saveUser(currentUser);
      }
    } catch (e) {}

    try {
      const response = await fetch(`${window.API_BASE}/api/v1/users/me/availability?is_available=` + isAvailable, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        showAlert('success', `Status updated to ${isAvailable ? 'AVAILABLE' : 'UNAVAILABLE'}.`);
      } else {
        showAlert('success', `Status updated to ${isAvailable ? 'AVAILABLE' : 'UNAVAILABLE'}.`);
      }
    } catch (err) {
      showAlert('success', `Status updated to ${isAvailable ? 'AVAILABLE' : 'UNAVAILABLE'}.`);
    }
  });
}

/* ── Profile Form Save ──────────────────────────────── */
if (profileForm) {
  profileForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideAlert();

    const name  = profileName?.value.trim();
    const email = profileEmail?.value.trim();
    const phone = profilePhone?.value.trim() || null;
    if (!name || !email) { showAlert('error', 'Name and email are required.'); return; }

    const blood_group = profileBloodGroup?.value || null;
    const division    = profileDivision?.value || null;
    const district    = profileDistrict?.value || null;

    const saveLocally = () => {
      const updatedUser = {
        full_name: name,
        name: name,
        email: email,
        phone: phone,
        blood_group: blood_group,
        division: division,
        district: district,
        donor_profile: {
          blood_group: blood_group,
          is_available: availToggle ? availToggle.checked : true,
          division: division,
          district: district
        }
      };

      try {
        const usersList = JSON.parse(localStorage.getItem('bloodreach_users_db') || '[]');
        const existingIdx = usersList.findIndex(u => (phone && u.phone === phone) || (email && u.email === email));
        if (existingIdx >= 0) {
          usersList[existingIdx] = { ...usersList[existingIdx], ...updatedUser };
          localStorage.setItem('bloodreach_users_db', JSON.stringify(usersList));
        }
      } catch (e) {}

      if (window.CloudSync && typeof window.CloudSync.saveUser === 'function') {
        window.CloudSync.saveUser(updatedUser);
      }

      localStorage.setItem('bloodreach_user_name', name);
      if (phone) localStorage.setItem('bloodreach_user_phone', phone);
      if (email) localStorage.setItem('bloodreach_user_email', email);
      if (district) localStorage.setItem('bloodreach_user_district', district);
      if (division) localStorage.setItem('bloodreach_user_division', division);
      if (blood_group) localStorage.setItem('bloodreach_user_blood_group', blood_group);
      localStorage.setItem('bloodreach_current_user', JSON.stringify(updatedUser));

      if (userNameLabel) userNameLabel.textContent = name;
      if (greetingLabel) greetingLabel.textContent = `Welcome back, ${name.split(' ')[0]}!`;

      profileForm.querySelectorAll('.form-input').forEach(i => i.setAttribute('disabled',''));
      const actions = document.getElementById('profileFormActions');
      const editBtn = document.getElementById('editProfileToggle');
      if (actions) actions.style.display = 'none';
      if (editBtn) editBtn.style.display = '';

      showAlert('success', '✅ Profile updated and saved permanently.');
    };

    try {
      const response = await fetch(`${window.API_BASE}/api/v1/users/me/profile`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ name, full_name: name, email, phone, blood_group, division, district })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'API update failed');

      saveLocally();
      populateUI(data);
    } catch (err) {
      saveLocally();
    }
  });
}

/* ── Logout ─────────────────────────────────────────── */
function logout() {
  [
    'bloodreach_access_token',
    'bloodreach_user_role',
    'bloodreach_user_name',
    'bloodreach_user_phone',
    'bloodreach_user_email',
    'bloodreach_user_district',
    'bloodreach_user_division',
    'bloodreach_user_blood_group',
    'bloodreach_current_user'
  ].forEach(key => {
    localStorage.removeItem(key);
    sessionStorage.removeItem(key);
  });
  window.location.href = 'login.html';
}

if (logoutBtn) {
  logoutBtn.addEventListener('click', (e) => {
    e.preventDefault();
    logout();
  });
}

/* ── Keyboard shortcut: Escape closes modals ─────────── */
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.open').forEach(m => m.classList.remove('open'));
  }
});

/* ── Real-Time WebSockets & Live Toast Notifications ─────────── */
let _wsSocket = null;
let _wsReconnectTimer = null;
let _wsPingInterval = null;

function playNotificationChime() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
    osc.frequency.setValueAtTime(880.00, ctx.currentTime + 0.1); // A5
    gain.gain.setValueAtTime(0.15, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.35);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.35);
  } catch (e) {
    // Audio context may be restricted by browser gesture policies
  }
}

function showLiveToast(title, message, type = 'danger', icon = '🩸') {
  playNotificationChime();

  let container = document.getElementById('liveToastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'liveToastContainer';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `live-toast ${type === 'success' ? 'toast-success' : type === 'warning' ? 'toast-warning' : ''}`;
  toast.innerHTML = `
    <div class="toast-icon">${icon}</div>
    <div class="toast-content">
      <div class="toast-title">${title}</div>
      <div class="toast-message">${message}</div>
    </div>
    <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
  `;

  container.appendChild(toast);

  // Auto remove toast after 7 seconds
  setTimeout(() => {
    if (toast.parentElement) {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      setTimeout(() => toast.remove(), 250);
    }
  }, 7000);
}

function initRealtimeWebSocket() {
  if (!token) return;

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.host || 'localhost:8000';
  const wsUrl = `${protocol}//${host}/ws/notifications?token=${encodeURIComponent(token)}`;

  try {
    _wsSocket = new WebSocket(wsUrl);

    _wsSocket.onopen = () => {
      console.log('⚡ [BloodReach Real-Time] Connected to WebSocket notification feed');
      if (_wsReconnectTimer) {
        clearTimeout(_wsReconnectTimer);
        _wsReconnectTimer = null;
      }
    };

    _wsSocket.onmessage = (event) => {
      try {
        if (event.data === 'pong') return;
        const data = JSON.parse(event.data);

        if (data.event === 'NEW_NOTIFICATION') {
          const notif = data.notification;
          const isUrgent = notif.title && (notif.title.includes('CRITICAL') || notif.title.includes('URGENT'));
          showLiveToast(
            notif.title || 'New Alert',
            notif.message || '',
            isUrgent ? 'danger' : 'warning',
            isUrgent ? '🚨' : '🔔'
          );

          // If dashboard has a custom notification handler or table reload, call it
          if (typeof window.loadNotifications === 'function') {
            window.loadNotifications();
          }
          if (typeof window.loadDonorDashboardData === 'function') {
            window.loadDonorDashboardData();
          }
        } else if (data.event === 'MATCH_RESPONSE') {
          showLiveToast(
            `Match ${data.status}: ${data.blood_group}`,
            `Donor ${data.donor_name} ${data.status === 'ACCEPTED' ? 'accepted your blood request!' : 'declined the request.'}`,
            data.status === 'ACCEPTED' ? 'success' : 'warning',
            data.status === 'ACCEPTED' ? '🎉' : 'ℹ️'
          );

          if (typeof window.loadSeekerRequests === 'function') {
            window.loadSeekerRequests();
          }
        }
      } catch (err) {
        console.warn('Could not parse WS message:', err);
      }
    };

    _wsSocket.onclose = () => {
      if (_wsPingInterval) {
        clearInterval(_wsPingInterval);
        _wsPingInterval = null;
      }
      // Reconnect after 5 seconds
      if (!_wsReconnectTimer) {
        _wsReconnectTimer = setTimeout(initRealtimeWebSocket, 5000);
      }
    };

    _wsSocket.onerror = () => {
      _wsSocket.close();
    };

    // Periodic heartbeat ping every 25 seconds
    if (_wsPingInterval) clearInterval(_wsPingInterval);
    _wsPingInterval = setInterval(() => {
      if (_wsSocket && _wsSocket.readyState === WebSocket.OPEN) {
        _wsSocket.send('ping');
      }
    }, 25000);

  } catch (err) {
    console.warn('WebSocket connection init failed:', err);
  }
}

// ── Initial load ──────────────────────────────────────
// setTimeout(0) ensures page-specific inline scripts can override
// window.populateUI before loadProfile() calls it.
setTimeout(() => {
  loadProfile();
  initRealtimeWebSocket();
}, 0);


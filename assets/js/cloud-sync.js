/**
 * BloodReach BD — Universal Real-Time Cross-Device Cloud Sync
 * Automatically syncs registered users and emergency requests across Mobile, Laptop, and Desktop.
 */
const CLOUD_SYNC_ID = 'ff808181a058d43f01a0590be1570248';
const CLOUD_SYNC_URL = `https://api.restful-api.dev/objects/${CLOUD_SYNC_ID}`;

window.CloudSync = {
  // Fetch latest global users & requests from cloud
  async fetchCloudData() {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3500);
      const res = await fetch(CLOUD_SYNC_URL, { signal: controller.signal });
      clearTimeout(timeoutId);
      if (res.ok) {
        const json = await res.json();
        if (json && json.data) {
          const cloudUsers = Array.isArray(json.data.users) ? json.data.users : [];
          const cloudRequests = Array.isArray(json.data.requests) ? json.data.requests : [];

          // Merge with local storage
          let localUsers = [];
          let localRequests = [];
          try {
            localUsers = JSON.parse(localStorage.getItem('bloodreach_users_db') || '[]');
            localRequests = JSON.parse(localStorage.getItem('bloodreach_requests_db') || '[]');
          } catch (e) {}

          const mergedUsers = [...cloudUsers];
          localUsers.forEach(lu => {
            if (!mergedUsers.some(cu => (cu.phone && cu.phone === lu.phone) || (cu.id && cu.id === lu.id))) {
              mergedUsers.push(lu);
            }
          });

          const mergedRequests = [...cloudRequests];
          localRequests.forEach(lr => {
            if (!mergedRequests.some(cr => (cr.id && cr.id === lr.id) || (cr.request_id && cr.request_id === lr.request_id))) {
              mergedRequests.push(lr);
            }
          });

          localStorage.setItem('bloodreach_users_db', JSON.stringify(mergedUsers));
          localStorage.setItem('bloodreach_requests_db', JSON.stringify(mergedRequests));

          return { users: mergedUsers, requests: mergedRequests };
        }
      }
    } catch (e) {
      console.warn('Cloud sync fetch note:', e);
    }

    // Fallback to local
    let users = [];
    let requests = [];
    try {
      users = JSON.parse(localStorage.getItem('bloodreach_users_db') || '[]');
      requests = JSON.parse(localStorage.getItem('bloodreach_requests_db') || '[]');
    } catch (e) {}
    return { users, requests };
  },

  // Save new or updated user to global cloud registry
  async saveUser(userRecord) {
    // Save to local first
    let usersList = [];
    try {
      usersList = JSON.parse(localStorage.getItem('bloodreach_users_db') || '[]');
      const idx = usersList.findIndex(u => (u.phone && u.phone === userRecord.phone) || (u.email && u.email === userRecord.email));
      if (idx >= 0) usersList[idx] = { ...usersList[idx], ...userRecord };
      else usersList.push(userRecord);
      localStorage.setItem('bloodreach_users_db', JSON.stringify(usersList));
    } catch (e) {}

    // Push to Cloud
    try {
      const data = await this.fetchCloudData();
      let currentUsers = data.users || [];
      const idx = currentUsers.findIndex(u => (u.phone && u.phone === userRecord.phone) || (u.email && u.email === userRecord.email));
      if (idx >= 0) currentUsers[idx] = { ...currentUsers[idx], ...userRecord };
      else currentUsers.push(userRecord);

      const payload = {
        name: 'BloodReach_BD_Cloud_Registry',
        data: {
          app: 'bloodreach-bd',
          users: currentUsers,
          requests: data.requests || []
        }
      };

      fetch(CLOUD_SYNC_URL, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      }).catch(() => {});
    } catch (e) {}
  },

  // Save new blood request to global cloud registry
  async saveRequest(reqRecord) {
    let reqs = [];
    try {
      reqs = JSON.parse(localStorage.getItem('bloodreach_requests_db') || '[]');
      const idx = reqs.findIndex(r => (r.id && r.id === reqRecord.id) || (r.request_id && r.request_id === reqRecord.request_id));
      if (idx >= 0) reqs[idx] = { ...reqs[idx], ...reqRecord };
      else reqs.unshift(reqRecord);
      localStorage.setItem('bloodreach_requests_db', JSON.stringify(reqs));
    } catch (e) {}

    try {
      const data = await this.fetchCloudData();
      let currentReqs = data.requests || [];
      const idx = currentReqs.findIndex(r => (r.id && r.id === reqRecord.id) || (r.request_id && r.request_id === reqRecord.request_id));
      if (idx >= 0) currentReqs[idx] = { ...currentReqs[idx], ...reqRecord };
      else currentReqs.unshift(reqRecord);

      const payload = {
        name: 'BloodReach_BD_Cloud_Registry',
        data: {
          app: 'bloodreach-bd',
          users: data.users || [],
          requests: currentReqs
        }
      };

      fetch(CLOUD_SYNC_URL, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      }).catch(() => {});
    } catch (e) {}
  }
};

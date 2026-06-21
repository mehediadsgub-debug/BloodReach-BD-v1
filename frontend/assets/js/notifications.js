async function loadNotifications() {
  // TODO: apiRequest("/notifications") -> render bell badge count + dropdown list
}

async function markAsRead(notifId) {
  return apiRequest(`/notifications/${notifId}/read`, { method: "PATCH" });
}

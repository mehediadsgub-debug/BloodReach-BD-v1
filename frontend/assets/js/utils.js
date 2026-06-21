function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString();
}

function urgencyBadgeClass(level) {
  return `badge badge--${level.toLowerCase()}`;
}

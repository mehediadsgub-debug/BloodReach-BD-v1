async function toggleAvailability(donorId, isAvailable) {
  return apiRequest(`/donors/${donorId}/availability`, {
    method: "PATCH",
    body: { is_available: isAvailable },
  });
}

async function loadDonationHistory(donorId) {
  // TODO: apiRequest(`/donors/${donorId}/donations`) and render into #donation-history
}

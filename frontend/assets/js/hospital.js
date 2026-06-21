async function loadInventory(hospitalId) {
  // TODO: apiRequest(`/hospitals/${hospitalId}/inventory`) -> render into #inventory-table
}

async function updateUnits(invId, unitsAvailable) {
  return apiRequest(`/hospital-inventory/${invId}/units`, {
    method: "PATCH",
    body: { units_available: unitsAvailable },
  });
}

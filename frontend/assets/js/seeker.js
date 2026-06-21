async function submitBloodRequest(event) {
  event.preventDefault();
  const payload = {
    blood_group: document.getElementById("blood-group").value,
    quantity_units: Number(document.getElementById("quantity-units").value),
    urgency_level: document.getElementById("urgency-level").value,
    // TODO: district_id from a populated dropdown
  };

  try {
    await apiRequest("/blood-requests/", { method: "POST", body: payload });
    // TODO: refresh donor results / show confirmation
  } catch (err) {
    alert(err.message);
  }
}

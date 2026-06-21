async function handleLogin(event) {
  event.preventDefault();
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  try {
    const { access_token } = await apiRequest("/auth/login", {
      method: "POST",
      body: { email, password },
    });
    localStorage.setItem("access_token", access_token);
    // TODO: redirect based on role (donor-dashboard.html / seeker-dashboard.html / etc.)
  } catch (err) {
    alert(err.message);
  }
}

async function handleRegister(event) {
  event.preventDefault();
  const payload = {
    name: document.getElementById("name").value,
    email: document.getElementById("email").value,
    password: document.getElementById("password").value,
    role: document.getElementById("role").value,
    // TODO: district_id from a populated dropdown
  };

  try {
    await apiRequest("/auth/register", { method: "POST", body: payload });
    window.location.href = "login.html";
  } catch (err) {
    alert(err.message);
  }
}

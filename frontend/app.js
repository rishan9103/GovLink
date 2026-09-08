const API_BASE = "http://localhost:5000";
const state = { services: [], category: "All", query: "" };
const DEMO_SERVICES = [
  { id: "demo-1", name: "PM-KISAN", category: "Agriculture", description: "Income support for eligible farmer families.", eligibility: "Small and marginal farmer families with cultivable land." },
  { id: "demo-2", name: "National Scholarship Portal", category: "Education", description: "Find and apply for scholarships from one place.", eligibility: "Eligibility varies by scholarship and student category." },
  { id: "demo-3", name: "Mahatma Gandhi NREGA", category: "Employment", description: "Guaranteed wage employment for rural households.", eligibility: "Adult members of rural households willing to do unskilled manual work." },
  { id: "demo-4", name: "Ayushman Bharat", category: "Welfare", description: "Health cover for eligible low-income families.", eligibility: "Families listed in the eligible government database." },
  { id: "demo-5", name: "PM SVANidhi", category: "Subsidies", description: "Working-capital support for street vendors.", eligibility: "Street vendors with an eligible vending certificate or survey record." }
];
const $ = (selector) => document.querySelector(selector);

function setStatus(online) {
  $("#status-dot").className = `status-dot ${online ? "online" : "offline"}`;
  $("#status-label").textContent = online ? "Backend connected" : "Backend offline";
}

function renderServices() {
  const filtered = state.services.filter((service) => {
    const matchesCategory = state.category === "All" || service.category === state.category;
    const text = `${service.name} ${service.description || ""} ${service.category || ""}`.toLowerCase();
    return matchesCategory && text.includes(state.query.toLowerCase());
  });
  const list = $("#service-list");
  if (!filtered.length) { list.innerHTML = '<div class="loading">No matching services found.</div>'; return; }
  list.innerHTML = filtered.map((service, index) => `<article class="service-item" data-id="${service.id}"><span class="service-number">${String(index + 1).padStart(2, "0")}</span><div><span class="service-name">${escapeHtml(service.name)}</span><span class="service-category">${escapeHtml(service.category || "General")}</span></div><span class="service-arrow">-></span></article>`).join("");
  list.querySelectorAll(".service-item").forEach((item) => item.addEventListener("click", () => showDetail(state.services.find((service) => String(service.id) === item.dataset.id), item)));
}

function showDetail(service, item) {
  if (!service) return;
  document.querySelectorAll(".service-item").forEach((entry) => entry.classList.remove("selected"));
  item.classList.add("selected");
  $("#service-detail").innerHTML = `<p class="detail-kicker">${escapeHtml(service.category || "GOVERNMENT SERVICE")}</p><h3>${escapeHtml(service.name)}</h3><p>${escapeHtml(service.description || "Information about this government service.")}</p><div class="detail-rule"></div><span class="detail-hint">Eligibility: ${escapeHtml(service.eligibility || "See official details")}</span>${service.official_url ? `<br><a class="detail-link" href="${escapeAttribute(service.official_url)}" target="_blank" rel="noreferrer">Visit official website -></a>` : ""}`;
}

function renderCategories(categories) {
  $("#category-row").innerHTML = ["All", ...categories.map((category) => category.name)].map((name) => `<button class="category ${name === "All" ? "active" : ""}" data-category="${escapeAttribute(name)}">${name === "All" ? "All services" : escapeHtml(name)}</button>`).join("");
  $("#category-row").querySelectorAll(".category").forEach((button) => button.addEventListener("click", () => { state.category = button.dataset.category; document.querySelectorAll(".category").forEach((entry) => entry.classList.remove("active")); button.classList.add("active"); renderServices(); }));
}

async function loadDirectory() {
  try {
    const [servicesResponse, categoriesResponse] = await Promise.all([fetch(`${API_BASE}/api/services`), fetch(`${API_BASE}/api/categories`)]);
    if (!servicesResponse.ok || !categoriesResponse.ok) throw new Error("API request failed");
    const servicesPayload = await servicesResponse.json(); const categoriesPayload = await categoriesResponse.json();
    state.services = servicesPayload.services || [];
    $("#service-count").textContent = state.services.length;
    renderCategories(categoriesPayload.categories || []); renderServices(); setStatus(true);
  } catch (error) {
    state.services = DEMO_SERVICES;
    $("#service-count").textContent = state.services.length;
    renderCategories([...new Set(DEMO_SERVICES.map((service) => service.category))].map((name) => ({ name })));
    renderServices(); setStatus(false);
  }
}

async function sendMessage(event) {
  event.preventDefault(); const input = $("#chat-input"); const message = input.value.trim(); if (!message) return;
  const messages = $("#messages"); messages.insertAdjacentHTML("beforeend", `<div class="message user">${escapeHtml(message)}</div>`); input.value = ""; input.disabled = true;
  const pending = document.createElement("div"); pending.className = "message assistant"; pending.textContent = "Looking through the available guidance..."; messages.appendChild(pending); messages.scrollTop = messages.scrollHeight;
  try { const response = await fetch(`${API_BASE}/api/chat`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message, language: "en" }) }); const payload = await response.json(); if (!response.ok) throw new Error(payload.error?.message || "Unable to answer"); pending.textContent = payload.answer || "I could not find an answer in the available documents."; setStatus(true); } catch (error) { pending.textContent = "Demo answer: check the service directory above for eligibility and application guidance. Connect the Flask backend for document-grounded answers."; setStatus(false); } finally { input.disabled = false; input.focus(); }
}

function escapeHtml(value) { return String(value).replace(/[&<>"']/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" })[character]); }
function escapeAttribute(value) { return escapeHtml(value).replace(/javascript:/gi, ""); }
$("#service-search").addEventListener("input", (event) => { state.query = event.target.value; renderServices(); });
$("#chat-form").addEventListener("submit", sendMessage);
loadDirectory();

// Settings are kept in localStorage under "notes.settings".
const KEY = "notes.settings";

function loadSettings() {
  try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch { return {}; }
}

function saveSettings(s) {
  localStorage.setItem(KEY, JSON.stringify(s));
}

const perPage = document.getElementById("per-page");
const reminders = document.getElementById("reminders");
if (perPage) {
  const s = loadSettings();
  perPage.value = s.perPage || 10;
  reminders.checked = !!s.reminders;
  perPage.addEventListener("change", () => saveSettings({ ...loadSettings(), perPage: Number(perPage.value) }));
  reminders.addEventListener("change", () => saveSettings({ ...loadSettings(), reminders: reminders.checked }));
}

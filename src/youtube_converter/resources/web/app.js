/* ============================================================
   app.js — frontend logic + bridge to Python (pywebview)
   ============================================================ */

const $ = (id) => document.getElementById(id);
const api = () => window.pywebview.api;

const VIDEO_QUALITIES = ["360p", "480p", "720p", "1080p", "1440p", "2160p (4K)"];
const VIDEO_FORMATS = ["MP4", "MKV", "WEBM", "AVI", "MOV"];
const COMPRESSION = ["High", "Medium", "Low"];
const AUDIO_FORMATS = ["mp3", "m4a", "flac", "wav", "ogg"];
const AUDIO_BITRATES = ["128", "192", "256", "320"];
const LOSSLESS = new Set(["flac", "wav"]);
const FILENAME_TPL = {
  "Titre": "%(title)s.%(ext)s",
  "Titre + ID": "%(title)s_%(id)s.%(ext)s",
  "Chaîne - Titre": "%(uploader)s - %(title)s.%(ext)s",
  "Date + Titre": "%(upload_date)s_%(title)s.%(ext)s",
};

let currentFormat = "video";
let lastFilepath = "";

/* ---------- helpers ---------- */
function fillSelect(el, values, selected) {
  el.innerHTML = "";
  values.forEach((v) => {
    const o = document.createElement("option");
    o.value = v; o.textContent = v;
    if (v === selected) o.selected = true;
    el.appendChild(o);
  });
}

function tr(dict, key) {
  return key.split(".").reduce((o, k) => (o && o[k] != null ? o[k] : null), dict);
}
function applyTranslations(dict) {
  if (!dict) return;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const v = tr(dict, el.dataset.i18n);
    if (v != null) el.textContent = v;
  });
  document.querySelectorAll("[data-i18n-ph]").forEach((el) => {
    const v = tr(dict, el.dataset.i18nPh);
    if (v != null) el.placeholder = v;
  });
}

function log(message, kind) {
  const el = $("statusLog");
  const ts = new Date().toLocaleTimeString();
  const cls = kind ? ` class="l-${kind}"` : "";
  el.innerHTML += `<span${cls}>[${ts}] ${escapeHtml(message)}</span>\n`;
  el.scrollTop = el.scrollHeight;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

/* ---------- init ---------- */
let booted = false;
window.addEventListener("pywebviewready", async () => {
  booted = true;
  initWithConfig(await api().get_config());
});

// Browser fallback (design preview without pywebview): populate with sample data.
window.addEventListener("DOMContentLoaded", () => {
  setTimeout(() => {
    if (window.pywebview || booted) return;
    initWithConfig({
      output_dir: "C:\\Users\\you\\Downloads\\YouTube_Downloads",
      language: "fr", translations: null, ffmpeg_ok: true,
      profiles: ["iPhone", "Android", "TV", "Web", "Custom"],
      defaults: { video_quality: "1080p", video_format: "MP4", audio_format: "mp3", audio_bitrate: "192", compression_preset: "Medium", compression_enabled: false },
      history: [
        { format: "video", title: "Lofi mix — 1 hour", quality: "MP4 1080p", status: "success", timestamp: new Date().toISOString() },
        { format: "audio", title: "Podcast épisode 12", quality: "MP3 192kbps", status: "success", timestamp: new Date().toISOString() },
      ],
    });
    renderQueue([
      { url: "https://www.youtube.com/watch?v=dQw4w9WgXcQ", format_type: "mp4", quality: "MP4 1080p", status: "downloading" },
      { url: "https://vimeo.com/76979871", format_type: "mp4", quality: "MP4 720p", status: "pending" },
    ]);
    onPush("progress", { percent: 62 });
  }, 200);
});

function initWithConfig(cfg) {
  $("folderInput").value = cfg.output_dir;
  $("langSelect").value = cfg.language;
  if (!cfg.ffmpeg_ok) {
    const pill = $("ffmpegPill");
    pill.textContent = "FFmpeg ✕";
    pill.className = "pill pill-warn";
  }

  const d = cfg.defaults;
  fillSelect($("videoQuality"), VIDEO_QUALITIES, d.video_quality);
  fillSelect($("videoFormat"), VIDEO_FORMATS, d.video_format);
  fillSelect($("compPreset"), COMPRESSION, d.compression_preset);
  fillSelect($("filenameTpl"), Object.keys(FILENAME_TPL), "Titre + ID");
  fillSelect($("audioFormat"), AUDIO_FORMATS, d.audio_format);
  fillSelect($("audioBitrate"), AUDIO_BITRATES, d.audio_bitrate);
  fillSelect($("profileSelect"), cfg.profiles, "Custom");

  $("compEnabled").checked = !!d.compression_enabled;
  $("compPreset").disabled = !d.compression_enabled;
  $("audioBitrate").disabled = LOSSLESS.has(d.audio_format);

  applyTranslations(cfg.translations);
  renderHistory(cfg.history);
  log("Prêt.");
}

/* ---------- language ---------- */
$("langSelect").addEventListener("change", async () => {
  const dict = await api().set_language($("langSelect").value);
  applyTranslations(dict);
});

/* ---------- URL validation ---------- */
let urlTimer;
$("urlInput").addEventListener("input", () => {
  clearTimeout(urlTimer);
  urlTimer = setTimeout(async () => {
    const url = $("urlInput").value.trim();
    const card = document.querySelector(".url-card");
    const status = $("urlStatus");
    if (!url) { card.className = "card url-card"; status.textContent = ""; return; }
    const ok = await api().validate_url(url);
    card.className = "card url-card " + (ok ? "valid" : "invalid");
    status.textContent = ok ? "✓" : "✕";
    status.style.color = ok ? "var(--success)" : "var(--danger)";
  }, 200);
});

/* ---------- format toggle ---------- */
document.querySelectorAll("#formatToggle .seg").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll("#formatToggle .seg").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    currentFormat = btn.dataset.format;
    $("videoOpts").classList.toggle("hidden", currentFormat !== "video");
    $("audioOpts").classList.toggle("hidden", currentFormat !== "audio");
  });
});

/* ---------- option persistence ---------- */
$("videoQuality").addEventListener("change", () => api().save_pref("video_quality", $("videoQuality").value));
$("videoFormat").addEventListener("change", () => api().save_pref("video_format", $("videoFormat").value));
$("audioBitrate").addEventListener("change", () => api().save_pref("audio_bitrate", $("audioBitrate").value));
$("filenameTpl").addEventListener("change", () => api().save_pref("filename_template", FILENAME_TPL[$("filenameTpl").value]));

$("compPreset").addEventListener("change", () => api().save_pref("compression_preset", $("compPreset").value));
$("compEnabled").addEventListener("change", () => {
  const on = $("compEnabled").checked;
  $("compPreset").disabled = !on;
  api().save_pref("compression_enabled", on);
});

$("audioFormat").addEventListener("change", () => {
  api().save_pref("audio_format", $("audioFormat").value);
  $("audioBitrate").disabled = LOSSLESS.has($("audioFormat").value);
});

/* ---------- device profile ---------- */
$("profileSelect").addEventListener("change", async () => {
  const name = $("profileSelect").value;
  if (name === "Custom") return;
  const p = await api().apply_profile(name);
  if (p.video_format) { $("videoFormat").value = p.video_format; api().save_pref("video_format", p.video_format); }
  if (p.video_quality) { $("videoQuality").value = p.video_quality; api().save_pref("video_quality", p.video_quality); }
  if (p.compression) { $("compPreset").value = p.compression; api().save_pref("compression_preset", p.compression); }
  log(`Profil ${name} appliqué.`, "ok");
});

/* ---------- folder ---------- */
$("browseBtn").addEventListener("click", async () => {
  const folder = await api().browse_folder();
  $("folderInput").value = folder;
});

/* ---------- add to queue ---------- */
async function addToQueue(formatType) {
  const url = $("urlInput").value.trim();
  if (!url) { log("Veuillez coller une URL.", "err"); return; }
  if (!(await api().validate_url(url))) { log("URL invalide.", "err"); return; }

  const payload = {
    url,
    format_type: formatType,
    video_quality: $("videoQuality").value,
    video_format: $("videoFormat").value,
    compression_enabled: $("compEnabled").checked,
    compression_preset: $("compPreset").value,
    audio_format: $("audioFormat").value,
    audio_bitrate: $("audioBitrate").value,
    filename_template: FILENAME_TPL[$("filenameTpl").value],
  };
  renderQueue(await api().add_task(payload));
  $("urlInput").value = "";
  document.querySelector(".url-card").className = "card url-card";
  $("urlStatus").textContent = "";
  log(`Ajouté à la file : ${url}`);
}
$("addVideoBtn").addEventListener("click", () => addToQueue("mp4"));
$("addAudioBtn").addEventListener("click", () => addToQueue("audio"));

/* ---------- start / stop / clear ---------- */
$("startBtn").addEventListener("click", async () => {
  const started = await api().start_queue();
  if (!started) { log("La file est vide.", "warn"); return; }
  $("postActions").classList.add("hidden");
  setRunning(true);
});
$("stopBtn").addEventListener("click", async () => {
  await api().stop_queue();
  log("Arrêt demandé…", "warn");
});
$("clearQueueBtn").addEventListener("click", async () => {
  renderQueue(await api().clear_queue());
  log("File vidée.");
});

function setRunning(state) {
  $("startBtn").classList.toggle("hidden", state);
  $("stopBtn").classList.toggle("hidden", !state);
  $("addVideoBtn").disabled = state;
  $("addAudioBtn").disabled = state;
}

/* ---------- history actions ---------- */
$("exportCsvBtn").addEventListener("click", async () => {
  const path = await api().export_history_csv();
  if (path) log("Historique exporté : " + path, "ok");
});
$("clearHistoryBtn").addEventListener("click", async () => {
  renderHistory(await api().clear_history());
  log("Historique effacé.");
});

/* ---------- post-download actions ---------- */
$("openFolderBtn").addEventListener("click", () => api().open_folder());
$("playFileBtn").addEventListener("click", async () => {
  const ok = await api().play_file(lastFilepath);
  if (!ok) log("Fichier introuvable.", "err");
});

/* ---------- rendering ---------- */
function renderQueue(tasks) {
  const list = $("queueList");
  list.innerHTML = "";
  $("queueBadge").textContent = tasks.filter((t) => t.status === "pending").length;
  tasks.forEach((t, i) => {
    const tag = t.format_type === "audio" ? "AUD" : "VID";
    const row = document.createElement("div");
    row.className = "row";
    row.innerHTML = `
      <span class="dot ${t.status}"></span>
      <span class="tag">${tag}</span>
      <div class="row-body">
        <div class="row-title">${escapeHtml(t.url)}</div>
        <div class="row-sub">${escapeHtml(t.quality)} · ${t.status}</div>
      </div>
      ${t.status === "pending" ? `<button class="row-x" data-i="${i}">&times;</button>` : ""}`;
    list.appendChild(row);
  });
  list.querySelectorAll(".row-x").forEach((b) => {
    b.addEventListener("click", async () => {
      renderQueue(await api().remove_task(parseInt(b.dataset.i, 10)));
    });
  });
}

function renderHistory(entries) {
  const list = $("historyList");
  list.innerHTML = "";
  entries.forEach((e) => {
    const tag = e.format === "audio" ? "AUD" : "VID";
    let when = e.timestamp || "";
    try { when = new Date(e.timestamp).toLocaleString("fr-FR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" }); } catch (_) {}
    const row = document.createElement("div");
    row.className = "row";
    row.innerHTML = `
      <span class="dot ${e.status}"></span>
      <span class="tag">${tag}</span>
      <div class="row-body">
        <div class="row-title">${escapeHtml(e.title || e.url)}</div>
        <div class="row-sub">${escapeHtml(e.quality || "")} · ${when}</div>
      </div>`;
    list.appendChild(row);
  });
}

/* ---------- tabs ---------- */
document.querySelectorAll(".nav-item").forEach((b) => {
  b.addEventListener("click", async () => {
    document.querySelectorAll(".nav-item").forEach((x) => x.classList.remove("active"));
    b.classList.add("active");
    const tab = b.dataset.tab;
    $("tabQueue").classList.toggle("hidden", tab !== "queue");
    $("tabHistory").classList.toggle("hidden", tab !== "history");
    if (tab === "history") renderHistory(await api().get_history());
  });
});

/* ---------- push events from Python ---------- */
window.onPush = (event, data) => {
  switch (event) {
    case "progress": {
      const pct = data.percent;
      $("progressBar").style.width = pct + "%";
      $("progressBar").classList.toggle("done", pct >= 100);
      $("progressPct").textContent = pct.toFixed(0) + "%";
      break;
    }
    case "status":
      log(data.message);
      break;
    case "task_start":
      log(`Téléchargement : ${data.task.url}`);
      api().get_queue().then(renderQueue);
      break;
    case "task_complete":
      if (data.success) { log("Terminé : " + data.message, "ok"); lastFilepath = data.filepath || ""; }
      else log("Échec : " + data.message, "err");
      api().get_queue().then(renderQueue);
      break;
    case "queue_empty":
      setRunning(false);
      $("progressBar").style.width = "100%";
      $("progressBar").classList.add("done");
      $("progressPct").textContent = "100%";
      $("postActions").classList.remove("hidden");
      log("Tous les téléchargements sont terminés.", "ok");
      api().get_history().then(renderHistory);
      break;
  }
};

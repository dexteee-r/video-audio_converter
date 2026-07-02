/* ============================================================
   app.js — frontend logic + bridge to Python (pywebview)
   Refonte « Collage intelligent » : coller -> détection -> 1 clic.
   ============================================================ */

const $ = (id) => document.getElementById(id);
const api = () => window.pywebview.api;

const VIDEO_QUALITIES = ["360p", "480p", "720p", "1080p", "1440p", "2160p (4K)"];
const AUDIO_FORMATS = ["MP3", "M4A", "FLAC", "WAV", "OGG"];
const VIDEO_CONTAINERS = ["MP4", "MKV", "WEBM", "AVI", "MOV"];
const AUDIO_BITRATES = ["128", "192", "256", "320"];
const LOSSLESS = new Set(["flac", "wav"]);
const FILENAME_TPL = {
  "Titre": "%(title)s.%(ext)s",
  "Titre + ID": "%(title)s_%(id)s.%(ext)s",
  "Chaîne - Titre": "%(uploader)s - %(title)s.%(ext)s",
  "Date + Titre": "%(upload_date)s_%(title)s.%(ext)s",
};

// Minimal FR fallback for JS-generated text when translations are absent
// (browser design preview, or a failed load). The real app passes the full dict.
const FALLBACK_I18N = {
  ui: {
    detect_analyzing: "analyse…", detect_found: "✓ détecté",
    quality_avail: "{q} dispo", audio_avail: "audio dispo",
    st_pending: "en attente", st_downloading: "téléchargement", st_done: "terminé", st_error: "erreur",
    queue_empty_label: "— file vide —", play: "Lire", redownload: "Re-DL",
    dl_video_sub: "image + son", dl_audio_sub: "son seul",
    card_empty_title: "Aucun média analysé", card_empty_sub: "Collez un lien pour afficher l'aperçu",
    ffmpeg_missing_label: "FFmpeg introuvable",
    ytdlp_label: "yt-dlp", ytdlp_checking: "vérification…", ytdlp_uptodate: "à jour", ytdlp_updated: "mise à jour prête — redémarrez",
  },
  messages: {
    invalid_url: "URL invalide.", added_to_queue: "Ajouté à la file : {url} [{quality}]",
    queue_cleared: "File d'attente vidée.", stop_requested: "Arrêt demandé…",
    download_task: "Téléchargement : {url} [{quality}]", download_success: "Terminé : {message}",
    download_error: "Échec : {message}", download_complete: "Tous les téléchargements sont terminés.",
    file_not_found: "Fichier introuvable.", history_exported: "Historique exporté : {filepath}",
    history_cleared: "Historique effacé.", profile_applied: "Profil {profile} appliqué.", queue_empty: "",
  },
};

let D = null;                 // current translations dict
let detect = "idle";          // idle | analyzing | found
let vidQual = "1080p";
let audFmt = "MP3";
let currentProgress = 0;      // % of the active (downloading) task
let lastFilepath = "";
const titleCache = {};        // url -> media title (for queue/history rows)
let urlTimer = null;

const cfg = {                 // settings applied to every download
  video_format: "MP4",
  compression_enabled: false,
  compression_preset: "Medium",
  filename_template: FILENAME_TPL["Titre + ID"],
  audio_bitrate: "192",
};

/* ---------- i18n helpers ---------- */
function tr(dict, key) {
  return key.split(".").reduce((o, k) => (o && o[k] != null ? o[k] : null), dict);
}
function t(key, vars) {
  let s = tr(D, key);
  if (s == null) return key;
  if (vars) for (const k in vars) s = s.replace(`{${k}}`, vars[k]);
  return s;
}
function applyTranslations(dict) {
  D = dict || D;
  if (!D) return;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const v = tr(D, el.dataset.i18n);
    if (v != null) el.textContent = v;
  });
  document.querySelectorAll("[data-i18n-ph]").forEach((el) => {
    const v = tr(D, el.dataset.i18nPh);
    if (v != null) el.placeholder = v;
  });
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}
function log(message, kind) {
  const el = $("statusLog");
  const ts = new Date().toLocaleTimeString();
  const cls = kind ? ` class="l-${kind}"` : "";
  el.innerHTML += `<span${cls}>[${ts}] ${escapeHtml(message)}</span>\n`;
  el.scrollTop = el.scrollHeight;
}

/* ---------- boot ---------- */
let booted = false;
window.addEventListener("pywebviewready", async () => {
  booted = true;
  initWithConfig(await api().get_config());
});

// Browser fallback (design preview without pywebview): sample data.
window.addEventListener("DOMContentLoaded", () => {
  setTimeout(() => {
    if (window.pywebview || booted) return;
    initWithConfig({
      output_dir: "C:\\Users\\you\\Downloads\\YouTube_Downloads",
      language: "fr", translations: null, ffmpeg_ok: true,
      profiles: ["Custom", "iPhone", "Android", "TV", "Web"],
      defaults: { video_quality: "1080p", audio_format: "mp3", audio_bitrate: "192",
        video_format: "MP4", compression_preset: "Medium", compression_enabled: false },
      history: [
        { format: "video", title: "Lofi mix — 1 hour", quality: "MP4 1080p", status: "success", timestamp: new Date().toISOString(), filepath: "x.mp4" },
        { format: "audio", title: "Podcast épisode 12", quality: "MP3 192kbps", status: "success", timestamp: new Date().toISOString(), filepath: "y.mp3" },
      ],
    });
    // sample detected media + queue for visual preview
    showMedia({ title: "Lofi beats — 1 hour study mix", uploader: "ChillHop Music", duration: "1:02:14", qualities: ["360p", "720p", "1080p"], has_audio: true });
    titleCache["https://youtu.be/demo1"] = "Tutoriel React — hooks avancés";
    titleCache["https://youtu.be/demo2"] = "Podcast tech — épisode 12";
    currentProgress = 62;
    renderQueue([
      { url: "https://youtu.be/demo1", format_type: "mp4", quality: "MP4 1080p", status: "downloading" },
      { url: "https://youtu.be/demo2", format_type: "audio", quality: "MP3 192kbps", status: "pending" },
    ]);
  }, 200);
});

function initWithConfig(c) {
  applyTranslations(c.translations || FALLBACK_I18N);
  $("langSelect").value = c.language || "fr";
  $("folderInput").value = c.output_dir || "";

  if (!c.ffmpeg_ok) {
    const pill = $("ffmpegPill");
    pill.textContent = "ffmpeg :: ✕";
    pill.className = "pill pill-warn";
    $("depFfmpeg").textContent = t("ui.ffmpeg_missing_label");
    $("depFfmpeg").previousElementSibling.className = "dot error";
  }

  const d = c.defaults || {};
  vidQual = d.video_quality || "1080p";
  audFmt = (d.audio_format || "mp3").toUpperCase();
  cfg.video_format = d.video_format || "MP4";
  cfg.compression_preset = d.compression_preset || "Medium";
  cfg.compression_enabled = !!d.compression_enabled;
  cfg.audio_bitrate = d.audio_bitrate || "192";

  // video / audio choices now live in the Settings tab
  fillSelect($("videoQuality"), VIDEO_QUALITIES, vidQual);
  fillSelect($("videoFormat"), VIDEO_CONTAINERS, cfg.video_format);
  fillSelect($("audioFormat"), AUDIO_FORMATS, audFmt);
  fillSelect($("audioBitrate"), AUDIO_BITRATES, cfg.audio_bitrate);
  $("audioBitrate").disabled = LOSSLESS.has(audFmt.toLowerCase());

  fillSelect($("profileSelect"), c.profiles || ["Custom"], "Custom");
  fillSelect($("filenameTpl"), Object.keys(FILENAME_TPL), "Titre + ID");
  fillSelect($("compPreset"), ["High", "Medium", "Low"], cfg.compression_preset);
  $("compEnabled").checked = cfg.compression_enabled;
  $("compPreset").disabled = !cfg.compression_enabled;
  $("autoUpdate").checked = d.auto_update_ytdlp !== false;
  updateFilenamePreview();
  updateButtonSubs();

  renderHistory(c.history || []);
  log(t("messages.queue_empty") ? "Prêt." : "Prêt.");
}

function fillSelect(el, values, selected) {
  el.innerHTML = "";
  values.forEach((v) => {
    const o = document.createElement("option");
    o.value = v; o.textContent = v;
    if (v === selected) o.selected = true;
    el.appendChild(o);
  });
}

/* ---------- tabs ---------- */
document.querySelectorAll("#tabs .tab").forEach((btn) => {
  btn.addEventListener("click", async () => {
    document.querySelectorAll("#tabs .tab").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    const tab = btn.dataset.tab;
    $("panel-queue").classList.toggle("hidden", tab !== "queue");
    $("panel-history").classList.toggle("hidden", tab !== "history");
    $("panel-settings").classList.toggle("hidden", tab !== "settings");
    if (tab === "history" && window.pywebview) renderHistory(await api().get_history());
  });
});

/* ---------- smart paste ---------- */
$("urlInput").addEventListener("input", () => {
  const url = $("urlInput").value.trim();
  $("pasteBar").classList.toggle("dirty", !!url);
  clearTimeout(urlTimer);
  if (!url) { setDetect("idle"); resetMedia(); return; }
  urlTimer = setTimeout(() => analyze(url), 650);
});

async function analyze(url) {
  if (window.pywebview) {
    const ok = await api().validate_url(url);
    if (!ok) { setDetect("idle"); resetMedia(); log(t("messages.invalid_url"), "err"); return; }
  }
  setDetect("analyzing");
  if (!window.pywebview) { setTimeout(() => { setDetect("found"); showMedia(null); }, 600); return; }
  try {
    const info = await api().fetch_info(url);
    if (info && info.success) {
      titleCache[url] = info.title;
      setDetect("found");
      showMedia(info);
    } else {
      // graceful degradation: allow download with URL as title
      setDetect("found");
      showMedia({ title: url, uploader: "", duration: "--:--", qualities: [], has_audio: true });
    }
  } catch (_) {
    setDetect("found");
    showMedia({ title: url, uploader: "", duration: "--:--", qualities: [], has_audio: true });
  }
}

function setDetect(state) {
  detect = state;
  const bar = $("pasteBar");
  bar.classList.remove("analyzing", "found");
  const chip = $("detectChip");
  chip.className = "detect-chip";
  $("analyzing").classList.toggle("hidden", state !== "analyzing");
  $("mediaCard").classList.toggle("hidden", state === "analyzing");
  if (state === "analyzing") { bar.classList.add("analyzing"); chip.classList.add("analyzing"); chip.textContent = t("ui.detect_analyzing"); }
  else if (state === "found") { bar.classList.add("found"); chip.classList.add("found"); chip.textContent = t("ui.detect_found"); }
  else { chip.textContent = ""; }
}

function showMedia(info) {
  const card = $("mediaCard");
  card.classList.add("ready");
  if (info) {
    $("mediaTitle").textContent = info.title || "";
    $("mediaChannel").textContent = info.uploader || "";
    $("mediaDur").textContent = info.duration || "--:--";
    const badges = $("mediaBadges");
    badges.innerHTML = "";
    const best = (info.qualities || []).slice(-1)[0];
    if (best) badges.innerHTML += `<span class="badge-q">${t("ui.quality_avail", { q: best })}</span>`;
    if (info.has_audio) badges.innerHTML += `<span class="badge-dim">${t("ui.audio_avail")}</span>`;
  }
}

function resetMedia() {
  const card = $("mediaCard");
  card.classList.remove("ready");
  $("mediaTitle").textContent = t("ui.card_empty_title");
  $("mediaChannel").textContent = t("ui.card_empty_sub");
  $("mediaDur").textContent = "--:--";
  $("mediaBadges").innerHTML = "";
}

/* ---------- video / audio settings (choices live in the Settings tab) ---------- */
function updateButtonSubs() {
  const v = $("vidSubText"), a = $("audSubText");
  if (v) v.textContent = `${t("ui.dl_video_sub")} · ${cfg.video_format} ${vidQual}`;
  const lossless = LOSSLESS.has(audFmt.toLowerCase());
  if (a) a.textContent = `${t("ui.dl_audio_sub")} · ${audFmt}${lossless ? "" : " " + cfg.audio_bitrate + "k"}`;
}
$("videoQuality").addEventListener("change", () => {
  vidQual = $("videoQuality").value; updateButtonSubs();
  if (window.pywebview) api().save_pref("video_quality", vidQual);
});
$("videoFormat").addEventListener("change", () => {
  cfg.video_format = $("videoFormat").value; updateButtonSubs();
  if (window.pywebview) api().save_pref("video_format", cfg.video_format);
});
$("audioFormat").addEventListener("change", () => {
  audFmt = $("audioFormat").value;
  $("audioBitrate").disabled = LOSSLESS.has(audFmt.toLowerCase());
  updateButtonSubs();
  if (window.pywebview) api().save_pref("audio_format", audFmt.toLowerCase());
});
$("audioBitrate").addEventListener("change", () => {
  cfg.audio_bitrate = $("audioBitrate").value; updateButtonSubs();
  if (window.pywebview) api().save_pref("audio_bitrate", cfg.audio_bitrate);
});

/* ---------- one-click add + start ---------- */
async function addAndStart(formatType) {
  if (detect !== "found") return;
  const url = $("urlInput").value.trim();
  if (!url) return;

  const payload = {
    url, format_type: formatType,
    video_quality: vidQual,
    video_format: cfg.video_format,
    compression_enabled: cfg.compression_enabled,
    compression_preset: cfg.compression_preset,
    audio_format: audFmt.toLowerCase(),
    audio_bitrate: cfg.audio_bitrate,
    filename_template: cfg.filename_template,
  };

  if (window.pywebview) {
    renderQueue(await api().add_task(payload));
    await api().start_queue();
  }
  $("postActions").classList.add("hidden");
  log(t("messages.added_to_queue", { url, quality: formatType === "audio" ? audFmt : vidQual }));
  // reset paste/card for the next link
  $("urlInput").value = "";
  $("pasteBar").classList.remove("dirty");
  setDetect("idle");
  resetMedia();
}
$("addVideoBtn").addEventListener("click", () => addAndStart("mp4"));
$("addAudioBtn").addEventListener("click", () => addAndStart("audio"));

/* ---------- queue ---------- */
$("clearQueueBtn").addEventListener("click", async () => {
  if (window.pywebview) renderQueue(await api().clear_queue());
  else renderQueue([]);
  log(t("messages.queue_cleared"));
});
$("stopBtn").addEventListener("click", async () => {
  if (window.pywebview) await api().stop_queue();
  log(t("messages.stop_requested"), "warn");
});

function statusWord(s) {
  return { pending: t("ui.st_pending"), downloading: t("ui.st_downloading"),
    success: t("ui.st_done"), done: t("ui.st_done"), error: t("ui.st_error") }[s] || s;
}

function renderQueue(tasks) {
  const list = $("queueList");
  list.innerHTML = "";
  $("queueBadge").textContent = tasks.length;
  $("queueCount").textContent = tasks.length;
  const running = tasks.some((t) => t.status === "downloading");
  $("stopBtn").classList.toggle("hidden", !running);

  if (!tasks.length) {
    list.innerHTML = `<div class="row-empty">${escapeHtml(t("ui.queue_empty_label"))}</div>`;
    return;
  }

  tasks.forEach((task, i) => {
    const isDl = task.status === "downloading";
    const pct = isDl ? Math.round(currentProgress) : 0;
    const isAud = task.format_type === "audio";
    const tag = isAud ? `<span class="tag tag-aud">&#9834; AUD</span>` : `<span class="tag tag-vid">&#9654; VID</span>`;
    const title = titleCache[task.url] || task.url;
    const row = document.createElement("div");
    row.className = "row" + (isDl ? " is-downloading" : "");
    row.innerHTML = `
      <span class="dot ${task.status}"></span>
      ${tag}
      <div class="row-body">
        <div class="row-title">${escapeHtml(title)}</div>
        <div class="row-line">
          <span class="row-sub">${escapeHtml(task.quality)} · ${escapeHtml(statusWord(task.status))}</span>
          <span class="row-track"><span class="row-fill ${isDl ? "striped" : ""}" style="width:${pct}%"></span></span>
        </div>
      </div>
      <span class="row-pct">${pct}%</span>
      ${task.status === "pending" ? `<button class="row-x" data-i="${i}">&times;</button>` : ""}`;
    list.appendChild(row);
  });

  list.querySelectorAll(".row-x").forEach((b) => {
    b.addEventListener("click", async () => {
      if (window.pywebview) renderQueue(await api().remove_task(parseInt(b.dataset.i, 10)));
    });
  });
}

/* live progress on the active row, without full re-render */
function updateActiveProgress(pct) {
  currentProgress = pct;
  const row = $("queueList").querySelector(".row.is-downloading");
  if (!row) return;
  const fill = row.querySelector(".row-fill");
  if (fill) fill.style.width = pct + "%";
  const p = row.querySelector(".row-pct");
  if (p) p.textContent = Math.round(pct) + "%";
}

/* ---------- history ---------- */
function renderHistory(entries) {
  const list = $("historyList");
  list.innerHTML = "";
  if (!entries || !entries.length) {
    list.innerHTML = `<div class="row-empty">—</div>`;
    return;
  }
  entries.forEach((e) => {
    const isAud = e.format === "audio";
    const tag = isAud ? `<span class="tag tag-aud">&#9834; AUD</span>` : `<span class="tag tag-vid">&#9654; VID</span>`;
    let when = e.timestamp || "";
    try { when = new Date(e.timestamp).toLocaleString("fr-FR", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" }); } catch (_) {}
    const row = document.createElement("div");
    row.className = "row";
    row.innerHTML = `
      <span class="dot ${e.status === "success" ? "success" : "error"}"></span>
      ${tag}
      <div class="row-body">
        <div class="row-title">${escapeHtml(e.title || e.url)}</div>
        <div class="row-line"><span class="row-sub">${escapeHtml(e.quality || "")} · ${when}</span></div>
      </div>
      <button class="row-play">&#9654; ${escapeHtml(t("ui.play"))}</button>
      <button class="row-redl">${escapeHtml(t("ui.redownload"))}</button>`;
    row.querySelector(".row-play").addEventListener("click", async () => {
      if (window.pywebview && !(await api().play_file(e.filepath || ""))) log(t("messages.file_not_found"), "err");
    });
    row.querySelector(".row-redl").addEventListener("click", async () => {
      if (!window.pywebview) return;
      titleCache[e.url] = e.title || e.url;
      const payload = {
        url: e.url, format_type: e.format === "audio" ? "audio" : "mp4",
        video_quality: vidQual, video_format: cfg.video_format,
        compression_enabled: cfg.compression_enabled, compression_preset: cfg.compression_preset,
        audio_format: audFmt.toLowerCase(), audio_bitrate: cfg.audio_bitrate,
        filename_template: cfg.filename_template,
      };
      renderQueue(await api().add_task(payload));
      await api().start_queue();
      document.querySelector('#tabs .tab[data-tab="queue"]').click();
      log(t("messages.added_to_queue", { url: e.url, quality: "" }));
    });
    list.appendChild(row);
  });
}
$("exportCsvBtn").addEventListener("click", async () => {
  if (!window.pywebview) return;
  const path = await api().export_history_csv();
  if (path) log(t("messages.history_exported", { filepath: path }), "ok");
});
$("clearHistoryBtn").addEventListener("click", async () => {
  if (window.pywebview) renderHistory(await api().clear_history());
  else renderHistory([]);
  log(t("messages.history_cleared"));
});

/* ---------- post-run actions ---------- */
$("openFolderBtn").addEventListener("click", () => { if (window.pywebview) api().open_folder(); });
$("playLastBtn").addEventListener("click", async () => {
  if (window.pywebview && !(await api().play_file(lastFilepath))) log(t("messages.file_not_found"), "err");
});

/* ---------- settings ---------- */
$("browseBtn").addEventListener("click", async () => {
  if (window.pywebview) $("folderInput").value = await api().browse_folder();
});
$("langSelect").addEventListener("change", async () => {
  if (!window.pywebview) return;
  const dict = await api().set_language($("langSelect").value);
  applyTranslations(dict);
  updateButtonSubs();
  if (detect === "found") setDetect("found"); else resetMedia();
});
$("profileSelect").addEventListener("change", async () => {
  const name = $("profileSelect").value;
  if (name === "Custom" || !window.pywebview) return;
  const p = await api().apply_profile(name);
  if (p.video_format) { cfg.video_format = p.video_format; $("videoFormat").value = p.video_format; api().save_pref("video_format", p.video_format); }
  if (p.video_quality) { vidQual = p.video_quality; $("videoQuality").value = vidQual; api().save_pref("video_quality", vidQual); }
  if (p.compression) { cfg.compression_preset = p.compression; $("compPreset").value = p.compression; api().save_pref("compression_preset", p.compression); }
  updateButtonSubs();
  log(t("messages.profile_applied", { profile: name }), "ok");
});
$("filenameTpl").addEventListener("change", () => {
  cfg.filename_template = FILENAME_TPL[$("filenameTpl").value];
  updateFilenamePreview();
  if (window.pywebview) api().save_pref("filename_template", cfg.filename_template);
});
$("compEnabled").addEventListener("change", () => {
  cfg.compression_enabled = $("compEnabled").checked;
  $("compPreset").disabled = !cfg.compression_enabled;
  if (window.pywebview) api().save_pref("compression_enabled", cfg.compression_enabled);
});
$("compPreset").addEventListener("change", () => {
  cfg.compression_preset = $("compPreset").value;
  if (window.pywebview) api().save_pref("compression_preset", cfg.compression_preset);
});
$("autoUpdate").addEventListener("change", () => {
  if (window.pywebview) api().save_pref("auto_update_ytdlp", $("autoUpdate").checked);
});

function updateFilenamePreview() {
  const tpl = cfg.filename_template;
  const ex = tpl
    .replace("%(title)s", "Lofi_beats")
    .replace("%(id)s", "dQw4w9")
    .replace("%(uploader)s", "ChillHop")
    .replace("%(upload_date)s", "20260701")
    .replace("%(ext)s", "mp4");
  $("filenamePreview").textContent = "→ " + ex;
}

/* ---------- push events from Python ---------- */
window.onPush = (event, data) => {
  switch (event) {
    case "progress":
      updateActiveProgress(data.percent);
      break;
    case "status":
      log(data.message);
      break;
    case "task_start":
      currentProgress = 0;
      $("postActions").classList.add("hidden");
      log(t("messages.download_task", { index: "", total: "", url: data.task ? data.task.url : "", quality: data.task ? data.task.quality : "" }));
      api().get_queue().then(renderQueue);
      break;
    case "task_complete":
      if (data.success) { log(t("messages.download_success", { message: data.message }), "ok"); lastFilepath = data.filepath || ""; }
      else log(t("messages.download_error", { message: data.message }), "err");
      api().get_queue().then(renderQueue);
      break;
    case "ytdlp_status": {
      const el = $("depYtdlp"), dot = $("depYtdlpDot");
      const ver = data.version && data.version !== "0" ? " · " + data.version : "";
      if (data.state === "checking") {
        el.textContent = t("ui.ytdlp_label") + ver + " · " + t("ui.ytdlp_checking");
      } else if (data.state === "uptodate") {
        el.textContent = t("ui.ytdlp_label") + ver + " · " + t("ui.ytdlp_uptodate");
        if (dot) dot.className = "dot success";
      } else if (data.state === "updated") {
        el.textContent = t("ui.ytdlp_label") + " · " + data.latest + " · " + t("ui.ytdlp_updated");
        if (dot) dot.className = "dot downloading";
        log(`yt-dlp ${data.version} → ${data.latest} — ${t("ui.ytdlp_updated")}`, "ok");
      } else {
        el.textContent = t("ui.ytdlp_label") + ver;
        if (dot) dot.className = "dot pending";
      }
      break;
    }
    case "queue_empty":
      currentProgress = 0;
      $("stopBtn").classList.add("hidden");
      $("postActions").classList.toggle("hidden", !lastFilepath);
      log(t("messages.download_complete"), "ok");
      api().get_queue().then(renderQueue);
      api().get_history().then(renderHistory);
      break;
  }
};

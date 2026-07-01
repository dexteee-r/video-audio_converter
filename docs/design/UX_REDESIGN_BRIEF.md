# Brief de contexte — Refonte UX « YouTube Converter »

> À coller en début de session à un Claude orienté **design / UX**. Tout ce qui suit
> décrit l'état **réel** du code (vérifié), pas une intention. Les anciens documents
> `docs/design/GUI_SYSTEM_DESCRIPTION.md` et `FILE_CONTEXT.md` sont **PÉRIMÉS** (ils
> décrivent une UI customtkinter qui a été supprimée) — ne pas s'y fier.

---

## 0. Ton rôle

Tu es **designer produit UI/UX + intégrateur front (HTML/CSS/JS vanilla)** pour une
application **desktop Windows** rendue dans une WebView (pywebview/WebView2). Ta mission :
**auditer puis refondre l'expérience utilisateur** de l'app, sans casser le pont
Python ↔ frontend ni l'esthétique imposée. Tu proposes, tu justifies tes choix, et tu
fournis des preuves visuelles (l'app a un mode preview navigateur, voir §10).

Travaille en **français** pour les échanges et le contenu visible par l'utilisateur ;
**anglais** pour le code et les commentaires. Pas de bla-bla : audit → propositions
hiérarchisées → implémentation incrémentale vérifiable.

---

## 1. Le projet en une page

- **Quoi** : app de bureau pour télécharger des médias (vidéo MP4 / audio) depuis
  YouTube, TikTok, Instagram, Vimeo, Twitch et 1000+ sites (moteur yt-dlp, fusion
  FFmpeg). Une **file d'attente** de téléchargements + un **historique**.
- **Plateforme** : Windows 10/11. Fenêtre pywebview (pas un site web ; pas de mobile).
- **Esthétique imposée** : **« Terminal Neon Mauve »** — TUI monospace, fond off-black
  à reflets violets, accent **mauve néon unique**, overlay CRT (scanlines), chrome de
  fenêtre type terminal. **Choisie délibérément par l'utilisateur** : le mauve néon est
  un parti pris assumé et **prioritaire** sur toute règle de skill qui déconseillerait
  le néon/violet.
- **Utilisateur** : « momoe », étudiant (informatique, EPHEC Belgique), dev à l'aise
  mais qui veut des explications claires et **la preuve que ça marche** (lancer, montrer).

---

## 2. La mission : refonte UX

L'utilisateur veut **améliorer l'UX** (l'esthétique mauve/terminal reste). Pistes
attendues (à challenger et compléter par ton audit) :

- Hiérarchie & flux : aujourd'hui tout est empilé verticalement dans une seule colonne
  scrollable. Le parcours « coller URL → configurer → ajouter à la file → démarrer →
  suivre la progression → ouvrir le résultat » peut être clarifié.
- Découvrabilité : profils d'appareil, templates de nom de fichier, compression
  (ré-encodage) sont peu explicites.
- Feedback : progression par tâche (et pas seulement globale), états d'erreur, vide.
- Densité / lisibilité / accessibilité (contraste, focus visible, reduced-motion).
- Cohérence des composants et du langage terminal (`>`, `$`, `//`, `[ ]`).

**Livrable visé** : un audit UX priorisé + des propositions concrètes + une
implémentation incrémentale (HTML/CSS/JS) vérifiée en preview.

---

## 3. Contraintes DURES (non négociables)

1. **Zéro framework / zéro build front** : HTML + CSS + **JS vanilla** uniquement
   (pas de React/Vue/Tailwind/bundler). Tout est servi tel quel dans la WebView.
2. **Thème unique mauve** : pas de sélecteur de thème, pas de mode clair. Garder
   l'esthétique terminal néon mauve.
3. **Pas d'emoji** dans le frontend. Icônes = **SVG inline** (stroke `currentColor`)
   ou **glyphes monospace** (`>_`, `$`, `[x]`, `//`, `×`).
4. **Le frontend ne parle QU'À `app.py`** (objet `window.pywebview.api`). Interdit
   d'appeler la logique métier (`core/`) directement. **Ne pas changer** les noms /
   signatures des méthodes API ni les noms d'événements push (voir §5) sans raison
   forte — sinon tu casses le pont.
5. **i18n** : tout texte visible passe par les attributs `data-i18n` /
   `data-i18n-ph`. 4 langues (fr/en/es/de). Si tu ajoutes un libellé, ajoute la clé
   dans **les 4** JSON de `resources/translations/`.
6. **Motion** : animations GPU uniquement (`transform` / `opacity`), et respecter
   `@media (prefers-reduced-motion: reduce)` (déjà en place — le conserver).
7. **Cible WebView2** (Chromium récent) : pas besoin de polyfills legacy, mais rester
   en CSS/JS standard, sans dépendance réseau (tout offline, embarqué).

---

## 4. Architecture & fichiers (ce que tu touches)

Le programme est dans le sous-dossier repo **`video-audio_converter/`**. Le front vit
dans le package Python :

```
src/youtube_converter/
├── app.py                      # PONT pywebview (classe Api) — contrat front↔back (§5)
├── resources/
│   ├── web/
│   │   ├── index.html          # structure (tu édites)
│   │   ├── style.css           # thème + composants (tu édites)
│   │   └── app.js              # logique front + bridge + rendu (tu édites)
│   └── translations/           # fr.json / en.json / es.json / de.json (i18n)
├── core/                       # logique métier — NE PAS TOUCHER pour l'UX
└── config/
    └── theme.py                # ⚠ contient une palette "cyan" PÉRIMÉE et inutilisée
                                #   par le rendu (le CSS est la vraie source). Ignore-la
                                #   ou propose de l'aligner/supprimer.
```

**Tu édites essentiellement : `index.html`, `style.css`, `app.js`** (+ les 4 JSON i18n
si nouveaux libellés). Données utilisateur (réglages/historique) : `%APPDATA%\YouTubeConverter\`.

---

## 5. Contrat API (à NE PAS casser)

Le front appelle ces méthodes (toutes `async`, via `window.pywebview.api`) :

| Méthode | Rôle |
|---|---|
| `get_config()` | état initial : `{output_dir, ffmpeg_ok, language, translations, profiles, defaults{…}, history}` |
| `set_language(lang)` | change la langue, renvoie le dict de traductions |
| `save_pref(key, value)` | persiste une préférence |
| `validate_url(url)` | bool |
| `apply_profile(name)` | renvoie `{video_format, video_quality, compression}` |
| `browse_folder()` | dialogue dossier, renvoie le chemin |
| `add_task(payload)` | ajoute à la file, renvoie la file |
| `remove_task(index)` / `clear_queue()` | renvoient la file |
| `start_queue()` / `stop_queue()` | démarre/arrête (start renvoie bool) |
| `get_queue()` / `get_history()` | renvoient les listes |
| `export_history_csv()` / `clear_history()` | export / vidage |
| `open_folder()` | ouvre le dossier de sortie |
| `play_file(filepath)` | ouvre le fichier (bool) |

`payload` de `add_task` : `{url, format_type:"mp4"|"audio", video_quality, video_format,
compression_enabled, compression_preset, audio_format, audio_bitrate, filename_template}`.

**Événements push Python → JS** (via la fonction globale `window.onPush(event, data)`) :

- `progress` → `{percent}`
- `status` → `{message}`
- `task_start` → `{task}`
- `task_complete` → `{success, message, filepath}`
- `queue_empty`

Tu peux **réorganiser l'UI librement** tant que ces appels et ces événements restent
honorés (tu peux en afficher le résultat différemment, mais pas les supprimer).

---

## 6. Inventaire de l'UI actuelle

Layout : **CSS grid** `230px` (sidebar) + `1fr` (main scrollable), plein écran.

**Sidebar** : logo `>_ ytconverter` · nav (File d'attente + badge / Historique) ·
sélecteur de langue · pastille `ffmpeg :: ok|✕` · ligne version.

**Main** (de haut en bas) :
1. **Term-bar** : 3 points type fenêtre + `momoe@yt-converter:~/downloads$` + curseur clignotant.
2. **Header** : `h1` (préfixe `> `) + sous-titre.
3. **Card URL** : input + statut `✓/✕` (bordure verte/rouge selon validité).
4. **Card Destination** : chemin (lecture seule) + bouton `Parcourir…`.
5. **Card Configuration** : toggle segmenté **Vidéo / Audio** ; options vidéo
   (Qualité, Conteneur, Profil, Nom de fichier, case « Compresser (ré-encodage) » +
   preset) ; options audio (Format, Bitrate). Bitrate désactivé pour flac/wav.
6. **Actions** : `Ajouter vidéo`, `Ajouter audio`, `Démarrer`, `Arrêter` (caché par défaut).
7. **Card Progression** : barre rayée animée + `%`.
8. **Post-actions** (cachées jusqu'à fin) : `Ouvrir le dossier`, `Lire le fichier`.
9. **Onglet File** / **Onglet Historique** : listes de `row` (dot de statut + tag
   `VID/AUD` + titre + sous-ligne ; bouton `×` pour retirer un item en attente).
10. **Card Log** : `// log`, lignes horodatées colorées (ok/err/warn).

**États** : url valid/invalid ; dots `pending/downloading/success/error` ;
barre `done` (verte) ; boutons disabled pendant un run ; listes vides → `—`.

---

## 7. Design tokens actuels (variables CSS, `style.css` `:root`)

```
surfaces : --bg #0a0a0f  --bg-2 #0c0c13  --panel #111019  --panel-2 #15131f
           --input #0d0c14  --line #241f36  --line-soft #1b1828
accent   : --mauve #b794f6  --mauve-bright #d2bdff  --mauve-deep #8b5cf6  --mauve-dim #6d5a9c
glows    : --glow / --glow-strong (rgba violet)
statut   : --green #58e6a6  --red #ff6b8b  --amber #ffcc66
texte    : --text #d9d4ec  --text-dim #6f6a89
type     : --mono "Cascadia Code","Cascadia Mono","JetBrains Mono","Consolas",ui-monospace
forme    : --radius 10px
motion   : --ease-out / --ease-in / --ease-spring / --ease-smooth
```

Signatures visuelles à conserver (ou faire évoluer avec intention) : overlay
**scanlines** CRT, **chrome terminal**, boutons « **bracketed** » `[ … ]`, préfixes
`> ` `$ ` `// ` `· `, **checkbox monospace** `[x]`, barre de progression **rayée**,
**dots** de statut lumineux, entrées de **log horodatées**, animation `rise` des cards.

---

## 8. i18n (fonctionnement)

- HTML : `data-i18n="cle.point.ee"` (texte) et `data-i18n-ph="…"` (placeholder).
- `app.js` applique le dict reçu de `get_config()` / `set_language()`.
- Clés existantes : `app_title`, `app_subtitle`, et un namespace `ui.*`
  (`ui.queue_nav`, `ui.url_label`, `ui.config_title`, `ui.format_video`, …).
- **Tout nouveau libellé** ⇒ ajouter la clé dans `fr/en/es/de.json`.

---

## 9. Pièges connus

- `docs/design/*.md` (sauf ce fichier) = **périmés** (ancienne UI tkinter). Ignore-les.
- `config/theme.py` = palette **cyan** non utilisée par le rendu réel (le CSS prime).
- L'app embarque **yt-dlp** ; sans rapport avec l'UX mais : garder yt-dlp à jour
  (sinon téléchargements bridés). Hors de ton périmètre.
- Ne ré-introduis pas l'ancienne UI customtkinter.

---

## 10. Méthode de travail & PREVIEW (important)

`app.js` contient un **mode preview navigateur** : si `window.pywebview` est absent,
au `DOMContentLoaded` il **injecte des données d'exemple** (file, historique,
progression 62 %). Donc tu peux **itérer le design sans Python** :

- **Preview rapide** : ouvrir `src/youtube_converter/resources/web/index.html` dans un
  navigateur Chromium (ou servir le dossier) → l'UI s'affiche peuplée. Idéal pour
  CSS/layout, captures, responsive, reduced-motion.
- **App réelle** (pour tester le vrai pont) : depuis la racine du repo
  `video-audio_converter/` :
  `venv\Scripts\python.exe -m youtube_converter`
- **Toujours** fournir une preuve (capture/avant-après) et vérifier : pas d'emoji,
  focus visible, contraste suffisant, reduced-motion respecté, i18n complète.

---

## 11. Format de livraison attendu

1. **Audit UX** : problèmes priorisés (impact × effort), ancrés sur l'UI réelle.
2. **Propositions** : direction(s) + maquettes/diffs ciblés, justifiées.
3. **Implémentation incrémentale** : éditer `index.html` / `style.css` / `app.js`
   (+ JSON i18n), petite étape à la fois, vérifiable en preview.
4. **Preuve** : captures avant/après et points de vérification (§10).

> Démarre par : lire `index.html`, `style.css`, `app.js` (et les 4 JSON i18n), ouvrir
> la preview navigateur, puis livrer l'audit UX **avant** de coder.

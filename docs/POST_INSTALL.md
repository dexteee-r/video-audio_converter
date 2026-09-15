# Après l'installation — dépendance FFmpeg

`YouTubeConverter.exe` ne fonctionne pas seul : il a besoin de **FFmpeg** installé
sur votre machine et accessible dans le **PATH** Windows. FFmpeg n'est **pas**
inclus dans l'exécutable (pour garder sa taille raisonnable).

## À quoi sert FFmpeg ici

- Fusionner la vidéo et l'audio téléchargés séparément (formats HD/4K)
- Convertir l'audio (MP3, M4A, FLAC, WAV, OGG)
- Ré-encoder si la compression optionnelle est activée dans les Réglages

Sans FFmpeg, seuls quelques formats basse qualité déjà fusionnés (ex. 360p)
peuvent fonctionner, et l'export audio est impossible.

## Installation (Windows)

**Option recommandée — via winget** (Windows 10/11, PowerShell) :

```powershell
winget install ffmpeg
```

Fermez et rouvrez votre terminal (et l'application) après l'installation pour
que le PATH mis à jour soit pris en compte.

**Option manuelle** :

1. Téléchargez un build Windows sur https://www.gyan.dev/ffmpeg/builds/
   (section « release full » ou « release essentials »)
2. Extrayez l'archive, par ex. dans `C:\ffmpeg\`
3. Ajoutez `C:\ffmpeg\bin` au PATH :
   - Rechercher Windows → « Modifier les variables d'environnement système »
   - Bouton **Variables d'environnement…**
   - Dans **Variables système**, sélectionnez `Path` → **Modifier** → **Nouveau**
   - Collez `C:\ffmpeg\bin`, validez (OK partout)
4. **Redémarrez** l'application (et toute fenêtre de terminal ouverte)

## Vérifier l'installation

Ouvrez un terminal (PowerShell ou cmd) et lancez :

```powershell
ffmpeg -version
```

Si une version s'affiche, c'est bon. Si vous obtenez
« ffmpeg n'est pas reconnu en tant que commande interne… », le PATH n'est pas
à jour (redémarrez le terminal) ou l'installation a échoué.

## Dépannage

| Problème | Solution |
|----------|----------|
| L'app affiche « FFmpeg non détecté » | Installez FFmpeg (ci-dessus) puis **redémarrez l'application** |
| `ffmpeg -version` fonctionne mais l'app dit toujours qu'il manque | Fermez complètement l'app (icône barre des tâches incluse) et relancez-la — le PATH est lu au démarrage |
| Téléchargement plafonné à 360p sans FFmpeg | Normal : sans fusion audio/vidéo, seul le format déjà muxé le plus bas est utilisable — installez FFmpeg |
| La fenêtre de l'app ne s'ouvre pas du tout | Ce n'est pas lié à FFmpeg : installez le [WebView2 Runtime](https://developer.microsoft.com/microsoft-edge/webview2/) |

## Données de l'application

Réglages, historique et logs sont stockés dans `%APPDATA%\YouTubeConverter\`
(rien n'est écrit à côté de l'exécutable, aucun droit administrateur requis).

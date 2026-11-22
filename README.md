# launcher-catalog

Spieleliste für den [Mett Launcher](https://github.com/Mett-Gaming/mett-launcher). Der Launcher liest `games.json` direkt von
`https://raw.githubusercontent.com/Mett-Gaming/launcher-catalog/main/` und merkt sich die letzte gültige Fassung für den Offline-Betrieb.
Ein Push auf `main` reicht, damit alle Launcher das neue Spiel beim nächsten Start anzeigen.

## Neues Spiel aufnehmen

1. Das Spiel liegt als öffentliches Repo unter `Mett-Gaming/` und veröffentlicht GitHub-Releases mit Tags `vX.Y.Z` und einem Zip als Asset.
2. Cover (`covers/<id>.png`, 600×800) und Hero (`covers/<id>-hero.png`, 1920×620, ohne Text – der Launcher schreibt den Namen darüber) ablegen.
3. Eintrag in `games.json` ergänzen und pushen. Die CI prüft das Schema.

## Felder (Schema 1)

| Feld | Pflicht | Bedeutung |
|---|---|---|
| `id` | ja | Kurzname, nur `a-z0-9._-`. Wird zum Ordnernamen der Installation. |
| `name` | ja | Anzeigename. |
| `repo` | ja | `owner/name` des Spiel-Repos. |
| `tagline` | nein | Kurzbeschreibung. |
| `cover`, `hero` | nein | Bildpfade relativ zu diesem Repo. |
| `assetPattern` | ja | Regex für den Dateinamen des Release-Zips. |
| `stripTopFolder` | nein | `true`, wenn das Zip einen einzelnen Oberordner enthält (Standard `true`). |
| `exe` | ja | Startdatei relativ zum Installationsordner. |
| `args` | nein | Startargumente. |
| `preserve` | nein | Pfade im Installationsordner, die Updates überleben (z. B. Spielstände neben der exe). |
| `includePrereleases` | nein | Pre-Releases als normale Updates anbieten. |

`tools/make-kasse0-art.py` erzeugt die KASSE-0-Bilder (`uv run tools/make-kasse0-art.py <ArchivoBlack-Regular.ttf>`).

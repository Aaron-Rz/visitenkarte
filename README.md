# Visitenkarte

Kontaktseite für die NFC-Visitenkarte von Aaron Ratz: Kontakt speichern (vCard mit Foto) und LinkedIn mit einem Tipp.
Statisch, ohne Tracking und Cookies, ohne externe Anfragen (die Schrift liegt selbst gehostet in `fonts/`). Gehostet über GitHub Pages.

## Dateien

- `index.html`: die Seite (handgeschrieben)
- `daten.json`: Name, Titel, Telefon, E-Mail, LinkedIn für die vCard
- `build.py`: erzeugt `aaron-ratz.vcf` aus `daten.json` und `profil.jpg`
- `profil.jpg`, `apple-touch-icon.png`: werden von `build.py` aus einem Foto erzeugt

## Foto setzen oder ändern

```sh
python3 build.py /pfad/zum/foto.jpg              # mittig quadratisch zuschneiden, 480 px, ins vCard einbetten
python3 build.py /pfad/zum/foto.jpg 180:320:720  # eigener Ausschnitt: x:y:kantenlänge in Pixeln des Originals
```

Aktuelles Foto: `WhatsApp Image 2025-12-21 at 12.17.17 (1).jpeg` (1066×1600) mit Ausschnitt `180:320:720`.

Design nach der physischen Karte: mattschwarz, Name als silberne Serifenschrift (Crimson Pro, selbst gehostet).
Der „Kontakt speichern“-Link hat bewusst kein `download`-Attribut, sonst legt iOS-Safari die vCard in „Dateien“ ab,
statt direkt „Kontakt hinzufügen“ zu zeigen.

Braucht `ffmpeg`. HEIC vorher in JPEG umwandeln.

## Daten ändern

`daten.json` anpassen, `python3 build.py` laufen lassen. Telefon und E-Mail stehen zusätzlich in `index.html`
(die Links unten auf der Seite), dort mit ändern.

## Eigene Domain

1. Beim Domain-Anbieter eintragen:
   - `A` für `@`: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - `CNAME` für `www`: `aaron-rz.github.io`
2. Datei `CNAME` mit der Domain anlegen (z. B. `aaronratz.de`), committen, pushen.
3. In den Repo-Einstellungen unter Pages die Custom Domain setzen und „Enforce HTTPS“ einschalten.
4. In `index.html` `og:image` und `og:url` mit der absoluten Domain-URL ergänzen (für Link-Vorschauen).

Die NFC-Karte erst beschreiben, wenn die Domain mit HTTPS läuft.

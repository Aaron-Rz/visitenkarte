#!/usr/bin/env python3
"""Erzeugt aaron-ratz.vcf (und optional profil.jpg) aus daten.json.

  python3 build.py                          # nur vCard neu bauen
  python3 build.py FOTO.jpg                 # mittiges Quadrat zuschneiden, dann vCard bauen
  python3 build.py FOTO.jpg X:Y:KANTE       # eigenes Quadrat (Pixel im Original)

Zuschnitt läuft über ffmpeg (Quadrat, 480 px, JPEG).
"""
import base64
import json
import subprocess
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
FOTO = HIER / "profil.jpg"
ICON = HIER / "apple-touch-icon.png"
VCF = HIER / "aaron-ratz.vcf"
MAX_FOTO_BYTES = 80_000


def foto_zuschneiden(quelle: Path, ausschnitt: str | None = None) -> None:
    if ausschnitt:
        x, y, kante = ausschnitt.split(":")
        quadrat = f"crop={kante}:{kante}:{x}:{y}"
    else:
        quadrat = "crop='min(iw,ih)':'min(iw,ih)'"
    # Qualität schrittweise senken, bis das Foto klein genug für die vCard ist
    for q in (3, 5, 7, 9, 12):
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(quelle),
             "-vf", f"{quadrat},scale=480:480", "-q:v", str(q), str(FOTO)],
            check=True,
        )
        if FOTO.stat().st_size <= MAX_FOTO_BYTES:
            break
    FOTO.write_bytes(jpeg_bereinigen(FOTO.read_bytes()))
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(FOTO),
         "-vf", "scale=180:180", str(ICON)],
        check=True,
    )
    print(f"profil.jpg: {FOTO.stat().st_size // 1024} KB")


def jpeg_bereinigen(jpeg: bytes) -> bytes:
    """Entfernt Metadaten-Segmente (APP1–APP15, z. B. EXIF/ICC, und COM); JFIF-Kopf (APP0) und Bilddaten bleiben.

    Manche vCard-Importe sind bei eingebetteten Fotos empfindlich; ein schlichtes Baseline-JPEG ist am sichersten.
    """
    if jpeg[:2] != b"\xff\xd8":
        raise ValueError("kein JPEG")
    raus, i = bytearray(b"\xff\xd8"), 2
    while i < len(jpeg):
        if jpeg[i] != 0xFF:
            raise ValueError(f"unerwartetes Byte an Position {i}")
        marker = jpeg[i + 1]
        if marker == 0xDA:  # Start of Scan: Rest sind Bilddaten
            raus += jpeg[i:]
            break
        laenge = int.from_bytes(jpeg[i + 2:i + 4], "big")
        if not (0xE1 <= marker <= 0xEF or marker == 0xFE):
            raus += jpeg[i:i + 2 + laenge]
        i += 2 + laenge
    return bytes(raus)


def escape(wert: str) -> str:
    return (wert.replace("\\", "\\\\").replace(",", "\\,")
            .replace(";", "\\;").replace("\n", "\\n"))


def falten(zeile: str) -> str:
    """vCard-Line-Folding: max. 75 Oktette pro Zeile, Fortsetzung mit Leerzeichen."""
    roh = zeile.encode("utf-8")
    teile, start, breite = [], 0, 75
    while start < len(roh):
        ende = min(start + breite, len(roh))
        # nicht mitten in einem UTF-8-Zeichen trennen
        while ende < len(roh) and (roh[ende] & 0xC0) == 0x80:
            ende -= 1
        teile.append(roh[start:ende].decode("utf-8"))
        start, breite = ende, 74
    return "\r\n ".join(teile)


def vcard_bauen(d: dict) -> str:
    zeilen = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{escape(d['nachname'])};{escape(d['vorname'])};;;",
        f"FN:{escape(d['vorname'] + ' ' + d['nachname'])}",
        f"TITLE:{escape(d['titel'])}",
        f"TEL;TYPE=CELL,VOICE:{d['telefon']}",
        f"EMAIL;TYPE=INTERNET,PREF:{d['email']}",
        # bewusst kein URL-Feld: iOS zeigte LinkedIn sonst doppelt (Homepage + Social-Profil)
        # iOS zeigt den TYPE-Wert als Dienstnamen an, daher „LinkedIn“ mit großem L
        f"X-SOCIALPROFILE;TYPE=LinkedIn;x-user={d['linkedin'].rstrip('/').rsplit('/', 1)[-1]}:{d['linkedin']}",
    ]
    if d.get("notiz"):
        zeilen.append(f"NOTE:{escape(chr(10).join(d['notiz']))}")
    if FOTO.exists():
        b64 = base64.b64encode(jpeg_bereinigen(FOTO.read_bytes())).decode("ascii")
        zeilen.append(f"PHOTO;ENCODING=b;TYPE=JPEG:{b64}")
    zeilen.append("END:VCARD")
    return "".join(falten(z) + "\r\n" for z in zeilen)


def main() -> None:
    if len(sys.argv) > 1:
        foto_zuschneiden(Path(sys.argv[1]), sys.argv[2] if len(sys.argv) > 2 else None)
    daten = json.loads((HIER / "daten.json").read_text(encoding="utf-8"))
    VCF.write_bytes(vcard_bauen(daten).encode("utf-8"))
    print(f"{VCF.name}: {VCF.stat().st_size // 1024} KB, Foto: {'ja' if FOTO.exists() else 'nein'}")


if __name__ == "__main__":
    main()

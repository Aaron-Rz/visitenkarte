#!/usr/bin/env python3
"""Bereitet die öffentlichen Nachweis-PDFs für /profile auf.

  python dokumente.py QUELLORDNER

Braucht PyMuPDF (pip install pymupdf). Pro Dokument: Privatadresse schwärzen (echte Schwärzung,
bei Scans werden die Bildpixel überschrieben), Metadaten entfernen, Bilder verkleinern,
Ergebnis nach profile/docs/. In amtlichen Dokumenten wird nur geschwärzt, nie Text eingefügt.
"""
import sys
from pathlib import Path

import pymupdf

ZIEL = Path(__file__).resolve().parent.parent / "profile" / "docs"
SCHWARZ = (0.1, 0.1, 0.1)

# Ziel-Datei, Quell-Datei, Schwärzungen: Texte (Textebene) oder (Seite, Rechteck in PDF-Punkten, sichtbare Lage) für Scans
DOKUMENTE = [
    ("reference-werbeliebe.pdf", "Aaron_Ratz_Arbeitszeugnis_Werbeliebe.pdf", []),
    ("reference-tv-bw.pdf", "Aaron Ratz Zeugnis TVBW Praktikum.pdf", [(0, (322, 223.5, 499, 236))]),
    ("reference-schwabenrepro.pdf", "Aaron Ratz Zeugnis Schwabenrepro Praktikum.pdf", ["Kinzigstraße 22", "75210 Keltern"]),
    ("transcript-hs-pforzheim.pdf", "Prüfungsbescheinigung HS Pforzheim Aaron Ratz.pdf", []),
    ("transcript-abitur.pdf", "Allgemeine Hochschulreife Zeugnis Aaron Ratz.pdf", [(0, (255, 528, 425, 547))]),
    ("certificate-inside-lvmh.pdf", "Aaron Ratz - INSIDE LVMH CERTIFICATE - Track 2.pdf", []),
    ("certificate-bocconi.pdf", "Certificate Bocconi.pdf", []),
    ("certificate-mckinsey-forward.pdf", "McKinsey.orgForward Certificate.pdf", []),
    ("certificate-hootsuite.pdf", "CertificateOfCompletion_Social Media Marketing Professional Certificate by Hootsuite.pdf", []),
    ("certificate-dgp.pdf", "DGP Teilnahmezertifikat.pdf", []),
]


SCAN_DPI = 200
# Diese PDFs werden zusätzlich gerastert, weil einzelne Objekte (Vektor-Logo, verlustfreie Alphamasken) sie > 1,5 MB machen
RASTERN = {"reference-schwabenrepro.pdf", "certificate-inside-lvmh.pdf"}


def schwaerzen(doc: pymupdf.Document, schwaerzungen: list) -> int:
    """Text-Schwärzungen auf der Textebene; liefert die Zahl der Treffer."""
    treffer = 0
    for text in schwaerzungen:
        for seite in doc:
            for rect in seite.search_for(text):
                seite.add_redact_annot(rect + (-1, -1, 1, 1), fill=SCHWARZ)
                treffer += 1
    for seite in doc:
        seite.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_PIXELS, graphics=pymupdf.PDF_REDACT_LINE_ART_NONE)
    return treffer


def scan_schwaerzen(doc: pymupdf.Document, bereiche: list) -> pymupdf.Document:
    """Scans: jede Seite in sichtbarer Lage rastern, Bereiche direkt in den Pixeln füllen, neues PDF bauen.

    Die Originalseite (oft gedreht und aus Bildkacheln zusammengesetzt) fällt komplett weg, deshalb bleibt
    unter dem Balken garantiert nichts übrig.
    """
    faktor = SCAN_DPI / 72
    neu = pymupdf.open()
    for nr, seite in enumerate(doc):
        pix = seite.get_pixmap(dpi=SCAN_DPI)
        for seiten_nr, (x0, y0, x1, y1) in bereiche:
            if seiten_nr == nr:
                pix.set_rect(pymupdf.IRect(x0 * faktor, y0 * faktor, x1 * faktor, y1 * faktor),
                             tuple(round(c * 255) for c in SCHWARZ))
        ziel = neu.new_page(width=seite.rect.width, height=seite.rect.height)
        ziel.insert_image(ziel.rect, stream=pix.tobytes("jpeg", jpg_quality=80))
    return neu


def main() -> None:
    quelle = Path(sys.argv[1])
    ZIEL.mkdir(parents=True, exist_ok=True)
    for ziel, datei, schwaerzungen in DOKUMENTE:
        doc = pymupdf.open(quelle / datei)
        texte = [s for s in schwaerzungen if isinstance(s, str)]
        bereiche = [s for s in schwaerzungen if not isinstance(s, str)]
        treffer = schwaerzen(doc, texte)
        if treffer < len(texte):
            raise SystemExit(f"{datei}: nur {treffer} von {len(texte)} Text-Schwärzungen gefunden")
        if bereiche or ziel in RASTERN:
            doc = scan_schwaerzen(doc, bereiche)
            treffer += len(bereiche)
        doc.set_metadata({})
        doc.del_xml_metadata()
        doc.rewrite_images(dpi_threshold=170, dpi_target=150, quality=78)
        doc.subset_fonts()  # voll eingebettete Schriften machen manche Zertifikate > 1 MB
        doc.ez_save(ZIEL / ziel, garbage=4, clean=True)
        print(f"{ziel:34} {(ZIEL / ziel).stat().st_size // 1024:>5} KB  Schwärzungen: {treffer}")


if __name__ == "__main__":
    main()

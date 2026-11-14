// Rendert den Lebenslauf aus lebenslauf.json in ein Element; genutzt von profile/index.html (en) und cv-druck.html (en/de).
const BESCHRIFTUNG = {
  en: { erfahrung: "Experience", bildung: "Education", faehigkeiten: "Skills", sprachen: "Languages", zertifikate: "Certificates" },
  de: { erfahrung: "Berufserfahrung", bildung: "Ausbildung", faehigkeiten: "Fähigkeiten", sprachen: "Sprachen", zertifikate: "Zertifikate" },
};

function el(tag, klasse, text) {
  const e = document.createElement(tag);
  if (klasse) e.className = klasse;
  if (text !== undefined) e.textContent = text;
  return e;
}

function station(eintrag, sprache) {
  const li = el("li", "station");
  li.append(el("p", "zeit", eintrag.zeit[sprache]));
  const inhalt = el("div", "inhalt");
  const ort = typeof eintrag.ort === "string" ? eintrag.ort : eintrag.ort[sprache];
  inhalt.append(el("p", "rolle", eintrag.rolle[sprache]), el("p", "ort", ort));
  const punkte = eintrag.punkte?.[sprache] ?? [];
  if (punkte.length) {
    const ul = el("ul", "punkte");
    punkte.forEach(p => ul.append(el("li", "", p)));
    inhalt.append(ul);
  }
  li.append(inhalt);
  return li;
}

function abschnitt(titel, inhalt) {
  const s = el("section", "cv-abschnitt");
  s.append(el("h3", "", titel), inhalt);
  return s;
}

export async function lebenslaufLaden(url = "lebenslauf.json") {
  const antwort = await fetch(url);
  if (!antwort.ok) throw new Error(`Lebenslauf nicht geladen (${antwort.status})`);
  return antwort.json();
}

export function lebenslaufRendern(ziel, daten, sprache = "en") {
  const t = BESCHRIFTUNG[sprache];
  ziel.replaceChildren();
  ziel.append(el("p", "cv-profil", daten.profil[sprache]));

  const erfahrung = el("ol", "stationen");
  daten.erfahrung.forEach(e => erfahrung.append(station(e, sprache)));
  ziel.append(abschnitt(t.erfahrung, erfahrung));

  const bildung = el("ol", "stationen");
  daten.bildung.forEach(e => bildung.append(station(e, sprache)));
  ziel.append(abschnitt(t.bildung, bildung));

  const faehigkeiten = el("dl", "faehigkeiten");
  daten.faehigkeiten.forEach(f => {
    faehigkeiten.append(el("dt", "", f.stufe[sprache]), el("dd", "", f.liste[sprache].join(" · ")));
  });
  // Sprachen als letzte Zeile der Fähigkeiten: eine Überschrift weniger, der Druck-Lebenslauf bleibt einseitig
  faehigkeiten.append(el("dt", "", t.sprachen), el("dd", "", daten.sprachen[sprache].join(" · ")));
  ziel.append(abschnitt(t.faehigkeiten, faehigkeiten));

  const zertifikate = el("ul", "zertifikate");
  daten.zertifikate[sprache].forEach(z => zertifikate.append(el("li", "", z)));
  ziel.append(abschnitt(t.zertifikate, zertifikate));
}

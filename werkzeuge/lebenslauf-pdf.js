// Erzeugt profile/docs/cv-aaron-ratz-{en,de}.pdf aus profile/cv-druck.html.
//
//   PLAYWRIGHT_CORE=/pfad/zu/playwright-core CHROMIUM=/pfad/zu/chrome node werkzeuge/lebenslauf-pdf.js
//
// Startet selbst einen kleinen Webserver auf dem Repo (die Vorlage lädt lebenslauf.json per fetch).
const http = require("http");
const fs = require("fs");
const path = require("path");
const { chromium } = require(process.env.PLAYWRIGHT_CORE || "playwright-core");

const REPO = path.resolve(__dirname, "..");
const TYPEN = { ".html": "text/html", ".js": "text/javascript", ".json": "application/json", ".jpg": "image/jpeg", ".woff2": "font/woff2" };

const server = http.createServer((req, res) => {
  const datei = path.join(REPO, decodeURIComponent(new URL(req.url, "http://x").pathname));
  if (!datei.startsWith(REPO) || !fs.existsSync(datei) || fs.statSync(datei).isDirectory()) {
    res.writeHead(404).end();
    return;
  }
  res.writeHead(200, { "Content-Type": TYPEN[path.extname(datei)] || "application/octet-stream" });
  fs.createReadStream(datei).pipe(res);
});

server.listen(0, "127.0.0.1", async () => {
  const basis = `http://127.0.0.1:${server.address().port}`;
  const browser = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
  try {
    const page = await browser.newPage();
    for (const sprache of ["en", "de"]) {
      await page.goto(`${basis}/profile/cv-druck.html?lang=${sprache}`);
      await page.waitForSelector("body[data-fertig]");
      const ziel = path.join(REPO, "profile", "docs", `cv-aaron-ratz-${sprache}.pdf`);
      await page.pdf({ path: ziel, format: "A4", printBackground: true, preferCSSPageSize: true });
      console.log(ziel, Math.round(fs.statSync(ziel).size / 1024), "KB");
    }
  } finally {
    await browser.close();
    server.close();
  }
});

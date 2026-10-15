# BRIEFING: Gozo Cottage – Relaunch als moderne Pitch Page (SEO + GEO optimiert)

## 0. Pflicht vor dem Start
1. Lade den **Pitch Page Skill** und halte dich an seine Struktur, Design-Regeln und Output-Vorgaben. Er hat Vorrang vor allgemeinen Design-Entscheidungen.
2. Lies **alle** Bilder in:
   `/Users/david/Documents/RevenueWorks_Projects/Gozo_cottage/INFO/Images`
   Schau dir jedes Bild an und notiere kurz, was drauf ist (Produkt, Ort, Stimmung). Das brauchst du für Platzierung und Alt-Texte.
3. Crawle die Originalseite **https://www.gozocottage.com/** vollständig: Startseite, alle Unterseiten, Impressum/Legal, Datenschutz, AGB, Kontakt.
   Prüfe außerdem **https://www.facebook.com/GozoCottage/** (Öffnungszeiten, Adresse, Telefon, weitere Social-Links), soweit öffentlich lesbar.

Lege danach eine Datei `research.md` an mit:
- allen Fakten (Firmenname, Adresse, Telefon, E-Mail, Öffnungszeiten, Registernummer/VAT, Social-Links)
- dem echten Produktsortiment, so wie es auf der Seite steht
- allen Rechtstexten (wörtlich übernommen)
- einer Bild-Inventarliste (Dateiname → Inhalt → geplante Position auf der Seite)

## 1. Oberste Regel: Keine erfundenen Fakten
- Nutze **nur** Infos, die auf gozocottage.com oder der Facebook-Seite stehen.
- Adresse, Telefon, Geo-Koordinaten, Öffnungszeiten, Preise, Firmendaten: **nur echte Werte**. Fehlt etwas → `<!-- TODO: fehlt -->` im Code + Eintrag in `open-questions.md`. Niemals Platzhalter erfinden.
- Produktkategorien (Weine, Liköre, Käse, Wurstwaren, Marmeladen, Olivenöl, Essig): Nur die aufnehmen, die Gozo Cottage **wirklich** anbietet. Wenn eine Kategorie aus diesem Briefing auf der Originalseite nicht vorkommt → weglassen und in `open-questions.md` vermerken.
- Schema-Typ passend wählen: `Winery` nur, wenn sie selbst Wein herstellen. Sonst `LocalBusiness` / `Store` / `FoodEstablishment` – je nachdem, was die Fakten hergeben.
- Keine erfundenen Bewertungen, Zitate, Auszeichnungen oder Jahreszahlen.

## 2. Ziel
Eine neue, moderne One-Page-Website (Pitch Page), die:
- Gozo Cottage als **lokalen Produzenten authentischer gozitanischer Produkte** eindeutig positioniert
- bei Google (inkl. AI Overviews) und in KI-Suchen (ChatGPT, Perplexity, Claude) für Gozo-Food-Suchanfragen zitiert wird
- auf dem Handy perfekt läuft (mobile first)
- **alle** Bilder aus dem Ordner sinnvoll nutzt

**Sprache der Website:** Englisch.

## 3. Marke & Ton
- **Marke:** Gozo Cottage
- **Nische:** Authentische Produkte aus Gozo – Wein, Liköre, Marmeladen, Olivenöl, Käse, Wurstwaren (nur was real angeboten wird)
- **Zielgruppe:** Touristen, Malteser, Foodies, Souvenir-Käufer, Export-Kunden
- **Ton:** authentisch, warm, traditionell aber modern, stolz auf Gozo
- **Look:** modern, hochwertig, mediterran (warme Erdtöne, Kalkstein, Olivgrün, Meerblau), große Bilder, viel Luft. Kein Template-Look.

## 4. Seitenstruktur & Überschriften
**H1 (genau einmal):**
`Authentic Gozitan Produce & Artisanal Delicacies | Gozo Cottage`

**H2-Abschnitte:**
1. Traditional Gozo Wines & Liqueurs
2. Artisanal Jams & Olive Oils
3. Handcrafted Gozo Cheeses & Cured Meats
4. Grown & Harvested in Gozo
5. What Are Traditional Food Products from Gozo? (direkte Antwort-Sektion)
6. Frequently Asked Questions
7. Visit / Contact
(H2 für nicht angebotene Kategorien weglassen, siehe Regel 1.)

Darunter saubere H3s. Keine Überschriften-Ebene überspringen.

## 5. Inhalt (SEO + GEO)
**Haupttext:** 300–500 Wörter, keyword-stark, aber natürlich lesbar. Fokus: „Grown & Harvested in the Island Region of Gozo“.

**Keywords einbauen:** Gozo authentic produce, traditional Gozo food, Gozitan wine, local Gozo jams, traditional Maltese souvenirs, Gozo cottage products.

**GEO-Begriffe im Fließtext verankern:** Island of Gozo, Maltese Archipelago, Mediterranean gastronomy, Gozitan farmers, Victoria Gozo.

**Eigener Abschnitt zur Tradition der Landwirtschaft auf Gozo:** Mediterranean climate, terraced fields, fresh groundwater. Allgemeine Fakten über Gozo sind ok – aber nichts über Gozo Cottage behaupten, was nicht belegt ist.

**Direkt-Antworten für KI-Suchen:** Jede Antwort-Sektion beginnt mit einem klaren 1–2-Satz-Fazit, das allein stehend zitierbar ist. Danach Details. Keine Floskeln, kein Marketing-Blabla.

## 6. FAQ-Sektion (am Ende der Seite)
Jede Antwort **40–60 Wörter**, sachlich, direkt, ohne Floskeln:
1. What products does Gozo Cottage produce?
2. Are Gozo Cottage products authentic to the island of Gozo?
3. Can I buy Gozo Cottage wines, cheeses, and jams online or at trade fairs?
4. What makes Gozitan agricultural produce unique?

Frage 3 nur mit echten Infos beantworten (Online-Shop? Messen? Laden?). Unklar → TODO + `open-questions.md`.
Inhalt der FAQ im HTML und im `FAQPage`-Schema muss **identisch** sein.

## 7. Meta-Tags & Open Graph (Pflicht für JEDE Seite)
**Regel:** Jede HTML-Seite (Startseite, Impressum, Datenschutz, AGB und jede weitere Unterseite) bekommt **immer** einen eigenen, gültigen, SEO- und AEO-optimierten Satz an Meta-Daten. Keine Seite ohne, keine doppelten Titel oder Beschreibungen, keine Platzhalter.

**Meta Title**
- Max. **60 Zeichen**, mindestens 30
- Wichtigstes Keyword vorne, Marke hinten: `[Keyword/Thema] | Gozo Cottage`
- Beschreibt genau den Inhalt der jeweiligen Seite
- Startseite z. B.: `Authentic Gozo Produce & Delicacies | Gozo Cottage`

**Meta Description**
- **120–155 Zeichen**
- Beantwortet direkt, was die Seite bietet (zitierfähig für KI-Suchen), mit Ortsbezug (Gozo, Malta) und klarem Call-to-Action
- Kein Keyword-Stopfen, keine Floskeln

**Open Graph (jede Seite)**
- `og:title` – darf etwas länger und emotionaler sein als der Title (max. 90 Zeichen)
- `og:description` – max. 200 Zeichen, passend zur Seite
- `og:image` – absolute URL, **1200×630 px**, unter 300 KB, passend zum Seiteninhalt (aus den echten Bildern zugeschnitten, als eigene Datei z. B. `/images/og/og-home.jpg`)
- `og:image:width`, `og:image:height`, `og:image:alt`
- `og:url` (absolut, = Canonical), `og:type` (`website` für Start, `article` für Unterseiten), `og:site_name=Gozo Cottage`, `og:locale=en_GB`

**Twitter Card (jede Seite)**
- `twitter:card=summary_large_image`, `twitter:title`, `twitter:description`, `twitter:image`, `twitter:image:alt`

**Weitere Pflicht-Tags**
- Canonical (absolut, Startseite: `https://www.gozocottage.com/`)
- `<meta name="robots" content="index, follow, max-image-preview:large">`
- `lang="en"`, Favicon + Apple-Touch-Icon

**Prüfung (in `seo-report.md` als Tabelle ausgeben)**
Für jede Seite: Title + Zeichenzahl, Description + Zeichenzahl, og:title, og:description, og:image-Pfad + Maße + Dateigröße. Jeder Wert außerhalb der Grenzen oder doppelt = Fehler → korrigieren, bevor committet wird.

Validiere jedes Schema (gültiges JSON, Pflichtfelder vollständig).

## 9. Bilder
- Alle Bilder aus dem Ordner in **WebP** (und optional AVIF) umwandeln, über `<picture>` mit Fallback ausliefern
- Sinnvolle Größen (z. B. 640 / 1280 / 1920 px Breite) mit `srcset` + `sizes`
- Explizite `width` und `height` an jedem Bild (gegen Layout-Springen)
- `loading="lazy"` für alles unter dem ersten Bildschirm; Hero-Bild **nicht** lazy, sondern `fetchpriority="high"` + Preload
- Aussagekräftige Alt-Texte, die beschreiben, was wirklich auf dem Bild ist, z. B. `alt="Gozo Cottage artisanal wine cellar with oak barrels in Gozo"`
- Dateinamen SEO-freundlich umbenennen (`gozo-cottage-olive-oil-bottles.webp`)

## 10. Technik & Performance
- Semantisches HTML5: `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<footer>`
- CSS und JS inline und minifiziert (Lesbare Quellversion zusätzlich mitliefern)
- `rel="preconnect"` für Google Fonts bzw. alle externen Domains
- Fonts mit `font-display: swap`, maximal 2 Schriften
- Kein unnötiges JS, kein jQuery, keine schweren Frameworks
- Barrierefreiheit: Kontraste nach WCAG AA, Fokus-Zustände, Skip-Link
- Ziel: Lighthouse ≥ 95 in Performance, SEO, Accessibility, Best Practices

## 11. Footer & Legal
- **Alle** Rechtsinfos der Originalseite übernehmen (Impressum, Datenschutz, AGB, Firmendaten, VAT-Nummer etc.) – inhaltlich unverändert
- Links zu Facebook und allen weiteren gefundenen Social-Profilen (Icons, `rel="noopener"`, `target="_blank"`)
- Kontaktdaten als klickbare Links (`tel:`, `mailto:`, Google-Maps-Link)

## 12. Qualitätscheck (vor Abgabe selbst prüfen)
- [ ] Genau eine H1, H2-Struktur wie in Punkt 4
- [ ] Title ≤ 60 Zeichen, Description ≤ 155 Zeichen (Zeichen zählen und ausgeben)
- [ ] Jede FAQ-Antwort 40–60 Wörter (Wörter zählen und ausgeben)
- [ ] Alle Bilder aus dem Ordner verwendet, alle mit Alt, width, height
- [ ] JSON-LD gültig, FAQ-Text identisch mit HTML
- [ ] Alle GEO-Begriffe aus Punkt 5 im Fließtext enthalten
- [ ] Keine erfundenen Fakten – jede Firmenangabe ist in `research.md` belegt
- [ ] Mobile Ansicht (375 px) geprüft – kein horizontales Scrollen
- [ ] Lighthouse-Lauf durchgeführt, Ergebnisse notiert
- [ ] Jede Seite hat eigene, gültige Meta Title, Description, OG- und Twitter-Tags inkl. 1200×630-Bild – keine Duplikate, alle Längen eingehalten

## 13. Lieferung
Im Projektordner `/Users/david/Documents/RevenueWorks_Projects/Gozo_cottage/`:
- `index.html` (fertig, minifiziert)
- `index.src.html` (lesbare Version)
- `/images/` (optimierte Bilder)
- `research.md` (Fakten + Quellen + Bild-Inventar)
- `open-questions.md` (alles, was fehlt oder unklar ist)
- `seo-report.md` (Title/Description mit Zeichenzahl, FAQ-Wortzahlen, Lighthouse-Werte, Checkliste)

Arbeite die Phasen der Reihe nach ab: Recherche → Gliederung → Texte → Build → Bilder → Schema → Check. Stopp nur, wenn etwas Unumkehrbares ansteht. Bei fehlenden Infos nicht raten, sondern TODO setzen und weitermachen.

## 14. Git: Commit & Push
Wenn alles fertig ist und der Qualitätscheck aus Punkt 12 bestanden ist:

1. Repo: `https://github.com/selecdoo/gozo_cottage.git`
   - Ist der Projektordner noch kein Git-Repo → `git init`, Remote `origin` auf diese URL setzen.
   - Ist schon ein Remote gesetzt → prüfen, dass `origin` auf diese URL zeigt.
2. Vor dem Commit `git pull origin main --rebase`, falls im Repo schon etwas liegt. Bei Konflikten **stoppen** und mir Bescheid geben – nichts überschreiben.
3. `.gitignore` anlegen (`.DS_Store`, `node_modules/`, temporäre Dateien). Die Original-Bilder aus `INFO/Images` nur committen, wenn sie unter 10 MB pro Datei sind – sonst nur die optimierten Bilder aus `/images/`.
4. Alles committen mit einer klaren Nachricht, z. B.:
   `feat: Gozo Cottage relaunch – modern pitch page, SEO/GEO, JSON-LD, optimized images`
5. Push auf den Branch `main`: `git push -u origin main`
6. **Kein Force-Push.** Wenn der Push abgelehnt wird (z. B. fehlende Rechte, Branch-Schutz), stoppen und mir die Fehlermeldung zeigen.
7. Zum Schluss ausgeben: Commit-Hash, Link zum Repo und Liste der gepushten Dateien.
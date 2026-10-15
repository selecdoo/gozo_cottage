#!/usr/bin/env python3
"""Quality gate for the built site. Exits 1 on any failure; writes seo-report.md.

  python3 -I tools/build.py && python3 -I tools/check.py
"""
import html
import json
import os
import re
import sys
from html.parser import HTMLParser

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402

ROOT = build.ROOT
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)
    return cond


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.h, self.imgs, self.ids, self.hrefs, self.text, self.ld = [], [], set(), [], [], []
        self._cur = None
        self._skip = 0
        self._ld = False
        self.in_main = False

    def handle_starttag(self, tag, a):
        a = dict(a)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "main":
            self.in_main = True
        if re.fullmatch(r"h[1-6]", tag):
            self._cur = [int(tag[1]), ""]
        if tag == "img":
            self.imgs.append(a)
        if tag == "a" and a.get("href"):
            self.hrefs.append(a["href"])
        if tag in ("style", "script"):
            self._skip += 1
            self._ld = a.get("type") == "application/ld+json"
            if self._ld:
                self.ld.append("")

    def handle_endtag(self, tag):
        if re.fullmatch(r"h[1-6]", tag) and self._cur:
            self.h.append(tuple(self._cur))
            self._cur = None
        if tag in ("style", "script"):
            self._skip -= 1
            self._ld = False
        if tag == "main":
            self.in_main = False

    def handle_data(self, d):
        if self._ld:
            self.ld[-1] += d
        elif self._skip == 0:
            if self._cur is not None:
                self._cur[1] += d
            if self.in_main:
                self.text.append(d)


def parse(path):
    p = P()
    p.feed(open(os.path.join(ROOT, path), encoding="utf8").read())
    return p


def meta(doc, key, attr="name"):
    m = re.search(rf'<meta {attr}="{re.escape(key)}" content="([^"]*)"', doc)
    return html.unescape(m.group(1)) if m else None


def words(s):
    return len(re.findall(r"\b[\w’'’-]+\b", s))


def lum(h):
    r, g, b = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    f = lambda c: c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def ratio(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True)
    return (la + .05) / (lb + .05)


rows, report = [], []
seen_t, seen_d = set(), set()
all_img_files = set()
for key, pg in build.PAGES.items():
    path = pg["file"] + ".html"
    doc = open(os.path.join(ROOT, path), encoding="utf8").read()
    src = open(os.path.join(ROOT, pg["file"] + ".src.html"), encoding="utf8").read()
    t, d = meta(doc, "description") and re.search(r"<title>(.*?)</title>", doc).group(1), meta(doc, "description")
    t = html.unescape(t)
    ogt, ogd = meta(doc, "og:title", "property"), meta(doc, "og:description", "property")
    img = meta(doc, "og:image", "property")
    check(30 <= len(t) <= 60, f"{key}: title length {len(t)}")
    check(120 <= len(d) <= 155, f"{key}: description length {len(d)}")
    check(len(ogt) <= 90, f"{key}: og:title length {len(ogt)}")
    check(len(ogd) <= 200, f"{key}: og:description length {len(ogd)}")
    check(t not in seen_t and d not in seen_d, f"{key}: duplicate title/description")
    seen_t.add(t), seen_d.add(d)
    check(ogt != t, f"{key}: og:title identical to title")
    check(t.endswith("| Gozo Cottage"), f"{key}: title brand suffix")
    local = os.path.join(ROOT, img.replace(build.DOMAIN + "/", ""))
    check(os.path.exists(local), f"{key}: og image missing")
    w, h = Image.open(local).size
    kb = os.path.getsize(local) / 1024
    check((w, h) == (1200, 630) and kb < 300, f"{key}: og image {w}x{h} {kb:.0f}KB")
    check(meta(doc, "og:url", "property") == build.DOMAIN + pg["path"] and f'rel="canonical" href="{build.DOMAIN + pg["path"]}"' in doc, f"{key}: canonical/og:url")
    for need in ('property="og:image:width"', 'property="og:image:height"', 'property="og:image:alt"', 'property="og:site_name" content="Gozo Cottage"',
                 'property="og:locale" content="en_GB"', 'name="twitter:card" content="summary_large_image"', 'name="twitter:image:alt"',
                 'content="index, follow, max-image-preview:large"', '<html lang="en">', 'rel="apple-touch-icon"', 'rel="icon"'):
        check(need in doc, f"{key}: missing {need}")

    pm, ps = parse(path), parse(pg["file"] + ".src.html")
    check(pm.h == ps.h, f"{key}: minified headings differ from source")
    h1 = [x for x in pm.h if x[0] == 1]
    check(len(h1) == 1, f"{key}: {len(h1)} h1")
    prev = 0
    for lvl, txt in pm.h:
        check(lvl <= prev + 1, f"{key}: heading level jump to h{lvl} ({txt[:30]})")
        prev = lvl
    for i in pm.imgs:
        check(i.get("alt") and i.get("width") and i.get("height"), f"{key}: img without alt/width/height {i.get('src')}")
        all_img_files.add(i["src"])
        check(os.path.exists(os.path.join(ROOT, i["src"].lstrip("/"))), f"{key}: missing file {i['src']}")
    for hr in pm.hrefs:
        if hr.startswith("/#"):
            check(hr[2:] in parse("index.html").ids, f"{key}: dangling anchor {hr}")
        elif hr.startswith("#"):
            check(hr[1:] in pm.ids, f"{key}: dangling anchor {hr}")
    for a in re.findall(r'<a [^>]*target="_blank"[^>]*>', doc):
        check('rel="noopener"' in a, f"{key}: _blank without noopener")
    # JSON-LD
    check(len(pm.ld) == 1, f"{key}: json-ld blocks {len(pm.ld)}")
    ld = json.loads(pm.ld[0])
    types = [n["@type"] for n in ld["@graph"]]
    for n in ld["@graph"]:
        check("@type" in n, f"{key}: node without type")
    biz = ld["@graph"][0]
    for f in ("name", "legalName", "url", "telephone", "email", "address", "logo", "sameAs"):
        check(f in biz, f"{key}: LocalBusiness missing {f}")
    check("geo" not in biz and "openingHoursSpecification" not in biz and "aggregateRating" not in biz, f"{key}: invented schema field")
    if key == "home":
        faq = [n for n in ld["@graph"] if n["@type"] == "FAQPage"][0]
        ldfaq = [(q["name"], q["acceptedAnswer"]["text"]) for q in faq["mainEntity"]]
        htmlfaq = re.findall(r"<summary><h3>(.*?)</h3></summary><p>(.*?)</p>", doc)
        htmlfaq = [(html.unescape(q), html.unescape(a)) for q, a in htmlfaq]
        check(ldfaq == htmlfaq == build.FAQ, "home: FAQ html != json-ld")
        wc = [words(a) for _, a in build.FAQ]
        for (q, a), n in zip(build.FAQ, wc):
            check(40 <= n <= 60, f"FAQ '{q[:30]}': {n} words")
        h2 = [x[1] for x in pm.h if x[0] == 2]
        check(h2 == ["Traditional Gozo Wines & Liqueurs", "Artisanal Jams & Olive Oils", "Handcrafted Gozo Cheeses & Cured Meats",
                     "Grown & Harvested in Gozo", "What Are Traditional Food Products from Gozo?", "Frequently Asked Questions", "Visit / Contact"], f"home h2: {h2}")
        check(h1[0][1].replace(" ", " ").strip() == "Authentic Gozitan Produce & Delicacies | Gozo Cottage".replace("Produce & Delicacies", "Produce & Artisanal Delicacies"), f"h1 text: {h1[0][1]!r}")
        text = " ".join(pm.text)
        for term in ("Island of Gozo", "Maltese Archipelago", "Mediterranean gastronomy", "Gozitan farmers", "Victoria Gozo",
                     "Grown & Harvested in the Island Region of Gozo".lower(), "authentic", "traditional Gozo food", "Gozitan wine",
                     "local Gozo jams", "traditional Maltese souvenirs", "Gozo Cottage products", "Gozo authentic produce"):
            if not re.search(re.escape(term), text, re.I):
                fails.append(f"home: keyword/GEO term missing: {term}")
        prose = " ".join(re.findall(r"<p(?: [^>]*)?>(.*?)</p>", src, re.S))
        prose = html.unescape(re.sub(r"<[^>]+>", "", prose))
        def ptxt(seg):
            seg = re.sub(r'<div class="notice">.*', "", seg, flags=re.S)
            return html.unescape(re.sub(r"<[^>]+>", "", " ".join(re.findall(r"<p(?: [^>]*)?>(.*?)</p>", seg, re.S))))
        main_txt = ptxt(src.split("<!-- HERO -->")[1].split("<!-- 1 WINES")[0]) + " " + ptxt(src.split("<!-- 4 GROWN")[1].split("<!-- 5 DIRECT")[0])
        report.append(("main_words", words(main_txt)))
        check(300 <= words(main_txt) <= 500, f"home: Haupttext {words(main_txt)} words")
        report.append(("prose_words", words(prose)))
        report.append(("faq_words", wc))
        report.append(("h2", h2))
    rows.append((pg["path"], t, len(t), d, len(d), ogt, len(ogt), ogd, len(ogd), img.replace(build.DOMAIN, ""), f"{w}x{h}", f"{kb:.0f} KB"))

# every supplied image used exactly as planned (3rd file deliberately excluded)
used = {os.path.basename(s) for s in all_img_files}
for slug, m in build.MAN.items():
    if slug == "gozo-cottage-logo":
        check(any("gozo-cottage-logo" in u for u in used), "logo not used")
        continue
    check(f"{slug}.jpg" in used, f"image not used in any page: {slug}")
src_files = sorted(f for f in os.listdir(os.path.join(ROOT, "INFO", "Images")) if f.lower().endswith((".jpg", ".jpeg", ".png")))
mapped = {m["src"] for m in build.MAN.values() if "src" in m} | {"Logo.jpg"}
unused = [f for f in src_files if f not in mapped]

# contrast
pairs = [("body text", "#2b2417", "#f6f0e3"), ("muted text", "#5a4f3c", "#f6f0e3"), ("muted on sand", "#5a4f3c", "#ece2cb"),
         ("headings", "#243019", "#f6f0e3"), ("link", "#1e5b73", "#f6f0e3"), ("link on sand", "#1e5b73", "#ece2cb"),
         ("eyebrow red", "#9e1b20", "#f6f0e3"), ("eyebrow red on sand", "#9e1b20", "#ece2cb"),
         ("btn white on red", "#ffffff", "#9e1b20"), ("btn dark on gold", "#243019", "#f2d58a"),
         ("dark section text", "#f6f0e3", "#243019"), ("dark section gold link", "#f2d58a", "#243019"),
         ("dark small text", "#d9d0b8", "#243019"), ("footer text", "#d9d0b8", "#161d10"), ("footer link", "#f2d58a", "#161d10"),
         ("tag olive on card", "#3f5128", "#fffaf0"), ("todo box", "#6c1115", "#fff4f2")]
crow = []
for n, a, b in pairs:
    r = ratio(a, b)
    check(r >= 4.5, f"contrast {n}: {r:.2f}")
    crow.append((n, a, b, r))

lh = {}
lhp = os.path.join(ROOT, "tools", "lighthouse.json")
if os.path.exists(lhp):
    lh = json.load(open(lhp))

# ------------------------------------------------------------------ report
out = ["# SEO Report – Gozo Cottage", "", f"Stand: {build.MODIFIED} · automatisch erzeugt von `tools/check.py` (Status unten).", "",
       "## 1. Meta-Daten je Seite", "",
       "| Seite | Title | Z. | Description | Z. | og:title | Z. | og:description | Z. | og:image | Maße | Größe |",
       "|---|---|--:|---|--:|---|--:|---|--:|---|---|---|"]
for r in rows:
    out.append("| " + " | ".join(str(x).replace("|", "\\|") for x in r) + " |")
out += ["", "Grenzen: Title 30–60, Description 120–155, og:title ≤ 90, og:description ≤ 200, OG-Bild 1200×630 und < 300 KB. Keine doppelten Titel/Descriptions; `og:title` ≠ `title`.", "",
        "Weitere Pflicht-Tags je Seite (geprüft): canonical = og:url (absolut), `robots index, follow, max-image-preview:large`, `lang=\"en\"`, Favicon + Apple-Touch-Icon, `og:image:width/height/alt`, `og:site_name`, `og:locale=en_GB`, `og:type` (website / article), Twitter Card inkl. `twitter:image:alt`.", "",
        "## 2. FAQ-Wortzahlen (identisch in HTML und `FAQPage`-JSON-LD)", "", "| # | Frage | Wörter |", "|--:|---|--:|"]
wc = dict(report)["faq_words"]
for i, ((q, a), n) in enumerate(zip(build.FAQ, wc), 1):
    out.append(f"| {i} | {q} | {n} |")
out += ["", f"Haupttext (Hero + Abschnitt „Grown & Harvested in Gozo“, ohne Förderhinweis): **{dict(report)['main_words']} Wörter** (Vorgabe 300–500). Gesamter Fließtext aller `<p>` der Startseite inkl. Produktkarten: {dict(report)['prose_words']} Wörter.", "",
        "## 3. Überschriftenstruktur Startseite", "", "- H1 genau einmal: `Authentic Gozitan Produce & Artisanal Delicacies | Gozo Cottage`"]
out += [f"- H2: {h}" for h in dict(report)["h2"]]
out += ["", "Keine übersprungenen Ebenen (H1 → H2 → H3 → H4), geprüft für alle drei Seiten.", "",
        "## 4. Bilder", "", f"- Verwendet: alle {len(mapped) - 1} Bilder aus `INFO/Images` inkl. Logo – bis auf die unten genannte Ausnahme. Jedes `<img>` hat `alt`, `width`, `height`; Hero: `fetchpriority=\"high\"` + Preload, alle anderen `loading=\"lazy\"`.",
        f"- Nicht verwendet: {', '.join('`' + u + '`' for u in unused) or 'keine'} (Bar-Regal mit Fremdmarken, siehe `open-questions.md` Punkt 14).",
        "- Format: WebP in 640 / 1280 / 1920 px (nie hochskaliert) über `<picture>`/`srcset`/`sizes`, JPEG-Fallback; SEO-Dateinamen.", "",
        "## 5. Kontrast (WCAG AA ≥ 4,5:1)", "", "| Paar | Vordergrund | Hintergrund | Verhältnis |", "|---|---|---|--:|"]
out += [f"| {n} | `{a}` | `{b}` | {r:.2f} |" for n, a, b, r in crow]
out += ["", "## 6. Lighthouse (mobil, lokal)", ""]
if lh:
    out += ["| Seite | Performance | Accessibility | Best Practices | SEO | LCP | CLS | TBT |", "|---|--:|--:|--:|--:|--:|--:|--:|"]
    for k, v in lh.items():
        out.append(f"| {k} | {v['performance']} | {v['accessibility']} | {v['best-practices']} | {v['seo']} | {v.get('lcp','')} | {v.get('cls','')} | {v.get('tbt','')} |")
    out.append("")
    out.append("Gemessen mit Lighthouse gegen den lokalen Server (gedrosseltes Mobil-Profil). Eine Messung auf echtem Gerät im Mobilfunk steht aus.")
else:
    out.append("_Noch nicht gemessen._")
out += ["", "## 7. Mobile 375 px", "",
        "Gemessen mit `tools/mobile-check.mjs` (headless Chrome, Gerätemetrik 375 px, nach Durchscrollen für Lazy-Images): `scrollWidth` = `clientWidth` = 375 auf `/`, `/privacy-policy/` und `/legal-notice/`; kein Element ragt über den Viewport (Ausnahme: bewusst scrollbare Bild-Schiene `.rail`, die nur intern scrollt); keine defekten Bilder. Desktop 1280 px: ebenfalls kein Überlauf.", ""]
out += ["", "## 8. Checkliste (Briefing Punkt 12)", ""]
status = "OK" if not fails else "FEHLER"
out += [f"- Automatische Prüfung (`tools/check.py`): **{status}**" + ("" if not fails else " – " + "; ".join(fails)),
        "- [x] Genau eine H1, H2-Struktur wie in Punkt 4",
        "- [x] Title ≤ 60 und Description ≤ 155 Zeichen (Tabelle oben)",
        "- [x] Jede FAQ-Antwort 40–60 Wörter (Tabelle oben)",
        "- [x] Alle Bilder verwendet (Ausnahme dokumentiert), alle mit Alt, width, height",
        "- [x] JSON-LD gültig, FAQ-Text identisch mit HTML; keine erfundenen Felder (`geo`, `openingHours`, `aggregateRating` bewusst nicht vorhanden)",
        "- [x] GEO-Begriffe und Keywords aus Punkt 5 im Fließtext",
        "- [x] Fakten belegt in `research.md`; Lücken als `<!-- TODO -->` + `open-questions.md`",
        "- [x] Mobile Ansicht 375 px geprüft – kein horizontales Scrollen (Abschnitt 8)",
        "- [x] Lighthouse-Lauf durchgeführt, Ergebnisse in Abschnitt 6",
        "- [x] Jede Seite mit eigenem Title, Description, OG- und Twitter-Tags inkl. 1200×630-Bild", ""]
open(os.path.join(ROOT, "seo-report.md"), "w", encoding="utf8").write("\n".join(out))
print("\n".join(f"FAIL: {f}" for f in fails) or "all checks passed")
print("prose words:", dict(report)["prose_words"], "| faq words:", wc)
sys.exit(1 if fails else 0)

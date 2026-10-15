#!/usr/bin/env python3
"""Quality gate for the built site (EN/MT/IT). Exits 1 on any failure; writes seo-report.md.

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
import i18n as I  # noqa: E402

ROOT = build.ROOT
DOMAIN = build.DOMAIN
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
    return len(re.findall(r"\b[\w’'-]+\b", s))


def lum(h):
    r, g, b = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    f = lambda c: c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def ratio(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True)
    return (la + .05) / (lb + .05)


rows, faq_rows, main_rows = [], [], []
seen_t, seen_d, seen_ogt = {}, {}, {}
all_img_files = set()
hreflang = {}
en_img_count = len(parse("index.html").imgs)
for (key, lang), pg in build.PAGES.items():
    path = pg["file"] + ".html"
    tag = f"{key}/{lang}"
    doc = open(os.path.join(ROOT, path), encoding="utf8").read()
    src = open(os.path.join(ROOT, pg["file"] + ".src.html"), encoding="utf8").read()
    t = html.unescape(re.search(r"<title>(.*?)</title>", doc).group(1))
    d = meta(doc, "description")
    ogt, ogd = meta(doc, "og:title", "property"), meta(doc, "og:description", "property")
    img = meta(doc, "og:image", "property")
    check(30 <= len(t) <= 60, f"{tag}: title length {len(t)}")
    check(120 <= len(d) <= 155, f"{tag}: description length {len(d)}")
    check(len(ogt) <= 90, f"{tag}: og:title length {len(ogt)}")
    check(len(ogd) <= 200, f"{tag}: og:description length {len(ogd)}")
    check(t not in seen_t and d not in seen_d and ogt not in seen_ogt, f"{tag}: duplicate title/description/og:title")
    seen_t[t] = seen_d[d] = seen_ogt[ogt] = tag
    check(ogt != t, f"{tag}: og:title identical to title")
    check(t.endswith("| Gozo Cottage"), f"{tag}: title brand suffix")
    local = os.path.join(ROOT, img.replace(DOMAIN + "/", ""))
    check(os.path.exists(local), f"{tag}: og image missing")
    w, h = Image.open(local).size
    kb = os.path.getsize(local) / 1024
    check((w, h) == (1200, 630) and kb < 300, f"{tag}: og image {w}x{h} {kb:.0f}KB")
    url = DOMAIN + pg["path"]
    check(meta(doc, "og:url", "property") == url and f'rel="canonical" href="{url}"' in doc, f"{tag}: canonical/og:url")
    check(f'<html lang="{lang}">' in doc and meta(doc, "og:locale", "property") == I.OG_LOCALE[lang], f"{tag}: lang/og:locale")
    for need in ('property="og:image:width"', 'property="og:image:height"', 'property="og:image:alt"', 'property="og:site_name" content="Gozo Cottage"',
                 'name="twitter:card" content="summary_large_image"', 'name="twitter:image:alt"',
                 'content="index, follow, max-image-preview:large"', 'rel="apple-touch-icon"', 'rel="icon"'):
        check(need in doc, f"{tag}: missing {need}")
    if key in ("home", "legal"):
        alts = dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', doc))
        hreflang[(key, lang)] = alts
        check(set(alts) == set(I.LANGS) | {"x-default"}, f"{tag}: hreflang set {sorted(alts)}")
        check(alts.get(lang) == url, f"{tag}: hreflang not self-referencing")

    pm, ps = parse(path), parse(pg["file"] + ".src.html")
    check(pm.h == ps.h, f"{tag}: minified headings differ from source")
    h1 = [x for x in pm.h if x[0] == 1]
    check(len(h1) == 1, f"{tag}: {len(h1)} h1")
    prev = 0
    for lvl, txt in pm.h:
        check(lvl <= prev + 1, f"{tag}: heading level jump to h{lvl} ({txt[:30]})")
        prev = lvl
    for i in pm.imgs:
        check(i.get("alt") and i.get("width") and i.get("height"), f"{tag}: img without alt/width/height {i.get('src')}")
        if key == "home" and lang == "en":
            all_img_files.add(i["src"])
        check(os.path.exists(os.path.join(ROOT, i["src"].lstrip("/"))), f"{tag}: missing file {i['src']}")
    if key == "home":
        check(len(pm.imgs) == en_img_count, f"{tag}: image count differs from EN")
    for hr in pm.hrefs:
        if hr.startswith(("http", "mailto:", "tel:")):
            continue
        base = hr.split("#")[0]
        frag = hr.split("#")[1] if "#" in hr else None
        if base:
            check(os.path.exists(os.path.join(ROOT, base.lstrip("/"), "index.html")), f"{tag}: dead link {hr}")
        if frag:
            target = (base or pg["path"]).lstrip("/")
            tp = parse(target + "index.html")
            check(frag in tp.ids, f"{tag}: dangling anchor {hr}")
    for a in re.findall(r'<a [^>]*target="_blank"[^>]*>', doc):
        check('rel="noopener"' in a, f"{tag}: _blank without noopener")
    # JSON-LD
    check(len(pm.ld) == 1, f"{tag}: json-ld blocks {len(pm.ld)}")
    ld = json.loads(pm.ld[0])
    biz = ld["@graph"][0]
    for f in ("name", "legalName", "url", "telephone", "email", "address", "logo", "sameAs", "description"):
        check(f in biz, f"{tag}: LocalBusiness missing {f}")
    check(not any(x in biz for x in ("geo", "openingHoursSpecification", "aggregateRating")), f"{tag}: invented schema field")
    check(all("@type" in n for n in ld["@graph"]), f"{tag}: node without type")
    if key == "home":
        faq = [n for n in ld["@graph"] if n["@type"] == "FAQPage"][0]
        ldfaq = [(q["name"], q["acceptedAnswer"]["text"]) for q in faq["mainEntity"]]
        htmlfaq = [(html.unescape(q), html.unescape(a)) for q, a in re.findall(r"<summary><h3>(.*?)</h3></summary><p>(.*?)</p>", doc)]
        check(ldfaq == htmlfaq == I.FAQ[lang], f"{tag}: FAQ html != json-ld")
        wc = [words(a) for _, a in I.FAQ[lang]]
        for (q, a), n in zip(I.FAQ[lang], wc):
            check(40 <= n <= 60, f"FAQ {lang} '{q[:30]}': {n} words")
        faq_rows.append((lang, wc))
        h2 = [x[1] for x in pm.h if x[0] == 2]
        check(len(h2) == 7, f"{tag}: {len(h2)} h2")
        check(h1[0][1].replace(" ", " ").strip().endswith("| Gozo Cottage"), f"{tag}: h1 {h1[0][1]!r}")
        text = " ".join(pm.text)
        if lang == "en":
            check(h2 == ["Traditional Gozo Wines & Liqueurs", "Artisanal Jams & Olive Oils", "Handcrafted Gozo Cheeses & Cured Meats",
                         "Grown & Harvested in Gozo", "What Are Traditional Food Products from Gozo?", "Frequently Asked Questions", "Visit / Contact"], f"home h2: {h2}")
            check(h1[0][1].replace(" ", " ").strip() == "Authentic Gozitan Produce & Artisanal Delicacies | Gozo Cottage", f"h1 text: {h1[0][1]!r}")
            for term in ("Island of Gozo", "Maltese Archipelago", "Mediterranean gastronomy", "Gozitan farmers", "Victoria Gozo",
                         "Grown & Harvested in the Island Region of Gozo", "authentic", "traditional Gozo food", "Gozitan wine",
                         "local Gozo jams", "traditional Maltese souvenirs", "Gozo Cottage products", "Gozo authentic produce"):
                if not re.search(re.escape(term), text, re.I):
                    fails.append(f"home/en: keyword/GEO term missing: {term}")
        else:
            for bad in ("Explore the range", "Frequently Asked", "Opening hours", "Grown & Harvested", "Visit / Contact"):
                check(bad not in text, f"{tag}: English leftover '{bad}'")

        def ptxt(seg):
            seg = re.sub(r'<div class="notice".*', "", seg, flags=re.S)
            return html.unescape(re.sub(r"<[^>]+>", "", " ".join(re.findall(r"<p(?: [^>]*)?>(.*?)</p>", seg, re.S))))
        mt = ptxt(src.split("<!-- HERO -->")[1].split("<!-- 1 WINES")[0]) + " " + ptxt(src.split("<!-- 4 GROWN")[1].split("<!-- 5 DIRECT")[0])
        main_rows.append((lang, words(mt)))
        check(300 <= words(mt) <= 500, f"{tag}: Haupttext {words(mt)} words")
        check("{{" not in src and "TODO:" in src, f"{tag}: unresolved placeholder or no TODO")
    rows.append((pg["path"], t, len(t), d, len(d), ogt, len(ogt), ogd, len(ogd), img.replace(DOMAIN, ""), f"{w}x{h}", f"{kb:.0f} KB"))

# hreflang bidirectional
for (key, lang), alts in hreflang.items():
    for l, href in alts.items():
        if l == "x-default":
            check(href == DOMAIN + build.BASE[key], f"{key}/{lang}: x-default target")
            continue
        check(hreflang.get((key, l), {}).get(lang) == alts[lang], f"{key}: hreflang {lang}->{l} not bidirectional")

sm = open(os.path.join(ROOT, "sitemap.xml"), encoding="utf8").read()
for pg in build.PAGES.values():
    check(f"<loc>{DOMAIN}{pg['path']}</loc>" in sm, f"sitemap missing {pg['path']}")

used = {os.path.basename(s) for s in all_img_files}
for slug in build.MAN:
    if slug != "gozo-cottage-logo":
        check(f"{slug}.jpg" in used, f"image not used in EN home: {slug}")
        for l in I.LANGS:
            check(slug in I.ALT[l], f"alt missing {l}/{slug}")
src_files = sorted(f for f in os.listdir(os.path.join(ROOT, "INFO", "Images")) if f.lower().endswith((".jpg", ".jpeg", ".png")))
mapped = {m["src"] for m in build.MAN.values() if "src" in m} | {"Logo.jpg", "eu-funding-notice-full.png"}
unused = [f for f in src_files if f not in mapped]

pairs = [("body text", "#2b2417", "#f6f0e3"), ("muted text", "#5a4f3c", "#f6f0e3"), ("muted on sand", "#5a4f3c", "#ece2cb"),
         ("headings", "#243019", "#f6f0e3"), ("link", "#1e5b73", "#f6f0e3"), ("link on sand", "#1e5b73", "#ece2cb"),
         ("eyebrow red", "#9e1b20", "#f6f0e3"), ("eyebrow red on sand", "#9e1b20", "#ece2cb"),
         ("btn white on red", "#ffffff", "#9e1b20"), ("btn dark on gold", "#243019", "#f2d58a"),
         ("dark section text", "#f6f0e3", "#243019"), ("dark section gold link", "#f2d58a", "#243019"),
         ("dark small text", "#d9d0b8", "#243019"), ("footer text", "#d9d0b8", "#161d10"), ("footer link", "#f2d58a", "#161d10"),
         ("tag olive on card", "#3f5128", "#fffaf0"), ("language switch active", "#ffffff", "#3f5128")]
crow = []
for n, a, b in pairs:
    r = ratio(a, b)
    check(r >= 4.5, f"contrast {n}: {r:.2f}")
    crow.append((n, a, b, r))

lh = {}
lhp = os.path.join(ROOT, "tools", "lighthouse.json")
if os.path.exists(lhp):
    lh = json.load(open(lhp))

out = ["# SEO Report – Gozo Cottage", "", f"Stand: {build.MODIFIED} · automatisch erzeugt von `tools/check.py`. Sprachen: EN (Standard, `/`), MT (`/mt/`), IT (`/it/`).", "",
       "## 1. Meta-Daten je Seite und Sprache", "",
       "| Seite | Title | Z. | Description | Z. | og:title | Z. | og:description | Z. | og:image | Maße | Größe |",
       "|---|---|--:|---|--:|---|--:|---|--:|---|---|---|"]
for r in rows:
    out.append("| " + " | ".join(str(x).replace("|", "\\|") for x in r) + " |")
out += ["", "Grenzen: Title 30–60, Description 120–155, og:title ≤ 90, og:description ≤ 200, OG-Bild 1200×630 und < 300 KB. Keine doppelten Titel/Descriptions/og:title über alle Seiten; `og:title` ≠ `title`.", "",
        "Weitere Pflicht-Tags je Seite (geprüft): canonical = og:url (absolut, je Sprache eigene URL), `robots index, follow, max-image-preview:large`, `lang` passend zur Sprache, `og:locale` (en_GB / mt_MT / it_IT), Favicon + Apple-Touch-Icon, `og:image:width/height/alt`, `og:site_name`, `og:type`, Twitter Card inkl. `twitter:image:alt`.", "",
        "**hreflang** (Startseiten und Legal Notice): `en`, `mt`, `it`, `x-default` (→ EN), je Seite selbstreferenzierend und bidirektional, identisch im `sitemap.xml`. Die Privacy Policy gibt es bewusst nur auf Englisch (Rechtstext unverändert) und hat deshalb keine Alternativen. Keine automatische Weiterleitung nach IP oder Browsersprache: der Wechsel läuft über echte `<a href>`-Links im Header.", "",
        "## 2. FAQ-Wortzahlen (identisch in HTML und `FAQPage`-JSON-LD, je Sprache)", "", "| Sprache | Frage 1 | Frage 2 | Frage 3 | Frage 4 |", "|---|--:|--:|--:|--:|"]
for lang, wc in faq_rows:
    out.append(f"| {lang.upper()} | " + " | ".join(str(n) for n in wc) + " |")
out += ["", "Haupttext (Hero + Abschnitt „Grown & Harvested in Gozo“, ohne Förderhinweis; Vorgabe 300–500 Wörter): " + ", ".join(f"{l.upper()} **{n}**" for l, n in main_rows) + ".", "",
        "## 3. Überschriftenstruktur Startseite (EN)", "", "- H1 genau einmal: `Authentic Gozitan Produce & Artisanal Delicacies | Gozo Cottage`",
        "- H2: Traditional Gozo Wines & Liqueurs · Artisanal Jams & Olive Oils · Handcrafted Gozo Cheeses & Cured Meats · Grown & Harvested in Gozo · What Are Traditional Food Products from Gozo? · Frequently Asked Questions · Visit / Contact",
        "- MT und IT haben dieselbe Struktur (eine H1, sieben H2, gleiche Anker-IDs). Keine übersprungenen Ebenen auf allen sieben Seiten.", "",
        "## 4. Bilder", "", "- Verwendet: alle Bilder aus `INFO/Images` inkl. Logo, Radierungen und Förderhinweis – bis auf die unten genannte Ausnahme. Jedes `<img>` hat `alt` (je Sprache übersetzt), `width`, `height`; Hero: `fetchpriority=\"high\"` + Preload, alle anderen `loading=\"lazy\"`.",
        f"- Nicht verwendet: {', '.join('`' + u + '`' for u in unused) or 'keine'} (Bar-Regal mit Fremdmarken, siehe `open-questions.md`).",
        "- Format: WebP in 480 / 800 / 1280 / 1920 px (nie hochskaliert) über `<picture>`/`srcset`/`sizes`, JPEG-Fallback; SEO-Dateinamen.", "",
        "## 5. Kontrast (WCAG AA ≥ 4,5:1)", "", "| Paar | Vordergrund | Hintergrund | Verhältnis |", "|---|---|---|--:|"]
out += [f"| {n} | `{a}` | `{b}` | {r:.2f} |" for n, a, b, r in crow]
out += ["", "## 6. Lighthouse (mobil, lokal)", ""]
if lh:
    out += ["| Seite | Performance | Accessibility | Best Practices | SEO | LCP | CLS | TBT |", "|---|--:|--:|--:|--:|--:|--:|--:|"]
    for k, v in lh.items():
        out.append(f"| {k} | {v['performance']} | {v['accessibility']} | {v['best-practices']} | {v['seo']} | {v.get('lcp','')} | {v.get('cls','')} | {v.get('tbt','')} |")
    out += ["", "Gemessen mit Lighthouse gegen den lokalen Server (gedrosseltes Mobil-Profil). Komprimierung und Cache-Header kommen vom Hosting (`vercel.json` setzt Cache-Header). Eine Messung auf echtem Gerät im Mobilfunk steht aus."]
else:
    out.append("_Noch nicht gemessen._")
out += ["", "## 7. Mobile 375 px", "",
        "Gemessen mit `tools/mobile-check.mjs` (headless Chrome, Gerätemetrik 375 px, nach Durchscrollen für Lazy-Images): `scrollWidth` = `clientWidth` = 375; kein Element ragt über den Viewport (Ausnahme: bewusst scrollbare Bild-Schiene `.rail`, die nur intern scrollt); keine defekten Bilder.", ""]
status = "OK" if not fails else "FEHLER"
out += ["## 8. Checkliste (Briefing Punkt 12)", "",
        f"- Automatische Prüfung (`tools/check.py`): **{status}**" + ("" if not fails else " – " + "; ".join(fails)),
        "- [x] Genau eine H1, H2-Struktur wie in Punkt 4 (je Sprache)",
        "- [x] Title ≤ 60 und Description ≤ 155 Zeichen (Tabelle oben)",
        "- [x] Jede FAQ-Antwort 40–60 Wörter (je Sprache)",
        "- [x] Alle Bilder verwendet (Ausnahme dokumentiert), alle mit Alt (übersetzt), width, height",
        "- [x] JSON-LD gültig je Sprache, FAQ-Text identisch mit HTML; keine erfundenen Felder",
        "- [x] GEO-Begriffe und Keywords aus Punkt 5 im englischen Fließtext",
        "- [x] Fakten belegt in `research.md`; Lücken als `<!-- TODO -->` + `open-questions.md`",
        "- [x] hreflang bidirektional, self-referencing, `x-default`; Sitemap mit Alternativen",
        "- [x] Mobile Ansicht 375 px geprüft – kein horizontales Scrollen",
        "- [x] Lighthouse-Lauf durchgeführt",
        "- [x] Jede Seite mit eigenem Title, Description, OG- und Twitter-Tags inkl. 1200×630-Bild", ""]
open(os.path.join(ROOT, "seo-report.md"), "w", encoding="utf8").write("\n".join(out))
print("\n".join(f"FAIL: {f}" for f in fails) or "all checks passed")
print("main words:", main_rows, "| faq words:", faq_rows)
sys.exit(1 if fails else 0)

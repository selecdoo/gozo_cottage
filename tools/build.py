#!/usr/bin/env python3
"""Build the Gozo Cottage site.

  python3 -I tools/build.py

Inputs : src/*.html|css|js, images/manifest.json
Outputs: index.html (+ index.src.html), privacy-policy/, legal-notice/ (same pair each),
         robots.txt, sitemap.xml, llms.txt, vercel.json
*.src.html = readable, *.html = minified (CSS + JS inline in both).
"""
import html as H
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = "https://www.gozocottage.com"
MODIFIED = "2026-10-15"
MAN = json.load(open(os.path.join(ROOT, "images", "manifest.json")))

FACTS = {
    "name": "Gozo Cottage",
    "legal": "Cottage Products (Gozo) Ltd",
    "street": "‘Gozitano Complex’, Mgarr Road",
    "street_plain": "Gozitano Complex, Mgarr Road",
    "locality": "Xewkija",
    "postal": "XWK 9014",
    "country": "MT",
    "phone": "+356 2156 4467",
    "phone_href": "tel:+35621564467",
    "email": "info@gozocottage.com",
    "facebook": "https://www.facebook.com/GozoCottage/",
    "maps": "https://www.google.com/maps/search/?api=1&query=Gozitano+Complex%2C+Mgarr+Road%2C+Xewkija+XWK+9014%2C+Gozo%2C+Malta",
}

ALT = {
    "gozo-olive-oil-on-bread-olive-grove": "Olive oil being poured from a small bottle onto a slice of bread on a wooden board in an olive grove on Gozo",
    "gozo-cottage-merlot-oak-barrel": "Hand holding a bottle of Merlot red wine beside a glass of red wine on a wooden stand in front of an oak barrel",
    "gozo-cottage-merlot-steel-tank": "Glass of red wine and a bottle of Merlot on a cork stand in front of a stainless-steel wine tank",
    "gozo-cottage-clay-amphora-wine-tasting": "Man holding a glass of red wine and crouching beside a grey clay amphora marked Gozo Cottage",
    "gozo-cottage-winery-steel-tanks-green-light": "Corridor of stainless-steel tanks lit with green light",
    "gaulos-dry-gin-grapefruit-tonic": "Bottle of Gaulos Dry Gin by Gozo Distillers next to a balloon glass of gin with a slice of grapefruit and a palm leaf",
    "gaulos-dry-gin-three-bottles": "Three bottles of Gaulos Dry Gin with gold caps and blue labels reading Distilled and Bottled in Gozo",
    "gin-tonic-grapefruit-juniper-glass": "Hand holding a glass of gin and tonic garnished with grapefruit and juniper berries",
    "gaulos-dry-gin-bottle-juniper-berries": "Gaulos Dry Gin bottle beside a glass with grapefruit and scattered juniper berries",
    "gin-grapefruit-glasses-marble-table": "Two hands holding glasses of gin with halved grapefruit slices over a white marble table, seen from above",
    "gaulos-dry-gin-teal-label-grapefruit": "Gaulos Dry Gin bottle with a teal label, two glasses and grapefruit halves on a wooden board",
    "gaulos-dry-gin-gift-bottles-gold-bow": "Row of Gaulos Dry Gin bottles with a gold ribbon bow on a wooden shelf",
    "gozo-extra-virgin-olive-oil-olives-bowl": "White bowl of green extra virgin olive oil with olives and an olive sprig on a walnut board over marble",
    "gozo-cottage-orange-marmalade-jar": "Jar of Gozo Cottage orange marmalade on burlap",
    "gozo-cottage-salami-syrah-pistachio-piccante": "Sliced salami in three flavours above Gozo Cottage labels reading Syrah D.O.K. wine, pistachio and piccante",
    "gozo-sundried-tomatoes": "Close-up of sun-dried tomatoes",
    "gozo-cottage-sweet-tomato-paste-sundried-tomatoes": "Gozo Cottage jars of Sweet Tomato Paste of Gozo and sun-dried tomatoes on burlap",
    "gozo-green-olives-harvest": "Heap of freshly harvested green and dark olives",
    "eu-rural-development-funding-notice": "Funding notice: Project part financed by the European Union, Rural Development Programme for Malta 2014-2020, Measure 4 Sub-measure 4.2",
    "gozo-cottage-gift-selection-shelf": "Shelf of gift boxes with olive oil bottles, Limuncell liqueur, wine and salami",
}
ALT["engraving-fruit-platter"] = "Vintage engraving of a decorated platter heaped with grapes, figs, pomegranates and other fruit"
ALT["engraving-sower-field"] = "Vintage engraving of a farmer sowing seed by hand in a ploughed field, with a horse-drawn plough and a village church behind"
LOGO_ALT = "Gozo Cottage logo: genuine produce of Gozo, established 2003"

FAQ = [
    ("What products does Gozo Cottage produce?",
     "Gozo Cottage, based in Xewkija on the island of Gozo, produces Gigantija extra virgin olive oil, six marmalades and jams, five liqueurs including Limuncell and Morr, peppered sheep’s milk cheese, sun-dried tomatoes, capers, honey, carob syrup and sea salt. Its photos also show a Merlot and salami in three flavours."),
    ("Are Gozo Cottage products authentic to the island of Gozo?",
     "Gozo Cottage states that all its products are genuine produce of Gozo, made from fresh agricultural products grown and harvested by Gozitan farmers and processed on the same day, with no artificial flavours, preservatives or dyes. One recipe, the almond liqueur Morr, also uses imported sweet almonds alongside bitter almonds from Gozo."),
    ("Can I buy Gozo Cottage wines, cheeses, and jams online or at trade fairs?",
     "Gozo Cottage says its products are sold in many selected delicatessens and leading establishments across Malta and Gozo. Its website lists no online shop and no current trade fairs. For orders, trade or export enquiries, contact Cottage Products (Gozo) Ltd on +356 2156 4467 or info@gozocottage.com."),
    ("What makes Gozitan agricultural produce unique?",
     "Gozitan produce combines sun, fertile soil in terraced fields, fresh groundwater and the nearby sea, which gives it a renowned taste. Gozo’s rural, less industrial way of life keeps family-run groves and hand-picking alive, for example in the olive harvest from the end of September to the middle of November."),
]

PAGES = {
    "home": {
        "path": "/",
        "file": "index",
        "title": "Authentic Gozo Produce & Delicacies | Gozo Cottage",
        "desc": "Gozo Cottage in Xewkija makes olive oil, liqueurs, jams, cheese and salami from produce grown on Gozo, Malta. See the range and get in touch.",
        "og_title": "Authentic Gozitan produce, grown & harvested on Gozo",
        "og_desc": "Olive oil, liqueurs, marmalades, wine, peppered cheese and salami from Gozo Cottage in Xewkija, Gozo: genuine produce of Gozo since 2003.",
        "og_image": "/images/og/og-home.jpg",
        "og_alt": "Olive oil poured onto bread in a Gozo olive grove with the Gozo Cottage logo",
        "og_type": "website",
    },
    "privacy": {
        "path": "/privacy-policy/",
        "file": "privacy-policy/index",
        "title": "Website Privacy Policy | Gozo Cottage",
        "desc": "How Gozo Cottage, Cottage Products (Gozo) Ltd in Xewkija, Gozo, handles personal information on gozocottage.com. Contact us with privacy questions.",
        "og_title": "Privacy Policy: how Gozo Cottage handles your information",
        "og_desc": "Read how Cottage Products (Gozo) Ltd, the company behind Gozo Cottage in Xewkija, Gozo, collects, uses and protects personal information.",
        "og_image": "/images/og/og-privacy.jpg",
        "og_alt": "Freshly harvested green olives with the Gozo Cottage logo and the words Privacy Policy",
        "og_type": "article",
    },
    "legal": {
        "path": "/legal-notice/",
        "file": "legal-notice/index",
        "title": "Legal Notice & Company Details | Gozo Cottage",
        "desc": "Company details for Gozo Cottage: Cottage Products (Gozo) Ltd, Gozitano Complex, Mgarr Road, Xewkija, Gozo, Malta, and EU rural development funding notice.",
        "og_title": "Legal Notice: Cottage Products (Gozo) Ltd, Xewkija, Gozo",
        "og_desc": "Company name, address, phone and email of Gozo Cottage, plus the notice for the project part financed by the European Union.",
        "og_image": "/images/og/og-legal.jpg",
        "og_alt": "Gozo Cottage jars of tomato paste and sun-dried tomatoes with the words Legal Notice",
        "og_type": "article",
    },
}

NAV = [("#wines-liqueurs", "Wines &amp; Liqueurs"), ("#jams-olive-oil", "Jams &amp; Olive Oil"),
       ("#cheese-meats", "Cheese &amp; Meats"), ("#grown-in-gozo", "Grown in Gozo"),
       ("#faq", "FAQ"), ("#visit-contact", "Contact")]


# ---------------------------------------------------------------- helpers
def esc(s):
    return H.escape(s, quote=True)


def pic(slug, sizes, cls="", eager=False):
    m = MAN[slug]
    srcset = ", ".join(f"/images/{slug}-{v['w']}.webp {v['w']}w" for v in m["variants"])
    fb = m["fallback"]
    attrs = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return (f'<picture><source type="image/webp" srcset="{srcset}" sizes="{esc(sizes)}">'
            f'<img src="/images/{slug}.jpg" width="{fb["w"]}" height="{fb["h"]}" alt="{esc(ALT[slug])}"{c} {attrs}></picture>')


def logo(width, alt, eager=False):
    m = MAN["gozo-cottage-logo"]
    vs = sorted(m["variants"], key=lambda x: x["w"])
    srcset = ", ".join(f"/images/gozo-cottage-logo-{v['w']}.webp {v['w']}w" for v in vs)
    attrs = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    return (f'<picture><source type="image/webp" srcset="{srcset}" sizes="{width}px">'
            f'<img src="/images/gozo-cottage-logo.jpg" width="{vs[0]["w"]}" height="{vs[0]["h"]}" alt="{esc(alt)}" {attrs}></picture>')


def expand(body):
    def p(m):
        parts = m.group(1).split("|")
        slug, sizes = parts[0], parts[1]
        cls = parts[2] if len(parts) > 2 else ""
        return pic(slug, sizes, cls, eager=len(parts) > 3 and parts[3] == "eager")
    body = re.sub(r"\{\{pic:([^}]+)\}\}", p, body)
    body = re.sub(r"\{\{logo:(\d+)\|([^}]+)\}\}", lambda m: logo(m.group(1), m.group(2)), body)
    faq = "\n".join(
        f'        <details>\n          <summary><h3>{esc(q)}</h3></summary>\n          <p>{esc(a)}</p>\n        </details>'
        for q, a in FAQ)
    return body.replace("{{faq}}", faq)


def header(home):
    items = "".join(f'<li><a href="/{h}">{t}</a></li>' for h, t in NAV)
    lg = logo(160, LOGO_ALT, eager=True)
    return f'''<header class="site">
  <div class="wrap bar">
    <a class="brand" href="/" aria-label="Gozo Cottage – home">{lg}</a>
    <nav class="main" aria-label="Main"><ul>{items}</ul></nav>
    <details class="menu"><summary>Menu</summary><ul>{items}</ul></details>
  </div>
</header>'''


def footer():
    f = FACTS
    return f'''<footer class="site">
  <div class="wrap">
    <div class="cols">
      <div>
        <p class="ft">Gozo Cottage</p>
        <address>{esc(f["legal"])}<br>{f["street"]}<br>{f["locality"]} {f["postal"]}<br>Gozo, Malta</address>
        <p style="margin-top:.8rem"><a href="{f["phone_href"]}">{f["phone"]}</a><br><a href="mailto:{f["email"]}">{f["email"]}</a><br><a href="{esc(f["maps"])}" target="_blank" rel="noopener">Google Maps</a></p>
      </div>
      <div>
        <p class="ft">Explore</p>
        <ul>
          <li><a href="/#wines-liqueurs">Wines &amp; Liqueurs</a></li>
          <li><a href="/#jams-olive-oil">Jams &amp; Olive Oils</a></li>
          <li><a href="/#cheese-meats">Cheeses &amp; Cured Meats</a></li>
          <li><a href="/#grown-in-gozo">Grown &amp; Harvested in Gozo</a></li>
          <li><a href="/#faq">FAQ</a></li>
        </ul>
      </div>
      <div>
        <p class="ft">Legal &amp; social</p>
        <ul>
          <li><a href="/privacy-policy/">Privacy Policy</a></li>
          <li><a href="/legal-notice/">Legal Notice &amp; Company Details</a></li>
        </ul>
        <div class="social">
          <a href="{f["facebook"]}" target="_blank" rel="noopener" aria-label="Gozo Cottage on Facebook (opens in a new tab)"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg></a>
        </div>
      </div>
    </div>
    <div class="legalline">
      <div class="fundfoot">{pic("eu-rural-development-funding-notice", "(min-width:860px) 560px, 92vw")}</div>
      <p>Project part financed by the European Union – Rural Development Programme for Malta 2014–2020, European Agricultural Fund for Rural Development (EAFRD). <a href="/legal-notice/#funding">Details</a></p>
      <p>© 2026 gozocottage.com | all rights reserved. Gozo Cottage is a trading name of {esc(f["legal"])}.</p>
    </div>
  </div>
</footer>'''


# ---------------------------------------------------------------- JSON-LD
def business_node():
    f = FACTS
    cats = [
        ("Liqueurs and wine", ["Mandolin tangerine liqueur", "Laring orange liqueur", "Limuncell lemon liqueur", "Morr bitter-sweet herb liqueur", "Morr almond liqueur", "Merlot red wine"]),
        ("Olive oil", ["Gigantija Extra Virgin Olive Oil"]),
        ("Marmalades and jams", ["Tangerine marmalade", "Orange marmalade", "Lemon marmalade", "Prickly pear jam", "Fig jam", "Bambinella pear jam"]),
        ("Cheese, cured meat and pantry", ["Peppered sheep’s milk cheese", "Salami (Syrah wine, pistachio, piccante)", "Sun-dried tomatoes", "Sweet tomato paste", "Capers", "Raw honey", "Carob syrup", "Natural sea salt"]),
    ]
    return {
        "@type": "LocalBusiness",
        "@id": DOMAIN + "/#business",
        "name": f["name"],
        "legalName": f["legal"],
        "url": DOMAIN + "/",
        "description": "Gozo Cottage (Cottage Products (Gozo) Ltd) is a food producer in Xewkija, Gozo, Malta, making olive oil, liqueurs, marmalades, wine, cheese, salami and other traditional products from produce grown and harvested on the island of Gozo.",
        "slogan": "Genuine produce of Gozo",
        "foundingDate": "2003",
        "logo": {"@type": "ImageObject", "url": DOMAIN + "/images/gozo-cottage-logo.jpg",
                 "width": MAN["gozo-cottage-logo"]["solid"]["w"], "height": MAN["gozo-cottage-logo"]["solid"]["h"]},
        "image": [DOMAIN + "/images/og/og-home.jpg"],
        "telephone": f["phone"],
        "email": f["email"],
        "address": {"@type": "PostalAddress", "streetAddress": f["street_plain"], "addressLocality": f["locality"],
                    "postalCode": f["postal"], "addressRegion": "Gozo", "addressCountry": f["country"]},
        "sameAs": [f["facebook"]],
        "hasOfferCatalog": {
            "@type": "OfferCatalog", "name": "Gozo Cottage products",
            "itemListElement": [
                {"@type": "OfferCatalog", "name": n,
                 "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Product", "name": p}} for p in ps]}
                for n, ps in cats],
        },
    }


def jsonld(key):
    pg = PAGES[key]
    url = DOMAIN + pg["path"]
    site = {"@type": "WebSite", "@id": DOMAIN + "/#website", "url": DOMAIN + "/", "name": "Gozo Cottage",
            "inLanguage": "en", "publisher": {"@id": DOMAIN + "/#business"}}
    page = {"@type": "WebPage" if key == "home" else "WebPage", "@id": url + "#webpage", "url": url, "name": pg["title"],
            "description": pg["desc"], "inLanguage": "en", "isPartOf": {"@id": DOMAIN + "/#website"},
            "about": {"@id": DOMAIN + "/#business"}, "dateModified": MODIFIED,
            "primaryImageOfPage": {"@type": "ImageObject", "url": DOMAIN + pg["og_image"], "width": 1200, "height": 630}}
    graph = [business_node(), site, page]
    if key == "home":
        graph.append({"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]})
    else:
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Gozo Cottage", "item": DOMAIN + "/"},
            {"@type": "ListItem", "position": 2, "name": pg["title"].split(" | ")[0], "item": url}]})
    return {"@context": "https://schema.org", "@graph": graph}


# ---------------------------------------------------------------- head
def head(key, css, preload=""):
    pg = PAGES[key]
    url = DOMAIN + pg["path"]
    img = DOMAIN + pg["og_image"]
    ld = json.dumps(jsonld(key), ensure_ascii=False, indent=2)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(pg["title"])}</title>
<meta name="description" content="{esc(pg["desc"])}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#f6f0e3">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:site_name" content="Gozo Cottage">
<meta property="og:locale" content="en_GB">
<meta property="og:type" content="{pg["og_type"]}">
<meta property="og:title" content="{esc(pg["og_title"])}">
<meta property="og:description" content="{esc(pg["og_desc"])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(pg["og_alt"])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(pg["og_title"])}">
<meta name="twitter:description" content="{esc(pg["og_desc"])}">
<meta name="twitter:image" content="{img}">
<meta name="twitter:image:alt" content="{esc(pg["og_alt"])}">
<link rel="preload" href="/fonts/fraunces-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/dm-sans-latin.woff2" as="font" type="font/woff2" crossorigin>
{preload}<style>
{css}
</style>
<script type="application/ld+json">
{ld}
</script>
</head>'''


HERO_PRELOAD = ('<link rel="preload" as="image" type="image/webp" fetchpriority="high" '
                'imagesrcset="{srcset}" imagesizes="(min-width:860px) 480px, min(90vw, 420px)">\n')


def page(key, body, css, js, preload=""):
    return (head(key, css, preload) + "\n<body>\n<a class=\"skip\" href=\"#main\">Skip to content</a>\n"
            + header(key == "home") + "\n" + body + "\n" + footer() + f"\n<script>\n{js}\n</script>\n</body>\n</html>\n")


# ---------------------------------------------------------------- minify
def min_css(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s*([{}:;,>~+])\s*", r"\1", s)
    s = s.replace(";}", "}")
    return s.strip()


def min_js(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    s = re.sub(r"(?m)^\s*//.*$", "", s)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s*([{}();,=<>!&|:+?])\s*", r"\1", s)
    return s.strip()


def min_html(doc):
    # keep ld+json compact, strip comments except TODO markers, collapse whitespace
    doc = re.sub(r'(<script type="application/ld\+json">)(.*?)(</script>)',
                 lambda m: m.group(1) + json.dumps(json.loads(m.group(2)), ensure_ascii=False, separators=(",", ":")) + m.group(3),
                 doc, flags=re.S)
    doc = re.sub(r"<!--(?!\s*TODO).*?-->", "", doc, flags=re.S)
    parts = re.split(r"(<style>.*?</style>|<script[^>]*>.*?</script>)", doc, flags=re.S)
    out = []
    for p in parts:
        if p.startswith("<style>"):
            out.append("<style>" + min_css(p[7:-8]) + "</style>")
        elif p.startswith("<script") and "ld+json" not in p[:40]:
            tag_end = p.index(">") + 1
            out.append(p[:tag_end] + min_js(p[tag_end:-9]) + "</script>")
        elif p.startswith("<script"):
            out.append(p)
        else:
            p = re.sub(r">\s+<", "> <", p)
            p = re.sub(r"\s+", " ", p)
            p = re.sub(r"\s*(</?(?:html|head|body|header|footer|main|section|div|nav|ul|li|h[1-4]|p|figure|figcaption|dl|dt|dd|details|summary|address|meta|link|title)\b[^>]*>)\s*", r"\1", p)
            out.append(p)
    return "".join(out).strip() + "\n"


# ---------------------------------------------------------------- bodies
def legal_body():
    f = FACTS
    return f'''<main id="main" class="doc">
  <div class="wrap">
    <p class="crumbs"><a href="/">Gozo Cottage</a> › Legal Notice</p>
    <h1>Legal Notice &amp; Company Details</h1>
    <p class="lead">This website is operated for Gozo Cottage by {esc(f["legal"])}, Xewkija, Gozo, Malta.</p>
    <h2>Company details</h2>
    <address>
      <strong>{esc(f["legal"])}</strong><br>
      {f["street"]}<br>
      {f["locality"]} {f["postal"]}<br>
      Gozo, Malta<br>
      Phone: <a href="{f["phone_href"]}">{f["phone"]}</a><br>
      Email: <a href="mailto:{f["email"]}">{f["email"]}</a>
    </address>
    <!-- TODO: fehlt – VAT-Nummer und Company-Registration-Number von Cottage Products (Gozo) Ltd (open-questions.md Punkt 2) -->
    <p class="small" style="margin-top:1rem">VAT and company registration numbers are not published on this website yet.</p>
    <h2 id="funding">Funding information</h2>
    <p>Project part financed by the European Union. “Diversification through the introduction of new infrastructure and equipment”, Measure 4 Investments in Physical Assets, Sub-measure 4.2 – “Support for Investments in processing/marketing and/or development of agriculture products”. Rural Development Programme for Malta 2014–2020, co-financing rate: 75% European Union; 25% Government of Malta. The European Agricultural Fund for Rural Development: Europe investing in rural areas.</p>
    <figure class="photo">{pic("eu-rural-development-funding-notice", "(min-width:860px) 780px, 92vw")}</figure>
    <h2>Privacy</h2>
    <p>See our <a href="/privacy-policy/">Privacy Policy</a>. This website sets no cookies and loads no third-party scripts, fonts or trackers.</p>
    <p><a class="btn ghost" href="/">Back to the homepage</a></p>
  </div>
</main>'''


def privacy_body():
    content = open(os.path.join(ROOT, "src", "privacy.content.html"), encoding="utf8").read()
    return f'''<main id="main" class="doc">
  <div class="wrap">
    <p class="crumbs"><a href="/">Gozo Cottage</a> › Privacy Policy</p>
    <h1>Privacy Policy</h1>
{content}
    <p><a class="btn ghost" href="/">Back to the homepage</a></p>
  </div>
</main>'''


# ---------------------------------------------------------------- write
def write_pair(rel, doc):
    base = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(base), exist_ok=True)
    open(base + ".src.html", "w", encoding="utf8").write(doc)
    open(base + ".html", "w", encoding="utf8").write(min_html(doc))


def main():
    css = open(os.path.join(ROOT, "src", "style.css"), encoding="utf8").read()
    js = open(os.path.join(ROOT, "src", "app.js"), encoding="utf8").read()
    hero = MAN["gozo-olive-oil-on-bread-olive-grove"]
    srcset = ", ".join(f"/images/gozo-olive-oil-on-bread-olive-grove-{v['w']}.webp {v['w']}w" for v in hero["variants"])
    pre = HERO_PRELOAD.format(srcset=srcset)

    home_body = expand(open(os.path.join(ROOT, "src", "index.body.html"), encoding="utf8").read())
    write_pair("index", page("home", home_body, css, js, pre))
    write_pair("privacy-policy/index", page("privacy", expand(privacy_body()), css, js))
    write_pair("legal-notice/index", page("legal", expand(legal_body()), css, js))

    # robots / sitemap / llms.txt / vercel.json
    bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User", "Claude-SearchBot", "anthropic-ai",
            "PerplexityBot", "Google-Extended", "Applebot-Extended", "Bingbot", "CCBot"]
    robots = "User-agent: *\nAllow: /\n\n" + "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots) + f"Sitemap: {DOMAIN}/sitemap.xml\n"
    open(os.path.join(ROOT, "robots.txt"), "w").write(robots)
    urls = "".join(f"  <url><loc>{DOMAIN}{p['path']}</loc><lastmod>{MODIFIED}</lastmod></url>\n" for p in PAGES.values())
    open(os.path.join(ROOT, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")
    f = FACTS
    llms = f"""# Gozo Cottage

> Gozo Cottage ({f['legal']}) is a food producer in Xewkija on the island of Gozo, Malta. It makes olive oil, liqueurs, marmalades and jams, wine, peppered cheese, salami and other traditional products from fresh produce grown and harvested on Gozo. Genuine produce of Gozo, est. 2003.

## Facts
- Name: Gozo Cottage (legal name: {f['legal']})
- Address: {f['street_plain']}, {f['locality']} {f['postal']}, Gozo, Malta
- Phone: {f['phone']}
- Email: {f['email']}
- Facebook: {f['facebook']}
- Opening hours: not published
- Sold in: many selected delicatessens and leading establishments across Malta and Gozo (per the company); no online shop listed

## Products
- Gigantija Extra Virgin Olive Oil
- Liqueurs: Mandolin (tangerine), Laring (orange), Limuncell (lemon), Morr (bitter-sweet herbs, bitter orange, carob), Morr (almond)
- Marmalades and jams: tangerine, orange, lemon, prickly pear, fig, Bambinella pear
- Peppered sheep's milk cheese, salami (Syrah wine, pistachio, piccante), sun-dried tomatoes, sweet tomato paste, capers
- Raw honey, carob syrup, natural sea salt (Xwejni Bay)
- Merlot red wine

## Pages
- [Home]({DOMAIN}/): products, farming tradition, FAQ, contact
- [Privacy Policy]({DOMAIN}/privacy-policy/)
- [Legal Notice]({DOMAIN}/legal-notice/)
"""
    open(os.path.join(ROOT, "llms.txt"), "w").write(llms)

    old = {"/about-us": "/#grown-in-gozo", "/process-2": "/#grown-in-gozo", "/products": "/#wines-liqueurs",
           "/contact-us": "/#visit-contact", "/news": "/", "/new-packaging": "/", "/new-website": "/", "/tradefair2010": "/"}
    redirects = []
    for s, d in old.items():
        redirects.append({"source": s, "destination": d, "permanent": True})
        redirects.append({"source": s + "/", "destination": d, "permanent": True})
    vercel = {
        "trailingSlash": True,
        "redirects": redirects,
        "headers": [
            {"source": "/images/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},
            {"source": "/fonts/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},
        ],
    }
    json.dump(vercel, open(os.path.join(ROOT, "vercel.json"), "w"), indent=2)
    print("built")


if __name__ == "__main__":
    main()

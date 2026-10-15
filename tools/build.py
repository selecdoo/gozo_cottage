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
import sys

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


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import i18n as I  # noqa: E402

LANGS = I.LANGS
PRIVACY_META = {
    "title": "Website Privacy Policy | Gozo Cottage",
    "desc": "How Gozo Cottage, Cottage Products (Gozo) Ltd in Xewkija, Gozo, handles personal information on gozocottage.com. Contact us with privacy questions.",
    "og_title": "Privacy Policy: how Gozo Cottage handles your information",
    "og_desc": "Read how Cottage Products (Gozo) Ltd, the company behind Gozo Cottage in Xewkija, Gozo, collects, uses and protects personal information.",
    "og_alt": "Freshly harvested green olives with the Gozo Cottage logo and the words Privacy Policy",
}
BASE = {"home": "/", "legal": "/legal-notice/", "privacy": "/privacy-policy/"}


def page_list():
    """Every built page: dict(key, lang, path, file, meta...)."""
    out = []
    for lang in LANGS:
        for key in ("home", "legal"):
            m = dict(I.META[lang][key])
            path = I.PREFIX[lang] + BASE[key]
            out.append(dict(m, key=key, lang=lang, path=path, file=(path + "index").lstrip("/"),
                            og_image=f"/images/og/og-{key}-{lang}.jpg", og_type="website" if key == "home" else "article"))
    out.append(dict(PRIVACY_META, key="privacy", lang="en", path=BASE["privacy"], file="privacy-policy/index",
                    og_image="/images/og/og-privacy.jpg", og_type="article"))
    return out


PAGES = {(p["key"], p["lang"]): p for p in page_list()}


def has_translations(key):
    return key in ("home", "legal")


# ---------------------------------------------------------------- helpers
def esc(s):
    return H.escape(s, quote=True)


def pic(slug, sizes, cls="", eager=False, lang="en"):
    m = MAN[slug]
    srcset = ", ".join(f"/images/{slug}-{v['w']}.webp {v['w']}w" for v in m["variants"])
    fb = m["fallback"]
    attrs = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return (f'<picture><source type="image/webp" srcset="{srcset}" sizes="{esc(sizes)}">'
            f'<img src="/images/{slug}.jpg" width="{fb["w"]}" height="{fb["h"]}" alt="{esc(I.ALT[lang][slug])}"{c} {attrs}></picture>')


def logo(width, lang, eager=False):
    m = MAN["gozo-cottage-logo"]
    vs = sorted(m["variants"], key=lambda x: x["w"])
    srcset = ", ".join(f"/images/gozo-cottage-logo-{v['w']}.webp {v['w']}w" for v in vs)
    attrs = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    return (f'<picture><source type="image/webp" srcset="{srcset}" sizes="{width}px">'
            f'<img src="/images/gozo-cottage-logo.jpg" width="{vs[0]["w"]}" height="{vs[0]["h"]}" alt="{esc(I.ALT[lang]["_logo"])}" {attrs}></picture>')


def expand(body, lang):
    def p(m):
        parts = m.group(1).split("|")
        return pic(parts[0], parts[1], parts[2] if len(parts) > 2 else "", eager=len(parts) > 3 and parts[3] == "eager", lang=lang)
    body = re.sub(r"\{\{pic:([^}]+)\}\}", p, body)
    body = re.sub(r"\{\{logo:(\d+)\}\}", lambda m: logo(m.group(1), lang), body)
    faq = "\n".join(
        f'        <details>\n          <summary><h3>{esc(q)}</h3></summary>\n          <p>{esc(a)}</p>\n        </details>'
        for q, a in I.FAQ[lang])
    return body.replace("{{faq}}", faq)


def header(lang, key):
    u = I.UI[lang]
    pre = I.PREFIX[lang]
    items = "".join(f'<li><a href="{pre}/{h}">{t}</a></li>' for h, t in u["nav"])
    lg = logo(160, lang, eager=True)
    sw = []
    for l in LANGS:
        href = I.PREFIX[l] + (BASE[key] if has_translations(key) else "/")
        cur = ' aria-current="true"' if l == lang else ""
        sw.append(f'<li><a href="{href}" hreflang="{l}" lang="{l}"{cur} aria-label="{l.upper()} – {I.LANG_NAME[l]}">{l.upper()}</a></li>')
    sws = "".join(sw)
    return f"""<header class="site">
  <div class="wrap bar">
    <a class="brand" href="{pre}/" aria-label="{esc(u["home_aria"])}">{lg}</a>
    <nav class="main" aria-label="{esc(u["nav_aria"])}"><ul>{items}</ul></nav>
    <ul class="lang" aria-label="{esc(u["lang_aria"])}">{sws}</ul>
    <details class="menu"><summary>{u["menu"]}</summary><ul>{items}</ul></details>
  </div>
</header>"""


def footer(lang):
    f = FACTS
    u = I.UI[lang]
    pre = I.PREFIX[lang]
    links = "\n".join(f'          <li><a href="{pre}/{h}">{t}</a></li>' for h, t in u["f_links"])
    leg = esc(f["legal"])
    legal_href = pre + BASE["legal"]
    fund = pic("eu-rural-development-funding-notice", "(min-width:860px) 560px, 92vw", lang=lang)
    copy = u["copy"].format(legal=leg)
    fb_path = "M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"
    return f"""<footer class="site">
  <div class="wrap">
    <div class="cols">
      <div>
        <p class="ft">Gozo Cottage</p>
        <address>{leg}<br>{f["street"]}<br>{f["locality"]} {f["postal"]}<br>Gozo, Malta</address>
        <p style="margin-top:.8rem"><a href="{f["phone_href"]}">{f["phone"]}</a><br><a href="mailto:{f["email"]}">{f["email"]}</a><br><a href="{esc(f["maps"])}" target="_blank" rel="noopener">{u["maps"]}</a></p>
      </div>
      <div>
        <p class="ft">{u["f_explore"]}</p>
        <ul>
{links}
        </ul>
      </div>
      <div>
        <p class="ft">{u["f_legal"]}</p>
        <ul>
          <li><a href="/privacy-policy/" hreflang="en" lang="en">{u["privacy"]}</a></li>
          <li><a href="{legal_href}">{u["legal"]}</a></li>
        </ul>
        <div class="social">
          <a href="{f["facebook"]}" target="_blank" rel="noopener" aria-label="{esc(u["fb_aria"])}"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="{fb_path}"/></svg></a>
        </div>
      </div>
    </div>
    <div class="legalline">
      <div class="fundfoot">{fund}</div>
      <p>{u["fund_line"]} <a href="{legal_href}#funding">{u["details"]}</a></p>
      <p>{copy}</p>
    </div>
  </div>
</footer>"""


# ---------------------------------------------------------------- JSON-LD
def business_node(lang, img):
    f = FACTS
    s = I.SCHEMA[lang]
    return {
        "@type": "LocalBusiness",
        "@id": DOMAIN + "/#business",
        "name": f["name"],
        "legalName": f["legal"],
        "url": DOMAIN + "/",
        "description": s["desc"],
        "slogan": s["slogan"],
        "foundingDate": "2003",
        "logo": {"@type": "ImageObject", "url": DOMAIN + "/images/gozo-cottage-logo.jpg",
                 "width": MAN["gozo-cottage-logo"]["solid"]["w"], "height": MAN["gozo-cottage-logo"]["solid"]["h"]},
        "image": [DOMAIN + img],
        "telephone": f["phone"],
        "email": f["email"],
        "address": {"@type": "PostalAddress", "streetAddress": f["street_plain"], "addressLocality": f["locality"],
                    "postalCode": f["postal"], "addressRegion": "Gozo", "addressCountry": f["country"]},
        "sameAs": [f["facebook"]],
        "hasOfferCatalog": {
            "@type": "OfferCatalog", "name": s["catalog"],
            "itemListElement": [
                {"@type": "OfferCatalog", "name": n,
                 "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Product", "name": p}} for p in ps]}
                for n, ps in s["cats"]],
        },
    }


def jsonld(pg):
    key, lang = pg["key"], pg["lang"]
    url = DOMAIN + pg["path"]
    home_url = DOMAIN + I.PREFIX[lang] + "/"
    site = {"@type": "WebSite", "@id": DOMAIN + "/#website", "url": DOMAIN + "/", "name": "Gozo Cottage",
            "inLanguage": LANGS, "publisher": {"@id": DOMAIN + "/#business"}}
    page = {"@type": "WebPage", "@id": url + "#webpage", "url": url, "name": pg["title"],
            "description": pg["desc"], "inLanguage": lang, "isPartOf": {"@id": DOMAIN + "/#website"},
            "about": {"@id": DOMAIN + "/#business"}, "dateModified": MODIFIED,
            "primaryImageOfPage": {"@type": "ImageObject", "url": DOMAIN + pg["og_image"], "width": 1200, "height": 630}}
    graph = [business_node(lang, pg["og_image"]), site, page]
    if key == "home":
        graph.append({"@type": "FAQPage", "@id": url + "#faq", "inLanguage": lang, "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in I.FAQ[lang]]})
    else:
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Gozo Cottage", "item": home_url},
            {"@type": "ListItem", "position": 2, "name": pg["title"].split(" | ")[0], "item": url}]})
    return {"@context": "https://schema.org", "@graph": graph}


# ---------------------------------------------------------------- head
def head(pg, css, preload=""):
    key, lang = pg["key"], pg["lang"]
    url = DOMAIN + pg["path"]
    img = DOMAIN + pg["og_image"]
    ld = json.dumps(jsonld(pg), ensure_ascii=False, indent=2)
    alts = ""
    og_alt_loc = ""
    if has_translations(key):
        for l in LANGS:
            alts += f'<link rel="alternate" hreflang="{l}" href="{DOMAIN + I.PREFIX[l] + BASE[key]}">\n'
        alts += f'<link rel="alternate" hreflang="x-default" href="{DOMAIN + BASE[key]}">\n'
        og_alt_loc = "".join(f'<meta property="og:locale:alternate" content="{I.OG_LOCALE[l]}">\n' for l in LANGS if l != lang)
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(pg["title"])}</title>
<meta name="description" content="{esc(pg["desc"])}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{url}">
{alts}<meta name="theme-color" content="#f6f0e3">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:site_name" content="Gozo Cottage">
<meta property="og:locale" content="{I.OG_LOCALE[lang]}">
{og_alt_loc}<meta property="og:type" content="{pg["og_type"]}">
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
</head>"""


HERO_PRELOAD = ('<link rel="preload" as="image" type="image/webp" fetchpriority="high" '
                'imagesrcset="{srcset}" imagesizes="(min-width:860px) 480px, min(90vw, 420px)">\n')


def page(pg, body, css, js, preload=""):
    lang, key = pg["lang"], pg["key"]
    skip = I.UI[lang]["skip"]
    return (head(pg, css, preload) + f'\n<body>\n<a class="skip" href="#main">{skip}</a>\n'
            + header(lang, key) + "\n" + body + "\n" + footer(lang) + f"\n<script>\n{js}\n</script>\n</body>\n</html>\n")


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
def legal_body(lang):
    f = FACTS
    u = I.UI[lang]
    pre = I.PREFIX[lang]
    leg = esc(f["legal"])
    lead = u["legal_lead"].format(legal=leg)
    fund = pic("eu-rural-development-funding-notice", "(min-width:860px) 780px, 92vw", lang=lang)
    return f"""<main id="main" class="doc">
  <div class="wrap">
    <p class="crumbs"><a href="{pre}/">{u["crumb_home"]}</a> › {u["crumb_legal"]}</p>
    <h1>{u["legal_h1"]}</h1>
    <p class="lead">{lead}</p>
    <h2>{u["legal_h2_company"]}</h2>
    <address>
      <strong>{leg}</strong><br>
      {f["street"]}<br>
      {f["locality"]} {f["postal"]}<br>
      Gozo, Malta<br>
      {u["phone"]}: <a href="{f["phone_href"]}">{f["phone"]}</a><br>
      {u["email"]}: <a href="mailto:{f["email"]}">{f["email"]}</a>
    </address>
    <!-- TODO: fehlt – VAT-Nummer und Company-Registration-Number von Cottage Products (Gozo) Ltd (open-questions.md Punkt 2) -->
    <p class="small" style="margin-top:1rem">{u["legal_vat"]}</p>
    <h2 id="funding">{u["legal_h2_fund"]}</h2>
    <p>{u["legal_fund"]}</p>
    <figure class="photo">{fund}</figure>
    <h2>{u["legal_h2_priv"]}</h2>
    <p>{u["legal_priv"]}</p>
    <p><a class="btn ghost" href="{pre}/">{u["back"]}</a></p>
  </div>
</main>"""


def privacy_body():
    content = open(os.path.join(ROOT, "src", "privacy.content.html"), encoding="utf8").read()
    back = I.UI["en"]["back"]
    return f"""<main id="main" class="doc">
  <div class="wrap">
    <p class="crumbs"><a href="/">Gozo Cottage</a> › Privacy Policy</p>
    <h1>Privacy Policy</h1>
{content}
    <p><a class="btn ghost" href="/">{back}</a></p>
  </div>
</main>"""


# ---------------------------------------------------------------- write
def write_pair(rel, doc):
    base = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(base), exist_ok=True)
    open(base + ".src.html", "w", encoding="utf8").write(doc)
    open(base + ".html", "w", encoding="utf8").write(min_html(doc))


LLMS = """# Gozo Cottage

> Gozo Cottage ({legal}) is a food producer in Xewkija on the island of Gozo, Malta. It makes olive oil, liqueurs, marmalades and jams, wine, peppered cheese, salami and other traditional products from fresh produce grown and harvested on Gozo. Genuine produce of Gozo, est. 2003.

## Facts
- Name: Gozo Cottage (legal name: {legal})
- Address: {street_plain}, {locality} {postal}, Gozo, Malta
- Phone: {phone}
- Email: {email}
- Facebook: {facebook}
- Opening hours: not published
- Sold in: many selected delicatessens and leading establishments across Malta and Gozo (per the company); no online shop listed
- Languages of this website: English, Maltese (Malti), Italian (Italiano)

## Products
- Gigantija Extra Virgin Olive Oil
- Liqueurs: Mandolin (tangerine), Laring (orange), Limuncell (lemon), Morr (bitter-sweet herbs, bitter orange, carob), Morr (almond)
- Marmalades and jams: tangerine, orange, lemon, prickly pear, fig, Bambinella pear
- Peppered sheep's milk cheese, salami (Syrah wine, pistachio, piccante), sun-dried tomatoes, sweet tomato paste, capers
- Raw honey, carob syrup, natural sea salt (Xwejni Bay)
- Merlot red wine

## Pages
- [Home (English)]({d}/): products, farming tradition, FAQ, contact
- [Home (Malti)]({d}/mt/)
- [Home (Italiano)]({d}/it/)
- [Legal Notice]({d}/legal-notice/) · [MT]({d}/mt/legal-notice/) · [IT]({d}/it/legal-notice/)
- [Privacy Policy (English only)]({d}/privacy-policy/)
"""


def main():
    css = open(os.path.join(ROOT, "src", "style.css"), encoding="utf8").read()
    js = open(os.path.join(ROOT, "src", "app.js"), encoding="utf8").read()
    hero = MAN["gozo-olive-oil-on-bread-olive-grove"]
    srcset = ", ".join(f"/images/gozo-olive-oil-on-bread-olive-grove-{v['w']}.webp {v['w']}w" for v in hero["variants"])
    pre = HERO_PRELOAD.format(srcset=srcset)

    for (key, lang), pg in PAGES.items():
        if key == "home":
            body = expand(open(os.path.join(ROOT, "src", f"index.body.{lang}.html"), encoding="utf8").read(), lang)
            write_pair(pg["file"], page(pg, body, css, js, pre))
        elif key == "legal":
            write_pair(pg["file"], page(pg, expand(legal_body(lang), lang), css, js))
        else:
            write_pair(pg["file"], page(pg, expand(privacy_body(), "en"), css, js))

    bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-User", "Claude-SearchBot", "anthropic-ai",
            "PerplexityBot", "Google-Extended", "Applebot-Extended", "Bingbot", "CCBot"]
    robots = "User-agent: *\nAllow: /\n\n" + "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots) + f"Sitemap: {DOMAIN}/sitemap.xml\n"
    open(os.path.join(ROOT, "robots.txt"), "w").write(robots)

    urls = ""
    for pg in PAGES.values():
        alt = ""
        if has_translations(pg["key"]):
            for l in LANGS:
                alt += f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{DOMAIN + I.PREFIX[l] + BASE[pg["key"]]}"/>'
            alt += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{DOMAIN + BASE[pg["key"]]}"/>'
        urls += f"  <url>\n    <loc>{DOMAIN}{pg['path']}</loc>\n    <lastmod>{MODIFIED}</lastmod>{alt}\n  </url>\n"
    open(os.path.join(ROOT, "sitemap.xml"), "w").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + urls + "</urlset>\n")

    open(os.path.join(ROOT, "llms.txt"), "w").write(LLMS.format(d=DOMAIN, **FACTS))

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
    print("built", len(PAGES), "pages")


if __name__ == "__main__":
    main()

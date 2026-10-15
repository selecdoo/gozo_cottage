# Open Questions – Gozo Cottage

Alles, was fehlt oder unklar ist. Im Code jeweils als `<!-- TODO: … -->` markiert. Nichts davon wurde erfunden.

## Fehlende Fakten
1. **Öffnungszeiten** – weder auf gozocottage.com noch öffentlich auf Facebook lesbar. Abschnitt „Visit / Contact“ sagt deshalb nur „not published“; kein `openingHoursSpecification` im Schema.
2. **VAT-Nummer / Company-Registration-Number** von Cottage Products (Gozo) Ltd – steht nirgends. Legal Notice trägt ein sichtbares TODO.
3. **Geo-Koordinaten** – nicht veröffentlicht; Schema ohne `geo`. Google-Maps-Link basiert nur auf der Postadresse. → Bitte Google-Business-Profil-Link oder Koordinaten liefern.
4. **Weitere Social-Profile** (Instagram, TikTok, YouTube …) – nur Facebook gefunden. Falls es Instagram gibt: Link nachliefern (Footer + `sameAs`).
5. **Facebook-Details** (Adresse, Telefon, Öffnungszeiten, Kategorie) – öffentlich ohne Login nicht auslesbar. Bitte gegen die Seite prüfen.
6. **Wo/wie kaufbar (FAQ 3)** – belegt ist nur: „selected delicatessens and … leading establishments all over Malta and Gozo“. Unklar: Online-Shop? Hofladen/Besuch möglich? Export/B2B-Preislisten? Messen (nur eine leere Seite „Trade Fair 2010“)? Die FAQ-Antwort sagt deshalb ausdrücklich, dass die bisherige Website keinen Online-Shop nennt.
7. **Preise** – nirgends angegeben, daher keine Preise auf der Seite.
8. **Liste der Verkaufsstellen (Delikatessengeschäfte)** – wäre ein starkes Local-SEO-Signal, liegt nicht vor.

## Sortiment – Abweichung zwischen Originalseite und Fotos
9. **Wein (Merlot) und Salami** stehen nicht im Produktkatalog der Originalseite, sind aber auf den mitgelieferten Gozo-Cottage-gebrandeten Fotos zu sehen (Etikett „Merlot“, Salami „Syrah D.O.K. Wine / Pistachio / Piccante“, Amphore mit Logo). Die Seite zeigt sie deshalb nur mit dem, was auf den Etiketten steht (keine Rebsorten-Herkunft, keine Zutaten, keine Preise). Bitte bestätigen: aktuelles Sortiment? Herkunft der Trauben (Gozo?) und Schweinefleisch („local pork“ nennt nur der Projekttext)?
10. **Gaulos Dry Gin (Gozo Distillers)** – Etikett „Distilled & Bottled in Gozo“, aber nicht Gozo-Cottage-Marke. Ist das ein eigenes Produkt, ein Partnerprodukt oder ein Vertriebsartikel? Auf der Seite wird er neutral als „Gaulos Dry Gin by Gozo Distillers“ gezeigt, ohne zu behaupten, dass Gozo Cottage ihn herstellt. Bei Fremdprodukt → Galerie entfernen oder umbetiteln.
11. **Sweet Tomato Paste** – nur auf dem Foto, nicht im Katalog der Originalseite.
12. **Nicht angeboten bzw. nicht belegt, daher nicht beworben:** Essig, Sekt, Dessertwein, Likörwein, frischer/gereifter Käse (nur „Peppered Cheese“ ist gelistet). Die Originalseite nennt diese nur als Teil des Förderprojekts („aims at producing“) – die Seite erwähnt sie deshalb nicht als Angebot.
13. **„Gozitan wine“ als Keyword** – im Text nur vorsichtig verwendet (Winery & Cellars laut Projektbeschreibung, Merlot auf Fotos). Falls die Trauben nicht aus Gozo stammen, bitte den Satz anpassen.

## Bilder
14. **Nicht verwendet:** `490181379…jpg` (Bar-Regal mit Smirnoff, Gordon’s, Jameson … und Luftballons) – fremde Marken, kein Produktbezug zu Gozo Cottage. Auf Wunsch einbaubar.
15. **Person auf Bild 18** (Mann mit Weinglas bei der Amphore) – Name/Rolle unbekannt, Alt-Text bleibt neutral. Einwilligung zur Veröffentlichung klären.
16. `627760286…jpg` (Orange-Marmelade) ist nur 720 × 960 px – für Hero zu klein, in der Seite nur als Karten-Bild genutzt.

## Rechtliches
17. **Privacy Policy ist ein generischer Fremdtext** – wörtlich wie gefordert übernommen, enthält aber Reste anderer Vorlagen („Zendesk“, „Our Service Agreement“, Verweis auf „Section 16“, Subscribers/Accounts/Live-Chat/Payment), die zur Seite nicht passen. Empfehlung: durch eine zur tatsächlichen Datenverarbeitung passende DSGVO-Erklärung ersetzen (neue Seite verarbeitet keine personenbezogenen Daten außer Server-Logs beim Hoster; kein Formular, keine Cookies, keine Drittanbieter).
18. **Kein Impressum / keine AGB** auf der Originalseite. `legal-notice/` enthält nur die belegten Firmendaten; Handelsregister-/VAT-Nummer fehlen (Punkt 2). AGB: keine vorhanden → keine Seite.
19. **EU-Förderhinweis:** Tafel („Project part financed by the European Union … 75 % EU / 25 % Government of Malta“) ist als Bild + Text eingebunden. Bitte prüfen, ob die Anzeigepflicht nach Projektende noch gilt/anders gefordert ist.
20. **Kontaktformular** der alten Seite (WordPress CF7) entfällt – statische Seite hat keinen Backend-Endpunkt. Ersatz: `mailto:` + `tel:`. Bei Bedarf Formular-Dienst nachrüsten (dann Privacy Policy anpassen).

## Domain / Betrieb
21. **Canonical = https://www.gozocottage.com/** (laut Briefing). Solange die Seite auf einer anderen Domain (Preview/Staging) läuft, zeigen Canonical/OG auf die Live-Domain → Suchmaschinen indexieren die Kopie nicht. Beim Go-Live DNS/Hosting klären (Hosting ist nicht Teil dieses Auftrags).
22. **Robots-Policy:** Briefing verlangt `index, follow`; die Seite ist damit bei Veröffentlichung sofort indexierbar. Bei einem Staging-Test vorher `noindex` setzen.
23. **Redirects:** `vercel.json` enthält die 301-Map der alten URLs. Gilt nur, wenn auf Vercel gehostet; sonst auf den tatsächlichen Host übertragen.
24. **Lighthouse** – siehe `seo-report.md` (lokal gemessen; echte Mobilfunk-Messung steht noch aus).

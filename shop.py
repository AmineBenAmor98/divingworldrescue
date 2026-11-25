"""Render the equipment directory, grouped listings and local product pages."""
import re
import json
import unicodedata
from html import escape
from urllib.parse import urlencode
from typography import product_copy


def category_photo(page):
    selected = {
        "tauch-shop--atemregler-zubehoer": "Atemregler-Set Genius / Venus",
        "tauch-shop--jacket-bcd": "TDS Jacket Nemo",
        "tauch-shop--neopren": "TDS Zero 5.0 · Herren",
        "tauch-shop--bekleidung": "TDS Lycra-Shirt Whale",
        "frti-kurse--frti-material-eh-material": "First Aid Kit Small",
    }.get(page["slug"])
    if selected:
        return next(item["photos"][0] for item in catalogue_items(page) if item["name"] == selected)
    return "../" + next(b["src"] for b in page["blocks"] if b["type"] == "photo")


def shop_directory(pages):
    departments = [
        ("ausruestung", "Ausrüstung zum Tauchen", [
            ("tauch-shop--masken-flossenzubehoer", "Masken & Flossen", "ABC-Sets, einzelne Masken und Flossenbänder."),
            ("tauch-shop--neopren", "Anzüge & Neopren", "Nass- und Trockenanzüge, Füßlinge und Handschuhe."),
            ("tauch-shop--atemregler-zubehoer", "Atemregler", "Erste und zweite Stufen, Oktopusse und komplette Sets."),
            ("tauch-shop--jacket-bcd", "Tarierjackets & Wings", "Jackets für Sport- und Reisetauchen sowie Kupplungen."),
            ("tauch-shop--computer", "Tauchcomputer", "Uhrenmodelle von Ratio, DiveBrain und SUNROAD vergleichen."),
            ("hud", "Head-up-Display für die Maske", "Der Maskencomputer von Daïve zeigt Tauchdaten im Sichtfeld."),
        ]),
        ("unterwegs", "Packen & Ausrüsten", [
            ("tauch-shop--koffer-taschen", "Koffer & Taschen", "Trolleys für die Reise und gepolsterte Taschen für den Atemregler."),
            ("tauch-shop--zubehoer", "Zubehör für den Tauchgang", "Unterwassergehäuse, Logbücher, Halterungen und Werkzeuge."),
        ]),
        ("bekleidung-geschenke", "Bekleidung & Geschenke", [
            ("tauch-shop--bekleidung", "Bekleidung", "Lycra-Shirts fürs Wasser, Hoodies und Fleecejacken für an Land."),
            ("tauch-shop--schmuck", "Schmuck & Anhänger", "Ketten- und Schlüsselanhänger mit Motiven aus der Unterwasserwelt."),
        ]),
        ("erste-hilfe", "Erste Hilfe", [
            ("erste-hilfe-material-zubehoer", "Erste-Hilfe-Zubehör", "HEROTAG für den Schlüsselbund, Erste-Hilfe-Scheren und Diagnostikleuchten."),
            ("frti-kurse--frti-material-eh-material", "Material für Erste Hilfe & FRTI", "Pflasterboxen, kompakte Erste-Hilfe-Sets und weiteres Material."),
        ]),
    ]
    sections = []
    for anchor, title, entries in departments:
        rows = []
        for slug, label, description in entries:
            photo = category_photo(pages[slug])
            rows.append(f'''<a class="department-item" href="{slug}.html">
              <img src="{escape(photo)}" alt="" loading="lazy">
              <span><strong>{escape(label)}</strong><small>{escape(description)}</small></span>
              <i aria-hidden="true">→</i></a>''')
        sections.append(f'<section class="department" id="{anchor}"><h2>{escape(title)}</h2><div>{"".join(rows)}</div></section>')
    offers = [
        ("sonderangebote", "Sonderangebote", "Vom HOTDIVE ABC-Set bis zum Displayschutz. Hier stehen die Angebote und ihre Bedingungen."),
        ("im-auftrag-zu-verkaufen", "Verkauf im Kundenauftrag", "Einzelstücke wie Tauchcomputer, Anzüge und Flossen aus Kundenbesitz."),
    ]
    promos = []
    for slug, title, description in offers:
        photo = next(b["src"] for b in pages[slug]["blocks"] if b["type"] == "photo")
        promos.append(f'''<a class="shop-offer" href="{slug}.html"><img src="../{photo}" alt="" loading="lazy">
          <span><strong>{title}</strong><small>{description}</small></span><i aria-hidden="true">→</i></a>''')
    return '<div class="wrap shop-edit">' + shop_search(pages) + '<div class="shop-browse"><nav class="shop-offers" aria-label="Angebote und Einzelstücke">' + ''.join(promos) + '</nav>' + ''.join(sections) + '</div></div>'


def shop_search(pages):
    records = []
    for page in pages.values():
        if not (page["slug"].startswith("tauch-shop--") or page.get("catalogue")):
            continue
        for item in catalogue_items(page):
            records.append({"name": item["name"], "price": item["price"],
                "summary": item["summary"], "category": page["title"],
                "url": item["slug"] + ".html", "image": item["photos"][0],
                "terms": " ".join([item["group"], *item["specs"].values()])})
    # Repeated listings share one search result. Keep all descriptions and
    # category/specification terms searchable, while retaining every source page.
    merged = {}
    for record in records:
        key = record["name"].casefold()
        if key in merged:
            merged[key]["terms"] += " " + " ".join([record["category"], record["summary"], record["terms"]])
        else:
            merged[key] = record
    index = json.dumps(list(merged.values()), ensure_ascii=False).replace("<", "\\u003c")
    return f'''<section class="shop-search" hidden aria-labelledby="shop-search-title">
      <div><h2 id="shop-search-title">Was suchst du?</h2><p>Suche im Sortiment oder entdecke die Kategorien darunter.</p></div>
      <div><label for="shop-query">Produkt, Marke oder Eigenschaft</label><div class="search-field"><input type="search" id="shop-query" placeholder="z. B. Tauchcomputer, Ratio, Handschuhe" autocomplete="off" aria-controls="shop-search-results"><button type="button" hidden class="clear-search">Zurücksetzen</button></div></div>
      <p class="search-status" role="status" aria-live="polite"></p>
      <div id="shop-search-results" class="shop-results" hidden></div>
      <script type="application/json" id="shop-index">{index}</script>
    </section>'''


def inquiry(product):
    query = urlencode({"thema": "Ausrüstung und Verleih", "produkt": product})
    return f'<a class="product-link" href="anfrage.html?{escape(query)}">Verfügbarkeit anfragen</a>'


def slugify(text):
    folded = unicodedata.normalize("NFKD", text.casefold())
    ascii_text = folded.encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")


def catalogue_items(page):
    items = []
    for block in page["blocks"]:
        if "product" in block:
            product = block["product"]
            slug = "produkt-" + page["slug"].removeprefix("tauch-shop--") + "-" + slugify(product["name"])
            items.append(dict(product, slug=slug, blocks=[], photos=[]))
        if items:
            items[-1]["blocks"].append(block)
            if block["type"] == "photo":
                items[-1]["photos"].append("../" + block["src"])
    return items


def category_products(items):
    groups = {}
    for item in items:
        groups.setdefault(item["group"], []).append(item)
    navigation = []
    sections = []
    for label, members in groups.items():
        anchor = slugify(label)
        navigation.append(f'<a href="#{anchor}">{escape(label)} <span>{len(members)}</span></a>')
        rows = []
        for item in sorted(members, key=lambda i: i["name"].casefold()):
            url = item["slug"] + ".html"
            name = escape(item["name"])
            note = f'<small>{escape(item["note"])}</small>' if item.get("note") else ""
            terms = escape(" ".join([item["name"], item["summary"], item["group"], *item["specs"].values()]), quote=True)
            amount = re.search(r"(\d+),(\d{2})", item["price"])
            cents = int(amount[1]) * 100 + int(amount[2]) if amount else ""
            rows.append(f'''<article class="stock-row" data-cents="{cents}" data-name="{name}" data-search="{terms}"><a href="{url}">
              <span class="stock-thumb"><img src="{item["photos"][0]}" loading="lazy" alt=""></span>
              <div class="stock-caption"><h3>{name}</h3><p>{escape(item["summary"])}</p></div>
              <div class="stock-value"><strong>{escape(item["price"])}</strong>{note}
              <span class="view-item">Zum Produkt <span aria-hidden="true">→</span></span></div>
            </a></article>''')
        sections.append(f'<section class="stock-family" id="{anchor}"><h2>{escape(label)}</h2>{"".join(rows)}</section>')
    return f'''<div class="wrap catalogue"><nav class="catalogue-nav" aria-label="Produktgruppen">
    <div class="category-search" hidden><label for="category-query">In dieser Kategorie suchen</label><input id="category-query" type="search" placeholder="Produkt oder Eigenschaft" autocomplete="off"><p role="status" aria-live="polite"></p></div><details class="stock-groups"><summary>Produktgruppen</summary>{"".join(navigation)}</details>
    <label class="sort-order" hidden>Sortierung je Gruppe<select>
    <option value="name">Name (A–Z)</option><option value="asc">Preis aufsteigend</option>
    <option value="desc">Preis absteigend</option></select></label></nav><div>{"".join(sections)}</div></div>'''


def product_detail(item, parent):
    name = escape(item["name"])
    photos = item["photos"]
    image = f'<a class="item-photo" href="{photos[0]}" aria-label="Produktfoto vergrößern: {name}"><img src="{photos[0]}" alt="{name}"></a>'
    gallery = ''.join(f'<a href="{url}" aria-label="Produktansicht {i} vergrößern"><img src="{url}" alt="Produktansicht {i}" loading="lazy"></a>' for i, url in enumerate(photos[1:], 2))
    if gallery:
        gallery = f'<details class="item-views"><summary>Weitere Ansichten ({len(photos) - 1})</summary><div class="item-gallery">{gallery}</div></details>'
    specs = ''.join(f'<div><dt>{escape(k)}</dt><dd>{escape(v)}</dd></div>' for k, v in item["specs"].items())
    note = f'<p class="item-note">{escape(item["note"])}</p>' if item.get("note") else ""
    # Keep full listed specifications and options for shoppers who need more detail.
    paragraphs = []
    if not parent.get("catalogue"):
        for block in item["blocks"]:
            text = block.get("text", "").strip()
            if not text or text in paragraphs or text in ("Wir freuen uns über Ihre Nachricht.", "Merkmale:", "Eigenschaften:", "⚠ Wieder zu erhalten !!"):
                continue
            if re.fullmatch(r"[0-9., –-]+€", text) or "Nur für die besten Taucher" in text:
                continue
            paragraphs.append(text)
    extra = product_copy(paragraphs)
    if parent["slug"] == "tauch-shop--zubehoer":
        # The accessory specs are edited into label/value pairs. Retain longer
        # technical descriptions for items with functions or compatibility notes.
        supplemental = {
            "Unterwassergehäuse für Smartphones": [
                "Das KRAKEN-Gehäuse unterstützt Foto, Video und Wiedergabe sowie manuelle und automatische Fokussierung. Auch Smartphones mit mehreren Objektiven passen hinein, sofern ihre Maße stimmen.",
                "Die maximale Einsatztiefe ist mit 80 m angegeben. Für Weitwinkel und Makro gibt es separate Vorsätze. Die Boosterfunktion der Hydra-Leuchten wird nicht unterstützt.",
                "Die PRO-Version ergänzt einen Drucksensor und kann Tiefe, Temperatur und GPS-Position einblenden. Bitte die gewünschte Ausführung bei der Anfrage angeben."
            ],
            "Displayschutz aus Silikon": ["Als Beispiele nennt der Katalog Ratio, Mares Matrix und Smart sowie Suunto. Gib dein Modell bei der Anfrage an."],
            "TDS Halterung und Schere": ["Die Kydex-Halterung hat seitliche Ösen zur Befestigung sowie eine Öffnung, durch die Wasser ablaufen kann."],
            "Diver Knife": ["Zum Holster gehören zwei schwarze Gummibänder. Die Klinge hat auf einer Seite eine Sägezahnung."],
            "Mini-LED-Leuchte": ["Der Karabiner passt an eine Tasche oder einen Schlüsselbund. Auf der Rückseite sitzt ein Magnet. Die Leuchte hat außerdem einen Flaschenöffner."],
        }
        extra = ''.join(f'<p>{escape(t)}</p>' for t in supplemental.get(item["name"], []))
    if extra:
        extra = f'<details class="item-extra"><summary>Weitere Produktangaben</summary>{extra}</details>'
    spec_section = f'<h2>Produktdaten</h2><dl class="item-specs">{specs}</dl>' if specs else ""
    group_link = f'{parent["slug"]}.html#{slugify(item["group"])}'
    return f'''<div class="wrap item-page"><nav class="item-crumb" aria-label="Brotkrumennavigation">
    <a href="../index.html">Startseite</a> / <a href="tauch-shop.html">Tauchshop</a> / <a href="{group_link}">{escape(parent["title"])}</a></nav>
    <article class="item-layout">
    <div class="item-heading"><a class="item-group" href="{group_link}">{escape(item["group"])}</a>
    <h1>{name}</h1><p class="item-summary">{escape(item["summary"])}</p></div>
    <div class="item-media">{image}{gallery}</div>
    <div class="item-info">
    <div class="item-purchase"><strong>{escape(item["price"])}</strong>{note}{inquiry(item["name"])}</div>
    {spec_section}{extra}
    </div></article><nav class="item-next" aria-label="Weiter im Sortiment"><a href="{group_link}">Weitere Artikel aus {escape(item["group"])}</a><a href="tauch-shop.html">Zum gesamten Sortiment</a></nav></div>'''

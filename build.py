"""Build the independent, offline-browsable German website with Python 3."""
import json
import re
from hashlib import sha256
import shutil
import os
from urllib.parse import urlencode, urljoin, urlsplit
from shop import category_photo, catalogue_items, category_products, product_detail, shop_directory, slugify
from html import escape
from editorial import albums, closing_band, slot, course_link, dates, first_aid, guestbook, home_news, hud, jobs, legal, travel_archive, trip_tiles
from pathlib import Path
from design import decorate

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
DIST = ROOT / "dist"
PAGES = json.loads((ROOT / "content/pages.json").read_text())
BY_SLUG = {p["slug"]: p for p in PAGES}
HOME = (SRC / "home.html").read_text()


def link(slug, label=None):
    title = label or HUBS.get(slug) or BY_SLUG[slug]["title"]
    return f'<a href="{slug}.html">{escape(title)}</a>'


def overview():
    groups = [
        ("Tauchen und Erste Hilfe", [
            "kurse",
            "tauchen-lernen-kurse",
            "frti-kurse",
            "preis-kurse",
            "termine",
            "anfrage",
        ]),
        ("Shop und Verleih", [
            "tauch-shop",
            "equipment-verleih",
            "sonderangebote",
            "im-auftrag-zu-verkaufen",
            "hud",
            "erste-hilfe-material-zubehoer",
            "frti-kurse--frti-material-eh-material",
        ]),
        ("Tauchshop nach Kategorie", [
            "tauch-shop--jacket-bcd",
            "tauch-shop--computer",
            "tauch-shop--neopren",
            "tauch-shop--masken-flossenzubehoer",
            "tauch-shop--atemregler-zubehoer",
            "tauch-shop--koffer-taschen",
            "tauch-shop--zubehoer",
            "tauch-shop--bekleidung",
            "tauch-shop--schmuck",
        ]),
        ("Rund um die Schule", [
            "infos",
            "bilder-reisen-event-s",
            "glueckwuensche",
            "frti-kurse--frti-glueckwuensche",
            "wir-suchen-dich",
            "gaestebuch-bewertung",
            "impressum",
        ]),
    ]
    sections = []
    for title, slugs in groups:
        links = [link(slug, "Anfrage stellen" if slug == "anfrage" else None) for slug in slugs]
        items = "".join(f"<li>{item}</li>" for item in links)
        sections.append(f"<section><h2>{title}</h2><ul>{items}</ul></section>")
    return '<div class="site-map">' + "".join(sections) + "</div>"


def content(page):
    if page["slug"] == "uebersicht":
        return overview()
    if "courses" in page:
        cards = []
        for c in page["courses"]:
            items = ''.join(f'<li>{escape(t)}</li>' for t in c['details'][:-1])
            supplement = escape(c['details'][-1])
            cards.append(f'<section class="course-rate" id="{slugify(c["name"])}"><div class="rate"><h2>{escape(c["name"])}</h2><strong>{escape(c["price"])}</strong></div><p class="fee-supplement">{supplement}</p><details><summary>Ablauf und Leistungen</summary><ul>{items}</ul></details>{course_link("Tauchkurs", c["name"], "Kurs anfragen")}</section>')
        return '<div class="reading fees-list">' + ''.join(cards) + notes(page) + '</div>'
    if "rates" in page:
        durations = ("Tag", "Wochenende", "Woche")
        rows = []
        for name, *prices in page["rates"]:
            cells = "".join(f'<td data-label="{duration}">{escape(price)}</td>' for duration, price in zip(durations, prices))
            rows.append(f'<tr><th scope="row">{escape(name)}</th>{cells}</tr>')
        headings = "".join(f'<th scope="col">{label}</th>' for label in ("Ausrüstung", *durations))
        return f'<div class="reading"><div class="tablebox"><table class="rental-rates" aria-label="Verleihpreise"><thead><tr>{headings}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>' + notes(page) + course_link("Ausrüstung und Verleih", label="Mietzeit und Ausrüstung anfragen") + '</div>'
    slug = page["slug"]
    if slug == "anfrage":
        return (SRC / "inquiry.html").read_text()
    if slug in {"glueckwuensche", "frti-kurse--frti-glueckwuensche", "bilder-reisen-event-s"}:
        return albums(page)
    if slug == "termine":
        return dates(page)
    if slug == "gaestebuch-bewertung":
        return guestbook(page)
    if slug == "wir-suchen-dich":
        return jobs()
    if slug == "hud":
        return hud(page)
    if slug == "impressum":
        return legal(page)
    raise ValueError(f"Missing page layout for {slug}")


def notes(page):
    return ''.join('<p>'+escape(t)+'</p>' for t in page["notes"])


def footer(prefix):
    return (SRC / "footer.html").read_text().replace("{{root}}", prefix)


HUBS = {"kurse": "Tauchen", "frti-kurse": "Erste Hilfe", "tauch-shop": "Ausrüstung", "infos": "Tauchschule"}
INTRO = {
    "preis-kurse": "Vergleiche Kursgebühren, enthaltene Leistungen und zusätzliche Kosten für deine Tauchausbildung.",
    "equipment-verleih": "Leihpreise pro Tag, Wochenende oder Woche. Frag das Team, ob die Ausrüstung für deinen Termin verfügbar ist.",
    "sonderangebote": "Preisvorteile und Einzelangebote. Die jeweiligen Bedingungen findest du beim Artikel.",
    "im-auftrag-zu-verkaufen": "Einzelstücke aus Kundenbesitz. Größe, Zustand und Verfügbarkeit kannst du direkt beim Team erfragen.",
    "erste-hilfe-material-zubehoer": "Notfallausrüstung und Geräte für die Diagnostik.",
    "frti-kurse--frti-material-eh-material": "Erste-Hilfe-Sets, Einsatzmaterial und Dienstbekleidung im Überblick.",
    "glueckwuensche": "Abschlüsse und persönliche Meilensteine aus der Tauchschule.",
    "frti-kurse--frti-glueckwuensche": "Einblicke in die abgeschlossenen Ausbildungen bei First Response Training International.",
    "bilder-reisen-event-s": "Gemeinsame Tauchgänge, Kurse und Reisen. Entdecke die bisherigen Ausflüge und Veranstaltungen der Schule.",
    "anfrage": "Kurs, Ausrüstung oder Ausflug: Schreib uns, was du vorhast.",
    "kurse": "Schnuppertauchen, Tauchschein, Scubility und Weiterbildung. Finde den passenden Einstieg und plane deinen nächsten Kurs.",
    "tauch-shop": "Entdecke Ausrüstung für deinen nächsten Tauchgang. Atemregler, Jackets und weitere Ausrüstung kannst du auch für einen Tag, ein Wochenende oder eine Woche leihen.",
    "infos": "Das Team hinter Dive-World & Rescue, Einblicke in die Tauchschule und der direkte Kontakt zu uns.",
    "hud": "Ein Tauchcomputer direkt an der Maske. Entdecke das Head-up-Display von Daïve und frag das Team nach dem Gerät.",
    "wir-suchen-dich": "Du möchtest die Wasserrettung am Unterbacher See unterstützen? Hier erfährst du mehr über Aufgaben und Voraussetzungen.",
    "gaestebuch-bewertung": "Persönliche Erfahrungen unserer Teilnehmer mit Dive-World & Rescue.",
    "termine": "Hallentauchen, Seen und Reisen ans Rote Meer, mehrmals im Monat. Jeder ist willkommen.",
    "tauch-shop--computer": "Vergleiche die Modelle und frag direkt beim Team nach deinem Tauchcomputer.",
    "uebersicht": "Kurse, Ausrüstung und Informationen zur Tauchschule auf einen Blick.",
}


def section_for(slug):
    if slug.startswith("tauch-shop") or slug in {"hud", "equipment-verleih", "im-auftrag-zu-verkaufen", "sonderangebote", "frti-kurse--frti-material-eh-material", "erste-hilfe-material-zubehoer"}:
        return "tauch-shop"
    if slug in {"frti-kurse", "frti-kurse--frti-glueckwuensche"}:
        return "frti-kurse"
    if slug in {"kurse", "preis-kurse", "termine", "tauchen-lernen-kurse"}:
        return "kurse"
    return "infos"


def header(prefix, active=None, current=None):
    links = []
    for slug, title in HUBS.items():
        marker = ' aria-current="page"' if slug == current else (' aria-current="location"' if slug == active else "")
        links.append(f'<a href="{prefix}pages/{slug}.html"{marker}>{escape(title)}</a>')
    return (SRC / "header.html").read_text().replace("{{root}}", prefix).replace("{{links}}", "".join(links))


def inner(page):
    slug = page["slug"]
    title = escape({"tauch-shop": "Ausrüstung & Verleih", "kurse": "Tauchkurse", "infos": "Tauchschule & Kontakt"}.get(slug, page["title"]))
    section = section_for(slug)
    neutral = slug in {"uebersicht", "anfrage"}
    parent = "" if neutral or slug in HUBS else f' / <a href="{section}.html">{escape(HUBS[section])}</a>'
    crumb = f'<nav class="crumb" aria-label="Brotkrumennavigation"><a href="../index.html">Startseite</a>{parent} / {title}</nav>'
    if slug == "frti-kurse":
        return page_shell(title, first_aid(page, crumb), section, slug)
    if slug == "tauchen-lernen-kurse":
        fees = {course["name"]: course["price"] for course in BY_SLUG["preis-kurse"]["courses"]}
        main = (SRC / "dive-courses.html").read_text().replace("{{breadcrumb}}", crumb)
        main = main.replace("{{owd_price}}", escape(fees["Open Water Diver"]))
        main = main.replace("{{trial_price}}", escape(fees["Schnuppertauchen"]))
        main = main.replace("{{scuba_price}}", escape(fees["Scuba Diver"])).replace("{{aowd_price}}", escape(fees["Advanced Open Water Diver"]))
        def chips(names):
            return '<ul class="dive-chips">' + "".join(f'<li><a href="anfrage.html?{escape(urlencode({"thema": "Tauchkurs", "kurs": n}))}">{escape(n)}</a></li>' for n in names) + "</ul>"
        main = main.replace("{{reentry}}", chips(["Auffrischungskurs", "Indoor Diver", "Discover Scuba Diver"]))
        main = main.replace("{{pro}}", chips(["Rescue Diver", "Divemaster", "Assistant Instructor"]))
        main = main.replace("{{special}}", chips(["Nachttauchen", "Wracktauchen", "Tarierung", "Unterwassernavigation", "Tieftauchen", "Trockentauchen", "Suchen und Bergen", "UW-Scooter"]))
        main = main.replace("{{closing}}", closing_band("Noch unsicher, welcher Kurs passt?", "Erzähl uns kurz, was du schon gemacht hast. Wir empfehlen dir den passenden Einstieg.", "anfrage.html?thema=Tauchkurs", "Beratung anfragen", "dive-closing"))
        return page_shell(title, main, section, slug)
    if slug == "kurse":
        fees = {course["name"]: course["price"] for course in BY_SLUG["preis-kurse"]["courses"]}
        main = (SRC / "courses.html").read_text().replace("{{breadcrumb}}", crumb)
        main = re.sub(r"\{\{img:([\w.-]+)\|([\w.-]+)\}\}", lambda m: slot(m[1], m[2]), main)
        main = main.replace("{{trial_price}}", escape(fees["Schnuppertauchen"])).replace("{{aowd_price}}", escape(fees["Advanced Open Water Diver"]))
        main = main.replace("{{closing}}", closing_band("Welcher Kurs passt zu dir?", "Erzähl uns kurz, was du schon gemacht hast. Wir empfehlen dir den passenden Einstieg.", "anfrage.html?thema=Tauchkurs", "Beratung anfragen", "hub-closing"))
        return page_shell(escape("Tauchkurse in Düsseldorf"), main, section, slug)
    intro = f'<p class="cover-copy">{escape(INTRO[slug])}</p>' if slug in INTRO else ""
    if slug == "infos":
        intro += '<div class="cover-choices"><a class="cta mint" href="#kontakt">Kontakt aufnehmen</a><a class="plain" href="#team">Team kennenlernen</a></div>'
    if slug == "tauch-shop":
        intro += '<div class="cover-choices"><a class="cta mint" href="#ausruestung">Sortiment entdecken</a><a class="plain" href="equipment-verleih.html">Leihpreise ansehen</a></div>'
        body = shop_directory(BY_SLUG)
    elif slug.startswith("tauch-shop--") or page.get("catalogue"):
        items = catalogue_items(page)
        body = category_products(items)
        if slug == "tauch-shop--computer":
            body += '<nav class="context-link wrap" aria-label="Weitere Tauchcomputer"><a href="hud.html">Tauchdaten in der Maske sehen · Zum Head-up-Display →</a></nav>' 
        intro += f'<p class="catalog-count">{len(items)} Artikel</p>'
    elif slug == "termine":
        intro += '<div class="cover-choices"><a class="cta mint" href="anfrage.html?thema=Termine+und+Reisen">Nächsten Termin anfragen</a><a class="plain" href="#ziele">Tauchziele ansehen</a></div>'
        body = dates(page)
    elif slug == "bilder-reisen-event-s":
        intro += '<div class="cover-choices"><a class="cta mint" href="anfrage.html?thema=Termine+und+Reisen">Nächsten Ausflug anfragen</a><a class="plain" href="termine.html">Termine ansehen</a></div>'
        body = travel_archive(page)
    elif slug == "wir-suchen-dich":
        body = jobs()
    elif slug == "infos":
        body = (SRC / "info.html").read_text()
    else:
        body = f'<div class="wrap editorial-body">{content(page)}</div>' + (closing_band(*BANDS[slug]) if slug in BANDS else "")
    cover_class = "interior-cover shop-cover" if slug == "tauch-shop" else "interior-cover"
    if slug == "anfrage":
        cover_class = "interior-cover request-cover"
    if slug == "infos":
        cover_class = "interior-cover school-cover"
    if slug.startswith("tauch-shop--") or page.get("catalogue"):
        cover_class = "interior-cover catalogue-cover"
    main = f'<div class="{cover_class}"><div class="wrap">{crumb}<h1>{title}</h1>{intro}</div></div>{body}'
    return page_shell(title, main, None if neutral else section, slug)


BANDS = {
    "glueckwuensche": ("Dein nächster Schritt", "Vom ersten Tauchgang bis zur Weiterbildung. Wir finden den passenden Kurs für dich.", "tauchen-lernen-kurse.html", "Tauchkurse ansehen"),
    "frti-kurse--frti-glueckwuensche": ("Selbst Erste Hilfe lernen", "Kurse für Familie, Beruf und Tauchsport, mit Theorie in deinem Tempo.", "frti-kurse.html", "Erste-Hilfe-Kurse ansehen"),
    "gaestebuch-bewertung": ("Selbst abtauchen?", "Probier es beim Schnuppertauchen aus oder starte direkt mit deinem Tauchschein.", "anfrage.html?thema=Tauchkurs&amp;kurs=Schnuppertauchen", "Schnuppertauchen anfragen"),
    "hud": ("Interesse am Head-up-Display?", "Frag nach Preis und Verfügbarkeit. Wir beraten dich, ob es zu deiner Maske passt.", "anfrage.html?thema=Ausr%C3%BCstung+und+Verleih&amp;produkt=Da%C3%AFve+Head-up-Display", "Verfügbarkeit anfragen"),
    "equipment-verleih": ("Ausrüstung für deinen Termin", "Sag uns, was du brauchst und wann. Wir legen alles bereit.", "anfrage.html?thema=Ausr%C3%BCstung+leihen", "Ausrüstung anfragen"),
    "preis-kurse": ("Noch Fragen zum Kurs?", "Wir erklären dir Ablauf, Kosten und den nächsten freien Termin.", "anfrage.html?thema=Tauchkurs", "Kurs anfragen"),
}


def page_shell(title, main, section, slug):
    return f'''<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title} · Dive-World &amp; Rescue</title><link rel="stylesheet" href="../main.css"><script defer src="../home.js"></script></head>
<body><a class="skip" href="#inhalt">Zum Inhalt</a>{header("../", section, slug)}
<main id="inhalt">{main}</main>
{footer('../')}</body></html>'''



def home_offers():
    courses = {course["name"]: course for course in BY_SLUG["preis-kurse"]["courses"]}
    offers = [("Schnuppertauchen", "Erst einmal ausprobieren", "ausprobieren"), ("Open Water Diver", "Dein erster Tauchschein", "tauchschein")]
    rows = "".join(f'<li><a href="pages/tauchen-lernen-kurse.html#{anchor}"><span><small>{label}</small><strong>{name}</strong></span><em>{escape(courses[name]["price"])}</em></a></li>' for name, label, anchor in offers)
    return f'<ul class="program-prices">{rows}</ul><p class="fee-context">Kursgebühr zzgl. Eintritt und Fahrtkosten.</p>'


def hero_trust():
    data = json.loads((ROOT / "content/google-reviews.json").read_text())
    return f'''<ul class="hero-trust"><li><span class="review-stars" aria-hidden="true">★★★★★</span> {data["rating"]} bei Google</li><li>Ausbildung nach SDI/TDI, PSS &amp; FRTI</li></ul>'''


def equipment_preview():
    entries = [
        ("computer", "Tauchcomputer", "Uhrenmodelle von Ratio, DiveBrain und SUNROAD."),
        ("atemregler-zubehoer", "Atemregler", "Erste und zweite Stufen, Oktopusse und Sets."),
        ("jacket-bcd", "Jackets & Wings", "Tarierjackets für Sport- und Reisetauchen."),
        ("neopren", "Anzüge & Neopren", "Nass- und Trockenanzüge, Füßlinge, Handschuhe."),
    ]
    more = [
        ("tauch-shop--masken-flossenzubehoer", "Masken & Flossen"),
        ("tauch-shop--zubehoer", "Zubehör"),
        ("tauch-shop--koffer-taschen", "Koffer & Taschen"),
        ("tauch-shop--bekleidung", "Bekleidung"),
        ("tauch-shop--schmuck", "Schmuck"),
        ("hud", "Head-up-Display"),
    ]
    cards = []
    for suffix, label, description in entries:
        page = BY_SLUG["tauch-shop--" + suffix]
        photo = category_photo(page).removeprefix("../")
        count = len(catalogue_items(page))
        cards.append(f'''<a class="equip-card" href="pages/{page["slug"]}.html">
          <span class="equip-stage"><img src="{photo}" loading="lazy" alt=""></span>
          <span class="equip-body"><strong>{escape(label)}</strong><span>{escape(description)}</span><small>{count} Artikel</small></span></a>''')
    chips = ''.join(f'<li><a href="pages/{slug}.html">{escape(label)}</a></li>' for slug, label in more if slug in BY_SLUG)
    return '''<section class="home-equipment" id="ausruestung"><div class="wrap">
      <div class="page-head"><div><p class="kicker">Ausrüstung</p><h2>Passend zu deinem Tauchgang.</h2></div>
      <p>Kaufen oder leihen: Wir beraten dich persönlich, welches Modell zu dir und deinem Tauchplatz passt.</p></div>
      <div class="equip-layout"><div class="equip-grid">''' + ''.join(cards) + '''</div>
      <a class="equip-rent-tile" href="pages/equipment-verleih.html"><img src="assets/shop-cover.webp" width="764" height="508" loading="lazy" alt="">
        <span class="equip-rent-copy"><span class="program-chip">Ausrüstung leihen</span><strong>Lieber erst einmal leihen?</strong><span>Atemregler, Computer, Jackets und Anzüge für einen Tag, ein Wochenende oder eine Woche.</span><em>ab 7 € pro Tag</em><small>Leihpreise ansehen</small></span></a></div>
      <div class="equip-foot"><nav aria-label="Weitere Kategorien"><span>Außerdem im Shop</span><ul>''' + chips + '''</ul></nav>
      <div class="equip-actions"><a class="cta" href="pages/tauch-shop.html">Zum gesamten Sortiment</a><a class="path-action" href="pages/sonderangebote.html">Sonderangebote</a></div></div>
    </div></section>'''



def google_reviews():
    data = json.loads((ROOT / "content/google-reviews.json").read_text())
    url = escape(data["url"], quote=True)
    icon = '<img class="google-icon" src="assets/google-g.png" width="20" height="20" alt="">'
    quotes = []
    for review in data["reviews"]:
        author = escape(review["author"])
        quotes.append(f'''<figure class="google-review">
          <blockquote>„{escape(review["excerpt"])}“</blockquote>
          <figcaption><span class="review-stars" aria-label="{review["stars"]} von 5 Sternen"><span aria-hidden="true">★★★★★</span></span><strong>{author}</strong></figcaption>
        </figure>''')
    return f'''<section class="google-reviews" aria-labelledby="review-title"><div class="wrap">
      <div class="review-heading"><p class="kicker">Erfahrungen</p><h2 id="review-title">Das sagen unsere Kunden</h2>
      <a class="google-rating" href="{url}" target="_blank" rel="noopener noreferrer">{icon}<span class="review-stars" aria-hidden="true">★★★★★</span><span><strong>{data["rating"]}</strong> · {data["count"]} Google-Rezensionen</span></a></div>
      <div class="google-review-grid">{"".join(quotes)}</div>
      <p class="review-foot">Auszüge aus Google-Rezensionen, Stand <time datetime="{data["checked_on"]}">{data["checked_label"]}</time> · <a href="{url}" target="_blank" rel="noopener noreferrer">Alle Rezensionen auf Google</a></p>
    </div></section>'''



# Search titles and descriptions. Visible page copy stays as written; these
# only feed <title>, the meta description and social previews.
SEO = {
    "index.html": ("Tauchschule Düsseldorf: Tauchkurse & Erste Hilfe", "Tauchschule in Düsseldorf: Schnuppertauchen, Tauchschein nach SDI/TDI und PSS, inklusives Tauchen mit Scubility, Erste-Hilfe-Kurse nach FRTI sowie Tauchausrüstung zum Kaufen und Leihen."),
    "kurse": ("Tauchkurse in Düsseldorf: Schnuppertauchen bis Divemaster", "Tauchkurse in Düsseldorf: Schnuppertauchen, Open Water Diver, Advanced, Rescue und Spezialkurse nach SDI/TDI und PSS. Finde den passenden Einstieg."),
    "tauchen-lernen-kurse": ("Tauchen lernen in Düsseldorf: Tauchschein Open Water Diver", "Tauchen lernen in Düsseldorf: Mit dem Open Water Diver machst du deinen Tauchschein in Theorie, Hallenbad und Freiwasser. Auch Schnuppertauchen und Wiedereinstieg."),
    "preis-kurse": ("Tauchkurs Preise: Schnuppertauchen, Tauchschein & Weiterbildung", "Was kostet ein Tauchkurs? Kursgebühren für Schnuppertauchen, Scuba Diver, Open Water und Advanced Open Water Diver mit allen enthaltenen Leistungen."),
    "frti-kurse": ("Erste-Hilfe-Kurs Düsseldorf: Familie, Beruf & Tauchsport", "Erste-Hilfe-Kurse in Düsseldorf nach First Response Training International: für Eltern und Familie, für Betriebe und für Taucher mit Sauerstoffgabe."),
    "tauch-shop": ("Tauchshop Düsseldorf: Tauchausrüstung kaufen & leihen", "Tauchausrüstung in Düsseldorf: Atemregler, Tauchcomputer, Jackets, Anzüge, Masken und Flossen mit persönlicher Beratung, auch zum Leihen."),
    "equipment-verleih": ("Tauchausrüstung leihen in Düsseldorf: Leihpreise", "Tauchausrüstung leihen: Atemregler, Tauchcomputer, Jacket, Anzug und Flossen pro Tag, Wochenende oder Woche. Alle Leihpreise im Überblick."),
    "termine": ("Tauchausflüge & Termine: Hallentauchen, See & Rotes Meer", "Gemeinsam tauchen: Hallentauchen im TODI, Diveworld, Dive4Life und Monte Mare, Seetauchen in Xanten und Tauchreisen nach Safaga am Roten Meer."),
    "infos": ("Tauchschule Düsseldorf: Team & Kontakt", "Lerne das Team der Tauchschule Dive-World & Rescue in Düsseldorf kennen und nimm per Telefon, WhatsApp oder E-Mail Kontakt auf."),
    "wir-suchen-dich": ("Rettungsschwimmer gesucht: Unterbacher See Düsseldorf", "Rettungsschwimmer für die Badesaison am Unterbacher See in Düsseldorf gesucht. Aufgaben, Voraussetzungen und Bewerbung."),
    "anfrage": ("Anfrage: Tauchkurs, Erste Hilfe oder Ausrüstung", "Frag einen Tauchkurs, einen Erste-Hilfe-Kurs, Leihausrüstung oder einen Tauchausflug an. Antwort per WhatsApp oder E-Mail."),
    "impressum": ("Impressum und Datenschutz", "Impressum und Datenschutzerklärung von Dive-World & Rescue, Tauchschule und Erste-Hilfe-Ausbildung in Düsseldorf."),
}
CATEGORY_SEO = "{name} kaufen bei Dive-World & Rescue in Düsseldorf: Modelle vergleichen und persönlich beraten lassen."
SITEMAP = []


def site_origin():
    origin = os.environ.get("SITE_URL", "").strip()
    if not origin and (ROOT / "CNAME").exists():
        origin = "https://" + (ROOT / "CNAME").read_text().strip()
    return origin.rstrip("/") + "/"


def responsive_images(html, prefix):
    """Offer the 640w/1024w copies of large photos so tiles don't load 1600px files."""
    def swap(m):
        tag, src = m[0], m[2]
        if "srcset=" in tag or not src.endswith(".webp"):
            return tag
        local = ROOT / "public" / src.removeprefix(prefix)
        width = re.search(r'\swidth="(\d+)"', tag)
        sources = [(f"{src[:-5]}-{w}w.webp", w) for w in (640, 1024) if local.with_name(f"{local.stem}-{w}w.webp").exists()]
        if not sources or not width:
            return tag
        srcset = ", ".join(f"{s} {w}w" for s, w in sources) + f", {src} {width[1]}w"
        sizes = "auto, (max-width: 700px) 100vw, 50vw" if 'loading="lazy"' in tag else "(max-width: 700px) 100vw, 50vw"
        return tag.replace(m[1], f'{m[1]} srcset="{srcset}" sizes="{sizes}"', 1)
    return re.sub(r'<img\b[^>]*?(src="([^"]+)")[^>]*>', swap, html)


def breadcrumb_ld(html, origin, path):
    nav = re.search(r'<nav class="crumb"[^>]*>(.*?)</nav>', html, re.S)
    if not nav:
        return ""
    items = [(urljoin(urljoin(origin, path), href), re.sub("<[^>]+>", "", text).strip()) for href, text in re.findall(r'<a href="([^"]+)"[^>]*>(.*?)</a>', nav[1])]
    current = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.S)
    if current:
        items.append((urljoin(origin, path), re.sub("<[^>]+>", " ", current[1]).split()))
        items[-1] = (items[-1][0], " ".join(items[-1][1]))
    items = [(origin if u == urljoin(origin, "index.html") else u, n) for u, n in items]
    data = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": name.replace("&amp;", "&"), "item": url} for i, (url, name) in enumerate(items)]}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>"


def business_ld(origin):
    data = {
        "@context": "https://schema.org", "@type": "SportsActivityLocation",
        "name": "Dive-World & Rescue", "description": SEO["index.html"][1],
        "url": origin, "logo": urljoin(origin, "assets/icon-192.png"), "image": urljoin(origin, "assets/tauchgang.webp"),
        "telephone": "+49 176 85639763", "email": "dive-world@mail.de",
        "address": {"@type": "PostalAddress", "streetAddress": "Bebelstr. 1", "postalCode": "40627", "addressLocality": "Düsseldorf", "addressCountry": "DE"},
        "areaServed": "Düsseldorf",
    }
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>"


def add_metadata(html, path, title, description, prefix, share_image="assets/tauchgang.webp"):
    slug = path.removeprefix("pages/").removesuffix(".html")
    brand = " · Dive-World & Rescue"
    if path in SEO or slug in SEO:
        seo_title, description = SEO.get(path) or SEO[slug]
        title = seo_title + brand
    elif slug.startswith("tauch-shop--"):
        description = CATEGORY_SEO.format(name=title.removesuffix(brand))
        title = title.removesuffix(brand) + " kaufen" + brand
    html = re.sub(r"<title>.*?</title>", f"<title>{escape(title)}</title>", html, count=1, flags=re.S)
    html = decorate(html, path)
    html = responsive_images(html, prefix)
    editorial_version = sha256((SRC / "editorial.css").read_bytes()).hexdigest()[:10]
    html = html.replace('</head>', f'<link rel="stylesheet" href="{prefix}editorial.css?v={editorial_version}"></head>')
    for asset in ("main.css", "home.js", "inquiry.js"):
        version = sha256((SRC / asset).read_bytes()).hexdigest()[:10]
        html = html.replace(f'"{prefix}{asset}"', f'"{prefix}{asset}?v={version}"')
    logo_version = sha256((ROOT / "public" / "assets" / "logo-mark.png").read_bytes()).hexdigest()[:10]
    html = html.replace('assets/logo-mark.png"', f'assets/logo-mark.png?v={logo_version}"')
    if 'class="album-grid"' in html or 'class="photo-mosaic"' in html or 'class="item-photo"' in html:
        css_version = sha256((SRC / "gallery.css").read_bytes()).hexdigest()[:10]
        script_version = sha256((SRC / "gallery.js").read_bytes()).hexdigest()[:10]
        html = html.replace("</head>", (
            f'<link rel="stylesheet" href="{prefix}gallery.css?v={css_version}">'
            f'<script defer src="{prefix}gallery.js?v={script_version}"></script></head>'
        ))
    tags = [
        f'<meta name="description" content="{escape(description, quote=True)}">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:title" content="{escape(title, quote=True)}">',
        f'<meta property="og:description" content="{escape(description, quote=True)}">',
        f'<link rel="icon" href="{prefix}favicon.ico" sizes="48x48">',
        f'<link rel="icon" type="image/png" sizes="32x32" href="{prefix}assets/favicon-32.png">',
        f'<link rel="icon" type="image/png" sizes="64x64" href="{prefix}assets/favicon.png">',
        f'<link rel="icon" type="image/png" sizes="192x192" href="{prefix}assets/icon-192.png">',
        f'<link rel="apple-touch-icon" href="{prefix}assets/apple-touch-icon.png">',
    ]
    origin = site_origin()
    if origin != "/":
        parsed = urlsplit(origin)
        if parsed.scheme not in {"https", "http"} or not parsed.netloc or parsed.query or parsed.fragment:
            raise ValueError("SITE_URL must be an absolute website base URL.")
        url = origin if path == "index.html" else urljoin(origin, path)
        tags.extend([
            f'<link rel="canonical" href="{escape(url, quote=True)}">',
            f'<meta property="og:url" content="{escape(url, quote=True)}">',
            f'<meta property="og:image" content="{escape(urljoin(origin, share_image), quote=True)}">',
            f'<meta property="og:image:alt" content="{escape(title, quote=True)}">',
            '<meta property="og:locale" content="de_DE">',
            '<meta property="og:site_name" content="Dive-World &amp; Rescue">',
            '<meta name="twitter:card" content="summary_large_image">',
        ])
        if path == "index.html":
            tags.append(business_ld(origin))
            tags.append(f'<link rel="preload" as="image" href="assets/tauchgang.webp" fetchpriority="high">')
        crumb = breadcrumb_ld(html, origin, path)
        if crumb:
            tags.append(crumb)
        SITEMAP.append(url)
    return html.replace("</head>", "\n".join(tags) + "</head>")

def write_not_found():
    """Branded 404 for GitHub Pages. It is served at any missing path, so every link is absolute."""
    origin = site_origin()
    base = origin if origin != "/" else "/"
    main = f'''<div class="interior-cover not-found"><div class="wrap"><p class="kicker">Fehler 404</p><h1>Diese Seite gibt es nicht mehr.</h1>
      <p class="cover-copy">Vielleicht wurde sie verschoben, als wir die Website erneuert haben. Hier geht es weiter:</p>
      <div class="cover-choices"><a class="cta mint" href="../index.html">Zur Startseite</a><a class="plain" href="uebersicht.html">Alle Seiten ansehen</a></div></div></div>
      <section class="hub-plan"><div class="wrap"><h2 class="aid-paths-title">Beliebte Seiten</h2><nav class="hub-plan-grid" aria-label="Beliebte Seiten">
        <a href="tauchen-lernen-kurse.html"><strong>Tauchen lernen</strong><span>Schnuppertauchen, Scuba Diver und Open Water Diver.</span></a>
        <a href="frti-kurse.html"><strong>Erste-Hilfe-Kurse</strong><span>Für Familie, Beruf und Tauchsport.</span></a>
        <a href="tauch-shop.html"><strong>Ausrüstung</strong><span>Shop, Verleih und Sonderangebote.</span></a>
      </nav></div></section>'''
    html = page_shell("Seite nicht gefunden", main, None, "404")
    editorial_version = sha256((SRC / "editorial.css").read_bytes()).hexdigest()[:10]
    html = html.replace("</head>", f'<link rel="stylesheet" href="../editorial.css?v={editorial_version}"><meta name="robots" content="noindex"><link rel="icon" href="../favicon.ico" sizes="48x48"></head>')
    html = decorate(html, "pages/404.html")
    # Rewrite every relative link to an absolute one so the page works at any depth.
    html = re.sub(r'(href|src)="\.\./', lambda m: f'{m[1]}="{base}', html)
    html = re.sub(r'(href|src)="(?!https?:|/|#|tel:|mailto:)([^"]+)"', lambda m: f'{m[1]}="{base}pages/{m[2]}"', html)
    (DIST / "404.html").write_text(html)


def build():
    DIST.mkdir(exist_ok=True)
    (DIST / "pages").mkdir(exist_ok=True)
    shutil.copytree(ROOT / "public", DIST, dirs_exist_ok=True)
    for name in ("main.css", "editorial.css", "home.js", "inquiry.js", "gallery.css", "gallery.js"):
        shutil.copyfile(SRC / name, DIST / name)
    home = HOME.replace("<!-- site-header -->", header("")).replace("<!-- site-footer -->", footer(""))
    home = home.replace("<!-- hero-trust -->", hero_trust()).replace("<!-- home-news -->", home_news(BY_SLUG["termine"], BY_SLUG["glueckwuensche"])).replace("<!-- trip-tiles -->", trip_tiles(BY_SLUG["bilder-reisen-event-s"], "pages/termine.html", "")).replace("<!-- course-preview -->", home_offers()).replace("<!-- equipment-preview -->", equipment_preview()).replace("<!-- google-reviews -->", google_reviews())
    (DIST / "index.html").write_text(add_metadata(home, "index.html", "Tauchen und Erste Hilfe · Dive-World & Rescue", "Tauchkurse, Scubility, Erste Hilfe und Ausrüstung bei Dive-World & Rescue.", ""))
    for page in [*PAGES, {"slug":"kurse", "title":HUBS["kurse"]}, {"slug":"infos", "title":HUBS["infos"]}, {"slug":"anfrage", "title":"Anfrage stellen"}, {"slug":"uebersicht", "title":"Alle Seiten"}]:
        description = INTRO.get(page["slug"], page["title"] + " bei Dive-World & Rescue.")
        html = add_metadata(inner(page), "pages/" + page["slug"] + ".html", page["title"] + " · Dive-World & Rescue", description, "../")
        (DIST / "pages" / (page["slug"]+".html")).write_text(html)
        if page["slug"].startswith("tauch-shop--") or page.get("catalogue"):
            items = catalogue_items(page)
            for item in items:
                main = product_detail(item, page, items)
                html = page_shell(escape(item["name"]), main, "tauch-shop", item["slug"])
                html = add_metadata(html, "pages/" + item["slug"] + ".html", item["name"] + " · Dive-World & Rescue", item["summary"], "../", item["photos"][0].removeprefix("../"))
                (DIST / "pages" / (item["slug"] + ".html")).write_text(html)

    write_not_found()
    origin = site_origin()
    if origin != "/":
        urls = "".join(f"<url><loc>{escape(u)}</loc></url>" for u in SITEMAP)
        (DIST / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
        (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {urljoin(origin, 'sitemap.xml')}\n")


if __name__ == "__main__":
    build()

"""Build the independent, offline-browsable German website with Python 3."""
import json
import shutil
from shop import catalogue_items, category_products, product_detail, shop_directory
from html import escape
from editorial import albums, course_link, dates, first_aid, guestbook, hud, jobs, legal
from pathlib import Path

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
            items = ''.join(f'<li>{escape(t)}</li>' for t in c['details'])
            cards.append(f'<section class="course-rate"><div class="rate"><h2>{escape(c["name"])}</h2><strong>{escape(c["price"])}</strong></div><details><summary>Leistungen und Zusatzkosten</summary><ul>{items}</ul></details>{course_link("Tauchkurs", c["name"], "Kurs anfragen")}</section>')
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


HUBS = {"kurse": "Kurse", "tauch-shop": "Tauchshop", "infos": "Infos & Kontakt"}
INTRO = {
    "preis-kurse": "Vergleiche Kursgebühren, enthaltene Leistungen und zusätzliche Kosten für deine Tauchausbildung.",
    "equipment-verleih": "Leihpreise pro Tag, Wochenende oder Woche. Frag das Team, ob die Ausrüstung für deinen Termin verfügbar ist.",
    "sonderangebote": "Preisvorteile und Einzelangebote. Die jeweiligen Bedingungen findest du beim Artikel.",
    "im-auftrag-zu-verkaufen": "Einzelstücke aus Kundenbesitz. Größe, Zustand und Verfügbarkeit kannst du direkt beim Team erfragen.",
    "erste-hilfe-material-zubehoer": "Notfallausrüstung und Geräte für die Diagnostik.",
    "frti-kurse--frti-material-eh-material": "Erste-Hilfe-Sets, Einsatzmaterial und Dienstbekleidung im Überblick.",
    "glueckwuensche": "Abschlüsse und persönliche Meilensteine aus der Tauchschule.",
    "frti-kurse--frti-glueckwuensche": "Einblicke in die abgeschlossenen Ausbildungen bei First Response Training International.",
    "bilder-reisen-event-s": "Bilder und Erinnerungen an gemeinsame Tauchgänge, Kurse und Reisen.",
    "anfrage": "Wähle dein Thema und schreib dem Team per WhatsApp oder E-Mail.",
    "kurse": "Vom Schnuppertauchen bis zur Ersten Hilfe. Hier findest du die Ausbildung, die zu dir passt.",
    "tauch-shop": "Entdecke Ausrüstung für deinen nächsten Tauchgang. Atemregler, Jackets und weitere Ausrüstung kannst du auch für einen Tag, ein Wochenende oder eine Woche leihen.",
    "infos": "Das Team hinter Dive-World & Rescue, Einblicke in die Tauchschule und der direkte Kontakt zu uns.",
    "tauch-shop--computer": "Vergleiche die Modelle und frag direkt beim Team nach deinem Tauchcomputer.",
    "uebersicht": "Kurse, Ausrüstung und Informationen zur Tauchschule auf einen Blick.",
}


def section_for(slug):
    if slug.startswith("tauch-shop") or slug in {"hud", "equipment-verleih", "im-auftrag-zu-verkaufen", "sonderangebote", "frti-kurse--frti-material-eh-material", "erste-hilfe-material-zubehoer"}:
        return "tauch-shop"
    if slug in {"kurse", "frti-kurse", "preis-kurse", "termine", "tauchen-lernen-kurse"}:
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
    title = escape(page["title"])
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
        return page_shell(title, main, section, slug)
    intro = f'<p class="cover-copy">{escape(INTRO[slug])}</p>' if slug in INTRO else ""
    if slug == "tauch-shop":
        intro += '<div class="cover-choices"><a class="cta mint" href="#ausruestung">Sortiment entdecken</a><a class="plain" href="equipment-verleih.html">Leihpreise ansehen</a></div>'
        body = shop_directory(BY_SLUG)
    elif slug.startswith("tauch-shop--") or page.get("catalogue"):
        items = catalogue_items(page)
        body = category_products(items)
        if slug == "tauch-shop--computer":
            body += '<nav class="context-link wrap" aria-label="Weitere Tauchcomputer"><a href="hud.html">Tauchdaten in der Maske sehen · Zum Head-up-Display →</a></nav>' 
        intro += f'<p class="catalog-count">{len(items)} Artikel</p>'
    elif slug in {"kurse", "infos"}:
        template = "courses.html" if slug == "kurse" else "info.html"
        body = (SRC / template).read_text()
    else:
        body = f'<div class="wrap editorial-body">{content(page)}</div>' 
    cover_class = "interior-cover shop-cover" if slug == "tauch-shop" else "interior-cover"
    if slug.startswith("tauch-shop--") or page.get("catalogue"):
        cover_class = "interior-cover catalogue-cover"
    main = f'<div class="{cover_class}"><div class="wrap">{crumb}<h1>{title}</h1>{intro}</div></div>{body}'
    return page_shell(title, main, None if neutral else section, slug)


def page_shell(title, main, section, slug):
    return f'''<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title} · Dive-World &amp; Rescue</title><link rel="stylesheet" href="../main.css"><script defer src="../home.js"></script></head>
<body><a class="skip" href="#inhalt">Zum Inhalt</a>{header("../", section, slug)}
<main id="inhalt">{main}</main>
{footer('../')}</body></html>'''


def build():
    DIST.mkdir(exist_ok=True)
    (DIST / "pages").mkdir(exist_ok=True)
    shutil.copytree(ROOT / "public", DIST, dirs_exist_ok=True)
    for name in ("main.css", "home.js", "inquiry.js"):
        shutil.copyfile(SRC / name, DIST / name)
    (DIST / "index.html").write_text(HOME.replace("<!-- site-header -->", header("")).replace("<!-- site-footer -->", footer("")))
    for page in [*PAGES, {"slug":"kurse", "title":HUBS["kurse"]}, {"slug":"infos", "title":HUBS["infos"]}, {"slug":"anfrage", "title":"Anfrage stellen"}, {"slug":"uebersicht", "title":"Alle Seiten"}]:
        (DIST / "pages" / (page["slug"]+".html")).write_text(inner(page))
        if page["slug"].startswith("tauch-shop--") or page.get("catalogue"):
            for item in catalogue_items(page):
                main = product_detail(item, page)
                html = page_shell(escape(item["name"]), main, "tauch-shop", item["slug"])
                (DIST / "pages" / (item["slug"] + ".html")).write_text(html)


if __name__ == "__main__":
    build()

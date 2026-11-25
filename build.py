"""Build the independent, offline-browsable German website with Python 3."""
import json
from hashlib import sha256
import shutil
import os
from urllib.parse import urljoin, urlsplit
from shop import category_photo, catalogue_items, category_products, product_detail, shop_directory
from html import escape
from editorial import albums, course_link, dates, first_aid, guestbook, hud, jobs, legal
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
            cards.append(f'<section class="course-rate"><div class="rate"><h2>{escape(c["name"])}</h2><strong>{escape(c["price"])}</strong></div><p class="fee-supplement">{supplement}</p><details><summary>Ablauf und Leistungen</summary><ul>{items}</ul></details>{course_link("Tauchkurs", c["name"], "Kurs anfragen")}</section>')
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
    "termine": "Frag nach dem nächsten Kurs oder Tauchausflug. Frühere Ausschreibungen findest du im Terminarchiv.",
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
    title = escape({"tauch-shop": "Ausrüstung & Verleih", "kurse": "Tauchen lernen & weiterkommen", "infos": "Tauchschule & Kontakt"}.get(slug, page["title"]))
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
    if slug == "anfrage":
        cover_class = "interior-cover request-cover"
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



def home_offers():
    courses = {course["name"]: course for course in BY_SLUG["preis-kurse"]["courses"]}
    offers = [
        ("Schnuppertauchen", "Erst einmal ausprobieren", "ausprobieren"),
        ("Open Water Diver", "Dein erster Tauchschein", "tauchschein"),
    ]
    rows = []
    for name, label, anchor in offers:
        course = courses[name]
        rows.append(f'<a href="pages/tauchen-lernen-kurse.html#{anchor}"><span>{label}</span><strong>{name}</strong><span class="home-course-fee">{escape(course["price"])}</span></a>')
    return '<div class="home-course-choices">' + ''.join(rows) + '</div><p class="fee-context">Kursgebühr zzgl. Eintritt und Fahrtkosten. Beim Open Water Diver kommen Lehrmaterial und Zertifizierung hinzu. Einzelheiten beim Kurs.</p>'


def equipment_preview():
    entries = [
        ("computer", "Tauchcomputer"),
        ("atemregler-zubehoer", "Atemregler"),
        ("jacket-bcd", "Jackets & Wings"),
        ("neopren", "Anzüge & Neopren"),
    ]
    cards = []
    for suffix, label in entries:
        page = BY_SLUG["tauch-shop--" + suffix]
        photo = category_photo(page).removeprefix("../")
        cards.append(f'<a href="pages/{page["slug"]}.html"><img src="{photo}" loading="lazy" alt=""><strong>{escape(label)}</strong></a>')
    return '''<section class="home-equipment" id="ausruestung"><div class="wrap">
      <div class="landing-heading"><div><p class="kicker">Ausrüstung kaufen</p><h2>Passend zu deinem Tauchgang.</h2></div><a class="path-action" href="pages/tauch-shop.html">Zum gesamten Sortiment</a></div>
      <div class="home-equipment-grid">''' + ''.join(cards) + '''</div>
      <nav class="equipment-categories" aria-label="Weitere Ausrüstung"><a href="pages/tauch-shop--masken-flossenzubehoer.html">Masken &amp; Flossen</a><a href="pages/tauch-shop--koffer-taschen.html">Koffer &amp; Taschen</a><a href="pages/tauch-shop--zubehoer.html">Zubehör</a><a href="pages/tauch-shop--bekleidung.html">Bekleidung</a><a href="pages/tauch-shop--schmuck.html">Schmuck</a><a href="pages/hud.html">Head-up-Display</a></nav>
      <div class="home-equipment-services"><a href="pages/sonderangebote.html"><strong>Sonderangebote</strong><span>Aktionspreise und Bedingungen ansehen</span></a><a href="pages/im-auftrag-zu-verkaufen.html"><strong>Verkauf im Kundenauftrag</strong><span>Einzelstücke aus Kundenbesitz entdecken</span></a><a href="pages/tauch-shop.html#erste-hilfe"><strong>Erste-Hilfe-Material</strong><span>Notfallausrüstung und Dienstbekleidung</span></a></div>
    </div></section>'''



def google_reviews():
    data = json.loads((ROOT / "content/google-reviews.json").read_text())
    url = escape(data["url"], quote=True)
    icon = '<img class="google-icon" src="assets/google-g.png" width="24" height="24" alt="">'
    cards = []
    for review in data["reviews"]:
        author = escape(review["author"])
        initials = "".join(part[0] for part in review["author"].split()[:2])
        cards.append(f'''<figure class="google-review">
          <figcaption class="review-person">
            <span class="review-avatar" aria-hidden="true">{initials}</span>
            <span><strong>{author}</strong><span class="review-stars" aria-label="{review["stars"]} von 5 Sternen"><span aria-hidden="true">★★★★★</span></span></span>
            <a class="review-origin" href="{url}" target="_blank" rel="noopener noreferrer" aria-label="Rezension von {author} auf Google lesen">{icon}<span>Google</span></a>
          </figcaption>
          <blockquote>„{escape(review["excerpt"])}“</blockquote>
          <a class="review-read" href="{url}" target="_blank" rel="noopener noreferrer">Rezension lesen <span aria-hidden="true">↗</span></a>
        </figure>''')
    return f'''<section class="google-reviews" aria-labelledby="review-title"><div class="wrap">
      <div class="review-heading"><div><p class="review-eyebrow">{icon}<span>Google-Rezensionen</span></p>
      <h2 id="review-title">Das sagen unsere Kunden</h2></div>
      <a class="google-rating" href="{url}" target="_blank" rel="noopener noreferrer" aria-label="{data["rating"]} von 5 Sternen aus {data["count"]} Rezensionen auf Google">
        <strong>{data["rating"]}</strong><span><span class="review-stars" aria-hidden="true">★★★★★</span><span>aus {data["count"]} Rezensionen</span><span class="rating-source">Auf Google ansehen ↗</span></span>
      </a></div>
      <div class="google-review-grid">{"".join(cards)}</div>
      <div class="review-foot"><span>Auszüge aus Google-Rezensionen · Stand <time datetime="{data["checked_on"]}">{data["checked_label"]}</time></span>
      <a href="{url}" target="_blank" rel="noopener noreferrer">Alle Rezensionen auf Google <span aria-hidden="true">↗</span></a></div>
    </div></section>'''



def add_metadata(html, path, title, description, prefix, share_image="assets/tauchgang.webp"):
    html = decorate(html, path)
    editorial_version = sha256((SRC / "editorial.css").read_bytes()).hexdigest()[:10]
    html = html.replace('</head>', f'<link rel="stylesheet" href="{prefix}editorial.css?v={editorial_version}"></head>')
    for asset in ("main.css", "home.js", "inquiry.js"):
        version = sha256((SRC / asset).read_bytes()).hexdigest()[:10]
        html = html.replace(f'"{prefix}{asset}"', f'"{prefix}{asset}?v={version}"')
    tags = [
        f'<meta name="description" content="{escape(description, quote=True)}">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:title" content="{escape(title, quote=True)}">',
        f'<meta property="og:description" content="{escape(description, quote=True)}">',
        f'<link rel="icon" type="image/png" sizes="64x64" href="{prefix}assets/favicon.png">',
    ]
    origin = os.environ.get("SITE_URL", "").rstrip("/") + "/"
    if origin != "/":
        parsed = urlsplit(origin)
        if parsed.scheme not in {"https", "http"} or not parsed.netloc or parsed.query or parsed.fragment:
            raise ValueError("SITE_URL must be an absolute website base URL.")
        url = urljoin(origin, path)
        tags.extend([
            f'<link rel="canonical" href="{escape(url, quote=True)}">',
            f'<meta property="og:url" content="{escape(url, quote=True)}">',
            f'<meta property="og:image" content="{escape(urljoin(origin, share_image), quote=True)}">',
            f'<meta property="og:image:alt" content="{escape(title, quote=True)}">',
        ])
    return html.replace("</head>", "\n".join(tags) + "</head>")

def build():
    DIST.mkdir(exist_ok=True)
    (DIST / "pages").mkdir(exist_ok=True)
    shutil.copytree(ROOT / "public", DIST, dirs_exist_ok=True)
    for name in ("main.css", "editorial.css", "home.js", "inquiry.js"):
        shutil.copyfile(SRC / name, DIST / name)
    home = HOME.replace("<!-- site-header -->", header("")).replace("<!-- site-footer -->", footer(""))
    home = home.replace("<!-- course-preview -->", home_offers()).replace("<!-- equipment-preview -->", equipment_preview()).replace("<!-- google-reviews -->", google_reviews())
    (DIST / "index.html").write_text(add_metadata(home, "index.html", "Tauchen und Erste Hilfe · Dive-World & Rescue", "Tauchkurse, Scubility, Erste Hilfe und Ausrüstung bei Dive-World & Rescue.", ""))
    for page in [*PAGES, {"slug":"kurse", "title":HUBS["kurse"]}, {"slug":"infos", "title":HUBS["infos"]}, {"slug":"anfrage", "title":"Anfrage stellen"}, {"slug":"uebersicht", "title":"Alle Seiten"}]:
        description = INTRO.get(page["slug"], page["title"] + " bei Dive-World & Rescue.")
        html = add_metadata(inner(page), "pages/" + page["slug"] + ".html", page["title"] + " · Dive-World & Rescue", description, "../")
        (DIST / "pages" / (page["slug"]+".html")).write_text(html)
        if page["slug"].startswith("tauch-shop--") or page.get("catalogue"):
            for item in catalogue_items(page):
                main = product_detail(item, page)
                html = page_shell(escape(item["name"]), main, "tauch-shop", item["slug"])
                html = add_metadata(html, "pages/" + item["slug"] + ".html", item["name"] + " · Dive-World & Rescue", item["summary"], "../", item["photos"][0].removeprefix("../"))
                (DIST / "pages" / (item["slug"] + ".html")).write_text(html)


if __name__ == "__main__":
    build()

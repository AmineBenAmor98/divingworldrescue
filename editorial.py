"""Visitors' guides, galleries and reference pages for the German site."""
import re
from html import escape
from itertools import groupby
from urllib.parse import urlencode
from shop import inquiry, slugify
from typography import paragraphs

from pathlib import Path

ASSETS = Path(__file__).parent / "public" / "assets"
WHATSAPP = "https://wa.me/4917685639763"


def slot(name, fallback):
    """Use a commissioned image when it exists, otherwise a stand-in."""
    return f"../assets/{name}" if (ASSETS / name).exists() else f"../assets/{fallback}"


def closing_band(title, text, href, label, anchor="closing"):
    return f'''<section class="landing-contact" aria-labelledby="{anchor}"><div class="wrap"><div><h2 id="{anchor}">{title}</h2><p>{text}</p></div>
      <div class="closing-actions"><a class="cta mint" href="{href}">{label}</a><a class="plain" href="{WHATSAPP}">WhatsApp schreiben</a></div></div></section>'''


def section_head(kicker, title, text="", anchor=""):
    ident = f' id="{anchor}"' if anchor else ""
    side = f"<p>{text}</p>" if text else ""
    return f'<div class="page-head"><div><p class="kicker">{kicker}</p><h2{ident}>{title}</h2></div>{side}</div>'


def course_link(topic, course=None, label="Termin anfragen"):
    params = {"thema": topic}
    if course:
        params["kurs"] = course
    return f'<a class="path-action" href="anfrage.html?{escape(urlencode(params))}">{escape(label)} <span aria-hidden="true">→</span></a>'


AID_GROUPS = {
    "Alltag & Familie": ("erste-hilfe-familie.webp", "erste-hilfe.webp", "Für Eltern, Großeltern, Betreuende und alle, die im Notfall sicher helfen möchten.", "Eltern, Großeltern, Babysitter"),
    "Beruf & Betrieb": ("erste-hilfe-beruf.webp", "erste-hilfe.webp", "Für Unternehmen, Betreuungspersonal und alle, die bei der Arbeit Verantwortung tragen.", "Firmen, Kitas, Schulen"),
    "Tauchsport": ("erste-hilfe-tauchen.webp", "tauchen.webp", "Für Taucher und Begleiter: richtig handeln, wenn beim Tauchen etwas passiert.", "Taucher, Tauchprofis, Bootspersonal"),
}


def euro(value):
    return float(value.replace("€", "").replace(".", "").replace(",", ".").strip())


def aid_card(c):
    """One course row: what it is on the left, what the material costs and the request on the right."""
    request = course_link("Erste Hilfe", c["name"], "Anfragen").replace('class="path-action"', 'class="cta aid-request"')
    if c["online"]:
        cheapest = min((c["online"], c["book"]), key=euro)
        price = f'''<p class="aid-from"><small>Lernmaterial ab</small><strong>{cheapest}</strong></p>
          <p class="aid-options"><span>E-Learning {c["online"]}</span> · <span>Handbuch {c["book"]}</span></p>'''
    else:
        price = '<p class="aid-from"><small>Preis</small><strong class="aid-ask">auf Anfrage</strong></p>'
    return f'''<article class="aid-course-row"><div class="aid-course-copy"><h3>{escape(c["name"])}</h3><p>{escape(c["summary"])}</p></div>
      <div class="aid-course-buy">{price}{request}</div></article>'''


def first_aid(page, breadcrumb):
    request = "anfrage.html?" + escape(urlencode({"thema": "Erste Hilfe"}))
    paths, sections = [], []
    groups = [(g, list(cs)) for g, cs in groupby(page["programmes"], key=lambda c: c["group"])]
    for i, (group, courses) in enumerate(groups):
        anchor = slugify(group)
        image, fallback, intro, audience = AID_GROUPS.get(group, ("", "erste-hilfe.webp", "", ""))
        count = f'{len(courses)} Kurs{"e" if len(courses) != 1 else ""}'
        paths.append(f'''<a class="aid-path" href="#{anchor}"><img src="{slot(image, fallback)}" alt="" loading="lazy">
          <span class="aid-path-copy"><span class="program-chip">{count}</span><strong>{escape(group)}</strong><span>{escape(audience)}</span></span></a>''')
        extra = ""
        if group == "Beruf & Betrieb":
            extra = f'''<aside class="aid-team-offer"><h3>Für dein ganzes Team</h3><p>Wir schulen Firmen, Kindergärten und Schulklassen ab der ersten Klasse als Gruppe. Eine Ausbildung nach DGUV&nbsp;304&#8209;001 kannst du anfragen.</p>
              {course_link("Erste Hilfe", label="Gruppenkurs anfragen")}</aside>'''
        sections.append(f'''<section class="aid-group{' aid-group-alt' if i % 2 else ''}" id="{anchor}" aria-labelledby="{anchor}-title"><div class="wrap aid-group-layout">
          <div class="aid-group-head"><p class="kicker">{count}</p><h2 id="{anchor}-title">{escape(group)}</h2><p>{escape(intro)}</p>{extra}</div>
          <div class="aid-course-list">{"".join(aid_card(c) for c in courses)}</div></div></section>''')
    return f'''<header class="aid-cover aid-cover-v2"><div class="wrap">{breadcrumb}<h1>Erste-Hilfe-Kurse</h1><p>Vom Kindernotfall bis zum Tauchunfall: Lerne, im Ernstfall ruhig und richtig zu helfen. Nach den Standards von First Response Training International (FRTI).</p>
    <div class="cover-choices"><a class="cta mint" href="{request}">Kurs anfragen</a><a class="plain" href="#ablauf">So läuft ein Kurs ab</a></div></div></header>
    <section class="aid-paths-section" aria-labelledby="aid-paths-title"><div class="wrap">
      <h2 id="aid-paths-title" class="aid-paths-title">Für wen ist der Kurs?</h2>
      <nav class="aid-paths" aria-label="Kursbereiche">{"".join(paths)}</nav></div></section>
    <section class="aid-how" id="ablauf" aria-labelledby="ablauf-title"><div class="wrap aid-how-layout">
      <div><p class="kicker">Ablauf</p><h2 id="ablauf-title">So läuft ein Kurs ab</h2></div>
      <ol class="step-list aid-how-steps">
        <li><strong>Theorie vorbereiten</strong><span>Per E-Learning oder mit dem Handbuch, in deinem Tempo. Du wählst eins davon.</span></li>
        <li><strong>Praxis mit Ausbilder</strong><span>Die praktischen Übungen und der Abschluss folgen mit einem Ausbilder. Die Kosten dafür kommen je nach Ort hinzu.</span></li>
        <li><strong>Ab 18 Jahren</strong><span>Mit Zustimmung der Eltern kannst du schon ab 10 Jahren teilnehmen.</span></li>
      </ol></div></section>
    {"".join(sections)}
    <section class="aid-more"><div class="wrap"><a class="aid-material" href="tauch-shop.html#erste-hilfe"><strong>Erste-Hilfe-Material</strong><span>Erste-Hilfe-Sets, Pflaster, Scheren und Diagnostikleuchten aus unserem Shop.</span><span class="path-action">Material ansehen</span></a></div></section>
    {closing_band("Bereit für den Ernstfall?", "Sag uns, welcher Kurs passt und wann du Zeit hast. Wir melden uns mit einem Termin.", request, "Kurs anfragen", "aid-closing")}'''


def image_gallery(blocks, title, start=1):
    out = []
    for i, b in enumerate(blocks, start):
        caption = escape(b.get("caption", ""))
        alt = caption or f'{escape(title)} · Abbildung {i}'
        src = "../" + escape(b["src"])
        desc = f'<figcaption>{caption}</figcaption>' if caption else ''
        out.append(f'<figure><a href="{src}" aria-label="Bild vergrößern: {alt}"><img src="{src}" loading="lazy" alt="{alt}"></a>{desc}</figure>')
    return '<div class="album-grid">' + ''.join(out) + '</div>'


TRIP_KINDS = [
    (("Safaga", "Ägypten"), "Tauchreise"),
    (("TODI", "Diveworld", "Dive4Life", "Monte Mare"), "Hallentauchen"),
    (("Xanten", "Südsee"), "See"),
    (("FRTI",), "Erste Hilfe"),
    (("Messe",), "Messe"),
]


def trip_kind(text):
    return next((kind for keys, kind in TRIP_KINDS if any(k in text for k in keys)), "Ausflug")


def trip_tiles(page, base="termine.html", root="../"):
    """Three destination tiles, shared by the travel page and the homepage. Each opens its own destination on the dates page."""
    tiles = [
        ("Tauchreise", "Rotes Meer", "Safaga in Ägypten, mehrmals im Jahr mit Flug ab Düsseldorf.", slot("reisen-rotes-meer.webp", "tauchgang.webp"), "#ziel-safaga", "Zur Reise nach Safaga"),
        ("Hallentauchen", "Tauchzentren", "TODI, Diveworld, Dive4Life und Monte Mare: tauchen bei jedem Wetter.", slot("reisen-hallenbad.webp", "tauchen.webp"), "#ziel-hallentauchen", "Zu den 4 Tauchzentren"),
        ("See", "Freiwasser", "Die Südsee in Xanten für Kurse, Refresher und Fun-Dives.", slot("reisen-see.webp", "see.webp"), "#ziel-sudsee", "Zum See in Xanten"),
    ]
    return "".join(f'''<a class="trip-tile" href="{base}{anchor}"><img src="{img.replace("../", root, 1)}" alt="" loading="lazy"><span class="trip-tile-copy">
      <span class="trip-kind kind-{slugify(kind)}">{kind}</span><strong>{title}</strong><span>{text}</span><small>{label}</small></span></a>''' for kind, title, text, img, anchor, label in tiles)


def home_news(termine, glueck):
    """Three short news items built from the site's own content."""
    latest = termine["archive"][0]
    venue, _, place = latest["name"].partition(" · ")
    kind = VENUE_KIND.get(latest["name"], "Ausflug")
    trip_photo = {"Tauchreise": "assets/media/ba9e4421064b6920.webp", "See": "assets/reisen-see.webp"}.get(kind, "assets/reisen-hallenbad.webp")
    trip_title = f"Zurück aus {place}" if kind == "Tauchreise" else f"Zuletzt unterwegs: {venue}"
    heading = next((b["text"] for b in glueck["blocks"] if b["type"] == "p"), "")
    month = re.search(r"(Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s+\d{4}", heading)
    items = [
        ("assets/media/c515206b12fed44e.webp", "Übergabe einer SDI-Urkunde", month[0] if month else "Tauchabschlüsse", "Tauchabschlüsse",
         "Neue Brevets im Team", "Herzlichen Glückwunsch an Bernd zum Instructor und an Silvia zum Divemaster.", "pages/glueckwuensche.html", "Alle Tauchabschlüsse"),
        (trip_photo, "", f'{latest["date"]} {latest["year"]}', kind,
         trip_title, f"{venue} in {place}. Alle bisherigen Ausflüge und Reisen findest du im Rückblick.", "pages/bilder-reisen-event-s.html#rueckblick", "Zum Rückblick"),
        ("assets/rettungsschwimmer.webp", "", "Mitarbeit", "Unterbacher See",
         "Rettungsschwimmer gesucht", "Für die Badesaison am Unterbacher See, vor allem an Wochenenden und Feiertagen.", "pages/wir-suchen-dich.html", "Mehr erfahren"),
    ]
    cards = "".join(f'''<article class="news-item"><a href="{href}"><span class="news-photo"><img src="{img}" alt="{escape(alt)}" loading="lazy"></span>
      <span class="news-meta"><time>{escape(when)}</time><span>{escape(tag)}</span></span><strong>{escape(title)}</strong><span class="news-text">{escape(text)}</span><span class="news-link">{label}</span></a></article>'''
                    for img, alt, when, tag, title, text, href, label in items)
    return f'''<section class="home-news" id="aktuelles" aria-labelledby="news-title"><div class="wrap">
      <div class="page-head"><div><p class="kicker">Aktuelles</p><h2 id="news-title">Neues aus der Tauchschule</h2></div></div>
      <div class="news-grid">{cards}</div></div></section>'''


def travel_archive(page):
    highlights = page["highlights"]
    entries = [(year, event) for year, events in highlights.items() for event in events]
    tile_html = trip_tiles(page)
    years = []
    for year, events in highlights.items():
        cards = []
        for event in events:
            text = re.sub(r"\s{2,}", " ", event).strip()
            title, _, people = text.partition(" mit ")
            kind = trip_kind(text)
            who = f'<p class="moment-people">mit {escape(people)}</p>' if people else ""
            cards.append(f'<li class="moment"><span class="trip-kind kind-{slugify(kind)}">{kind}</span><h4>{escape(title.strip(" ,"))}</h4>{who}</li>')
        label = "Ohne Jahr" if not year[:1].isdigit() else year
        years.append(f'<section class="moment-year"><h3>{escape(label)}<small>{len(events)} Rückblick{"e" if len(events) != 1 else ""}</small></h3><ol class="moments">{"".join(cards)}</ol></section>')
    picks = ["ba9e4421064b6920", "4affc21280160622", "d88380ee965ce574", "0b0901195a9a7b6c", "4223fcc09b4bdb38"]
    mosaic = "".join(f'<a href="../assets/media/{pid}.webp" aria-label="Foto vergrößern"><img src="../assets/media/{pid}.webp" alt="Foto aus einem Kurs oder einer Reise der Tauchschule" loading="lazy"></a>' for pid in picks)
    request = "anfrage.html?" + escape(urlencode({"thema": "Termine und Reisen"}))
    return f'''<section class="trip-section"><div class="wrap">{section_head("Unterwegs", "Wohin wir gemeinsam fahren", "Vom Hallenbad in der Nähe bis ans Rote Meer. Jeder ist willkommen, auch Begleitung ohne Tauchschein.")}
      <div class="trip-tiles">{tile_html}</div></div></section>
    <section class="photo-section"><div class="wrap">{section_head("Eindrücke", "Echte Momente mit der Tauchschule", 'Vom Bootsdeck vor Safaga bis zum Abschluss im Hallenbad. <a class="path-action" href="glueckwuensche.html#weitere-kursfotos">Weitere Fotos ansehen</a>')}
      <div class="photo-mosaic">{mosaic}</div></div></section>
    <section class="moments-section" id="rueckblick"><div class="wrap">{section_head("Rückblick", "Erlebt mit der Tauchschule", f'{len(entries)} Ausflüge, Kurse und Reisen. <a class="path-action" href="termine.html#archiv">Alle Termine mit Ausschreibung</a>')}
      {"".join(years)}</div></section>
    {closing_band("Beim nächsten Mal dabei sein?", "Sag uns, wohin du mitkommen möchtest. Wir melden uns mit Termin und Details.", request, "Ausflug anfragen", "travel-closing")}'''


def albums(page):
    if page["slug"] == "bilder-reisen-event-s":
        return travel_archive(page)
    groups = {}
    for b in page["blocks"]:
        if b["type"] == "photo":
            groups.setdefault(b["album"], []).append(b)
    out = []
    for index, (label, photos) in enumerate(groups.items()):
        certs = all(p.get("caption") for p in photos)
        classes = "album" + (" album-certs" if certs else "") + (" album-latest" if index == 0 and len(photos) <= 4 else "")
        count = (f'{len(photos)} Abschluss' if len(photos) == 1 else f'{len(photos)} Abschlüsse') if certs else f'{len(photos)} Fotos'
        if index == 0 and len(photos) <= 4:
            count = "Neueste Abschlüsse"
        grid = image_gallery(photos, label)
        if not certs and len(photos) > 12:
            grid = image_gallery(photos[:12], label) + f'<details class="album-more"><summary>Alle {len(photos)} Fotos zeigen</summary>{image_gallery(photos[12:], label, 13)}</details>'
        out.append(f'<section class="{classes}" id="{slugify(label)}"><div class="album-head"><h2>{escape(label)}</h2><span>{count}</span></div>{grid}</section>')
    if "highlights" in page:
        out.append('<section class="reading"><h2>Reisen und Kurse im Rückblick</h2>')
        for year, events in page["highlights"].items():
            items = ''.join(f'<li>{escape(e)}</li>' for e in events)
            out.append(f'<details class="archive-period"><summary>{escape(year)}</summary><ul>{items}</ul></details>')
        out.append('</section>')
    return ''.join(out)


VENUES = [
    ("TODI · Beringen", "Hallentauchen", "Belgien", "Freitagabend und Samstag tauchen, auf Wunsch mit Übernachtung im Hotel."),
    ("Dive4Life · Siegburg", "Hallentauchen", "Deutschland", "Kurse und freies Tauchen, oft übers Wochenende mit Hotel."),
    ("Diveworld · Enschede", "Hallentauchen", "Niederlande", "Freitagabend tauchen, Anreise ab 16 Uhr, Hotel möglich."),
    ("Monte Mare · Rheinbach", "Hallentauchen", "Deutschland", "Schnuppertauchen, Open-Water-Kurs und Fun-Dive."),
    ("Südsee · Xanten", "See", "Deutschland", "Refresher, Kurse und freies Tauchen im Freiwasser."),
    ("Safaga · Ägypten", "Tauchreise", "Rotes Meer", "7 bis 10 Tauchtage, Flug ab Düsseldorf. Auch für Nichttaucher."),
]
VENUE_KIND = {name: kind for name, kind, _, _ in VENUES} | {"Unterbacher See · Düsseldorf": "See"}


def notice(text):
    text = re.sub(r"⚠+|!AUSGEBUCHT!", "", text)
    text = re.sub(r"\s*,(\s*,)+", ",", text)
    text = re.sub(r"^([A-Z]) ([a-z])", r"\1\2", text.strip())
    return re.sub(r"\s{2,}", " ", text).strip(" ,")


# Small inline flags: emoji flags show as two letters on Windows, SVG works everywhere.
FLAG_STRIPES = {
    "Belgien": ("v", "#000", "#fdda24", "#ef3340"),
    "Deutschland": ("h", "#000", "#dd0000", "#ffce00"),
    "Niederlande": ("h", "#ae1c28", "#fff", "#21468b"),
    "Ägypten": ("h", "#ce1126", "#fff", "#000"),
}


def flag(country):
    if country not in FLAG_STRIPES:
        return ""
    axis, *colors = FLAG_STRIPES[country]
    rects = "".join(
        f'<rect x="{i * 10}" y="0" width="10" height="20" fill="{c}"/>' if axis == "v" else f'<rect x="0" y="{i * 20 / 3:.2f}" width="30" height="{20 / 3:.2f}" fill="{c}"/>'
        for i, c in enumerate(colors))
    if country == "Ägypten":
        rects += '<circle cx="15" cy="10" r="2.2" fill="#c09300"/>'
    return f'<svg class="flag" viewBox="0 0 30 20" width="21" height="14" aria-hidden="true">{rects}</svg>'


# How often each destination comes round, read from the dates archive (2025 and 2026).
VENUE_RHYTHM = {
    "Safaga · Ägypten": ("Dreimal im Jahr", "Meist im März, im Juni/Juli und im Herbst"),
    "Südsee · Xanten": ("Jeden Sommer", "Im Juli und August"),
    "TODI · Beringen": ("4–5× im Jahr", ""),
    "Dive4Life · Siegburg": ("Etwa 4× im Jahr", ""),
    "Monte Mare · Rheinbach": ("Mehrmals im Jahr", ""),
    "Diveworld · Enschede": ("2× im Jahr", ""),
}
CALENDAR = '<svg width="{0}" height="{0}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 11h18"/></svg>'
FACT_ICONS = {
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "plane": '<path d="M16 10h4a2 2 0 0 1 0 4h-4l-4 7h-3l2-7H7l-2 2H2l2-4-2-4h3l2 2h4L9 3h3z"/>',
    "people": '<circle cx="9" cy="7" r="4"/><path d="M3 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2M16 3.1a4 4 0 0 1 0 7.8M21 21v-2a4 4 0 0 0-3-3.9"/>',
}


def destinations():
    """Safaga as the feature card, the lake beside one panel that groups the four pools."""
    venues = {name: (kind, region, program) for name, kind, region, program in VENUES}

    def ask(name):
        return "anfrage.html?" + escape(urlencode({"thema": "Termine und Reisen", "ziel": name}))

    def country(name):
        _, region, _ = venues[name]
        place = name.split(" · ")[1]
        label = place if flag(place) else region
        return f'<span class="trip-country">{flag(label)}{escape(label)}</span>'

    def when(name):
        title, detail = VENUE_RHYTHM[name]
        return f'<p class="ziel-when">{CALENDAR.format(18)}<span><strong>{title}</strong>{escape(detail)}</span></p>'

    note = '<span class="ziel-here" aria-hidden="true">Du bist hier</span>'
    safaga = "Safaga · Ägypten"
    facts = [("sun", "7 bis 10", "Tauchtage"), ("plane", "Flug", "ab Düsseldorf"), ("people", "Auch", "für Nichttaucher")]
    fact_items = "".join(f'<li><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{FACT_ICONS[i]}</svg><span><strong>{a}</strong> {b}</span></li>' for i, a, b in facts)
    feature = f'''<article class="ziel ziel-feature" id="ziel-safaga">{note}
        <div class="ziel-photo"><img src="{slot("reisen-rotes-meer.webp", "tauchgang.webp")}" alt="Taucher auf dem Deck eines Tauchboots vor der Küste bei Safaga" loading="lazy"><span class="ziel-badge">Unsere große Reise</span></div>
        <div class="ziel-body"><p class="trip-meta"><span class="trip-kind kind-tauchreise">Tauchreise</span>{country(safaga)}</p>
          <div><h3>Safaga</h3><p class="trip-place">Rotes Meer</p></div>
          <p class="ziel-desc">Unsere gemeinsame Tauchreise ans Rote Meer. Jeder ist willkommen, auch Begleitung ohne Tauchschein.</p>
          <ul class="ziel-facts">{fact_items}</ul>
          {when(safaga)}
          <p class="ziel-actions"><a class="ziel-link ziel-button" href="{ask(safaga)}">Reise anfragen<span class="sr-only"> nach Safaga</span></a><a class="ziel-more" href="bilder-reisen-event-s.html">Bilder vergangener Reisen</a></p></div></article>'''
    lake_name = "Südsee · Xanten"
    lake = f'''<article class="ziel ziel-lake" id="ziel-sudsee">{note}
        <div class="ziel-photo"><img src="{slot("reisen-see.webp", "see.webp")}" alt="Zwei Taucher bereiten am Seeufer ihre Ausrüstung vor" loading="lazy"></div>
        <div class="ziel-body"><p class="trip-meta"><span class="trip-kind kind-see">See</span>{country(lake_name)}</p>
          <div><h3>Südsee</h3><p class="trip-place">Xanten</p></div>
          <p class="ziel-desc">{escape(venues[lake_name][2])}</p>
          {when(lake_name)}
          <a class="ziel-link" href="{ask(lake_name)}">Termin anfragen<span class="sr-only"> für die Südsee in Xanten</span></a></div></article>'''
    pools = []
    for name in ("TODI · Beringen", "Dive4Life · Siegburg", "Monte Mare · Rheinbach", "Diveworld · Enschede"):
        venue, place = name.split(" · ")
        program = venues[name][2].replace("auf Wunsch mit Übernachtung im Hotel", "auf Wunsch mit Hotel")
        pools.append(f'''<article class="ziel-pool" id="ziel-{slugify(venue)}">
          <div class="ziel-pool-top"><h4>{escape(venue)}</h4>{country(name)}</div><span class="trip-place">{escape(place)}</span>
          <p>{escape(program)}</p>
          <div class="ziel-pool-foot"><span class="ziel-freq">{CALENDAR.format(15)}{VENUE_RHYTHM[name][0]}</span><a class="ziel-link" href="{ask(name)}">Anfragen<span class="sr-only"> für {escape(venue)} in {escape(place)}</span></a></div></article>''')
    panel = f'''<section class="ziel-pools" id="ziel-hallentauchen" aria-labelledby="ziel-hallen-title">{note}
        <div class="ziel-pools-head"><div class="ziel-photo"><img src="{slot("reisen-hallenbad.webp", "tauchen.webp")}" alt="" loading="lazy"></div>
          <div><span class="trip-kind">Hallentauchen</span><h3 id="ziel-hallen-title">Bei jedem Wetter</h3><p>Vier Tauchzentren in der Region: zum Üben, für Kurse und Fun-Dives, auch im Winter.</p></div></div>
        <div class="ziel-pool-grid">{"".join(pools)}</div></section>'''
    return f'<div class="ziele">{feature}<div class="ziel-row">{lake}{panel}</div></div>'


def dates(page):
    archive = page["archive"]
    first_year = min(record["year"] for record in archive)
    request = "anfrage.html?" + escape(urlencode({"thema": "Termine und Reisen"}))
    facts = [
        ("Jeder ist willkommen", "Einsteiger, erfahrene Taucher und Begleitung. Melde dich per Mail, Telefon oder WhatsApp."),
        ("Anmeldung vorab", "Meist bis etwa eine Woche vor dem Termin, bei Reisen früher."),
        ("Übernachten möglich", "Bei Ausflügen nach Belgien, in die Niederlande und nach Siegburg auf Wunsch mit Hotel."),
        ("Andere Termine auf Anfrage", "Du hast einen Wunschtermin oder suchst einen Kurs? Frag einfach nach."),
    ]
    years = []
    for index, (year, records) in enumerate(groupby(archive, key=lambda e: e["year"])):
        records = list(records)
        rows = []
        for record in records:
            venue, _, place = record["name"].partition(" · ")
            text = [notice(page["blocks"][i]["text"].replace(" JANUAR 2025", "")) for i in record["text_indices"]]
            kind = VENUE_KIND.get(record["name"], "Ausflug")
            body = "".join(f"<p>{escape(t)}</p>" for t in text if t)
            rows.append(f'''<li><details><summary><time>{escape(record["date"])}</time><span class="log-name"><strong>{escape(venue)}</strong> {escape(place)}</span><span class="trip-kind kind-{slugify(kind)}">{kind}</span><span class="log-toggle">Ausschreibung</span></summary>
              <div class="log-notice">{body}</div></details></li>''')
        open_attr = " open" if index == 0 else ""
        years.append(f'''<details class="log-year"{open_attr}><summary><span>{year}</span><small>{len(records)} Termine</small></summary><ol class="trip-log">{"".join(rows)}</ol></details>''')
    return f'''<section class="trip-section" id="ziele"><div class="wrap">
      <div class="trip-head"><div><p class="kicker">Tauchziele</p><h2>Hier tauchen wir regelmäßig.</h2></div>
      <p>Vom Hallenbad in der Nähe bis ans Rote Meer. Such dir ein Ziel aus, wir sagen dir den nächsten Termin.</p></div>
      {destinations()}</div></section>
    <section class="trip-facts" aria-label="So funktioniert es"><div class="wrap"><ul>{"".join(f"<li><strong>{a}</strong><span>{b}</span></li>" for a, b in facts)}</ul></div></section>
    <section class="trip-archive" id="archiv"><div class="wrap">
      <div class="trip-head"><div><p class="kicker">Rückblick</p><h2>Bisherige Termine</h2></div>
      <p>{len(archive)} Ausflüge, Kurse und Reisen seit Januar {first_year}. <a class="path-action" href="bilder-reisen-event-s.html">Bilder ansehen</a></p></div>
      {"".join(years)}</div></section>
    <section class="landing-contact" aria-labelledby="trip-closing"><div class="wrap"><div><h2 id="trip-closing">Beim nächsten Mal dabei sein?</h2><p>Sag uns, wohin du mitkommen möchtest. Wir melden uns mit Termin und Details.</p></div>
      <div class="closing-actions"><a class="cta mint" href="{request}">Termin anfragen</a><a class="plain" href="https://wa.me/4917685639763">WhatsApp schreiben</a></div></div></section>'''


def guestbook(page):
    b = page["blocks"]
    first, last = b[1]["text"], b[2]["text"]
    copy = ''.join(paragraphs(x['text']) for x in b[4:])
    initials = (first[:1] + last[:1]).upper()
    return f'''<section class="guest-section"><div class="wrap">
      <article class="guest-card">
        <aside class="guest-author"><span class="guest-avatar" aria-hidden="true">{escape(initials)}</span>
          <div><strong>{escape(first)} {escape(last)}</strong><time datetime="2026-01-18">18. Januar 2026</time></div>
          <ul class="guest-tags"><li>Tauchausbildung</li><li>mit Sohn (12)</li></ul></aside>
        <div class="guest-body"><p class="guest-pull">„Fachlich exzellent, menschlich großartig und mit einem klaren Fokus auf Sicherheit.“</p>
          <blockquote>{copy}</blockquote></div>
      </article></div></section>'''


def jobs():
    mail = "mailto:dive-world@mail.de?subject=" + escape("Bewerbung Rettungsschwimmer Unterbacher See")
    tasks = ["Badebetrieb beaufsichtigen und Badegäste betreuen", "Rettungs- und Erste-Hilfe-Maßnahmen durchführen", "Ausrüstung kontrollieren und das Team bei der Organisation unterstützen"]
    needs = ["Aktuelles Rettungsschwimmabzeichen", "Erste-Hilfe-Nachweis, höchstens zwei Jahre alt", "Körperliche Fitness", "Freude an der Arbeit im Team"]
    check = lambda items: "".join(f"<li>{escape(i)}</li>" for i in items)
    return f'''<section class="job-intro"><div class="wrap">
      <img class="job-photo" src="{slot("rettungsschwimmer.webp", "see.webp")}" alt="" loading="lazy">
      <div class="job-copy"><p class="kicker">Wasserrettung · Unterbacher See</p><h2>Rettungsschwimmer gesucht</h2>
      <p>Du möchtest in der Badesaison am Unterbacher See mitarbeiten? Frag uns nach freien Einsätzen, vor allem an Wochenenden und Feiertagen.</p>
      <ul class="job-facts"><li>Badesaison</li><li>Wochenenden &amp; Feiertage</li><li>ab 18 Jahren (Richtwert)</li></ul>
      <div class="job-actions"><a class="cta" href="{mail}">Jetzt bewerben</a><a class="path-action" href="tel:+4917685639763">0176 8563 9763</a></div></div>
    </div></section>
    <section class="job-details"><div class="wrap">
      <article class="job-card"><h3>Deine Aufgaben</h3><ul class="check-list">{check(tasks)}</ul></article>
      <article class="job-card"><h3>Das bringst du mit</h3><ul class="check-list">{check(needs)}</ul><p class="job-note">18 Jahre sind ein Richtwert, wir freuen uns auch über Anfragen von Jüngeren.</p></article>
      <article class="job-card job-train"><h3>Wir bilden dich aus</h3><p>Rettungsschwimmer- und Rescue-Diver-Ausbildung, Erste-Hilfe-Kurse und Auffrischungen sind direkt bei uns möglich.</p>
        <div class="job-links"><a class="path-action" href="frti-kurse.html">Erste-Hilfe-Kurse</a><a class="path-action" href="tauchen-lernen-kurse.html#weiterlernen">Rescue Diver</a></div></article>
    </div></section>
    <section class="landing-contact" aria-labelledby="job-closing"><div class="wrap"><div><h2 id="job-closing">Bewirb dich bei uns</h2><p>Schick deine Unterlagen per Mail oder ruf uns an.</p></div>
      <div class="closing-actions"><a class="cta mint" href="{mail}">dive-world@mail.de</a><a class="plain" href="tel:+4917685639763">0176 8563 9763</a></div></div></section>'''


def hud(page):
    photos = [b for b in page["blocks"] if b["type"] == "photo"]
    return f'''<section class="reader-panel"><div><h2>Tauchdaten im Sichtfeld</h2><p>Daïve entwickelt einen Tauchcomputer, der an einer Standard-Tauchmaske befestigt wird. Das Head-up-Display zeigt Tiefe, Zeit, Aufstiegsgeschwindigkeit, Dekompressionswarnungen und Alarme an.</p></div>
    <div><h3>Preis auf Anfrage</h3>{inquiry("Daïve Head-up-Display")}<a class="dive-text-link" href="tauch-shop--computer.html">Tauchcomputer vergleichen</a></div></section>
    <section class="album"><h2>Produktinformationen von Daïve</h2>{image_gallery(photos,"Daïve Head-up-Display")}</section>'''


def legal(page):
    blocks = page["blocks"]
    def source(start, end):
        return ' '.join(b['text'] for b in blocks[start:end])
    def address(start, end):
        return '<address>' + '<br>'.join(escape(b['text']) for b in blocks[start:end]) + '</address>'
    def row(label, value):
        return f'<div><dt>{escape(label)}</dt><dd>{value}</dd></div>'
    contact = [
        row('Telefon', '<a href="tel:+4917685639763">+49 176 85639763</a>'),
        row('Fax', '01805002068423'),
        row('E-Mail', '<a href="mailto:dive-world@mail.de">dive-world@mail.de</a><br><a href="mailto:info@dive-world-rescue.de">info@dive-world-rescue.de</a>'),
        row('Web', 'www.dive-world-rescue.de'),
        row('Facebook', escape(blocks[15]['text'])),
        row('Twitter', escape(blocks[17]['text'])),
        row('Inhaber', 'Micha Becker'),
        row('Gewerbe', escape(blocks[19]['text'])),
    ]
    provider = '<h3>Anschrift</h3>' + address(2,6) + '<h3>Kontakt</h3><dl class="legal-facts">' + ''.join(contact) + '</dl>'
    # The EU ODR platform (block 20) closed on 20 July 2025, so only the e-mail line stays.
    provider += paragraphs(blocks[21]['text'])
    # An empty source heading is omitted; it names no provider or service.
    copyright = '<h3>Copyright / Urheberrecht</h3>' + paragraphs(source(24,26))
    copyright += '<h3>Bildinhaber</h3>' + paragraphs(blocks[27]['text'])
    copyright += '<h3>Dekoration</h3>' + paragraphs(source(29,31))
    social = paragraphs(blocks[32]['text']) + '<ul>' + ''.join(f'<li>{escape(blocks[i]["text"])}</li>' for i in [33,34]) + '</ul>'
    privacy = [paragraphs(blocks[35]['text'].removeprefix('DATENSCHUTZERKLÄRUNG '))]
    i = 36
    while i < len(blocks):
        b = blocks[i]
        if b['type'] == 'heading':
            privacy.append(f'<h3 id="{slugify(b["text"])}">{escape(b["text"].rstrip(":"))}</h3>')
            i += 1
            if i == 37:
                privacy.append(address(37,42))
                i = 42
        elif b['text'].startswith('– '):
            items = []
            while i < len(blocks) and blocks[i]['text'].startswith('– '):
                items.append('<li>' + escape(blocks[i]['text'][2:]) + '</li>')
                i += 1
            privacy.append('<ul>' + ''.join(items) + '</ul>')
        else:
            privacy.append(paragraphs(b['text']))
            i += 1
    parts = {'Anbieter und Kontakt': provider, 'Urheberrecht und Produktbilder': copyright,
             'Soziale Medien': social, 'Datenschutzerklärung': ''.join(privacy)}
    links = ''.join(f'<a href="#{slugify(t)}">{escape(t)}</a>' for t in parts)
    text = ''.join(f'<section id="{slugify(t)}"><h2>{escape(t)}</h2>{body}</section>' for t, body in parts.items())
    return f'<div class="legal-layout"><nav aria-label="Abschnitte">{links}</nav><div class="legal-text">{text}</div></div>'

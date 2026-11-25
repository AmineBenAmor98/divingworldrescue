"""Visitors' guides, galleries and reference pages for the German site."""
import re
from collections import Counter
from html import escape
from itertools import groupby
from urllib.parse import urlencode
from shop import inquiry, slugify
from typography import paragraphs


def course_link(topic, course=None, label="Termin anfragen"):
    params = {"thema": topic}
    if course:
        params["kurs"] = course
    return f'<a class="path-action" href="anfrage.html?{escape(urlencode(params))}">{escape(label)} <span aria-hidden="true">→</span></a>'


def first_aid(page, breadcrumb):
    sections = []
    tabs = []
    for group, courses in groupby(page["programmes"], key=lambda c: c["group"]):
        anchor = slugify(group)
        tabs.append(f'<a href="#{anchor}">{escape(group)} <span aria-hidden="true">↓</span></a>')
        items = []
        for c in courses:
            if c["online"]:
                fees = f'<h4 class="material-label">Lernmaterial · wahlweise</h4><dl class="format-fees"><div><dt>E-Learning</dt><dd>{c["online"]}</dd></div><div><dt>Handbuch</dt><dd>{c["book"]}</dd></div></dl><small>Die Praxisschulung kommt hinzu und kostet je nach Ort unterschiedlich viel.</small>'
            else:
                fees = '<p>Preis und Ablauf auf Anfrage.</p>'
            items.append(f'''<article class="aid-course"><div><h3>{escape(c["name"])}</h3><p>{escape(c["summary"])}</p>
              </div><div class="aid-fees">{fees}</div><div class="aid-enquire">{course_link("Erste Hilfe", c["name"], "Diesen Kurs anfragen")}</div></article>''')
        sections.append(f'<section class="aid-group" id="{anchor}"><h2>{escape(group)}</h2><div>{"".join(items)}</div></section>')
    return f'''<header class="aid-cover"><div class="wrap">{breadcrumb}<h1>Erste-Hilfe-Kurse</h1><p>Vom Kindernotfall bis zum Tauchunfall. Finde die Ausbildung von First Response Training International, die zu deinem Alltag passt.</p></div></header>
    <nav class="dive-routes" aria-label="Kursbereiche"><div class="wrap">{"".join(tabs)}</div></nav>
    <div class="wrap editorial-body">{"".join(sections)}
    <section class="reader-panel"><div><h2>Teilnahme &amp; Ablauf</h2><p>Bei den Kursen mit Materialpreisen bereitest du die Theorie per E-Learning oder Handbuch vor. Die praktischen Übungen und der Abschluss folgen mit einem Ausbilder.</p><p>Für diese Kurse nennt die Schule 18 Jahre als Mindestalter, mit Zustimmung der Eltern 10 Jahre.</p></div>
    <div><h3>Als Gruppe teilnehmen</h3><p>Es gibt auch Angebote für Firmen, Kindergärten und Schulklassen ab der ersten Klasse. Eine Ausbildung nach DGUV 304-001 kannst du anfragen.</p>{course_link("Erste Hilfe", label="Gruppenkurs anfragen")}<a class="dive-text-link" href="tauch-shop.html#erste-hilfe">Erste-Hilfe-Material ansehen</a></div></section></div>'''


def image_gallery(blocks, title):
    out = []
    for i, b in enumerate(blocks, 1):
        caption = escape(b.get("caption", ""))
        alt = caption or f'{escape(title)} · Abbildung {i}'
        src = "../" + escape(b["src"])
        desc = f'<figcaption>{caption}</figcaption>' if caption else ''
        out.append(f'<figure><a href="{src}" aria-label="Bild vergrößern: {alt}"><img src="{src}" loading="lazy" alt="{alt}"></a>{desc}</figure>')
    return '<div class="album-grid">' + ''.join(out) + '</div>'


def travel_archive(page):
    years = []
    for i, (year, events) in enumerate(page["highlights"].items()):
        items = ''.join(f'<li>{escape(event)}</li>' for event in events)
        opened = ' open' if i < 2 else ''
        years.append(f'<details class="travel-year"{opened}><summary>{escape(year)}<small>{len(events)} Rückblick' + ('e' if len(events) != 1 else '') + f'</small></summary><ul>{items}</ul></details>')
    return '''<section class="reader-panel"><div><h2>Gemeinsam unterwegs</h2><p>Vom Indoor-Tauchgang bis zur Reise nach Safaga. Hier findest du die bisherigen Ausflüge und Veranstaltungen unserer Schule.</p></div><div>''' + course_link("Termine und Reisen", label="Nächsten Ausflug anfragen") + '''<a class="dive-text-link" href="glueckwuensche.html">Tauchabschlüsse ansehen</a></div></section>
    <section class="travel-archive" aria-labelledby="reise-archiv"><h2 id="reise-archiv">Reisen &amp; Veranstaltungen im Rückblick</h2>''' + ''.join(years) + '</section>'


def albums(page):
    if page["slug"] == "bilder-reisen-event-s":
        return travel_archive(page)
    groups = {}
    for b in page["blocks"]:
        if b["type"] == "photo":
            groups.setdefault(b["album"], []).append(b)
    out = []
    for label, photos in groups.items():
        out.append(f'<section class="album"><h2>{escape(label)}</h2>{image_gallery(photos, label)}</section>')
    if "highlights" in page:
        out.append('<section class="reading"><h2>Reisen und Kurse im Rückblick</h2>')
        for year, events in page["highlights"].items():
            items = ''.join(f'<li>{escape(e)}</li>' for e in events)
            out.append(f'<details class="archive-period"><summary>{escape(year)}</summary><ul>{items}</ul></details>')
        out.append('</section>')
    if page["slug"] == "frti-kurse--frti-glueckwuensche":
        target, heading, copy = "frti-kurse.html", "Selbst Erste Hilfe lernen", "Entdecke die Kurse für Familie, Beruf und Tauchsport."
    elif page["slug"] == "glueckwuensche":
        target, heading, copy = "tauchen-lernen-kurse.html", "Dein nächster Schritt", "Vom ersten Tauchgang bis zur Weiterbildung. Finde deinen Kurs."
    else:
        target, heading, copy = "termine.html", "Beim nächsten Mal dabei sein", "Frag das Team nach dem nächsten Tauchausflug oder deinem Wunschkurs."
    out.append(f'<aside class="archive-next"><h2>{heading}</h2><p>{copy}</p><a class="path-action" href="{target}">Mehr erfahren</a></aside>')
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


def dates(page):
    archive = page["archive"]
    counts = Counter(record["name"] for record in archive)
    first_year = min(record["year"] for record in archive)
    request = "anfrage.html?" + escape(urlencode({"thema": "Termine und Reisen"}))
    cards = []
    for name, kind, region, program in VENUES:
        venue, place = name.split(" · ")
        link = "anfrage.html?" + escape(urlencode({"thema": "Termine und Reisen", "ziel": name}))
        cards.append(f'''<article class="trip-card"><p class="trip-meta"><span class="trip-kind kind-{slugify(kind)}">{kind}</span>{escape(region)}</p>
          <h3>{escape(venue)}</h3><p class="trip-place">{escape(place)}</p><p>{escape(program)}</p>
          <footer><span>{counts[name]} Termine seit {first_year}</span><a href="{link}">Mitkommen<span class="sr-only"> nach {escape(place)}</span></a></footer></article>''')
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
      <div class="trip-grid">{"".join(cards)}</div></div></section>
    <section class="trip-facts" aria-label="So funktioniert es"><div class="wrap"><ul>{"".join(f"<li><strong>{a}</strong><span>{b}</span></li>" for a, b in facts)}</ul></div></section>
    <section class="trip-archive"><div class="wrap">
      <div class="trip-head"><div><p class="kicker">Rückblick</p><h2>Bisherige Termine</h2></div>
      <p>{len(archive)} Ausflüge, Kurse und Reisen seit Januar {first_year}. <a class="path-action" href="bilder-reisen-event-s.html">Bilder ansehen</a></p></div>
      {"".join(years)}</div></section>
    <section class="landing-contact" aria-labelledby="trip-closing"><div class="wrap"><div><h2 id="trip-closing">Beim nächsten Mal dabei sein?</h2><p>Sag uns, wohin du mitkommen möchtest. Wir melden uns mit Termin und Details.</p></div>
      <div class="closing-actions"><a class="cta mint" href="{request}">Termin anfragen</a><a class="plain" href="https://wa.me/4917685639763">WhatsApp schreiben</a></div></div></section>'''


def guestbook(page):
    b = page["blocks"]
    copy = ''.join(paragraphs(x['text']) for x in b[4:])
    return f'''<article class="reading guest-entry"><h2>{escape(b[1]["text"])} {escape(b[2]["text"])}</h2>
    <time datetime="2026-01-18">18. Januar 2026</time><blockquote>{copy}</blockquote><a class="dive-text-link" href="tauchen-lernen-kurse.html">Zur Tauchausbildung →</a></article>'''


def jobs():
    return '''<article class="reader-panel"><div><h2>Rettungsschwimmer am Unterbacher See</h2><p>Du möchtest in der Badesaison am Unterbacher See mitarbeiten? Frag uns nach freien Einsätzen, vor allem an Wochenenden und Feiertagen.</p>
    <h3>Deine Aufgaben</h3><ul><li>Badebetrieb beaufsichtigen und Badegäste betreuen</li><li>Rettungs- und Erste-Hilfe-Maßnahmen durchführen</li><li>Ausrüstung kontrollieren und das Team bei der Organisation unterstützen</li></ul>
    <h3>Das bringst du mit</h3><p>Ein aktuelles Rettungsschwimmerabzeichen, einen höchstens zwei Jahre alten Erste-Hilfe-Nachweis, körperliche Fitness und Freude an der Arbeit im Team. Die Schule nennt 18 Jahre als Richtwert und nimmt auch Anfragen von Jüngeren entgegen.</p>
    <p>Rettungsschwimmer- und Rescue-Diver-Ausbildung sowie Erste-Hilfe-Kurse und Auffrischungen sind bei der Schule möglich.</p></div>
    <div><h3>Bewerbung &amp; Rückfragen</h3><p>Schick deine Unterlagen direkt an das Team oder ruf täglich ab 13 Uhr an.</p><a class="dive-text-link" href="mailto:dive-world@mail.de">dive-world@mail.de</a><a class="dive-text-link" href="tel:+4917685639763">0176 8563 9763</a></div></article>'''


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
    provider += paragraphs(source(20,22))
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

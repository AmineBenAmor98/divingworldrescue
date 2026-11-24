"""Visitors' guides, galleries and reference pages for the German site."""
from html import escape
from itertools import groupby
from urllib.parse import urlencode
from shop import inquiry, slugify


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
                fees = f'<dl class="format-fees"><div><dt>E-Learning</dt><dd>{c["online"]}</dd></div><div><dt>Handbuch</dt><dd>{c["book"]}</dd></div></dl><small>Wahlweise. Die Praxisschulung kommt hinzu und kostet je nach Ort unterschiedlich viel.</small>'
            else:
                fees = '<p>Preis und Ablauf auf Anfrage.</p>'
            items.append(f'''<article class="aid-course"><div><h3>{escape(c["name"])}</h3><p>{escape(c["summary"])}</p>
              {course_link("Erste Hilfe", c["name"], "Diesen Kurs anfragen")}</div><div class="aid-fees">{fees}</div></article>''')
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
        alt = caption or f'{escape(title)} · Foto {i}'
        src = "../" + escape(b["src"])
        desc = f'<figcaption>{caption}</figcaption>' if caption else ''
        out.append(f'<figure><a href="{src}" aria-label="Bild vergrößern: {alt}"><img src="{src}" loading="lazy" alt="{alt}"></a>{desc}</figure>')
    return '<div class="album-grid">' + ''.join(out) + '</div>'


def albums(page):
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
    return ''.join(out)


def dates(page):
    out = ['<section class="reader-panel"><div><h2>Den nächsten Termin finden</h2><p>Du möchtest einen Kurs machen oder mittauchen? Nenne uns den Kurs oder Tauchplatz und deinen Wunschzeitraum.</p></div><div>' + course_link("Termine und Reisen") + '<a class="dive-text-link" href="bilder-reisen-event-s.html">Fotos von früheren Ausflügen</a></div></section><section class="reading"><h2>Terminarchiv</h2>']
    for year, records in groupby(page["archive"], key=lambda e: e["year"]):
        out.append(f'<details class="archive-period"><summary>{year}</summary><ol class="event-log">')
        for record in records:
            source = [page["blocks"][i]["text"].replace(" JANUAR 2025", "") for i in record["text_indices"]]
            more = ' '.join(source)
            out.append(f'<li><span>{escape(record["date"])}</span><div><strong>{escape(record["name"])}</strong><details><summary>Damals ausgeschrieben</summary><p>{escape(more)}</p></details></div></li>')
        out.append('</ol></details>')
    return ''.join(out) + '</section>'


def guestbook(page):
    b = page["blocks"]
    paragraphs = ''.join(f'<p>{escape(x["text"])}</p>' for x in b[4:])
    return f'''<article class="reading guest-entry"><h2>{escape(b[1]["text"])} {escape(b[2]["text"])}</h2>
    <time datetime="2026-01-18">18. Januar 2026</time><blockquote>{paragraphs}</blockquote><a class="dive-text-link" href="tauchen-lernen-kurse.html">Zur Tauchausbildung →</a></article>'''


def jobs():
    return '''<article class="reader-panel"><div><h2>Rettungsschwimmer am Unterbacher See</h2><p>Für die Badesaison sucht die Schule Unterstützung, vor allem an Wochenenden und Feiertagen. Einsätze unter der Woche sind je nach Bedarf möglich.</p>
    <h3>Deine Aufgaben</h3><ul><li>Badebetrieb beaufsichtigen und Badegäste betreuen</li><li>Rettungs- und Erste-Hilfe-Maßnahmen durchführen</li><li>Ausrüstung kontrollieren und das Team bei der Organisation unterstützen</li></ul>
    <h3>Das bringst du mit</h3><p>Ein aktuelles Rettungsschwimmerabzeichen, einen höchstens zwei Jahre alten Erste-Hilfe-Nachweis, körperliche Fitness und Freude an der Arbeit im Team. Die Schule nennt 18 Jahre als Richtwert und nimmt auch Anfragen von Jüngeren entgegen.</p>
    <p>Rettungsschwimmer- und Rescue-Diver-Ausbildung sowie Erste-Hilfe-Kurse und Auffrischungen sind bei der Schule möglich.</p></div>
    <div><h3>Bewerbung &amp; Rückfragen</h3><p>Schick deine Unterlagen direkt an das Team oder ruf täglich ab 13 Uhr an.</p><a class="dive-text-link" href="mailto:dive-world@mail.de">dive-world@mail.de</a><a class="dive-text-link" href="tel:+4917685639763">0176 8563 9763</a></div></article>'''


def hud(page):
    photos = [b for b in page["blocks"] if b["type"] == "photo"]
    return f'''<section class="reader-panel"><div><h2>Tauchdaten im Sichtfeld</h2><p>Daïve entwickelt einen Tauchcomputer, der an einer Standard-Tauchmaske befestigt wird. Das Head-up-Display zeigt Tiefe, Zeit, Aufstiegsgeschwindigkeit, Dekompressionswarnungen und Alarme an.</p></div>
    <div><h3>Preis auf Anfrage</h3>{inquiry("Daïve Head-up-Display")}<a class="dive-text-link" href="tauch-shop--computer.html">Tauchcomputer vergleichen</a></div></section>
    <section class="album"><h2>Ansichten des Displays</h2>{image_gallery(photos,"Daïve Head-up-Display")}</section>'''


def legal(page):
    parts = {}
    for b in page["blocks"][1:]:
        if "section" in b:
            title = b["section"]
            parts[title] = []
        tag = "h3" if b["type"] == "heading" else "p"
        parts[title].append(f'<{tag}>{escape(b["text"])}</{tag}>')
    links = ''.join(f'<a href="#{slugify(t)}">{escape(t)}</a>' for t in parts)
    text = ''.join(f'<section id="{slugify(t)}"><h2>{escape(t)}</h2>{"".join(blocks)}</section>' for t, blocks in parts.items())
    return f'<div class="legal-layout"><nav aria-label="Abschnitte">{links}</nav><div class="legal-text">{text}</div></div>'

"""Check the built site and ensure every internal destination is reachable."""
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote, parse_qs
import re

DIST = Path(__file__).resolve().parent / "dist"
CNAME = Path(__file__).resolve().parent / "CNAME"
OWN_HOST = CNAME.read_text().strip() if CNAME.exists() else None


class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.urls = []
        self.main_count = 0
        self.headings = 0
        self.viewport = False

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'main':
            self.main_count += 1
        if tag == 'h1':
            self.headings += 1
        if tag == 'meta' and values.get('name') == 'viewport':
            self.viewport = 'width=device-width' in values.get('content', '')
        if tag == 'img':
            assert 'alt' in values, values
        if 'id' in values:
            assert values['id'] not in self.ids, 'Duplicate ID ' + values['id']
            self.ids.add(values['id'])
        for key in ('src', 'poster', 'href', 'action'):
            if values.get(key):
                self.urls.append(values[key])
        if values.get('srcset'):
            self.urls.extend(part.split()[0] for part in values['srcset'].split(','))
        if tag == 'meta' and values.get('property') in ('og:url', 'og:image'):
            self.urls.append(values['content'])


def check():
    docs = {}
    edges = defaultdict(set)
    for path in DIST.rglob('*.html'):
        doc = Document()
        doc.feed(path.read_text())
        assert doc.main_count == 1 and doc.headings == 1 and doc.viewport, path
        docs[path] = doc
    for path, doc in docs.items():
        for url in doc.urls:
            parts = urlsplit(url)
            if parts.scheme in ('tel', 'mailto'):
                continue
            if OWN_HOST and parts.hostname == OWN_HOST:
                assert parts.scheme == 'https', (path, url)
                target = DIST / (unquote(parts.path).lstrip('/') or 'index.html')
                assert target.is_file(), (path, url)
                continue
            if parts.scheme or parts.netloc:
                allowed = parts.hostname == 'wa.me' or (parts.hostname == 'www.google.com' and parts.path.startswith('/maps/place/'))
                assert parts.scheme == 'https' and allowed, (path, url)
                continue
            target = (path.parent / unquote(parts.path)).resolve() if parts.path else path
            assert target.is_relative_to(DIST) and target.is_file(), (path, url)
            if target.name == 'anfrage.html':
                parameters = parse_qs(parts.query)
                if 'kurs' in parameters:
                    assert parameters.get('thema') in (['Tauchkurs'], ['Erste Hilfe']), (path, url)
                if 'produkt' in parameters:
                    assert parameters.get('thema') == ['Ausrüstung und Verleih'], (path, url)
            if target in docs:
                edges[path].add(target)
                assert not parts.fragment or unquote(parts.fragment) in docs[target].ids, (path, url)
    for css in DIST.rglob('*.css'):
        for value in re.findall(r"url\(([^)]+)\)", css.read_text()):
            resource = (css.parent / value.strip("'\" ")).resolve()
            assert resource.is_relative_to(DIST) and resource.is_file(), (css, value)
    seen = set()
    todo = [DIST / 'index.html']
    while todo:
        current = todo.pop()
        if current not in seen:
            seen.add(current)
            todo.extend(edges[current] - seen)
    reachable = set(docs) - {DIST / "404.html"}  # GitHub Pages serves it for missing paths
    assert seen == reachable, reachable - seen
    if OWN_HOST:
        sitemap = (DIST / 'sitemap.xml').read_text()
        listed = {DIST / (urlsplit(u).path.lstrip('/') or 'index.html') for u in re.findall(r'<loc>([^<]+)</loc>', sitemap)}
        # Product copies listed in a second category point their canonical at the main page.
        copies = {d for d in reachable if (m := re.search(r'rel="canonical" href="([^"]+)"', d.read_text())) and DIST / (urlsplit(m[1]).path.lstrip('/') or 'index.html') != d}
        assert listed == reachable - copies, (reachable - copies) ^ listed
    print(f'{len(docs)} pages reachable. Local links, media, anchors and form destinations passed.')


if __name__ == '__main__':
    check()

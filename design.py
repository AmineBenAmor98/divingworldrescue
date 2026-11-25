"""Shared illustrated category icons and semantic navigation treatments.

Artwork remains local, decorative and paired with visible text. Functional
controls retain simple SVGs; WhatsApp uses the unmodified Simple Icons mark.
"""
from pathlib import Path
from html import unescape
from urllib.parse import urlsplit
import re

UI_FILES = {'mask': 'goggles', 'people': 'users', 'aid': 'first-aid-kit', 'equipment': 'backpack', 'rental': 'timer', 'school': 'graduation-cap', 'book': 'book-open', 'compass': 'compass', 'calendar': 'calendar-blank', 'watch': 'watch', 'regulator': 'gauge', 'suit': 't-shirt', 'bag': 'suitcase-rolling', 'tools': 'wrench', 'shirt': 't-shirt', 'gem': 'diamond', 'tag': 'tag', 'box': 'package', 'chat': 'chat-circle-text', 'mail': 'envelope-simple', 'phone': 'phone', 'camera': 'camera', 'certificate': 'certificate', 'star': 'star', 'lifering': 'lifebuoy', 'search': 'magnifying-glass', 'legal': 'scales', 'pin': 'map-pin'}
ICON_ROOT = Path(__file__).parent / "public/assets/ui"
UI_SVGS = {key: re.sub(r"^<svg\b[^>]*>|</svg>$", "", (ICON_ROOT / (name + ".svg")).read_text().strip()) for key, name in UI_FILES.items()}
ARTWORK = {
    'mask':'diving', 'people':'inclusive', 'aid':'first-aid',
    'equipment':'equipment', 'rental':'rental', 'school':'school',
    'book':'school', 'compass':'trips', 'calendar':'trips',
    'watch':'computer', 'regulator':'regulator', 'suit':'clothing',
    'shirt':'clothing', 'bag':'bags', 'tools':'accessories',
    'gem':'jewelry', 'tag':'offers', 'box':'preowned',
    'certificate':'qualification', 'star':'reviews', 'legal':'legal',
    'lifering':'rescue',
}

WA_PATH = re.search(r'<path d="([^"]+)"', (Path(__file__).parent/'public/assets/whatsapp.svg').read_text())[1]


def icon(name, prefix=''):
    if name == 'whatsapp':
        return f'<svg class="ui-icon brand-whatsapp" viewBox="0 0 24 24" width="24" height="24" aria-hidden="true" focusable="false" fill="currentColor"><path d="{WA_PATH}"/></svg>'
    if name in ARTWORK:
        return f'<img class="ui-icon illustrated-ui icon-{name}" src="{prefix}assets/illustrated-icons/{ARTWORK[name]}.webp" width="32" height="32" alt="" aria-hidden="true">'
    return f'<svg class="ui-icon phosphor-icon icon-{name}" viewBox="0 0 256 256" width="24" height="24" aria-hidden="true" focusable="false" fill="currentColor" stroke="none">{UI_SVGS[name]}</svg>'


def route_visual(href):
    if href in {'#angebote', '#ausruestung', '#tauchschein', '#ausprobieren', '#weiterlernen'}:
        return {'#angebote':('book','ocean'),'#ausruestung':('equipment','sand'),'#tauchschein':('certificate','ocean'),'#ausprobieren':('mask','ocean'),'#weiterlernen':('book','ocean')}[href]
    slug = urlsplit(unescape(href)).path.rsplit('/',1)[-1].removesuffix('.html')
    if '#erste-hilfe' in href: return 'aid','aid'
    if 'anfrage' in slug: return 'chat','ocean'
    if 'schmuck' in slug: return 'gem','sand'
    if 'masken' in slug: return 'mask','ocean'
    if 'computer' in slug: return 'watch','sand'
    if 'atemregler' in slug: return 'regulator','sand'
    if 'jacket' in slug: return 'equipment','sand'
    if 'neopren' in slug: return 'suit','sand'
    if 'bekleidung' in slug: return 'shirt','sand'
    if 'koffer' in slug: return 'bag','sand'
    if 'material' in slug: return 'aid','aid'
    if 'zubehoer' in slug: return 'tools','sand'
    if 'sonderangebote' in slug: return 'tag','sand'
    if 'auftrag' in slug: return 'box','sand'
    if 'verleih' in slug: return 'rental','sand'
    if 'hud' == slug: return 'mask','sand'
    if 'tauch-shop' == slug: return 'equipment','sand'
    if 'glueckwuensche' in slug: return 'certificate','school'
    if 'frti' in slug: return 'aid','aid'
    if 'preis' in slug: return 'tag','ocean'
    if 'termine' in slug: return 'calendar','ocean'
    if 'bilder' in slug: return 'compass','ocean'
    if 'suchen' in slug: return 'lifering','school'
    if 'gaestebuch' in slug: return 'star','school'
    if 'impressum' in slug: return 'legal','school'
    if 'infos' == slug: return 'school','school'
    if 'scubility' in href: return 'people','sage'
    if 'kurse' in slug: return 'mask','ocean'
    return None,None


def badge(name, tone, extra='', prefix=None):
    if prefix is not None and name in ARTWORK:
        src = prefix + 'assets/illustrated-icons/' + ARTWORK[name] + '.webp'
        return f'<span class="art-badge {extra}" aria-hidden="true"><img class="category-illustration" src="{src}" width="112" height="112" alt=""></span>'
    return f'<span class="ui-badge tone-{tone} {extra}" aria-hidden="true">{icon(name)}</span>'


def classes(attrs, extra):
    if 'class="' in attrs:
        return re.sub(r'class="([^"]*)"', lambda m:f'class="{m[1]} {extra}"', attrs,count=1)
    return attrs + f' class="{extra}"'


def decorate(html, path):
    prefix = "" if path == "index.html" else "../"
    # Remove decorative arrows; icons supply a consistent visual language.
    html=re.sub(r'<(span|i)\b[^>]*aria-hidden="true"[^>]*>[→↗↓↑]</\1>', '', html)
    html=html.replace(' ↗','').replace(' →','').replace(' ↓','')
    # Footer section labels remain quiet; only their group headings get icons.
    labels={'Tauchen':('mask','ocean'),'Erste Hilfe':('aid','aid'),'Ausrüstung':('equipment','sand'),'Infos &amp; Kontakt':('school','school')}
    def footer_group(m):
        key=m[1]
        if key not in labels:return m[0]
        name,tone=labels[key]
        return f'<summary><span class="summary-label tone-{tone}">{icon(name,prefix)}<span>{key}</span></span></summary>'
    html=re.sub(r'<summary>([^<]+)</summary>',footer_group,html)
    # Stash breadcrumb and footer-group links so they do not accumulate icons.
    protected=[]
    def stash(m):
        protected.append(m[0]);return f'<!--design-protected-{len(protected)-1}-->'
    html=re.sub(r'<nav\b[^>]*class="(?:crumb|item-crumb|footer-groups)[^"]*"[^>]*>.*?</nav>',stash,html,flags=re.S)
    def link(m):
        attrs,body=m[1],m[2]
        # Editorial rows already carry one leading illustration for the topic.
        if 'editorial-link' in attrs:
            return m[0]
        href_match=re.search(r'href="([^"]+)"',attrs)
        if not href_match:return m[0]
        href=unescape(href_match[1])
        name,tone=route_visual(href)
        if href.startswith('https://wa.me/'):
            name,tone='whatsapp','sage'
            body=re.sub(r'<svg\b.*?</svg>','',body,flags=re.S).strip()
            attrs=classes(attrs,'whatsapp-link')
        elif href.startswith('mailto:') or href.startswith('tel:'):
            name='mail' if href.startswith('mailto:') else 'phone'
            tone='ocean'
            body=re.sub(r'<svg\b.*?</svg>','',body,flags=re.S).strip()
        if not name or '<img' in body or '<svg' in body:return f'<a{attrs}>{body}</a>'
        if body.lstrip().startswith('<strong>') and '<span>' in body:
            # Homepage goal cards and the three shopping service cards.
            if 'pages/' in href:
                return f'<a{classes(attrs,"visual-card tone-"+tone)}>{badge(name,tone,prefix=prefix)}<span class="visual-card-copy">{body}</span></a>'
        if '<' in body and not (href.startswith(('mailto:','tel:','https://wa.me/')) or 'path-action' in attrs or 'plain' in attrs):return m[0]
        return f'<a{classes(attrs,"icon-link")}>{icon(name,prefix)}{body}</a>'
    html=re.sub(r'<a\b([^>]*)>(.*?)</a>',link,html,flags=re.S)
    # Photograph tiles already communicate their category visually. Keep their
    # captions quiet; illustrated icons are used on the adjacent category chips.
    # Buttons retain their actual form behaviour and accessible text.
    def form_button(m):
        name='whatsapp' if 'value="chat"' in m[1] else ('mail' if 'value="mail"' in m[1] else None)
        return f'<button{classes(m[1],"icon-link")}>{icon(name,prefix)}{m[2]}</button>' if name else m[0]
    html=re.sub(r'<button\b([^>]*)>(.*?)</button>',form_button,html,flags=re.S)
    # Add one coloured area marker to each inner-page cover.
    name,tone=route_visual(path)
    photo_course_pages = {'pages/tauchen-lernen-kurse.html', 'pages/frti-kurse.html'}
    if path!='index.html' and path not in photo_course_pages and not path.rsplit('/',1)[-1].startswith('produkt-') and name in ARTWORK:
        html=re.sub(r'<h1\b',badge(name,tone,'page-mark',prefix=prefix)+'<h1',html,count=1)
    for i,value in enumerate(protected):html=html.replace(f'<!--design-protected-{i}-->',value)
    return html

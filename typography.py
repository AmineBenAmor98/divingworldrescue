"""Structure imported copy without changing the supplied facts or wording."""
from html import escape
import re


def paragraphs(text, limit=430):
    """Break long source paragraphs at sentences, keeping abbreviations intact."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return ""
    # Sentence boundaries must be followed by a capital letter. Protect the
    # abbreviations present in the German catalogue and legal source.
    protected = re.sub(r"\b(?:z\.B\.|z\. B\.|bzw\.|gem\.|etc\.|Art\.|Abs\.|Nr\.|sog\.|ca\.|inkl\.|zzgl\.|i\.V\.m\.|D\.h\.|d\.h\.|entspr\.)", lambda m: m[0].replace('.', '\u2024'), text)
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-ZÄÖÜ„»])', protected)
    chunks, current = [], ""
    for sentence in sentences:
        sentence = sentence.replace('\u2024', '.')
        if current and len(current) + len(sentence) > limit:
            chunks.append(current)
            current = ""
        current = (current + " " + sentence).strip()
    if current:
        chunks.append(current)
    return ''.join(f'<p>{escape(chunk)}</p>' for chunk in chunks)


def product_copy(texts):
    """Turn source line fragments and feature runs into readable paragraphs/lists."""
    cleaned = []
    seen = set()
    for i, text in enumerate(texts):
        text = re.sub(r'\s+', ' ', text).strip()
        if not text or text in {'Wir freuen uns über Ihre Nachricht.', '⚠ Wieder zu erhalten !!'} or 'Nur für die besten Taucher' in text:
            continue
        if i == 0:
            # Product headings and their price already appear above the copy.
            # One imported heading also contains the start of its description.
            match = re.search(r'\d[\d.,-]*\s*€\s*', text)
            if match:
                remainder = text[match.end():].strip()
                if len(remainder) > 160 and re.match(r'(Der|Die|Das|Ein|Eine)\b', remainder):
                    text = remainder
                else:
                    continue
            elif len(text) < 150:
                continue
        if re.fullmatch(r'[\d., –-]+€', text):
            continue
        key = text.casefold()
        if key in seen:
            continue
        seen.add(key)
        if cleaned and not text.startswith(('•', '●', '–')) and (cleaned[-1].endswith(',') or re.match(r'^[a-zäöü]', text)):
            cleaned[-1] += ' ' + text
        else:
            cleaned.append(text)
    out, items = [], []
    def flush():
        if items:
            out.append('<ul>' + ''.join(f'<li>{escape(t)}</li>' for t in items) + '</ul>')
            items.clear()
    for text in cleaned:
        if text.casefold() in {'merkmale:', 'eigenschaften:', 'verschiedene farben:', 'planungsvorbereitung und protokoll:'}:
            flush()
            out.append(f'<h3>{escape(text.rstrip(":"))}</h3>')
        elif re.search(r'[•●]', text):
            items.extend(t.strip() for t in re.split(r'[•●]', text) if t.strip())
        elif len(text) < 180:
            items.append(text)
        else:
            flush()
            out.append(paragraphs(text))
    flush()
    return ''.join(out)

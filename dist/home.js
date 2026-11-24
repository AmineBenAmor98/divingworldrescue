
const menu = document.querySelector('.menu');
const drawer = document.querySelector('.drawer');
function setMenu(open) {
  drawer.hidden = !open;
  menu.setAttribute('aria-expanded', String(open));
  menu.setAttribute('aria-label', open ? 'Menü schließen' : 'Menü öffnen');
}
menu.addEventListener('click', () => setMenu(drawer.hidden));
drawer.addEventListener('click', event => { if (event.target.closest('a')) setMenu(false); });
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && !drawer.hidden) { setMenu(false); menu.focus(); }
});
matchMedia('(min-width:701px)').addEventListener('change', () => setMenu(false));

function setupFilm() {
  const film = document.querySelector('#dive');
  if (!film) return;
  const legacySections = {
    '#team': 'infos.html#team',
    '#kontakt': 'infos.html#kontakt',
    '#kurse': 'kurse.html',
  };
  if (Object.hasOwn(legacySections, location.hash)) {
    const courses = document.querySelector('.nav a');
    location.replace(new URL(legacySections[location.hash], courses.href));
    return;
  }
  const playback = document.querySelector('.playback');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  film.muted = true;
  playback.hidden = false;
  function reflectPlayback() {
    playback.classList.toggle('paused', film.paused);
    playback.setAttribute('aria-label', film.paused ? 'Animation abspielen' : 'Animation pausieren');
  }
  function startFilm() { film.play().catch(reflectPlayback); }
  film.addEventListener('play', reflectPlayback);
  film.addEventListener('pause', reflectPlayback);
  playback.addEventListener('click', () => { if (film.paused) startFilm(); else film.pause(); });
  reduced.addEventListener('change', event => { if (event.matches) film.pause(); });
  if (!reduced.matches) startFilm();
}
setupFilm();

function setupProductSorting() {
  const label = document.querySelector('.sort-order');
  if (!label) return;
  const select = label.querySelector('select');
  const names = new Intl.Collator('de');
  function sortGroups() {
    for (const section of document.querySelectorAll('.stock-family')) {
      const rows = [...section.querySelectorAll('.stock-row')];
      rows.sort((a, b) => {
        const byName = names.compare(a.dataset.name, b.dataset.name);
        if (select.value === 'name') return byName;
        const first = a.dataset.cents;
        const second = b.dataset.cents;
        if (!first || !second) return Number(!first) - Number(!second) || byName;
        const delta = Number(first) - Number(second);
        return (select.value === 'asc' ? delta : -delta) || byName;
      });
      section.append(...rows);
    }
  }
  select.addEventListener('change', sortGroups);
  sortGroups();
  label.hidden = false;
}
setupProductSorting();

function setDisclosureLayout(query, selector) {
  const layout = matchMedia(query);
  function update() {
    document.querySelectorAll(selector).forEach(details => { details.open = layout.matches; });
  }
  update();
  layout.addEventListener('change', update);
}
setDisclosureLayout('(min-width:701px)', '.footer-groups details');
setDisclosureLayout('(min-width:721px)', '.page-links details');
document.querySelector('.mast').classList.add('menu-ready');

setDisclosureLayout('(min-width:851px)', '.stock-groups');
const stockGroups = document.querySelector('.stock-groups');
if (stockGroups) {
  stockGroups.addEventListener('click', event => {
    if (event.target.closest('a') && matchMedia('(max-width:850px)').matches) {
      stockGroups.open = false;
      const section = document.querySelector(event.target.closest('a').hash);
      section.tabIndex = -1;
      section.focus({ preventScroll: true });
    }
  });
}

function searchableText(value) {
  return value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('de').replace(/ß/g, 'ss');
}

function setupShopSearch() {
  const panel = document.querySelector('.shop-search');
  if (!panel) return;
  const items = JSON.parse(document.querySelector('#shop-index').textContent);
  const query = panel.querySelector('input');
  const clear = panel.querySelector('.clear-search');
  const results = panel.querySelector('.shop-results');
  const status = panel.querySelector('.search-status');
  const browse = document.querySelector('.shop-browse');
  function update() {
    const words = searchableText(query.value.trim()).split(/\s+/).filter(Boolean);
    clear.hidden = words.length === 0;
    results.replaceChildren();
    results.hidden = words.length === 0;
    browse.hidden = words.length !== 0;
    status.textContent = '';
    if (!words.length) return;
    const matches = items.filter(item => words.every(word => searchableText([item.name, item.summary, item.category, item.terms].join(' ')).includes(word)));
    status.textContent = matches.length === 1 ? '1 passender Artikel' : matches.length + ' passende Artikel';
    if (!matches.length) {
      const empty = document.createElement('p');
      empty.textContent = 'Kein passender Artikel gefunden. Versuche einen anderen Begriff oder entdecke die Kategorien.';
      results.append(empty);
      return;
    }
    for (const item of matches) {
      const link = document.createElement('a');
      link.className = 'shop-result';
      link.href = item.url;
      const img = document.createElement('img');
      img.src = item.image;
      img.alt = '';
      img.loading = 'lazy';
      const copy = document.createElement('span');
      const category = document.createElement('small');
      category.textContent = item.category;
      const name = document.createElement('strong');
      name.textContent = item.name;
      const summary = document.createElement('span');
      summary.textContent = item.summary;
      const price = document.createElement('b');
      price.textContent = item.price;
      copy.append(category, name, summary);
      link.append(img, copy, price);
      results.append(link);
    }
  }
  query.addEventListener('input', update);
  clear.addEventListener('click', () => { query.value = ''; update(); query.focus(); });
  document.querySelector('a[href="#ausruestung"]').addEventListener('click', () => { query.value = ''; update(); });
  panel.hidden = false;
}
setupShopSearch();

function setupCategorySearch() {
  const panel = document.querySelector('.category-search');
  if (!panel) return;
  const query = panel.querySelector('input');
  const status = panel.querySelector('[role="status"]');
  const groups = [...document.querySelectorAll('.stock-family')];
  function update() {
    const words = searchableText(query.value.trim()).split(/\s+/).filter(Boolean);
    let count = 0;
    for (const group of groups) {
      let shown = 0;
      for (const row of group.querySelectorAll('.stock-row')) {
        row.hidden = !words.every(word => searchableText(row.dataset.search).includes(word));
        if (!row.hidden) shown++;
      }
      group.hidden = shown === 0;
      count += shown;
      const link = document.querySelector('.stock-groups a[href="#' + group.id + '"]');
      if (link) link.hidden = group.hidden;
    }
    status.textContent = words.length ? count + ' passende Artikel' : '';
  }
  query.addEventListener('input', update);
  panel.hidden = false;
}
setupCategorySearch();

function setupGalleryViewer() {
  if (typeof HTMLDialogElement === 'undefined' || !HTMLDialogElement.prototype.showModal) return;

  const albums = [...document.querySelectorAll('.album')].map(album =>
    [...album.querySelectorAll('.album-grid figure > a')]
  ).filter(photos => photos.length);
  if (!albums.length) return;

  const viewer = document.createElement('dialog');
  viewer.className = 'gallery-viewer';
  viewer.setAttribute('aria-label', 'Fotoansicht');
  viewer.innerHTML = `
    <div class="gallery-viewer-panel">
      <div class="gallery-viewer-top">
        <span class="gallery-viewer-count" aria-live="polite"></span>
        <button type="button" class="gallery-viewer-close" autofocus>Schließen <span aria-hidden="true">×</span></button>
      </div>
      <figure>
        <div class="gallery-viewer-image"><img alt=""><p hidden>Das Bild konnte nicht geladen werden.</p></div>
        <figcaption hidden></figcaption>
      </figure>
      <nav class="gallery-viewer-controls" aria-label="Fotos durchblättern">
        <button type="button" data-direction="-1"><span aria-hidden="true">‹</span> Zurück</button>
        <button type="button" data-direction="1">Weiter <span aria-hidden="true">›</span></button>
      </nav>
    </div>`;
  document.body.append(viewer);

  const image = viewer.querySelector('img');
  const error = viewer.querySelector('.gallery-viewer-image p');
  const caption = viewer.querySelector('figcaption');
  const count = viewer.querySelector('.gallery-viewer-count');
  const close = viewer.querySelector('.gallery-viewer-close');
  const controls = viewer.querySelector('.gallery-viewer-controls');
  let activeAlbum = [];
  let current = 0;
  let opener;

  function showPhoto(index) {
    current = (index + activeAlbum.length) % activeAlbum.length;
    const link = activeAlbum[current];
    const title = link.closest('figure').querySelector('figcaption')?.textContent.trim() || '';
    error.hidden = true;
    image.hidden = false;
    image.alt = link.querySelector('img').alt;
    image.src = link.href;
    caption.textContent = title;
    caption.hidden = !title;
    count.textContent = `Foto ${current + 1} von ${activeAlbum.length}`;
    controls.hidden = activeAlbum.length < 2;
  }

  for (const photos of albums) {
    photos.forEach((link, index) => {
      link.setAttribute('aria-haspopup', 'dialog');
      link.addEventListener('click', event => {
        if (event.defaultPrevented || event.button !== 0 || event.metaKey ||
            event.ctrlKey || event.shiftKey || event.altKey) return;
        event.preventDefault();
        opener = link;
        activeAlbum = photos;
        showPhoto(index);
        viewer.showModal();
      });
    });
  }

  image.addEventListener('error', () => {
    if (!viewer.open) return;
    image.hidden = true;
    error.hidden = false;
  });
  close.addEventListener('click', () => viewer.close());
  viewer.addEventListener('click', event => {
    if (event.target === viewer) viewer.close();
  });
  viewer.addEventListener('close', () => {
    image.removeAttribute('src');
    opener?.focus({ preventScroll: true });
  });
  for (const button of controls.querySelectorAll('button')) {
    button.addEventListener('click', () => showPhoto(current + Number(button.dataset.direction)));
  }
  viewer.addEventListener('keydown', event => {
    if (activeAlbum.length < 2 || !['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
    event.preventDefault();
    showPhoto(current + (event.key === 'ArrowLeft' ? -1 : 1));
  });
}

setupGalleryViewer();

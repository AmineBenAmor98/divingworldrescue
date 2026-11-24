const form = document.querySelector('#inquiry');
const topic = form.querySelector('#topic');
const message = form.querySelector('#message');
const params = new URLSearchParams(location.search);
const selected = params.get('thema');
if ([...topic.options].some(option => option.value === selected)) topic.value = selected;
const product = params.get('produkt');
if (product && selected === 'Ausrüstung und Verleih') {
  message.value = 'Hallo, ich interessiere mich für folgenden Artikel: ' + product.slice(0, 160) + '. Ist er verfügbar?';
}
const course = params.get('kurs');
if (course && ['Tauchkurs', 'Erste Hilfe'].includes(selected)) {
  message.value = 'Hallo, ich interessiere mich für den Kurs ' + course.slice(0, 100) + '. Wann ist ein Termin möglich?';
}
form.querySelector('#mail-button').hidden = false;
form.addEventListener('submit', event => {
  event.preventDefault();
  if (!message.value.trim()) {
    message.setCustomValidity('Bitte gib eine Nachricht ein.');
    message.reportValidity();
    return;
  }
  const body = 'Anfrage · ' + topic.value + '\n\n' + message.value.trim();
  const email = 'mailto:dive-world@mail.de?subject=' + encodeURIComponent('Anfrage · ' + topic.value) + '&body=';
  const url = event.submitter?.value === 'mail' ? email : 'https://wa.me/4917685639763?text=';
  location.href = url + encodeURIComponent(body);
});
message.addEventListener('input', () => message.setCustomValidity(''));

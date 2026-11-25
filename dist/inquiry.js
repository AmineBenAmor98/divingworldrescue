const inquiryTopics = {
  'Tauchkurs': { interest: 'Kurs', placeholder: 'z. B. Schnuppertauchen oder Open Water Diver', period: 'Wunschzeitraum' },
  'Scubility': { interest: 'Kurs', placeholder: 'Scubility Diving oder Dive Buddy', period: 'Wunschzeitraum' },
  'Erste Hilfe': { interest: 'Kurs', placeholder: 'z. B. Erste Hilfe für Kinder', period: 'Wunschzeitraum' },
  'Ausrüstung kaufen': { interest: 'Artikel', placeholder: 'Produkt oder Modell', period: null },
  'Ausrüstung leihen': { interest: 'Ausrüstung', placeholder: 'z. B. Jacket, Anzug oder ein Set', period: 'Mietzeitraum' },
  'Termine und Reisen': { interest: 'Ausflug oder Tauchplatz', placeholder: 'Wohin möchtest du mitkommen?', period: 'Wunschzeitraum' },
};

function formatInquiry({ topic, interest, period, message }) {
  const fields = inquiryTopics[topic];
  const lines = ['Anfrage · ' + topic];
  if (fields && interest.trim()) lines.push(fields.interest + ': ' + interest.trim());
  if (fields?.period && period.trim()) lines.push(fields.period + ': ' + period.trim());
  return lines.join('\n') + '\n\n' + message.trim();
}

function inquiryURL(channel, values) {
  const body = encodeURIComponent(formatInquiry(values));
  return channel === 'mail'
    ? 'mailto:dive-world@mail.de?subject=' + encodeURIComponent('Anfrage · ' + values.topic) + '&body=' + body
    : 'https://wa.me/4917685639763?text=' + body;
}

const form = document.querySelector('#inquiry');
if (form) {
  const topic = form.querySelector('#topic');
  const interest = form.querySelector('#interest');
  const period = form.querySelector('#period');
  const message = form.querySelector('#message');
  const context = form.querySelector('#request-context');
  const periodField = form.querySelector('#period-field');

  function updateFields() {
    const fields = inquiryTopics[topic.value];
    context.hidden = !fields;
    interest.disabled = !fields;
    period.disabled = !fields?.period;
    periodField.hidden = !fields?.period;
    context.classList.toggle('single-field', !fields?.period);
    if (fields) {
      form.querySelector('#interest-label').textContent = fields.interest;
      interest.placeholder = fields.placeholder;
      form.querySelector('#period-label').textContent = fields.period || 'Wunschzeitraum';
      period.placeholder = topic.value === 'Ausrüstung leihen' ? 'z. B. 12.–14. Juni' : 'z. B. im Juni oder am Wochenende';
    }
  }

  const params = new URLSearchParams(location.search);
  const product = params.get('produkt');
  const course = params.get('kurs');
  const destination = params.get('ziel');
  let selected = params.get('thema');
  // Preserve catalogue and rental links after separating the two enquiry topics.
  if (selected === 'Ausrüstung und Verleih') selected = product ? 'Ausrüstung kaufen' : 'Ausrüstung leihen';
  if ([...topic.options].some(option => option.value === selected)) topic.value = selected;
  if (product && selected === 'Ausrüstung kaufen') {
    interest.value = product.slice(0, 160);
    message.value = 'Hallo, ich interessiere mich für diesen Artikel. Ist er verfügbar?';
  }
  if (course && ['Tauchkurs', 'Erste Hilfe'].includes(selected)) {
    interest.value = course.slice(0, 160);
    message.value = 'Hallo, ich interessiere mich für diesen Kurs. Wann ist ein Termin möglich?';
  }
  if (destination && selected === 'Termine und Reisen') {
    interest.value = destination.slice(0, 160);
    message.value = 'Hallo, ich möchte beim nächsten Termin mitkommen. Wann geht es wieder los?';
  }
  updateFields();
  topic.addEventListener('change', updateFields);
  form.querySelector('#mail-button').hidden = false;
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (!message.value.trim()) {
      message.setCustomValidity('Bitte gib eine Nachricht ein.');
      message.reportValidity();
      return;
    }
    location.href = inquiryURL(event.submitter?.value, {
      topic: topic.value, interest: interest.value, period: period.value, message: message.value,
    });
  });
  message.addEventListener('input', () => message.setCustomValidity(''));
}

(() => {
  'use strict';

  const DEADLINE = new Date('2026-09-25T00:00:00-03:00');
  const FORM_RECIPIENT = 'dai2@bombeiros.mg.gov.br';
  const BRIDGE_URL = ''; // Preencher com a URL /exec do Apps Script após implantação.
  const BRIDGE_VERSION = 'reuniao-dai2-2026-v1';
  const MESSAGE_TYPE = 'REUNIAO_DAI2_SUBMIT_RESULT';
  const startedAt = Date.now();

  const countdown = document.getElementById('countdown');
  const form = document.getElementById('meetingForm');
  const status = document.getElementById('formStatus');
  const channel = document.getElementById('channelStatus');
  const submitButton = document.getElementById('submitButton');
  const bridgeFrame = document.getElementById('bridgeFrame');

  let lastSubmissionId = '';
  let bridgePending = false;

  function setStatus(message, type = '') {
    status.textContent = message;
    status.className = 'form-status' + (type ? ' ' + type : '');
  }

  function updateCountdown() {
    const diff = DEADLINE - new Date();
    if (diff <= 0) {
      countdown.textContent = 'Prazo encerrado';
      if (submitButton) submitButton.disabled = true;
      return;
    }
    const days = Math.floor(diff / 86400000);
    const hours = Math.floor((diff % 86400000) / 3600000);
    countdown.textContent = `${days}d ${hours}h restantes`;
  }

  function updateChannelBadge() {
    if (!channel) return;
    if (BRIDGE_URL) {
      channel.textContent = 'Canal de resposta: Google Forms integrado';
      channel.classList.add('connected');
    } else {
      channel.textContent = 'Canal de resposta: envio institucional por e-mail';
      channel.classList.remove('connected');
    }
  }

  function formAnswers() {
    const answers = {};
    const fd = new FormData(form);
    fd.forEach((value, key) => {
      const v = String(value || '').trim();
      if (v) answers[key] = v;
    });
    return answers;
  }

  function answersText() {
    const answers = formAnswers();
    const blocks = Object.entries(answers).map(([key, value]) => `${key.toUpperCase()}\n${value}`);
    return [
      'REUNIÃO PRESENCIAL DAI/2 — 13/11/2026',
      'Rastreio para consolidação de pauta',
      '',
      ...blocks
    ].join('\n\n');
  }

  function makeSubmissionId() {
    if (lastSubmissionId) return lastSubmissionId;
    const random = (window.crypto && crypto.randomUUID) ? crypto.randomUUID() : Math.random().toString(36).slice(2) + Date.now().toString(36);
    lastSubmissionId = `dai2-${random}`;
    return lastSubmissionId;
  }

  async function copyAnswers(showMessage = true) {
    if (!form.reportValidity()) return false;
    const text = answersText();
    try {
      await navigator.clipboard.writeText(text);
    } catch (_) {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.setAttribute('readonly', '');
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      ta.remove();
    }
    if (showMessage) setStatus('Respostas copiadas para a área de transferência.', 'ok');
    return true;
  }

  function populateReceipt() {
    if (!form.reportValidity()) return false;
    const answers = formAnswers();
    const receiptMeta = document.getElementById('receiptMeta');
    const receiptAnswers = document.getElementById('receiptAnswers');
    const generatedAt = new Intl.DateTimeFormat('pt-BR', {dateStyle:'short', timeStyle:'short'}).format(new Date());

    receiptMeta.innerHTML = '';
    const meta = [
      ['Nome', answers['Nome completo'] || '—'],
      ['Posto/Graduação', answers['Posto/Graduação'] || '—'],
      ['Órgão', answers['Órgão Externo'] || '—'],
      ['E-mail', answers['E-mail funcional'] || '—'],
      ['Gerado em', generatedAt],
      ['Identificador local', makeSubmissionId()]
    ];
    meta.forEach(([label, value]) => {
      const div = document.createElement('div');
      const b = document.createElement('b');
      b.textContent = label;
      const span = document.createElement('span');
      span.textContent = value;
      div.append(b, span);
      receiptMeta.appendChild(div);
    });

    receiptAnswers.innerHTML = '';
    Object.entries(answers).forEach(([label, value]) => {
      const wrap = document.createElement('div');
      wrap.className = 'receipt-answer';
      const b = document.createElement('b');
      b.textContent = label;
      const p = document.createElement('p');
      p.textContent = value;
      wrap.append(b, p);
      receiptAnswers.appendChild(wrap);
    });
    return true;
  }

  function savePdf() {
    if (!populateReceipt()) return;
    document.body.classList.add('print-receipt');
    setStatus('A janela de impressão será aberta. Selecione “Salvar como PDF” para guardar sua cópia.', 'ok');
    window.print();
  }

  function submitByEmail() {
    copyAnswers(false).then(() => {
      const org = document.getElementById('orgao').value || 'Órgão externo';
      const nome = document.getElementById('nome').value.trim() || 'Assessor';
      const subject = encodeURIComponent(`Reunião DAI/2 · pauta e apresentação · ${org} · ${nome}`);
      const body = encodeURIComponent(
        'Prezados,\n\nEncaminho as informações para consolidação da pauta da reunião presencial da DAI/2 de 13/11/2026.\n\nAs respostas completas foram copiadas para a área de transferência. Cole-as abaixo desta linha antes do envio.\n\nRespeitosamente,\n' + nome
      );
      setStatus('O e-mail institucional será aberto. Cole as respostas copiadas no corpo da mensagem e envie.', 'ok');
      window.location.href = `mailto:${FORM_RECIPIENT}?subject=${subject}&body=${body}`;
    });
  }

  function submitToBridge() {
    if (!BRIDGE_URL) return submitByEmail();
    const payload = {
      version: BRIDGE_VERSION,
      submissionId: makeSubmissionId(),
      startedAt,
      submittedAt: Date.now(),
      answers: formAnswers()
    };

    const transport = document.createElement('form');
    transport.method = 'POST';
    transport.action = BRIDGE_URL;
    transport.target = 'bridgeFrame';
    transport.hidden = true;
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'payload';
    input.value = JSON.stringify(payload);
    transport.appendChild(input);
    document.body.appendChild(transport);
    bridgePending = true;
    submitButton.disabled = true;
    setStatus('Registrando resposta no Google Forms…');
    transport.submit();
    transport.remove();

    window.setTimeout(() => {
      if (!bridgePending) return;
      bridgePending = false;
      submitButton.disabled = false;
      setStatus('Não foi possível confirmar o registro automático. Suas respostas permanecem na página; use o envio institucional por e-mail.', 'error');
    }, 15000);
  }

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    if (new Date() >= DEADLINE) {
      setStatus('O prazo de resposta foi encerrado em 24/09/2026.', 'error');
      return;
    }
    if (!form.reportValidity()) return;
    submitToBridge();
  });

  window.addEventListener('message', (event) => {
    if (!BRIDGE_URL || !bridgePending) return;
    if (!/^https:\/\/script\.google(?:usercontent)?\.com$/.test(event.origin)) return;
    const data = event.data || {};
    if (data.type !== MESSAGE_TYPE) return;
    bridgePending = false;
    submitButton.disabled = false;
    if (data.ok) {
      setStatus('Resposta registrada no Google Forms. Você pode gerar uma cópia em PDF para arquivo pessoal.', 'ok');
    } else {
      setStatus(data.message || 'Não foi possível registrar a resposta no Google Forms.', 'error');
    }
  });

  document.getElementById('copyAnswers').addEventListener('click', () => copyAnswers(true));
  document.getElementById('savePdf').addEventListener('click', savePdf);
  window.addEventListener('afterprint', () => document.body.classList.remove('print-receipt'));

  document.getElementById('addCalendar').addEventListener('click', () => {
    const ics = [
      'BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//CBMMG DAI2//Reuniao DAI2 2026//PT-BR','CALSCALE:GREGORIAN','METHOD:PUBLISH',
      'BEGIN:VEVENT','UID:reuniao-dai2-20261113@bombeiros.mg.gov.br','DTSTAMP:20260910T170000Z',
      'DTSTART;TZID=America/Sao_Paulo:20261113T090000','DTEND;TZID=America/Sao_Paulo:20261113T120000',
      'SUMMARY:DAI/2 · Reunião Presencial',
      'LOCATION:Plenário do Prédio Minas - Rodovia Papa João Paulo II, 4143 - Serra Verde - Belo Horizonte/MG',
      'DESCRIPTION:Reunião presencial da DAI/2. Assessores: responder rastreio de pauta até 24/09/2026 e preparar apresentação.',
      'END:VEVENT','END:VCALENDAR'
    ].join('\r\n');
    const blob = new Blob([ics], {type:'text/calendar;charset=utf-8'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'reuniao-dai2-13-11-2026.ics';
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  });

  updateCountdown();
  updateChannelBadge();
  window.setInterval(updateCountdown, 60000);
})();

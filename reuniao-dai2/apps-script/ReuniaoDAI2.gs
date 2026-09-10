/**
 * ReuniaoDAI2.gs
 * Google Apps Script para criar o Google Forms oficial da reunião DAI/2,
 * vincular a planilha de respostas e atuar como ponte segura para a página GitHub Pages.
 *
 * Uso:
 * 1. Criar um projeto em script.google.com e colar este arquivo.
 * 2. Executar setupReuniaoDAI2() uma única vez e autorizar.
 * 3. Implantar como Aplicativo da Web: executar como proprietário; acesso: qualquer pessoa.
 * 4. Informar a URL /exec na constante BRIDGE_URL da página.
 */

const CFG = Object.freeze({
  VERSION: 'reuniao-dai2-2026-v1',
  TITLE: 'Reunião Presencial DAI/2 — Rastreio de pauta e apresentações',
  DESCRIPTION: [
    'Reunião presencial da DAI/2 — 13 de novembro de 2026, das 09h00 às 12h00.',
    'Local: Plenário do Prédio Minas, Cidade Administrativa de Minas Gerais.',
    'Prazo para resposta: 24 de setembro de 2026.',
    'Cada assessor militar terá momento de apresentação durante o encontro.'
  ].join('\n'),
  DEADLINE: '2026-09-25T00:00:00-03:00',
  PROPERTY_FORM_ID: 'REUNIAO_DAI2_FORM_ID',
  PROPERTY_SHEET_ID: 'REUNIAO_DAI2_SHEET_ID',
  MESSAGE_TYPE: 'REUNIAO_DAI2_SUBMIT_RESULT',
  CACHE_TTL_SECONDS: 21600,
  MIN_FILL_MS: 1500
});

function setupReuniaoDAI2() {
  const props = PropertiesService.getScriptProperties();
  let formId = props.getProperty(CFG.PROPERTY_FORM_ID);
  let sheetId = props.getProperty(CFG.PROPERTY_SHEET_ID);
  let form;

  if (formId) {
    form = FormApp.openById(formId);
  } else {
    form = FormApp.create(CFG.TITLE);
    form.setDescription(CFG.DESCRIPTION);
    form.setConfirmationMessage('Resposta registrada. As informações serão consolidadas pela DAI/2 para a reunião de 13/11/2026.');
    form.setProgressBar(true);
    form.setShuffleQuestions(false);
    form.setAcceptingResponses(true);

    addQuestions_(form);
    formId = form.getId();
    props.setProperty(CFG.PROPERTY_FORM_ID, formId);
  }

  if (!sheetId) {
    const ss = SpreadsheetApp.create('Reunião DAI/2 — Pautas e apresentações — 2026');
    sheetId = ss.getId();
    props.setProperty(CFG.PROPERTY_SHEET_ID, sheetId);
    form.setDestination(FormApp.DestinationType.SPREADSHEET, sheetId);
  }

  scheduleDeadlineClosure_();

  const result = {
    formId: formId,
    formUrl: form.getPublishedUrl(),
    editUrl: form.getEditUrl(),
    spreadsheetUrl: SpreadsheetApp.openById(sheetId).getUrl(),
    deadline: CFG.DEADLINE
  };
  console.log(JSON.stringify(result));
  return result;
}

function addQuestions_(form) {
  form.addTextItem().setTitle('Nome completo').setRequired(true);
  form.addTextItem().setTitle('E-mail funcional').setRequired(true);
  form.addListItem().setTitle('Posto/Graduação').setChoiceValues([
    'Cel','Ten Cel','Maj','Cap','1º Ten','2º Ten','Subten','1º Sgt','2º Sgt','3º Sgt','Cb','Sd'
  ]).setRequired(true);
  form.addListItem().setTitle('Órgão Externo').setChoiceValues([
    'AFAS','ALMG','CEDEC','CTPM RMBH','Fundação SALVAR','GMG','Intendência CAMG','MPMG','OGE',
    'Secretaria Parlamentar','SEE','SEJUSP','SEMAD / IEF','SENASP / MJSP','SES','TJMG','TJMMG','Coordenação DAI/2'
  ]).setRequired(true);
  form.addListItem().setTitle('Situação prevista em 13/11').setChoiceValues([
    'Presença prevista','Em férias — dispensado, mas convidado','Licenciado — dispensado'
  ]).setRequired(true);
  form.addTextItem().setTitle('Link de material de apoio');

  form.addSectionHeaderItem().setTitle('Sua apresentação');
  form.addParagraphTextItem()
    .setTitle('Assuntos da apresentação')
    .setHelpText('Informe os pontos essenciais que os participantes precisam conhecer sobre as ações da sua assessoria.')
    .setRequired(true);

  form.addSectionHeaderItem().setTitle('Necessidades, desafios e alinhamentos');
  form.addParagraphTextItem().setTitle('Assuntos relevantes para a pauta');
  form.addParagraphTextItem().setTitle('Principais necessidades');
  form.addParagraphTextItem().setTitle('Principais desafios');
  form.addParagraphTextItem().setTitle('Pontos de alinhamento CBMMG x órgão externo');
  form.addParagraphTextItem().setTitle('Riscos oportunidades projetos boas práticas ou decisões');
  form.addParagraphTextItem().setTitle('Outras informações ou pautas');
}

function doGet() {
  try {
    const form = getForm_();
    return bridgeHtml_({
      ok: true,
      health: true,
      version: CFG.VERSION,
      formUrl: form.getPublishedUrl(),
      acceptingResponses: form.isAcceptingResponses(),
      deadline: CFG.DEADLINE
    });
  } catch (err) {
    return bridgeHtml_({ok:false, health:false, message:safeError_(err)});
  }
}

function doPost(e) {
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(10000)) return bridgeHtml_({ok:false,message:'Canal ocupado. Tente novamente em instantes.'});

  try {
    if (new Date() >= new Date(CFG.DEADLINE)) {
      closeForm_();
      throw new Error('Prazo de resposta encerrado.');
    }

    const raw = e && e.parameter ? e.parameter.payload : '';
    if (!raw) throw new Error('Payload ausente.');
    const payload = JSON.parse(raw);
    validateEnvelope_(payload);

    const cache = CacheService.getScriptCache();
    const key = 'reuniao-dai2:' + payload.submissionId;
    if (cache.get(key)) return bridgeHtml_({ok:true,duplicate:true,submissionId:payload.submissionId});

    const form = getForm_();
    if (!form.isAcceptingResponses()) throw new Error('Formulário encerrado.');

    const items = answerableMap_(form);
    const response = form.createResponse();
    Object.keys(payload.answers || {}).forEach(function(title){
      const value = payload.answers[title];
      if (isBlank_(value) || !items[title]) return;
      const entry = items[title];
      const ir = createItemResponse_(entry.item, entry.type, value);
      if (ir) response.withItemResponse(ir);
    });
    response.submit();
    cache.put(key, '1', CFG.CACHE_TTL_SECONDS);
    return bridgeHtml_({ok:true,submissionId:payload.submissionId});
  } catch (err) {
    console.error('ReuniaoDAI2: ' + safeError_(err));
    return bridgeHtml_({ok:false,message:safeError_(err)});
  } finally {
    lock.releaseLock();
  }
}

function getForm_() {
  const id = PropertiesService.getScriptProperties().getProperty(CFG.PROPERTY_FORM_ID);
  if (!id) throw new Error('Execute setupReuniaoDAI2() antes da implantação.');
  return FormApp.openById(id);
}

function validateEnvelope_(payload) {
  if (!payload || typeof payload !== 'object') throw new Error('Envelope inválido.');
  if (payload.version !== CFG.VERSION) throw new Error('Versão não suportada.');
  if (!payload.submissionId || String(payload.submissionId).length > 120) throw new Error('submissionId inválido.');
  if (!payload.answers || typeof payload.answers !== 'object' || Array.isArray(payload.answers)) throw new Error('Respostas inválidas.');
  const startedAt = Number(payload.startedAt || 0);
  const submittedAt = Number(payload.submittedAt || Date.now());
  if (!startedAt || submittedAt - startedAt < CFG.MIN_FILL_MS) throw new Error('Submissão rápida demais.');

  ['Nome completo','E-mail funcional','Posto/Graduação','Órgão Externo','Situação prevista em 13/11','Assuntos da apresentação']
    .forEach(function(title){ if (isBlank_(payload.answers[title])) throw new Error('Campo obrigatório ausente: ' + title); });
}

function answerableMap_(form) {
  const map = {};
  form.getItems().forEach(function(item){
    const type = item.getType();
    const title = item.getTitle();
    if (!title) return;
    if ([FormApp.ItemType.TEXT,FormApp.ItemType.PARAGRAPH_TEXT,FormApp.ItemType.LIST,FormApp.ItemType.MULTIPLE_CHOICE,FormApp.ItemType.CHECKBOX].indexOf(type) >= 0) {
      map[title] = {item:item,type:type};
    }
  });
  return map;
}

function createItemResponse_(item, type, value) {
  switch(type){
    case FormApp.ItemType.TEXT: return item.asTextItem().createResponse(String(value));
    case FormApp.ItemType.PARAGRAPH_TEXT: return item.asParagraphTextItem().createResponse(String(value));
    case FormApp.ItemType.LIST: return item.asListItem().createResponse(String(value));
    case FormApp.ItemType.MULTIPLE_CHOICE: return item.asMultipleChoiceItem().createResponse(String(value));
    case FormApp.ItemType.CHECKBOX: return item.asCheckboxItem().createResponse(Array.isArray(value) ? value.map(String) : [String(value)]);
    default: return null;
  }
}

function scheduleDeadlineClosure_() {
  ScriptApp.getProjectTriggers().forEach(function(t){
    if (t.getHandlerFunction() === 'closeForm_') ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('closeForm_').timeBased().at(new Date(CFG.DEADLINE)).create();
}

function closeForm_() {
  try {
    const form = getForm_();
    form.setAcceptingResponses(false);
    form.setCustomClosedFormMessage('Prazo de resposta encerrado em 24/09/2026. Em caso de necessidade institucional, contate a coordenação da DAI/2.');
  } catch (err) {
    console.error('Fechamento do formulário: ' + safeError_(err));
  }
}

function isBlank_(v) {
  if (v === null || typeof v === 'undefined') return true;
  if (Array.isArray(v)) return v.length === 0 || v.every(function(x){return String(x).trim()==='';});
  return String(v).trim() === '';
}

function safeError_(err) {
  return err && err.message ? String(err.message).slice(0,180) : 'Erro não identificado.';
}

function bridgeHtml_(data) {
  const msg = Object.assign({type:CFG.MESSAGE_TYPE},data || {});
  const json = JSON.stringify(msg).replace(/</g,'\\u003c');
  return HtmlService.createHtmlOutput('<!doctype html><meta charset="utf-8"><script>try{parent.postMessage(' + json + ',"*")}catch(e){}</script>')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

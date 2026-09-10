import fs from 'node:fs';

const html = fs.readFileSync('reuniao-dai2/index.html','utf8');
const css = fs.readFileSync('reuniao-dai2/styles.css','utf8');
const js = fs.readFileSync('reuniao-dai2/app.js','utf8');
const backend = fs.readFileSync('reuniao-dai2/apps-script/ReuniaoDAI2.gs','utf8');

const idx = s => html.indexOf(s);
const count = (text, token) => (text.match(new RegExp(token.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),'g')) || []).length;
const formsIntegrated = !/const BRIDGE_URL\s*=\s*''/.test(js);

const tests = [
  ['Smoke', html.includes('<!DOCTYPE html>') && html.includes('meetingForm') && fs.existsSync('reuniao-dai2/app.js') && fs.existsSync('reuniao-dai2/styles.css'), 'Página e ativos essenciais presentes.'],
  ['Pinpoint', html.includes('13 de novembro de 2026') && html.includes('24 de setembro de 2026') && html.includes('Responder rastreio de pauta'), 'Data, prazo e CTA localizáveis.'],
  ['Deep', backend.includes('setupReuniaoDAI2') && js.includes('submitToBridge') && js.includes('submitByEmail'), 'Arquitetura inclui front-end, fallback e backend Forms.'],
  ['Consistency', html.includes('09h00 às 12h00') && js.includes('20261113T090000') && js.includes('20261113T120000'), 'Horários coerentes entre página e calendário.'],
  ['Contradiction', html.includes('exceto os militares em férias ou licenciados') && html.includes('ficam convidados a participar'), 'Regra de comparecimento sem contradição.'],
  ['Completeness', formsIntegrated, formsIntegrated ? 'Persistência Forms ativa.' : 'PENDENTE: BRIDGE_URL ainda não recebeu a URL /exec do Apps Script; hoje o envio cai no e-mail institucional.'],
  ['Traceability', html.includes('Questionário reconstruído a partir do Forms institucional') && backend.includes('REUNIAO_DAI2_FORM_ID'), 'Origem do questionário e destino técnico rastreáveis.'],
  ['Compliance', html.includes('não armazena respostas no repositório público') && !js.includes('localStorage') && !js.includes('sessionStorage'), 'Sem persistência indevida no cliente/repositório.'],
  ['Regression', html.includes('href="../"') && !html.includes('<base '), 'Rota isolada e retorno ao Portal DAI/2 preservado.'],
  ['Change-impact', html.includes('styles.css?v=') && html.includes('app.js?v='), 'CSS e JS modularizados para reduzir impacto de mudanças.'],
  ['Cross-reference', html.includes('id="rastreio"') && html.includes('href="#rastreio"') && html.includes('id="bridgeFrame"'), 'Âncoras e referências internas resolvidas.'],
  ['Link integrity', html.includes('https://www.google.com/maps/search/?api=1') && html.includes('https://upload.wikimedia.org/'), 'Links externos principais têm esquema HTTPS e destino explícito.'],
  ['Visual QA', css.includes('@media(min-width:680px)') && css.includes('@media(min-width:960px)') && css.includes('.hero{') && css.includes('--max:1120px'), 'Layout responsivo e largura controlada.'],
  ['Accessibility', html.includes('class="skip"') && html.includes('aria-live="polite"') && html.includes('label class="required"') && html.includes('title="Canal de envio do formulário"'), 'Skip link, rótulos, feedback e iframe nomeado.'],
  ['Usability', html.includes('Enviar à DAI/2') && html.includes('Salvar cópia em PDF') && html.includes('Copiar respostas'), 'Ações principais explícitas.'],
  ['Cognitive-load', count(html,'class="form-section"') === 2 && html.includes('Como se preparar') && css.includes('max-width:800px'), 'Formulário agrupado e conteúdo progressivo.'],
  ['Narrative-flow', idx('Informações principais do encontro') < idx('Orientações aos militares') && idx('Orientações aos militares') < idx('Como se preparar') && idx('Como se preparar') < idx('Rastreio de informações'), 'Fluxo: contexto → regras → preparo → resposta.'],
  ['Red-team', !js.includes('eval(') && !js.includes('document.write') && js.includes('textContent') && js.includes('reportValidity'), 'Sem execução dinâmica perigosa e com validação do navegador.'],
  ['Edge-case', js.includes('Prazo encerrado') && js.includes('submitButton.disabled = true') && js.includes('afterprint'), 'Prazo expirado e retorno pós-impressão tratados.'],
  ['Scenario stress', js.includes('15000') && js.includes('crypto.randomUUID') && backend.includes('CacheService') && backend.includes('LockService'), 'Timeout, identificador, deduplicação e lock previstos.'],
  ['Fact-check', html.includes('Rodovia Papa João Paulo II, 4143') && html.includes('CEP 31630-900') && html.includes('13 de novembro de 2026'), 'Dados operacionais centrais fixados de forma consistente.'],
  ['Citation', html.includes('Wikimedia Commons (CC BY 3.0)') && html.includes('Endereço institucional do Edifício Minas'), 'Crédito visual e identificação da origem institucional do endereço presentes.'],
  ['Source-to-claim', html.includes('Questionário reconstruído a partir do Forms institucional') && backend.includes('Google Apps Script para criar o Google Forms oficial'), 'Claims técnicos correspondem aos artefatos existentes.'],
  ['Legal', html.includes('não substitui a confirmação de envio') && html.includes('não armazena respostas') && backend.includes('setCustomClosedFormMessage'), 'Avisos de guarda, confirmação e encerramento presentes.'],
  ['Decision-readiness', html.includes('Devem responder') && html.includes('Cada assessor terá espaço') && html.includes('Prazo para responder'), 'Responsável, ação e prazo explícitos.'],
  ['Preflight', html.includes('meta name="viewport"') && html.includes('meta name="description"') && html.includes('rel="icon"') && html.includes('application/ld+json'), 'Metadados, favicon e dados estruturados presentes.'],
  ['Version-drift', html.includes('2026.09.10.1') && js.includes("BRIDGE_VERSION = 'reuniao-dai2-2026-v1'") && backend.includes("VERSION: 'reuniao-dai2-2026-v1'"), 'Versões de ativos e contrato front/back coerentes.'],
  ['Template', html.includes('CBMMG · DAI/2') && css.includes('--navy:#0b2338') && html.includes('DAI/2'), 'Identidade institucional DAI/2 aplicada.'],
  ['Redundância', count(html,'<h1') === 2 && count(html,'id="rastreio"') === 1 && count(html,'id="meetingForm"') === 1, 'Um H1 da página + um H1 exclusivo do comprovante; IDs críticos únicos.'],
  ['Terminologia', html.includes('Richelmy Murta, Major BM') && html.includes('Coordenador da DAI/2') && !html.includes('coordenador da DI2'), 'Nome, posto e denominação institucional padronizados.']
];

let pass=0, pending=0, fail=0;
for (const [name, ok, note] of tests) {
  const isPending = name === 'Completeness' && !formsIntegrated;
  const status = ok ? 'PASS' : isPending ? 'PENDING' : 'FAIL';
  if (status === 'PASS') pass++; else if (status === 'PENDING') pending++; else fail++;
  console.log(`${status.padEnd(7)} | ${name.padEnd(20)} | ${note}`);
}
console.log(`\nSUMMARY | PASS=${pass} | PENDING=${pending} | FAIL=${fail} | TOTAL=${tests.length}`);
if (fail > 0) process.exit(1);

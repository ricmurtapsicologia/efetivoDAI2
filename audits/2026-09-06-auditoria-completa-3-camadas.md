# DAI/2 — AUDITORIA COMPLETA EM 3 CAMADAS

**Objeto:** Portal público DAI/2 — Efetivo e TPB 2026  
**Interface auditada:** 2.3.0  
**Commit de produção:** `3fdc7146137ccdcc5dd07cafd33b9f39cc752c08`  
**Data local da auditoria:** 06/09/2026  
**URL de produção:** https://ricmurtapsicologia.github.io/efetivoDAI2/  
**Método:** Auditoria 30/30 Institucional/Técnica + Auditoria Editorial Profissional 90/90 + Auditoria de Experiência e Qualidade Aplicada (E2E, QA, Acessibilidade, UX e UI).

## 1. Veredito executivo

**Página publicada / build atual: APROVADA.**

- Gate de produção: sucesso.
- Smoke na URL pública: **30/30 PASS**.
- Terceira camada em Chromium: **37/37 PASS**.
- Invariantes: DDQOD 101; efetivo 84; claro por P/G 23; excedentes por P/G 5; SEMAD 1 extra-DDQOD e 0 previsto.
- TPB público: somente agregado — escopo 85; feito 69; não feito 16; dispensas 9; exigem ação 7; sem data consolidada 15.
- Layout original: preservado, com 18 blocos.

**Veredito global de governança: APROVADO COM RESSALVA ALTA.**

A versão corrente e o GitHub Pages não publicam mais telefones, e-mails, aniversários nem registros individuais do TPB. Entretanto, os arquivos que continham esses dados existiram em commits anteriores de um repositório público. Excluir os arquivos do HEAD e do Pages não apaga automaticamente blobs históricos do Git. A eliminação integral desse passivo exige reescrita/purga do histórico Git e posterior verificação dos objetos remotos. Essa operação não foi executada nesta rodada.

## 2. Achado crítico que motivou o saneamento

A auditoria profunda encontrou uma discrepância com o relatório anterior: dados pessoais não estavam apenas “ocultos” na interface; eles estavam incluídos em arquivos JavaScript publicados no repositório/artefato público. Foram identificadas três classes de exposição: contatos/aniversários, e-mails e acompanhamento individual do TPB.

### Correções aplicadas

1. Removidos da versão corrente `data/contacts.js`, `data/emails.js` e `assets/js/email-actions.js`.
2. Removidas ações públicas de WhatsApp/e-mail.
3. `data/tpb.js` convertido para indicadores exclusivamente agregados; `DAI_TPB_ROWS=[]`.
4. Painel auxiliar convertido em informação de proteção de dados, sem carregar dados pessoais.
5. Mantida no efetivo apenas a allowlist pública necessária ao portal: posto/graduação, nome, órgão e subunidade.
6. Totais e números dos blocos deixaram de ser duplicados no HTML e são calculados da fonte canônica.
7. Reforçados foco, teclado, Escape, retorno de foco, focus trap, `inert`, ARIA, alvos de toque e reduced motion.
8. Criado gate permanente Playwright para E2E + QA + Acessibilidade + UX + UI.
9. Reforçado o smoke pós-deploy para reprovar retorno de dados de contato à camada pública.
10. Preservada a arquitetura visual original, sem redesign estrutural.

---

# CAMADA 1 — AUDITORIA 30/30 INSTITUCIONAL/TÉCNICA

Todos os 30 testes canônicos foram executados após as correções.

| # | Teste canônico | Status final | Evidência / conclusão |
|---:|---|---|---|
| 1 | Smoke test | PASS | URL pública HTTP 200; app 2.3 e dados carregados. |
| 2 | Pinpoint audit | PASS | Bloqueadores sentinela de privacidade, SEMAD, claro e TPB foram saneados no build atual. |
| 3 | Deep audit | PASS | Código, dados, runtime, privacidade, a11y, responsividade e CI reavaliados. |
| 4 | Consistency test | PASS | Totais e semântica reconciliados: 101 / 84 / claro P/G 23 / excedentes 5. |
| 5 | Contradiction scan | PASS | SEMAD permanece 0 previsto e 1 extra-DDQOD; não há regra concorrente de claro. |
| 6 | Completeness audit | PASS | Fluxos públicos essenciais, dados gerenciais, jurídico e TPB agregado presentes. |
| 7 | Traceability audit | PASS | Fonte canônica de efetivo/DDQOD e corte TPB documentados e testados. |
| 8 | Compliance test | PASS COM RESSALVA ALTA | Build atual respeita limite público; histórico Git anterior ainda requer purga. |
| 9 | Regression test | PASS | Layout original, 18 blocos, pesquisas, modais e DDQOD preservados após saneamento. |
| 10 | Change-impact analysis | PASS | Retirada de dados pessoais propagada ao HTML, JS, TPB, testes, CI e README. |
| 11 | Cross-reference test | PASS | Efetivo, DDQOD, claro, SEMAD e TPB reconciliam no mesmo runtime. |
| 12 | Link integrity | PASS COM RESSALVA | Assets locais não falham; dependência decorativa remota continua sujeita a disponibilidade externa. |
| 13 | Visual QA | PASS | Desktop e mobile auditados em navegador; sem overflow horizontal; hierarquia preservada. |
| 14 | Accessibility | PASS | Teclado, foco, modal, nomes acessíveis e alvos de toque aprovados no navegador. |
| 15 | Usability | PASS | Pesquisa, expansão DDQOD, modais e onboarding completam os fluxos esperados. |
| 16 | Cognitive-load | PASS | Indicadores têm semântica explícita; claro e extra-DDQOD deixaram de competir conceitualmente. |
| 17 | Narrative-flow | PASS | Visão geral → pesquisa → órgãos → DDQOD → fundamentos/TPB permanece coerente. |
| 18 | Red-team | PASS | Removidos dados pessoais do artefato corrente; CI passa a bloquear reincidência. |
| 19 | Edge-case | PASS | Excedentes de uma P/G não compensam claro de outra; SEMAD tratada como caso extra-DDQOD. |
| 20 | Scenario stress | PASS | Navegação, mobile, teclado, reload e persistência de onboarding testados. |
| 21 | Fact-check | PASS | Invariantes numéricos e corte TPB conferidos automaticamente. |
| 22 | Citation audit | PASS | Fonte/corte TPB e fonte primária jurídica explicitados na camada de informação. |
| 23 | Source-to-claim test | PASS | Indicadores exibidos derivam das estruturas canônicas e testes conferem os valores. |
| 24 | Legal defensibility | PASS | UI ressalva prevalência do ato/fonte primária e elimina dados pessoais desnecessários do build. |
| 25 | Decision-readiness | PASS | Página atual pode ser usada para consulta gerencial nos limites declarados. |
| 26 | Publication preflight | PASS | Build, navegador e GitHub Pages passaram os gates pós-merge. |
| 27 | Version-drift audit | PASS | Interface 2.3.0 e referências versionadas reconciliadas no HTML/README/CI. |
| 28 | Canonical-template test | PASS | Arquitetura visual original preservada; nenhum redesign estrutural detectado. |
| 29 | Duplication/redundancy scan | PASS | Totais e métricas hardcoded retirados do HTML; runtime deriva da fonte canônica. |
| 30 | Terminology audit | PASS | “Claro por P/G”, “extra-DDQOD”, órgãos e TPB agregado normalizados. |

**Resultado da camada 1:** 28 PASS + 2 PASS COM RESSALVA + 0 FAIL.  
**Smoke público adicional:** 30/30 verificações operacionais PASS.

---

# CAMADA 2 — AUDITORIA EDITORIAL PROFISSIONAL 90/90

Os 90 controles canônicos foram preservados. Para produto web, controles estritamente físicos/editoriais de impressão são marcados **N/A**, sem substituição por controles inventados. A prova de navegador resolve os controles de viewport/soft proof que são materialmente verificáveis no portal.

Legenda: **PASS** = aprovado; **PASS-R** = aprovado com ressalva; **N/A** = não aplicável ao produto web.

| # | Controle canônico | Status | Aplicação ao portal DAI/2 |
|---:|---|---|---|
| 1 | Propósito editorial | PASS | Consulta gerencial de efetivo/TPB claramente definida. |
| 2 | Público leitor | PASS | Uso institucional/gerencial delimitado e fronteira pública explicitada. |
| 3 | Experiência de leitura | PASS | Fluxo de consulta simples e testado ponta a ponta. |
| 4 | Arquitetura global | PASS | Estrutura original preservada e coerente. |
| 5 | Partes, unidades e capítulos | PASS | Adaptado a seções, blocos e modais com organização estável. |
| 6 | Progressão pedagógica | PASS | Adaptado à progressão informacional da consulta. |
| 7 | Extensão e densidade editorial | PASS | Densidade compatível com painel gerencial. |
| 8 | Edição de desenvolvimento | PASS | Fluxo e microcopy saneados sem patches concorrentes. |
| 9 | Edição substantiva | PASS | Semântica de DDQOD, claro e extra-DDQOD reconciliada. |
| 10 | Padronização de linguagem e terminologia | PASS | Terminologia normalizada. |
| 11 | Revisão técnico-científica especializada | PASS | Gates de dados/regras incorporados ao CI. |
| 12 | Fontes, referências e atribuições | PASS | Fontes/cortes e prevalência da fonte primária declarados. |
| 13 | Copyediting/preparação de originais | PASS | Microcopy revisada; Nr BM e chamadas indevidas removidos. |
| 14 | Revisão gramatical/ortotipográfica | PASS | Rótulos e textos da interface consistentes. |
| 15 | Formato físico | N/A | Controle de livro impresso. |
| 16 | Mancha gráfica | PASS | Layout e blocos validados em navegador. |
| 17 | Margens | PASS | Espaçamentos/viewport aprovados. |
| 18 | Medianiz/gutter | N/A | Requisito de encadernação. |
| 19 | Família tipográfica principal | PASS | Pilha de sistema robusta. |
| 20 | Família tipográfica complementar | PASS | Não crítica para o portal; sistema tipográfico é coerente. |
| 21 | Corpo de texto | PASS | Corpo 16 px no teste mobile. |
| 22 | Entrelinha | PASS | Leitura funcional. |
| 23 | Comprimento de linha | PASS | Containers/modais controlados. |
| 24 | Tracking e kerning | PASS | Renderização de navegador adequada. |
| 25 | Hierarquia tipográfica | PASS | Título 32 px e corpo 16 px no teste mobile; hierarquia preservada. |
| 26 | Estilos de parágrafo e caractere | PASS | CSS centralizado e componentes consistentes. |
| 27 | Recuos e espaçamentos | PASS | Consistência visual mantida. |
| 28 | Hifenização e justificação | PASS | Texto funcional na interface. |
| 29 | Rios de branco | N/A | Critério editorial de texto paginado. |
| 30 | Viúvas, órfãs e runts | N/A | Critério editorial de texto paginado. |
| 31 | Baseline grid | N/A | Não é requisito do portal. |
| 32 | Alinhamento vertical em páginas confrontantes | N/A | Não há páginas confrontantes. |
| 33 | Fólios, cabeçalhos e rodapés | PASS | Banner e footer preservados. |
| 34 | Lógica par/ímpar | N/A | Exclusiva de publicação paginada. |
| 35 | Aberturas de partes/unidades | PASS | Seções têm entradas claras. |
| 36 | Aberturas de capítulos | PASS | Adaptado a blocos/modais. |
| 37 | Identidade iconográfica | PASS | Interface funcional sem dependência de ícones de contato. |
| 38 | Linguagem gráfica para funções didáticas | PASS | Cores/rótulos têm função gerencial coerente. |
| 39 | Relação texto–imagem | PASS | Dados são prioritários; imagens são decorativas. |
| 40 | Direção de arte fotográfica | PASS-R | Ativo decorativo remoto permanece sem governança integral interna. |
| 41 | Seleção e tratamento fotográfico | PASS-R | Ativo decorativo remoto continua sujeito a disponibilidade externa. |
| 42 | Ilustrações autorais | N/A | Não requeridas para o escopo funcional. |
| 43 | Infográficos | PASS | Donuts redesenhados matematicamente como preenchido/claro. |
| 44 | Fluxogramas e algoritmos | N/A | Não requeridos na interface atual. |
| 45 | Organogramas, mapas, linhas do tempo e diagramas | N/A | Não requeridos na interface atual. |
| 46 | Precisão científica dos infográficos | PASS | Gráfico não soma categorias sobrepostas; preenchido/claro deriva por P/G. |
| 47 | Legendas, fontes e créditos visuais | PASS | Semântica e fontes/cortes declarados. |
| 48 | Acessibilidade visual | PASS | Navegação/controle/foco/viewport testados. |
| 49 | Paleta cromática | PASS | Paleta original preservada. |
| 50 | Função semântica da cor | PASS | Cor possui apoio textual e não é o único portador da informação. |
| 51 | Capa | PASS | Adaptado a banner/entrada do portal. |
| 52 | Lombada | N/A | Impresso. |
| 53 | Quarta capa | N/A | Impresso. |
| 54 | Coerência capa–miolo | PASS | Adaptado a banner–conteúdo; linguagem consistente. |
| 55 | Folhas de rosto, créditos e expediente | PASS | Rodapé/README fornecem identificação e versão. |
| 56 | Ficha catalográfica/ISBN | N/A | Não aplicável. |
| 57 | Sumário profissional | N/A | Navegação do portal substitui sumário paginado. |
| 58 | Índices remissivo/temático/lista de figuras | PASS | Busca funciona como índice operacional. |
| 59 | Boxes e quadros | PASS | Blocos e painéis funcionais. |
| 60 | Conversão de quadros em prosa | N/A | Não é objetivo da aplicação. |
| 61 | Elementos pedagógicos | N/A | Portal não é produto pedagógico. |
| 62 | Ritmo visual | PASS | Sequência e repetição dos blocos são estáveis. |
| 63 | Duplas de páginas/spreads | N/A | Não aplicável. |
| 64 | Espaços negativos | N/A | Critério editorial físico não utilizado como gate. |
| 65 | Equilíbrio de massa visual | N/A | Critério editorial físico; UI é coberta por prova em navegador. |
| 66 | Imagens x margens/dobras | PASS | Adaptado a viewport/cortes; mobile aprovado sem overflow. |
| 67 | Revisão de tabelas | N/A | Não há tabelas complexas no escopo. |
| 68 | Redesenho de tabelas | N/A | Não aplicável. |
| 69 | Resolução de imagens | PASS | Elementos funcionais são locais/canvas; imagem remota é decorativa. |
| 70 | Perfis de cor | PASS | RGB/sRGB adequado à web. |
| 71 | CMYK | N/A | Impressão. |
| 72 | Sangria | N/A | Impressão. |
| 73 | Marcas e especificações de impressão | N/A | Impressão. |
| 74 | Fontes incorporadas | PASS | Fontes de sistema; sem dependência de webfont. |
| 75 | Links e QR Codes | PASS | Ações públicas de contato removidas; assets locais verificados. |
| 76 | Prova após diagramação | PASS | Browser gate obrigatório no CI. |
| 77 | Prova visual página a página | PASS | Equivalente web executado em desktop/mobile e fluxos principais. |
| 78 | Prova de imposição/encadernação | N/A | Impressão. |
| 79 | Boneco físico | N/A | Impressão. |
| 80 | Avaliação em mão | N/A | Produto digital. |
| 81 | Soft proof | N/A | Controle editorial de impressão; equivalente web coberto no 77. |
| 82 | Preflight técnico do PDF | N/A | Não há PDF como produto. |
| 83 | Bleed, marcas, cores e saída | N/A | Impressão. |
| 84 | Capa na lombada final | N/A | Impressão. |
| 85 | Sumário x paginação | N/A | Não há paginação. |
| 86 | Referências cruzadas e chamadas de figuras | PASS | Dados, DDQOD, legal e TPB reconciliados na mesma estrutura. |
| 87 | Consistência títulos/legendas/índices | PASS | Rótulos/órgãos/indicadores normalizados. |
| 88 | Correções finais pós-diagramação | PASS | Achados desta rodada corrigidos e retestados. |
| 89 | Aprovação editorial final | PASS | Gate obrigatório de CI aprovado antes e após merge. |
| 90 | Master e derivados finais | PASS | `main` é o master corrente; Pages validado pós-merge. |

**Resultado da camada 2:** **56 PASS + 2 PASS-R + 32 N/A + 0 FAIL.**  
As duas ressalvas são exclusivamente de governança de fotografia/ativo decorativo remoto (controles 40 e 41).

---

# CAMADA 3 — EXPERIÊNCIA E QUALIDADE APLICADA

A terceira camada foi executada em Chromium via Playwright antes do merge e repetida na `main`. Resultado final: **37/37 PASS**.

## 3.1 E2E — 13/13 PASS

1. Página responde HTTP 200.
2. Onboarding etapa 1.
3. Onboarding etapa 2.
4. Onboarding etapa 3.
5. Onboarding etapa 4.
6. Conteúdo principal aparece após onboarding.
7. Bloco AFAS abre modal pelo teclado.
8. Escape fecha o modal.
9. Pesquisa nominal retorna o registro esperado.
10. Pesquisa de claro por P/G funciona.
11. Lista DDQOD expande.
12. Modal jurídico abre.
13. TPB agregado abre.

## 3.2 QA — 8/8 PASS

1. Sem erro JavaScript de console inicial.
2. Sem `pageerror` inicial.
3. Totais canônicos renderizados: 101 / 84 / 23.
4. SEMAD exibida como 0 previsto + extra-DDQOD.
5. Modal jurídico contém ressalva de fonte primária.
6. KPIs TPB agregados conferem.
7. Sem erros JavaScript ao final.
8. Assets locais sem falha de rede/HTTP.

## 3.3 Acessibilidade — 5/5 PASS

1. Modal possui título contextual.
2. Foco permanece dentro do modal.
3. Foco retorna ao acionador após fechar.
4. Controles visíveis têm nome acessível.
5. Alvos de toque possuem pelo menos 44 px.

## 3.4 UX — 3/3 PASS

1. Onboarding aparece no primeiro acesso.
2. Onboarding não reaparece depois de concluído.
3. Conteúdo principal permanece acessível no mobile.

## 3.5 UI — 4/4 PASS

1. 18 blocos renderizados.
2. Mobile 375×812 sem overflow horizontal.
3. Blocos mobile em coluna única.
4. Hierarquia tipográfica preservada (título 32 px; corpo 16 px no teste).

## 3.6 Verificação transversal de privacidade — 4/4 PASS

1. Painel público explica proteção de dados.
2. Nenhum telefone visível no DOM textual testado.
3. Nenhum e-mail visível no DOM textual testado.
4. TPB sem lista nominal nem input individual.

**Total camada 3: 13 E2E + 8 QA + 5 Acessibilidade + 3 UX + 4 UI + 4 verificações transversais de privacidade = 37/37 PASS.**

---

# 4. Reteste de produção

Após o merge na `main`, o workflow de produção repetiu os gates e executou `scripts/live_smoke.py` na URL pública.

Resultado do smoke público:

- 30/30 verificações PASS;
- URL pública HTTP 200;
- layout original e 18 blocos presentes;
- app 2.3 carregado;
- `runtime-updates.js` e Chart.js ausentes;
- Nº BM, arquivos de contato, ações diretas de contato e aniversários ausentes da camada pública;
- 101 previsto / 84 existente / claro P/G 23 / excedente P/G 5;
- SEMAD 0 previsto + 1 extra-DDQOD;
- TPB agregado no corte 03/09/2026: 85 / 69 / 16 / 9 / 7 / 15;
- estrutura de acessibilidade/UX/privacidade aprovada.

# 5. Risco residual

## R1 — Dados antigos no histórico Git

**Severidade: ALTA.**

Os arquivos foram removidos do HEAD e da publicação atual, mas commits históricos de um repositório público podem continuar contendo os blobs antigos. Isso não é corrigido por `git rm`/deleção normal.

**Ação necessária para encerramento integral:** reescrever/purgar o histórico Git dos objetos sensíveis, forçar a substituição das refs relevantes e verificar que os blobs anteriores não sejam mais recuperáveis pelos caminhos/SHAs históricos. Considerar também revalidação/rotação de dados de contato se houver risco operacional.

Até essa etapa, a **página em produção está aprovada**, mas a **governança histórica do repositório permanece aprovada com ressalva alta**.

# 6. Decisão final

- **Página DAI/2 interface 2.3.0:** APROVADA E PUBLICADA.
- **Camada 1 — 30/30:** 28 PASS + 2 PASS COM RESSALVA + 0 FAIL; smoke público adicional 30/30 PASS.
- **Camada 2 — 90/90:** 56 PASS + 2 PASS COM RESSALVA + 32 N/A + 0 FAIL.
- **Camada 3 — E2E/QA/Acessibilidade/UX/UI:** 37/37 PASS.
- **Governança do histórico Git:** RESSALVA ALTA até purga dos blobs históricos.
- **Gate global:** APROVADO COM RESSALVA ALTA.

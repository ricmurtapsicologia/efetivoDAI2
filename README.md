# DAI/2 · Efetivo e TPB 2026

Painel estático do CBMMG/DAI para consulta gerencial da distribuição do efetivo DAI/2 em órgãos externos, DDQOD, claro por posto/graduação, fundamentos correlatos e indicadores agregados do TPB 2026.

## Interface 2.5.0 · auditoria completa em 3 camadas

A versão 2.5.0 preserva a arquitetura funcional do portal e mantém o contato funcional por WhatsApp visível e direto em cada registro.

Foram preservados: splash inicial, onboarding, banner, título, quadro de dados gerais, atalhos, legenda de cores, campos de pesquisa, organização em linhas, 18 blocos dos órgãos, botão de previsão DDQOD, modais e rodapé.

Principais regras da versão:

- fonte canônica de efetivo e DDQOD em `data/data.js`, sem mutações por `runtime-updates.js`;
- claro calculado por posto/graduação; excedentes de uma P/G não compensam vagas de outra;
- SEMAD tratada como implantação extra-DDQOD: 0 previsto no DDQOD consultado e 1 militar em exercício;
- números de WhatsApp funcionais ficam visíveis e o botão abre diretamente o destinatário correspondente;
- e-mails, aniversários, Nº BM e situação individual de TPB permanecem fora do frontend;
- TPB 2026 permanece no mesmo atalho/modal, apenas com indicadores agregados;
- os números dos blocos são calculados a partir da fonte canônica em runtime, sem duplicação numérica no HTML;
- gráficos permanecem nos canvases originais e são desenhados localmente, sem Chart.js;
- acessibilidade reforçada com skip-link, foco visível, acionamento por teclado, Escape, retorno de foco, focus trap, `inert` do conteúdo de fundo, alvos de toque e `prefers-reduced-motion`;
- CI executa auditoria de invariantes e testes em navegador: E2E + QA + Acessibilidade + UX + UI;
- após merge em `main`, o smoke público 30/30 valida a URL efetivamente publicada.

## Identidade visual do banner e onboarding

O refino visual de 08/09/2026 adotou abordagem mobile-first, reduziu redundâncias textuais e reorganizou a primeira dobra em três elementos: hero institucional, visão geral do efetivo e onboarding sobre a própria página.

O hero usa a fotografia `Cidade Administrativa MG 1`, em resolução original de 3.500×2.333 px, disponibilizada no Wikimedia Commons sob licença CC BY 3.0. O portal aplica apenas recorte responsivo e gradientes de contraste em CSS. A procedência, licença e forma de uso estão registradas em `assets/hero-source.json` e `assets/img/banner-cbmmg-source.txt`, com atribuição também no rodapé público.

A splash não utiliza fotografia de pessoas. O onboarding mantém as quatro etapas originais — distribuição do efetivo, pesquisa e claro, gráficos interativos, previsão e TPB — e usa a identidade visual da DAI/2 informada para a abertura.

## Fontes de corte

Efetivo DAI/2: ficha-mestre dos órgãos externos, validação de 17/08/2026.

DDQOD: Anexo C da Resolução nº 1.268/2025.

TPB: Ofício CBMMG/DAI-2 nº 569/2026 (SEI 151390924), posição administrativa de 14/10/2026: todos os militares em atividade na DAI foram declarados concluintes. O recorte quantitativo de 03/09/2026 permanece identificável como histórico, sem ser apresentado como situação atual. Atos de convocação dos ciclos 26º, 28º, 29º, 30º e 32º não comprovam, isoladamente, participação ou aprovação.

## Regra do claro

`claro_PG = max(previsto_PG - existente_PG, 0)`

Invariantes da base atual:

- previsto oficial DDQOD: 100;
- efetivo atual total: 83;
- CTPM RMBH: 16 previstos, 15 existentes e 1 claro;
- SEMAD extra-DDQOD: 1;
- claro por P/G: 22;
- excedentes por P/G nos órgãos DDQOD: 4.

## TPB: situação institucional em 14/10/2026

- Pendências declaradas: 0, conforme Ofício CBMMG/DAI-2 nº 569/2026 (SEI 151390924).
- Todos os militares atualmente em atividade na DAI são declarados concluintes no ofício, sem fornecimento do número individualizado.
- O painel não infere 83/83 ou 100% da base de efetivo, cuja data e universo de referência não coincidem necessariamente com os do documento.
- Série histórica de 03/09/2026 preservada no Drive institucional, retirada da apresentação pública para evitar contradição com a posição mais recente.

Os registros nominais, datas pessoais, dados médicos e históricos de situação não integram a camada pública.

## Validação

```bash
python scripts/personnel_pipeline.py audit --input data/data.js
python scripts/site_audit.py
python scripts/browser_e2e.py
```

O workflow `.github/workflows/python-personnel-audit.yml` executa os gates em PRs e em `main`. Em produção, `scripts/live_smoke.py` executa 30 verificações na URL pública.

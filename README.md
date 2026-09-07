# DAI/2 · Efetivo e TPB 2026

Painel estático do CBMMG/DAI para consulta gerencial da distribuição do efetivo DAI/2 em órgãos externos, DDQOD, claro por posto/graduação, fundamentos correlatos e indicadores agregados do TPB 2026.

## Interface 2.5.0 · auditoria completa em 3 camadas

A versão 2.5.0 preserva a arquitetura visual original do portal e mantém o contato funcional por WhatsApp visível e direto em cada registro.

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

## Identidade visual do banner

O banner principal usa uma composição panorâmica 2400×900 criada a partir de uma fotografia de viatura do CBMMG encontrada em pesquisa visual no Pinterest. O ativo foi internalizado no próprio repositório para evitar hotlink e recebeu tratamento de fundo, contraste e área de leitura. A referência e o tratamento ficam registrados em `assets/hero-source.json` e `assets/img/banner-cbmmg-source.txt`.

## Fontes de corte

Efetivo DAI/2: ficha-mestre dos órgãos externos, validação de 17/08/2026.

DDQOD: Anexo C da Resolução nº 1.268/2025.

TPB: `Dashboard TPB DAI 2026 - controle por ata - 03-09-2026.xlsx`, corte 03/09/2026. O frontend público recebe somente os agregados consolidados desse corte.

## Regra do claro

`claro_PG = max(previsto_PG - existente_PG, 0)`

Invariantes da base atual:

- previsto oficial DDQOD: 101;
- efetivo atual total: 84;
- SEMAD extra-DDQOD: 1;
- claro por P/G: 23;
- excedentes por P/G nos órgãos DDQOD: 5.

## TPB agregado no corte de 03/09/2026

- escopo controlado: 85;
- TPB feito: 69;
- TPB não feito: 16;
- dispensas: 9;
- não feito e sem dispensa: 7;
- feito sem data consolidada: 15.

Os registros nominais, datas pessoais e históricos de situação não integram a camada pública.

## Validação

```bash
python scripts/personnel_pipeline.py audit --input data/data.js
python scripts/site_audit.py
python scripts/browser_e2e.py
```

O workflow `.github/workflows/python-personnel-audit.yml` executa os gates em PRs e em `main`. Em produção, `scripts/live_smoke.py` executa 30 verificações na URL pública.

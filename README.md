# DAI/2 · Efetivo e TPB 2026

Painel estático do CBMMG/DAI para consulta gerencial da distribuição do efetivo DAI/2 em órgãos externos, DDQOD, claro por posto/graduação, fundamentos correlatos e indicadores agregados do TPB 2026.

## Interface 2.3.0 · auditoria completa em 3 camadas

A versão 2.3.0 preserva a arquitetura visual original do portal e incorpora um limite explícito entre informação pública e dados funcionais internos.

Foram preservados: splash inicial, onboarding, banner, título, quadro de dados gerais, três atalhos, painel auxiliar, legenda de cores, campos de pesquisa, organização em linhas, 18 blocos dos órgãos, botão de previsão DDQOD, modais e rodapé.

Principais regras da versão:

- fonte canônica de efetivo e DDQOD em `data/data.js`, sem mutações por `runtime-updates.js`;
- claro calculado por posto/graduação; excedentes de uma P/G não compensam vagas de outra;
- SEMAD tratada como implantação extra-DDQOD: 0 previsto no DDQOD consultado e 1 militar em exercício;
- Nº BM, telefones, e-mails, aniversários e situação individual de TPB não são carregados na página pública;
- arquivos públicos de contatos/e-mails foram removidos; ações `wa.me` e `mailto:` não fazem parte do frontend público;
- TPB 2026 permanece no mesmo atalho/modal, porém apenas com indicadores agregados;
- os números dos blocos são calculados a partir da fonte canônica em runtime, sem duplicação numérica no HTML;
- gráficos permanecem nos canvases originais e são desenhados localmente, sem Chart.js;
- acessibilidade reforçada com skip-link, foco visível, acionamento por teclado, Escape, retorno de foco, focus trap, `inert` do conteúdo de fundo, alvos de toque e `prefers-reduced-motion`;
- CI executa a Auditoria Institucional/Técnica, invariantes, privacidade e a terceira camada automatizada em navegador: E2E + QA + Acessibilidade + UX + UI;
- após merge em `main`, o smoke público 30/30 valida a URL efetivamente publicada.

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

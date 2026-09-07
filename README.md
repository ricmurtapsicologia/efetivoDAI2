# DAI/2 · Efetivo e TPB 2026

Painel estático do CBMMG/DAI para consulta gerencial da distribuição do efetivo DAI/2 em órgãos externos, DDQOD, claro por posto/graduação, fundamentos correlatos, contatos WhatsApp e indicadores agregados do TPB 2026.

## Interface 2.5.0 · auditoria completa em 3 camadas

A versão 2.5.0 preserva a arquitetura visual original, mantém o TPB em formato agregado e publica o número de WhatsApp de cada militar para contato direto.

Principais regras da versão:

- fonte canônica de efetivo e DDQOD em `data/data.js`;
- diretório WhatsApp em `data/contacts.js`, com cobertura obrigatória de 100% do efetivo atual;
- cada militar exibe o número em formato internacional e possui botão que abre diretamente o destinatário no WhatsApp com mensagem pronta;
- números legados com DDD + 8 dígitos são normalizados para o padrão móvel brasileiro de 9 dígitos antes de formar o link `wa.me`;
- e-mails, aniversários e situação individual de TPB não são publicados;
- claro calculado por posto/graduação; excedentes de uma P/G não compensam vagas de outra;
- SEMAD tratada como implantação extra-DDQOD: 0 previsto no DDQOD consultado e 1 militar em exercício;
- TPB 2026 permanece agregado e utiliza linguagem operacional: concluídos, não concluídos, dispensados, ação necessária e sem data registrada;
- os números dos blocos são calculados da fonte canônica em runtime;
- gráficos são desenhados localmente nos canvases, sem Chart.js;
- acessibilidade inclui skip-link, foco visível, teclado, Escape, retorno de foco, focus trap, `inert`, alvos de toque e `prefers-reduced-motion`;
- CI executa auditoria estrutural, validação do diretório WhatsApp, E2E, QA, Acessibilidade, UX e UI;
- após merge em `main`, o smoke público 30/30 valida a URL efetivamente publicada.

## Hero corporativo

O hero atual utiliza fotografia real de ambiente corporativo:

- fotógrafa: Ufoma Ojo (`@ladyufoma001`);
- título: `Two women in white shirts stand in an office`;
- fonte: Unsplash;
- licença: Unsplash License;
- publicação: 15/05/2026;
- proveniência completa: `assets/hero-source.json`.

O teste E2E não verifica apenas a declaração CSS: ele carrega efetivamente a imagem remota e exige largura natural mínima de 1600 px.

## Fontes de corte

Efetivo DAI/2: ficha-mestre dos órgãos externos, validação de 17/08/2026.

DDQOD: Anexo C da Resolução nº 1.268/2025.

Contatos: base funcional DAI/2 restaurada do histórico validado do portal e reconciliada nominalmente com os 84 registros de efetivo.

TPB: `Dashboard TPB DAI 2026 - controle por ata - 03-09-2026.xlsx`, corte 03/09/2026. O frontend recebe apenas os agregados consolidados desse corte.

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
- TPB concluído: 69;
- TPB não concluído: 16;
- dispensas: 9;
- exigem ação: 7;
- concluídos sem data consolidada: 15.

## Validação

```bash
python scripts/personnel_pipeline.py audit --input data/data.js
python scripts/site_audit.py
python scripts/browser_e2e.py
```

O workflow `.github/workflows/python-personnel-audit.yml` usa `actions/checkout@v6`, `actions/setup-python@v6` e `actions/upload-artifact@v6`, compatíveis com Node.js 24. Em produção, `scripts/live_smoke.py` executa 30 verificações na URL pública.

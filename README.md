# DAI/2 · Efetivo e TPB 2026

Painel estático do CBMMG/DAI para consulta gerencial de efetivo DAI/2 em órgãos externos, DDQOD e claro por posto/graduação, contatos operacionais e acompanhamento do TPB 2026 da DAI.

## Interface 2.2.0 · layout original preservado

A versão 2.2.0 mantém integralmente a arquitetura visual original do portal. Não há redesign da página principal.

Foram preservados: splash inicial, onboarding, banner, título, quadro de dados gerais, atalhos, painel de aniversariantes, legenda de cores, campos de pesquisa, organização em linhas, os 18 blocos dos órgãos, botão de previsão DDQOD, modais e rodapé.

Os ajustes foram implementados dentro dessa estrutura:

- envio direto de WhatsApp restaurado nos cartões nominais e nos resultados de pesquisa;
- aniversariantes do dia novamente funcionais, com atalho de WhatsApp quando houver contato cadastrado;
- contatos e aniversários mantidos em `data/contacts.js`, separados da base canônica de efetivo;
- informações internas de rastreabilidade documental e pendências de produção não são exibidas no frontend nominal;
- TPB 2026 da DAI acessível por botão na área já existente de atalhos e exibido em modal;
- cálculo de claro por posto/graduação;
- SEMAD tratada como implantação extra-DDQOD, com 0 previsto no DDQOD e 1 militar em exercício;
- dados canônicos de efetivo consolidados em `data/data.js`, sem `runtime-updates.js`;
- Nº BM permanece excluído da camada pública;
- gráficos mantidos nos mesmos canvases dos blocos e desenhados localmente, sem Chart.js;
- onboarding persistente após a primeira visualização;
- melhorias de teclado, foco, contraste, alvos de toque e `prefers-reduced-motion` sem alteração da composição visual;
- imagens remotas do splash/banner mantidas apenas como elementos decorativos do layout original, com fundo local de contingência;
- CI em `pull_request` e `push` para `main`, com gate específico contra redesign e contra resíduos de bastidores no frontend.

A versão dos dados de efetivo permanece `2.0.0`; a versão `2.2.0` identifica a interface atual.

## Fontes de corte

Efetivo DAI/2: ficha-mestre dos órgãos externos, validação de 17/08/2026.

DDQOD: Anexo C da Resolução nº 1.268/2025.

TPB: `Dashboard TPB DAI 2026 - controle por ata - 03-09-2026.xlsx`, corte 03/09/2026.

## Regra do TPB

`TPB FEITO` significa participação comprovada em lista/ata ou consolidada como concluída/regularizada na fonte governada. Dispensa definitiva permanece separada e não é contabilizada como TPB feito.

No corte de 03/09/2026:

- escopo controlado: 85;
- TPB feito: 69;
- TPB não feito: 16;
- dispensa definitiva: 9;
- não feito e sem dispensa: 7;
- feito sem data consolidada: 15.

## Regra do claro

O claro é calculado por posto/graduação:

`claro_PG = max(previsto_PG - existente_PG, 0)`

Excedentes de uma graduação não compensam vagas de outra.

Invariantes da base atual:

- previsto oficial DDQOD: 101;
- efetivo atual total: 84;
- SEMAD extra-DDQOD: 1;
- claro por P/G: 23;
- excedentes por P/G nos órgãos DDQOD: 5.

## Contatos públicos

A camada pública disponibiliza posto/graduação, nome, órgão, subunidade e contato telefônico operacional para abertura direta do WhatsApp. O painel de aniversariantes usa a data de aniversário cadastrada. Nº BM permanece fora do frontend e dos dados públicos carregados pela página.

## Validação

```bash
python scripts/personnel_pipeline.py audit --input data/data.js
python scripts/site_audit.py
```

O workflow `.github/workflows/python-personnel-audit.yml` executa os gates em PRs e em `main`. Em produção, `scripts/live_smoke.py` executa 30 verificações na URL pública, incluindo preservação do layout, WhatsApp direto e ausência de resíduos de bastidores no frontend.

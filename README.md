# DAI/2 · Efetivo e TPB 2026

Painel estático do CBMMG/DAI para consulta gerencial de efetivo DAI/2 em órgãos externos, DDQOD e claro por posto/graduação, rastreabilidade funcional quando o ato está localizado e acompanhamento do TPB 2026 da DAI.

## Interface 2.1.0 · layout original preservado

A versão 2.1.0 mantém a arquitetura visual original do portal. Não há redesign da página principal.

Foram preservados: splash inicial, onboarding, banner, título, quadro de dados gerais, atalhos, painel de aniversariantes, legenda de cores, campos de pesquisa, organização em linhas, os 18 blocos dos órgãos, botão de previsão DDQOD, modais e rodapé.

Os ajustes foram implementados dentro dessa estrutura:

- TPB 2026 da DAI acessível por um novo botão na área já existente de atalhos e exibido em modal, sem criar nova navegação ou reorganizar a página;
- cálculo de claro por posto/graduação;
- SEMAD tratada como implantação extra-DDQOD, com 0 previsto no DDQOD consultado e 1 militar em exercício;
- dados canônicos consolidados em `data/data.js`, sem `runtime-updates.js`;
- camada pública sem Nº BM, telefone ou aniversário;
- gráficos mantidos nos mesmos canvases dos blocos, agora desenhados localmente e sem dependência de Chart.js;
- onboarding persistente após a primeira visualização;
- melhorias de teclado, foco, contraste, alvos de toque e `prefers-reduced-motion` sem alteração da composição visual;
- imagens remotas do splash/banner mantidas apenas como elementos decorativos do layout original, com fundo local de contingência caso não carreguem;
- CI em `pull_request` e `push` para `main`, com gate específico que reprova alterações estruturais do layout original.

A versão dos dados permanece `2.0.0`; a versão `2.1.0` identifica a interface compatível com o layout original.

## Fontes de corte

Efetivo DAI/2: ficha-mestre dos órgãos externos, validação de 17/08/2026.

DDQOD: Anexo C da Resolução nº 1.268/2025, quadro consultado.

TPB: `Dashboard TPB DAI 2026 - controle por ata - 03-09-2026.xlsx`, corte 03/09/2026.

Ato individual vigente e fonte primária prevalecem sobre qualquer síntese gerencial exibida na página.

## Regra do TPB

`TPB FEITO` significa participação comprovada em lista/ata ou consolidada como concluída/regularizada na fonte governada. Dispensa definitiva permanece separada e não é contabilizada como TPB feito.

No corte de 03/09/2026:

- escopo controlado: 85;
- TPB feito: 69;
- TPB não feito: 16;
- dispensa definitiva: 9;
- não feito e sem dispensa: 7;
- feito com data da evidência a recuperar: 15.

A planilha-fonte contém 4 históricos de ciclo com ano divergente de 2026. Esses históricos foram neutralizados na camada executiva e não são usados como evidência de conclusão ou programação.

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

## Segurança e privacidade

A camada pública usa apenas os campos necessários para consulta gerencial nominal: posto/graduação, nome, órgão e subunidade. Nº BM, telefone, aniversário e outros dados pessoais não necessários à consulta não são publicados.

## Validação

```bash
python scripts/personnel_pipeline.py audit --input data/data.js
python scripts/site_audit.py
```

O workflow `.github/workflows/python-personnel-audit.yml` executa os gates em PRs e em `main`. Em produção, `scripts/live_smoke.py` executa 30 verificações na URL pública, incluindo preservação do layout original.
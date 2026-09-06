# DAI/2 · Efetivo e TPB 2026

Painel estático do CBMMG/DAI para consulta gerencial de:

- efetivo DAI/2 em órgãos externos;
- DDQOD e claro por posto/graduação;
- rastreabilidade funcional quando o ato está localizado;
- acompanhamento mobile-first do TPB 2026 para o escopo DAI controlado.

## Versão 2.0.0

Principais mudanças:

- arquitetura mobile-first;
- TPB 2026 integrado ao painel, com velocímetro, KPIs, pendências, próximos ciclos e consulta individual;
- remoção de Chart.js e de imagens/dependências remotas obrigatórias;
- cálculo de claro por posto/graduação;
- SEMAD tratada como implantação extra-DDQOD, com 0 previsto no DDQOD consultado;
- dados canônicos consolidados em `data/data.js`;
- nenhuma mutação de dados em runtime;
- camada pública não publica Nº BM;
- onboarding persistente e acessibilidade de teclado/dialog;
- CI em `pull_request` e `push` para `main`.

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

## Segurança e privacidade

A camada pública usa apenas os campos necessários para consulta gerencial nominal: posto/graduação, nome, órgão e subunidade. Nº BM, telefone, aniversário e outros dados pessoais não necessários à consulta não são publicados.

## Validação

```bash
python scripts/personnel_pipeline.py audit --input data/data.js
python scripts/site_audit.py
```

O workflow `.github/workflows/python-personnel-audit.yml` executa os gates em PRs e em `main`.

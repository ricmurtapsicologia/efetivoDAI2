# Auditoria final DAI/2 · v2.0.0

Data: 05/09/2026.

## Resultado executivo

- Auditoria 30/30: 30/30 controles aplicáveis aprovados.
- Auditoria 90/90: 58/58 controles aplicáveis aprovados; 32 controles estritamente de produto impresso classificados como não aplicáveis; 0 reprovações aplicáveis.
- Smoke local: 320, 360, 390, 412, 768 e 1024 px sem overflow horizontal, nenhum alvo interativo abaixo de 44×44 px, tipografia operacional >=14 px, zero erro de console/página.
- Invariantes: DDQOD 101; efetivo 84; claro P/G 23; excedentes P/G DDQOD 5; SEMAD 1 extra-DDQOD.
- TPB 03/09/2026: escopo 85; feito 69; não feito 16; dispensados 9; exigem ação 7; data a conferir 15.

## Correções estruturais concluídas

1. Fonte canônica consolidada em `data/data.js`.
2. Remoção de `runtime-updates.js` e de mutações de dados em runtime.
3. SEMAD tratada como implantação extra-DDQOD, com 0 previsto no DDQOD consultado.
4. Claro calculado por posto/graduação; excedentes não compensam vagas de outra graduação.
5. TPB DAI integrado em arquitetura mobile-first.
6. Camada pública sem Nº BM, telefone ou aniversário.
7. Remoção de Chart.js e de imagens remotas obrigatórias.
8. UI sem `innerHTML` para dados; diálogos nativos e suporte a teclado/foco.
9. `prefers-reduced-motion`, safe-area e navegação mobile implementados.
10. CI em pull request e push para main com auditoria da allowlist e invariantes de produção.

## Observações de fonte

O TPB é derivado de `Dashboard TPB DAI 2026 - controle por ata - 03-09-2026.xlsx`. Quatro históricos de ciclo continham ano divergente de 2026; foram neutralizados na camada executiva e não são usados como evidência de conclusão ou programação.

Ato individual vigente e fonte primária prevalecem sobre sínteses gerenciais exibidas no portal.

## Gate de publicação

A versão só deve ser promovida após CI verde no PR e deve receber smoke de produção depois do deploy do GitHub Pages.

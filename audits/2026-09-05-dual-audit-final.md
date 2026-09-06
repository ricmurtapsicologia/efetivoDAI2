# Auditoria final DAI/2 · interface 2.1.0

Data: 05/09/2026.

## Diretriz canônica desta versão

O layout visual original da página DAI/2 é requisito de preservação. Correções de dados, segurança, acessibilidade, TPB e governança devem ocorrer dentro da arquitetura já existente, sem redesign da página principal.

Elementos canônicos preservados: splash, onboarding, banner, título, dados gerais, atalhos, painel de aniversariantes, legenda, pesquisas, organização em linhas, 18 blocos de órgãos com canvas, previsão DDQOD, modais e rodapé.

## Resultado executivo — rodada pós-restauração do layout

- Auditoria 30/30: 30/30 controles aplicáveis aprovados; 0 reprovações.
- Auditoria 90/90: 56 controles aplicáveis aprovados, 2 aprovados com ressalva, 32 controles estritamente de produto impresso classificados como não aplicáveis; 0 reprovações aplicáveis.
- Ressalvas 90/90: controles 40 (direção de arte fotográfica) e 41 (seleção/tratamento fotográfico). As imagens remotas históricas do splash e banner foram mantidas para preservar a identidade visual solicitada, mas são exclusivamente decorativas e possuem fundo local de contingência; nenhuma função ou dado depende delas.
- Gate automatizado do PR: aprovado, incluindo verificação explícita de preservação do layout original e dos invariantes de produção.
- Invariantes: DDQOD 101; efetivo 84; claro P/G 23; excedentes P/G DDQOD 5; SEMAD 1 extra-DDQOD e 0 previsto no DDQOD consultado.
- TPB 03/09/2026: escopo 85; feito 69; não feito 16; dispensados 9; exigem ação 7; data a conferir 15.

## Correções concluídas sem redesign

1. Layout original restaurado como composição canônica da página.
2. Fonte canônica consolidada em `data/data.js`.
3. Remoção de `runtime-updates.js` e de mutações de dados em runtime.
4. SEMAD tratada como implantação extra-DDQOD, sem criação artificial de vaga prevista.
5. Claro calculado por posto/graduação; excedentes não compensam vagas de outra graduação.
6. Gráficos mantidos nos canvases originais dos blocos, porém redesenhados por código local para representar vagas preenchidas e claro sem sobreposição matemática indevida.
7. TPB DAI integrado por botão na área já existente de atalhos e apresentado em modal, preservando a página principal.
8. Camada pública sem Nº BM, telefone ou aniversário.
9. Pesquisa nominal limitada a nome, posto/graduação, órgão e subunidade.
10. Rastreabilidade funcional apresentada quando há evidência cadastrada; lacunas documentais não são inferidas.
11. Onboarding mantido, com persistência resiliente após a primeira visualização.
12. Acessibilidade aprimorada com foco visível, teclado nos blocos, Escape/retorno de foco nos modais, contraste, alvos de toque e `prefers-reduced-motion`.
13. Chart.js removido sem retirar os gráficos do layout.
14. Imagens remotas históricas mantidas apenas como decoração visual, com fallback local para indisponibilidade.
15. CI em PR e `main` com auditoria de allowlist, invariantes de produção e gate de preservação do layout.
16. Smoke público de 30 pontos configurado para reprovar se a versão publicada perder qualquer elemento estrutural canônico do layout original.

## Observações de fonte

O TPB é derivado de `Dashboard TPB DAI 2026 - controle por ata - 03-09-2026.xlsx`. Quatro históricos de ciclo continham ano divergente de 2026; foram neutralizados na camada executiva e não são usados como evidência de conclusão ou programação.

Ato individual vigente e fonte primária prevalecem sobre sínteses gerenciais exibidas no portal.

## Gate de publicação

A publicação só é considerada concluída após: CI verde no PR, merge em `main`, GitHub Pages concluído com sucesso e smoke público 30/30 aprovado na URL efetivamente publicada. O resultado do smoke pós-deploy fica registrado nos logs do workflow de produção.
# DAI/2 — Auditoria Completa em 3 Camadas · UI 2.5.0

**Data:** 07/09/2026  
**Commit auditado em produção:** `20891ab8590fd3e6c23cfaa867f550032c3aaeb7`  
**URL:** https://ricmurtapsicologia.github.io/efetivoDAI2/  

## Veredito executivo

**APROVADO PARA USO, SEM FALHA FUNCIONAL.**

A não conformidade P1 do WhatsApp foi encerrada. O número está visível em cada registro e o botão abre diretamente o destinatário correspondente. A cobertura do diretório é 84/84.

Permanecem duas ressalvas de governança, sem bloqueio funcional:

1. os números de WhatsApp são publicados intencionalmente no portal público; a manutenção dessa exposição deve permanecer como decisão institucional explícita;
2. o hero é hospedado externamente no Unsplash. A fonte, fotógrafa e licença estão documentadas e o CI testa o carregamento real, porém ainda existe dependência operacional de terceiro.

## Camada 1 — Auditoria 30/30 Institucional/Técnica

**Resultado:** 28 PASS · 2 PASS COM RESSALVA · 0 FAIL.

1. Smoke test — PASS  
2. Pinpoint audit — PASS  
3. Deep audit — PASS  
4. Consistency test — PASS  
5. Contradiction scan — PASS  
6. Completeness audit — PASS  
7. Traceability audit — PASS  
8. Compliance test — PASS COM RESSALVA: diretório WhatsApp público por decisão funcional explícita.  
9. Regression test — PASS  
10. Change-impact analysis — PASS  
11. Cross-reference test — PASS  
12. Link integrity — PASS  
13. Visual QA — PASS  
14. Accessibility — PASS  
15. Usability — PASS  
16. Cognitive-load — PASS  
17. Narrative-flow — PASS  
18. Red-team — PASS  
19. Edge-case test — PASS  
20. Scenario stress test — PASS  
21. Fact-check audit — PASS  
22. Citation audit — PASS  
23. Source-to-claim test — PASS  
24. Legal defensibility — PASS COM RESSALVA: exposição pública dos números deve permanecer respaldada pela governança institucional aplicável.  
25. Decision-readiness — PASS  
26. Publication preflight — PASS  
27. Version-drift audit — PASS  
28. Canonical-template test — PASS  
29. Duplication/redundancy scan — PASS  
30. Terminology audit — PASS  

**Smoke público pós-deploy:** 30/30 PASS.

## Camada 2 — Auditoria Editorial Profissional 90/90

Os 90 controles canônicos foram preservados e adaptados ao produto web. Controles estritamente físicos de publicação impressa são N/A.

**Resultado:** 59 PASS · 1 PASS COM RESSALVA · 30 N/A · 0 FAIL.

### Controles 1–14 · Estratégia, arquitetura e conteúdo

1. Propósito editorial — PASS  
2. Público leitor — PASS  
3. Experiência de leitura — PASS  
4. Arquitetura global — PASS  
5. Partes/unidades — PASS  
6. Progressão informacional — PASS  
7. Extensão e densidade — PASS  
8. Edição de desenvolvimento — PASS  
9. Edição substantiva — PASS  
10. Linguagem e terminologia — PASS  
11. Revisão especializada — PASS  
12. Fontes/referências/atribuições — PASS  
13. Copyediting — PASS  
14. Revisão ortotipográfica — PASS  

### Controles 15–37 · Projeto editorial/tipográfico

15. Formato físico — N/A  
16. Mancha gráfica — PASS  
17. Margens — PASS  
18. Gutter — N/A  
19. Família tipográfica principal — PASS  
20. Família tipográfica complementar — PASS  
21. Corpo de texto — PASS  
22. Entrelinha — PASS  
23. Comprimento de linha — PASS  
24. Tracking/kerning — PASS  
25. Hierarquia tipográfica — PASS  
26. Estilos de parágrafo/caractere — PASS  
27. Recuos/espaçamentos — PASS  
28. Hifenização/justificação — PASS  
29. Rios de branco — N/A  
30. Viúvas/órfãs/runts — N/A  
31. Baseline grid — N/A  
32. Alinhamento em páginas confrontantes — N/A  
33. Fólios/cabeçalhos/rodapés — PASS  
34. Lógica par/ímpar — N/A  
35. Aberturas de partes — PASS  
36. Aberturas de capítulos — PASS  
37. Identidade iconográfica — PASS  

### Controles 38–50 · Linguagem visual

38. Linguagem gráfica funcional — PASS  
39. Relação texto–imagem — PASS  
40. Direção de arte fotográfica — PASS  
41. Seleção/tratamento fotográfico — PASS  
42. Ilustrações autorais — N/A  
43. Infográficos — PASS  
44. Fluxogramas/algoritmos — N/A  
45. Organogramas/mapas/linhas do tempo — N/A  
46. Precisão dos infográficos — PASS  
47. Legendas/fontes/créditos visuais — PASS  
48. Acessibilidade visual — PASS  
49. Paleta cromática — PASS  
50. Função semântica da cor — PASS  

### Controles 51–66 · Identidade e ritmo

51. Capa/hero digital — PASS  
52. Lombada — N/A  
53. Quarta capa — N/A  
54. Coerência capa–miolo — PASS  
55. Créditos/expediente — PASS  
56. Ficha catalográfica/ISBN — N/A  
57. Sumário profissional — N/A  
58. Índices/listas — PASS  
59. Boxes/quadros — PASS  
60. Conversão de quadros em prosa — N/A  
61. Elementos pedagógicos — N/A  
62. Ritmo visual — PASS  
63. Spreads — N/A  
64. Espaços negativos — N/A  
65. Equilíbrio de massa visual — PASS  
66. Imagens x margens/viewport — PASS  

### Controles 67–90 · Produção, prova e entrega

67. Revisão de tabelas — N/A  
68. Redesenho de tabelas — N/A  
69. Resolução de imagens — PASS: hero carregado em 2400×1599 no teste real.  
70. Perfis de cor — PASS  
71. CMYK — N/A  
72. Sangria — N/A  
73. Marcas/especificações de impressão — N/A  
74. Fontes incorporadas — PASS  
75. Links/ações — PASS: WhatsApp direto ao destinatário testado.  
76. Prova após diagramação — PASS  
77. Prova visual — PASS  
78. Prova de imposição/encadernação — N/A  
79. Boneco físico — N/A  
80. Avaliação em mão — N/A  
81. Soft proof de impressão — N/A  
82. Preflight PDF — N/A  
83. Bleed/marcas/saída — N/A  
84. Capa/lombada final — N/A  
85. Sumário x paginação — N/A  
86. Referências cruzadas — PASS  
87. Consistência títulos/legendas — PASS  
88. Correções finais pós-diagramação — PASS  
89. Aprovação editorial final — PASS  
90. Master e derivados finais — PASS COM RESSALVA: hero continua hospedado externamente; proveniência e teste de disponibilidade estão implementados.

## Camada 3 — Experiência e Qualidade Aplicada

**Resultado total:** 47/47 PASS.

- E2E: 18/18 PASS
- QA: 10/10 PASS
- Acessibilidade: 5/5 PASS
- UX: 6/6 PASS
- UI: 5/5 PASS
- Dados/limites funcionais: 3/3 PASS

### Evidências principais

- hero corporativo carregado efetivamente em 2400×1599;
- 18 blocos renderizados;
- 101 previstos, 84 existentes e claro P/G 23;
- cada militar exibido no modal possui número visível e botão WhatsApp;
- Silvana Tiengo exibida com `+55 (31) 99174-3862`;
- botão de Silvana abre `wa.me/5531991743862` diretamente;
- número legado de Diego Natalino é normalizado para `+55 (31) 98849-7210`;
- cobertura do diretório: 84/84;
- mobile 375 px sem overflow horizontal;
- controles com nomes acessíveis e alvos de toque ≥44 px;
- nenhum erro JavaScript;
- TPB preservado em formato agregado: 85 / 69 / 16 / 9 / 7 / 15.

## Infraestrutura

GitHub Actions atualizado para:

- `actions/checkout@v6`;
- `actions/setup-python@v6`;
- `actions/upload-artifact@v6`.

O aviso anterior de ações executando em runtime Node 20 foi eliminado.

## Decisão final

**Página DAI/2 UI 2.5.0: APROVADA PARA USO.**  
**Falhas críticas/altas funcionais: 0.**  
**Pendências bloqueadoras: 0.**  
**Ressalvas de governança: 2, ambas não bloqueadoras.**

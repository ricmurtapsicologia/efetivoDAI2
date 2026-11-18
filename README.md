# Portal DAI/2 — Efetivo em Órgãos Externos

Portal estático para consulta à distribuição do efetivo, às vagas previstas por posto/graduação (P/G), aos fundamentos documentais correlatos e ao TPB 2026.

**Página:** https://ricmurtapsicologia.github.io/efetivoDAI2/  
**Interface:** 2.7.0 · 18/11/2026.

## Escopo e posição da base

A interface apresenta **17 blocos ativos**, incluindo a Coordenação DAI/2 e a implantação SEMAD.

- **Efetivo:** ficha-mestre com referência geral de **17/08/2026**.
- **Ajuste do escopo:** 18/11/2026, com retirada de uma estrutura desativada. A data não representa uma nova conferência de todas as lotações.
- **DDQOD:** Anexo C da Resolução nº 1.268/2025; a soma exibida é a do recorte da página, e não uma alteração do instrumento oficial.
- **SEMAD:** implantação extra-DDQOD, com 0 vagas previstas na base consultada e 1 militar em exercício.
- **TPB 2026:** Ofício CBMMG/DAI-2 nº 569/2026 (SEI 151390924). Em 14/10/2026, a informação administrativa registra 0 pendências declaradas e conclusão do TPB pelos militares ativos, sem quantitativo nominal correspondente à base deste portal.

### Indicadores recalculados

| Indicador | Resultado |
|---|---:|
| Blocos ativos | 17 |
| Vagas previstas no recorte | 97 |
| Militares cadastrados | 82 |
| Claros por P/G | 20 |
| Excedentes por P/G, exceto implantação extra-DDQOD | 4 |
| Efetivo extra-DDQOD (SEMAD) | 1 |

**Cálculo do claro:** `max(previsto_PG - existente_PG, 0)`, separadamente por posto/graduação em cada órgão. Excedentes de uma P/G não compensam claros de outra. Os totais são calculados de `data/data.js`; não são números fixos no HTML.

## Recursos da página

- Visão geral e gráficos em Canvas de preenchimento das vagas por órgão.
- Consulta nominal e pesquisa por nome, posto/graduação, órgão ou contato funcional.
- Acesso direto ao WhatsApp funcional disponível em cada registro.
- Pesquisa de claros por posto/graduação e consulta às vagas do DDQOD.
- Modais acessíveis de relação de militares, instrumentos correlatos e situação agregada do TPB.
- Onboarding na primeira visita, acesso direto em visitas posteriores, skip link, foco visível, navegação por teclado, fechamento de modais com Escape e respeito a movimento reduzido.

O módulo de decisões e prioridades, seus indicadores, checklist, filtros e funções auxiliares **foram removidos integralmente**. A consulta ao efetivo e aos documentos mantém seu fluxo independente.

## Estrutura de arquivos

| Caminho | Responsabilidade |
|---|---|
| `index.html` | Interface, estrutura semântica, atalhos, modais e metadados sociais |
| `data/data.js` | Metadados, DDQOD, lotações e referências jurídicas |
| `data/contacts.js` | Diretório de contatos funcionais |
| `data/tpb.js` | Posição documental agregada do TPB |
| `assets/js/app.js` | Cálculos, pesquisa, gráficos, modais e navegação |
| `assets/css/main.css` | Layout e responsividade |
| `assets/css/banner-cbmmg.css` | Hero e identidade visual |
| `scripts/personnel_pipeline.py` | Validação e importação supervisionada da base |
| `scripts/site_audit.py` | Consistência de dados, privacidade e regressões estruturais |
| `scripts/browser_e2e.py` | Teste de interface com Playwright |
| `scripts/live_smoke.py` | Verificação da publicação no GitHub Pages |

Os blocos são identificados no DOM, sem mapa de órgãos duplicado no código JavaScript. A auditoria exige correspondência exata entre órgãos renderizados e DDQOD e rejeita lotações fora desse escopo.

## Fontes, privacidade e limitações

O site é público, estático e **não possui autenticação**. Nomes, postos/graduações, lotações e contatos funcionais cadastrados ficam acessíveis publicamente. A publicidade do diretório de contatos exige autorização e revisão institucional de privacidade; GitHub Pages não deve ser usado para registros sigilosos.

Nº BM, e-mails, aniversários e informações individuais de TPB não integram a apresentação. Os fundamentos documentais são referências, não comprovação de vigência ou substituição de atos oficiais; prevalecem a ficha-mestre, os instrumentos vigentes e o SEI.

O crédito e a licença da imagem do banner estão identificados no próprio hero e nos arquivos de proveniência de `assets/`.

## Executar e validar

Inicie um servidor local na raiz do repositório:

```bash
python -m http.server 8000
```

Audite as informações:

```bash
python scripts/personnel_pipeline.py audit --input data/data.js
python scripts/site_audit.py
```

Execute os testes de navegador:

```bash
python -m pip install playwright
python -m playwright install chromium
python scripts/browser_e2e.py
```

Após publicar em `main`, verifique a versão pública:

```bash
python scripts/live_smoke.py
python scripts/share_preview_smoke.py
```

O workflow `.github/workflows/python-personnel-audit.yml` automatiza auditorias de dados, testes de interface e smoke pós-publicação.

## Rotina de manutenção

1. Validar alterações de lotação, vagas e contatos em documentos oficiais.
2. Editar a base canônica, sem inserir números derivados no HTML.
3. Registrar a data específica da alteração sem confundi-la com a data de conferência geral.
4. Executar auditorias e testes antes da publicação.
5. Confirmar a publicação e as condições de acesso aos dados.

O formulário de reunião da DAI/2 utiliza a mesma relação atualizada de áreas; a versão de Apps Script requer publicação própria quando usada fora do GitHub Pages.

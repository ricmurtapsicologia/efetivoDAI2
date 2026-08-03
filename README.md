# Efetivo DAI/2 — Órgãos Externos

Portal estático de consulta da distribuição de efetivo da DAI/2.

## Versão

**v1.1.0 — 03/08/2026**

Refatoração conservadora do portal original. O frontend foi preservado: splash, onboarding, banner, fotografia, layout de cards, gráficos, pesquisa, modais, painel de aniversariantes e consulta jurídica mantêm a mesma apresentação e fluxo de uso.

## Atualização de efetivo

Fonte utilizada para a relação nominal:

`Planilha de Efetivo da DAI-2 _ Órgãos Externos(3).xlsx` — aba `TABELA`.

Foram considerados somente os dados necessários às funcionalidades já existentes na página:

- posto/graduação;
- nome completo;
- órgão;
- unidade do CTPM, quando existente;
- contato.

Campos administrativos adicionais da planilha, como número BM, e-mail, sexo, função e situação funcional, não foram publicados nesta versão.

## Resultado da atualização

- efetivo nominal atual: **82 militares**;
- DDQOD original mantido: **101 posições previstas**;
- o quantitativo existente e o claro por órgão são calculados dinamicamente a partir da base nominal;
- a distribuição prevista por P/G permanece a mesma do portal original.

## Arquitetura

```text
/
├── index.html
├── assets/
│   ├── css/
│   │   └── main.css
│   └── js/
│       └── app.js
├── data/
│   └── data.js
└── README.md
```

### Responsabilidades

- `index.html`: estrutura visual e semântica do portal;
- `assets/css/main.css`: estilos originais do frontend;
- `assets/js/app.js`: splash, onboarding, pesquisa, gráficos, modais, aniversários e cálculos;
- `data/data.js`: fonte nominal do efetivo, aniversários preservados, DDQOD original e instrumentos jurídicos correlatos.

## Regra de manutenção

Para novas atualizações de pessoal, alterar prioritariamente o bloco `DAI2_PERSONNEL` em `data/data.js`. O `index.html` não deve voltar a armazenar nomes, telefones ou listas nominais.

## Observação sobre aniversários

A planilha-fonte atual não contém data de aniversário. Por isso, foram preservadas apenas as datas já existentes no portal anterior para militares que permanecem na relação. Novos militares não receberam datas inferidas ou inventadas.

## Compatibilidade visual

A refatoração foi desenhada para não modificar o layout percebido pelo usuário. O objetivo é reduzir acoplamento e facilitar manutenção sem redesenhar o portal.

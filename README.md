# Efetivo DAI/2 — Órgãos Externos

Portal estático de consulta da distribuição de efetivo da DAI/2.

## Versão

**v1.1.1 — 03/08/2026**

Ajuste cirúrgico de efetivo no TJMMG sobre a arquitetura conservadora v1.1.0, sem alteração de layout, splash, onboarding, banner, cards, gráficos, pesquisa ou demais elementos do frontend.

### Alteração da v1.1.1

- removido do efetivo do TJMMG: **1º Sgt Rinaldo Cézar Fontes Cruz**;
- removida também a data de aniversário anteriormente associada a esse registro;
- incluído no TJMMG: **3º Sgt Diego Natalino dos Santos**;
- contato cadastrado: **+55 31 8849-7210**;
- a troca é 1 por 1 no mesmo órgão, portanto não altera o efetivo total nem o claro quantitativo do TJMMG;
- a validação do botão de WhatsApp foi ajustada para aceitar este número exatamente no formato informado, sem inserir dígito inexistente;
- cache de `data.js` e `app.js` atualizado para `v1.1.1`.

## Atualização de efetivo

A base nominal principal foi originalmente consolidada a partir de `Planilha de Efetivo da DAI-2 _ Órgãos Externos(3).xlsx`, aba `TABELA`, e recebe posteriormente movimentações pontuais formalmente informadas.

São publicados somente os dados necessários às funcionalidades da página: posto/graduação, nome, órgão, unidade do CTPM quando existente e contato. Número BM, e-mail, sexo, função, origem administrativa e demais campos administrativos não são publicados no portal.

## Resultado atual

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

Datas de aniversário são mantidas somente quando já conhecidas na base anterior. Novos militares não recebem datas inferidas ou inventadas.

## Compatibilidade visual

A arquitetura foi desenhada para não modificar o layout percebido pelo usuário. O objetivo é reduzir acoplamento e facilitar manutenção sem redesenhar o portal.

# Camada Python — Efetivo DAI/2

## Estado de segurança

Esta camada é aditiva. O portal atual continua consumindo `data/data.js` e nenhum arquivo do frontend foi alterado.

Ponto de rollback: `backup/pre-python-20260809`.

## O que já funciona

- `python scripts/personnel_pipeline.py audit` valida a base atual sem alterá-la;
- bloqueia campos fora da allowlist pública (`rank`, `name`, `org`, `subunit`, `phone`);
- detecta nomes duplicados, órgãos inexistentes, campos obrigatórios vazios e inconsistências básicas;
- compara quantidade existente com DDQOD e sinaliza excessos como alerta;
- `build` aceita futura planilha XLSX, gera somente `artifacts/data.generated.js` e um relatório de diferenças;
- a planilha de origem com colunas sensíveis é bloqueada por padrão e exige liberação explícita apenas para leitura; os campos sensíveis nunca são emitidos.

## Promoção segura

A saída gerada não substitui `data/data.js` automaticamente. Primeiro revisar `artifacts/personnel-diff.json`; somente depois promover deliberadamente o candidato.

## Comandos

```bash
python scripts/personnel_pipeline.py audit --input data/data.js
pip install openpyxl
python scripts/personnel_pipeline.py build --xlsx caminho/efetivo.xlsx
```

O workflow `Python personnel audit` executa a auditoria em pull requests relevantes e impede que uma base inválida seja aceita silenciosamente.

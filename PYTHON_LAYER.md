# Auditoria Python — Portal DAI/2

A base de efetivo permanece em `data/data.js`. A camada Python audita e prepara possíveis atualizações, sem publicá-las automaticamente.

- Campos permitidos em cada registro: `rank`, `name`, `org`, `subunit`.
- Contatos funcionais ficam em `data/contacts.js` e são conferidos pela auditoria do portal.
- Órgãos sem previsão cadastrada ou dados inválidos são sinalizados antes da publicação.
- Dados sensíveis da fonte XLSX não devem aparecer na camada pública.

### Comandos

```bash
python scripts/personnel_pipeline.py audit --input data/data.js
python scripts/site_audit.py
python scripts/personnel_pipeline.py build --xlsx caminho/efetivo.xlsx
```

O comando `build` produz um arquivo candidato e relatório de diferenças em `artifacts/`, para validação antes de eventual promoção. O workflow `.github/workflows/python-personnel-audit.yml` executa as auditorias e testes em alterações relevantes.

A correspondência entre DDQOD, lotações e blocos da interface é obrigatória. O recorte ativo contém 17 órgãos/blocos e não altera os atos oficiais.

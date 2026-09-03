# Contribuindo

FocusLens BR é um projeto pessoal e educacional — não está aberto a roadmap
externo nem aceita mudanças de escopo de produto por terceiros. Ainda assim,
correções técnicas (bug, typo, teste faltando) são bem-vindas via PR.

## Rodando localmente

Instruções completas de setup (Python fora do OneDrive, `.venv`, mobile) estão
no README: [rodar o app móvel](README.md#como-rodar-o-app-móvel) e
[rodar a referência Streamlit](README.md#como-rodar-a-referência-streamlit).
Resumo dos gates antes de abrir PR:

```bash
# Python
ruff check .
pytest tests/ -q --cov=. --cov-report=term-missing

# Mobile (dentro de mobile/)
npm run typecheck
npm test
```

## Convenções de código

- Separação motor puro (`focuslens/core/`) → adaptador de I/O
  (`focuslens/adapters/`) → apresentação (`focuslens/ui/`, `mobile/src/`).
  Motor puro não faz rede nem I/O; testes de motor não devem precisar de mock.
- Nenhum texto ou regra de indicador usa linguagem imperativa de investimento
  ("invista", "compre", "venda", "recomendo") — é conteúdo educacional, nunca
  recomendação personalizada. `tests/test_focus_regras.py` verifica isso
  automaticamente.
- Nunca versionar planilha B3 real, dado de carteira pessoal ou segredo. Testes
  de importação geram XLSX sintético em memória.
- Lint (`ruff`) e cobertura mínima (85%, `pyproject.toml`) são obrigatórios no
  CI; PR que não passar não é revisado.

## Escopo de PR

PRs pequenos e de intenção única (uma correção por vez) são mais fáceis de
revisar e têm chance real de merge. Mudanças de arquitetura ou de escopo de
produto devem abrir uma issue de discussão antes do código.

# Contribuindo

Este é um projeto pessoal e educacional. O trabalho das IAs autorizadas pelo titular acontece
diretamente na `main`, com commits pequenos e escopados. O repositório não mantém um fluxo de
Pull Request para colaboração externa nem recebe mudanças de roadmap por terceiros.

Antes de editar, leia [`AGENTS.md`](AGENTS.md) e o
[`protocolo de coordenação`](docs/coordenacao/PROTOCOLO.md). Comece com:

```bash
python scripts/equipe.py iniciar
python scripts/equipe.py reservar ID --agente NOME --maquina NOME
```

## Rodando localmente

Instruções completas de setup (Python fora do OneDrive, `.venv`, mobile) estão no README:
[rodar o app móvel](README.md#como-rodar-o-app-móvel) e
[rodar a referência Streamlit](README.md#como-rodar-a-referência-streamlit). Antes de qualquer
push, rode os gates aplicáveis:

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
- Lint (`ruff`) e cobertura mínima (85%, `pyproject.toml`) são obrigatórios no CI.

## Fechando o trabalho

Faça commit somente dos caminhos da tarefa, nunca `git add -A` às cegas. Antes do push, rode
`git pull --rebase --autostash`. Ao terminar, registre o resultado e libere a reserva:

```bash
python scripts/equipe.py fechar --resumo "O que mudou" --proximo "O que falta"
```

Mudanças de arquitetura ou escopo exigem decisão explícita do titular e registro no protocolo.

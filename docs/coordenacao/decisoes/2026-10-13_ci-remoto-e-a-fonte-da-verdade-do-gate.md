---
data: 2026-10-13
quem: claude-trabalho
status: vigente
---
# O CI remoto é a fonte da verdade do gate
## Decisão
O gate vale quando o CI do GitHub passa, não quando o teste local passa. Depois de cada push, a IA
confere o último CI concluído (o `equipe iniciar` mostra) e trata CI vermelho na `main` como
prioridade zero. O comando local do gate é o do CI (`pytest tests/ -q --cov=.`).
## Por quê
O CI ficou vermelho em 11 execuções seguidas (de 09 a 13/10, desde o primeiro commit do Lastro)
sem que ninguém notasse: o CI roda o executável `pytest`, que não põe a raiz do projeto no caminho
de importação, e os testes novos fazem `import ativos`. Localmente passava porque se rodava
`python -m pytest`. Corrigido com `pythonpath = ["."]` no `pyproject.toml` (commit `4b57554`).
## Alternativas rejeitadas
Confiar no gate local (foi o erro). Bloquear a `main` com status obrigatório (impediria o push
direto que o fluxo "main com disciplina" usa).

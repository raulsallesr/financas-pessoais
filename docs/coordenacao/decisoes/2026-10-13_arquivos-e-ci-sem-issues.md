---
data: 2026-10-13
quem: raul
status: vigente
---
# Coordenação em arquivos versionados e verificação no CI, sem Issues por ora
## Decisão
A verdade do estado do projeto vive em arquivos do repositório (`docs/coordenacao/`). O GitHub
entra com o CI (testes do protocolo e varredura de segredos), as tags `ckpt-*` e o ajuste dos
robôs. Sem Issues, Project ou Pull Request obrigatório.
## Por quê
Arquivos funcionam em qualquer máquina, sem login nem `gh`, e têm histórico. Sem `gh` no
trabalho e sem garantia de login em casa, Issues deixariam as IAs cegas.
## Alternativas rejeitadas
Espelho em Issues e Project (dois lados para manter alinhados). Issues como fonte da verdade.

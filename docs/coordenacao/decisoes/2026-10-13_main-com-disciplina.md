---
data: 2026-10-13
quem: raul
status: vigente
---
# Fluxo git: main com disciplina
## Decisão
Todas as IAs commitam na `main`, sempre com `git pull --rebase --autostash` antes do push,
reserva anunciada no quadro e suíte verde antes de empurrar. Branch só para refatoração grande
(ex.: item 1.6b), integrada por fast-forward. A `main` já bloqueia force-push e histórico não
linear (ruleset do GitHub).
## Por quê
O Raul é iniciante em Git e o `gh` não existe na máquina do trabalho, então Pull Request não
é automático lá. O trabalho é majoritariamente sequencial entre máquinas.
## Alternativas rejeitadas
Branch e PR sempre (mais passos, exige instalar o gh ou usar o navegador). Branch por máquina
(atrasa a visibilidade).

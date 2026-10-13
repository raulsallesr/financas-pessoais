---
data: 2026-10-13
origem: claude-trabalho
status: nova
---
# Tirar o repositório do OneDrive no PC do trabalho
## Problema
A pasta do projeto fica dentro do hub sincronizado pelo OneDrive. Isso já causou
`WinError 5` na limpeza de temporários, instalação de pacotes que trava e escritas concorrentes
de várias sessões sem aviso.
## Proposta
Clonar o repositório numa pasta curta fora do OneDrive (por exemplo `C:\dev\financas-pessoais`) e
manter no hub só um ponteiro. Decisão do Raul: mexe no caminho que o SuperHub e outros
processos usam.
## Custo e risco
Baixo técnico, médio de organização. Exige avisar o SuperHub e o Codex do novo caminho.

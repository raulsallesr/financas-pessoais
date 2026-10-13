# Protocolo de coordenação (IAs e máquinas)

Como as IAs que trabalham no Lastro (Claude, Codex e outras, no PC do trabalho e no PC de
casa) se comunicam sem memória compartilhada. O Raul não precisa ser o mensageiro: o que
importa fica **em arquivos do repositório**, e o GitHub sincroniza as máquinas. Decisão do
Raul de 2026-10-13. Esta página é a fonte das regras; `AGENTS.md` (raiz) é o resumo que
qualquer IA lê primeiro.

## Princípios

1. **A verdade vive em arquivos versionados.** Funcionam em qualquer máquina, sem login e
   sem `gh`. Nada importante fica só numa conversa.
2. **Um arquivo por evento** (reserva, sessão, ideia, decisão, checkpoint). Duas IAs nunca
   editam o mesmo arquivo, então não há conflito. `INDICE.md` é **gerado**, nunca editado.
3. **Um comando por rotina**: `python scripts/equipe.py <comando>` (Python puro, sem instalar
   nada). O Raul não decora comandos de git.
4. **Verificar antes de confiar.** O que outra IA entregou é reconferido (suíte, pipeline real,
   números contra a fonte), não aceito pelo resumo dela.
5. **O repositório é público.** Nunca escrever segredo, dado da empresa onde o Raul trabalha,
   dado da carteira real, e-mail ou identificador pessoal em arquivo de coordenação.
6. **Data do relógio, não dedução.** Toda data nova vem do sistema (`date`).

## Papéis

| Quem | Papel | Pode | Não faz |
|---|---|---|---|
| **Claude do trabalho** | Integrador e revisor (padrão) | Escrever specs, dar o veredito, consolidar `CONTEXT.md` e `QUADRO.md`, fazer checkpoint, disparar o Codex | Aceitar entrega sem reconferir |
| **Codex do trabalho** | Implementador | Implementar uma spec, rodar a suíte, atualizar o status do próprio item, deixar diário | Decidir escopo, editar `CONTEXT.md`, empurrar sem a suíte verde |
| **IAs de casa** | Qualquer papel, com o mesmo regime | Implementar ou revisar; **quem fecha o dia atualiza `CONTEXT.md`** | Ignorar reservas, diário e quadro |
| **Raul** | Dono das decisões | Decidir os itens marcados **"Decisão do Raul"** no quadro | — |

Quando uma IA não sabe o que as outras fizeram, ela roda `equipe iniciar`: ele conta.

## Ciclo de uma sessão

```
equipe iniciar        # estado, reservas, diário recente, dados, CI
equipe reservar 1.2   # anuncia o que vai tocar (cria e empurra a reserva)
...trabalho...        # suíte verde antes de empurrar
equipe fechar --resumo "..." --proximo "..."
```

`equipe iniciar --prompt` imprime o prompt de retomada pronto para colar em qualquer IA.

## Regras anti-colisão

1. **Começar com `equipe iniciar`** (faz `git fetch` e mostra o que mudou).
2. **Reservar antes de editar.** A reserva é um arquivo em `docs/coordenacao/reservas/`,
   empurrado na hora. Duas reservas do mesmo item colidem no push, e isso é o sinal.
3. **Árvore suja que não é sua é trabalho de outra IA.** Não sobrescrever, não rodar
   `git checkout --`, não apagar. Ler `git diff`, a reserva e o diário, e perguntar ao Raul.
   (Já aconteceu: uma sessão deixou 14 arquivos sem commit e sem aviso.)
4. **`git pull --rebase --autostash` antes de todo push.** O robô do GitHub commita em `main`
   por volta de 6 vezes por semana; só mexe em `dados/*.json`, que o `equipe` ignora no status.
   Push pequeno e frequente.
5. **Suíte verde antes do push** (`ruff check .` e `pytest tests/ -q --cov=.`, o comando exato do
   CI; `python -m pytest` esconde erros de importação que só o executável `pytest` mostra);
   commit escopado por caminho, nunca `git add -A` às cegas; mensagem por arquivo (`git commit -F`).
6. **Fechar com `equipe fechar`.** Reserva esquecida vence em 24 h e o `iniciar` avisa.
7. **Parar nas decisões do Raul.** Item com "Decisão do Raul" no quadro não avança sem ele.
8. **Conferir o CI depois do push.** Teste local verde não basta: o CI roda em Linux, com
   instalação limpa. O `equipe iniciar` mostra o último CI concluído da `main`; **CI vermelho é
   prioridade zero**, antes de qualquer item. (Já aconteceu: ficou vermelho 11 execuções seguidas,
   de 09 a 13/10, sem ninguém perceber, por um erro de importação que só o executável `pytest` revela.)

## Formatos dos arquivos

Todos em Markdown com um bloco inicial `---` de campos `chave: valor` (uma linha por campo,
sem aninhamento, listas separadas por vírgula), seguido do texto livre. Datas em ISO
(`AAAA-MM-DDTHH:MM`, horário local). Nomes de arquivo sem acento.

### `reservas/<item>.md` (um por tarefa em andamento; o nome é o ID do item, ex.: `1.2.md`)

```
---
item: 1.2
agente: codex
maquina: trabalho
desde: 2026-10-13T11:20
expira: 2026-10-14T11:20
arquivos: ativos/ui/pagina_qualidade.py, tests/test_qualidade_ui.py
---
Texto livre opcional (o que pretende fazer).
```

### `diario/AAAA-MM-DD_HHMM_<maquina>-<agente>.md` (um por sessão; imutável depois de criado)

```
---
data: 2026-10-13T11:30
maquina: trabalho
agente: claude
itens: 1.2, 1.3
commit: e121edc
suite: 369 passed
cobertura: 87.3
---
# Título curto da sessão
## O que fiz
## Decisões
## O que falta
## Perguntas ao Raul
```

### `ideias/AAAA-MM-DD_<slug>.md`

```
---
data: 2026-10-13
origem: claude-trabalho
status: nova            # nova | aceita | no-roteiro | descartada
---
# Título
## Problema
## Proposta
## Custo e risco
```

### `decisoes/AAAA-MM-DD_<slug>.md`

```
---
data: 2026-10-13
quem: raul
status: vigente         # vigente | substituida
---
# Título
## Decisão
## Por quê
## Alternativas rejeitadas
```

### `checkpoints/ckpt-NNN.md`

Campos `data`, `commit`, `suite`, `cobertura`, `ciclo`, `dados_cotacao`, `dados_gerado_em`,
seguidos do estado do ciclo em texto. Gerado por `equipe checkpoint`.

### `QUADRO.md` (tabela única, uma linha por item)

Colunas: `ID | Item | Status | Dono | Atualizado | Decisão do Raul | Notas`.
**Status:** `aberto`, `em andamento`, `pronto`, `bloqueado`. **Decisão do Raul:** `sim` ou vazio.
Quem muda o status do item edita só a própria linha. IDs seguem o plano em
`docs/product/DIAGNOSTICO_E_PLANO_2026-10-09.md` (mais o `0.x` de infraestrutura).

## Checkpoints

- **Sessão:** o diário que o `equipe fechar` grava.
- **Item:** quando o quadro vira `pronto`, o diário registra suíte e reconciliação.
- **Ciclo:** `equipe checkpoint --tag` ao fechar um ciclo do plano (`ckpt-001` = Ciclo 1).
  Cria `checkpoints/ckpt-NNN.md` e a tag git `ckpt-NNN`.

## Ideias e decisões

Qualquer IA (ou o Raul) abre uma ideia com `equipe ideia "título"` e registra uma decisão com
`equipe decisao "título"`. O integrador faz a triagem a cada ciclo: ideia aceita vai para
`docs/product/ROTEIRO_PROXIMAS_FASES.md` (status `no-roteiro`), a descartada fica com o motivo.
Decisão que muda outra marca a antiga como `substituida`.

## Dados de mercado

Os dados públicos (CVM e B3) devem estar iguais e frescos nas duas máquinas sem rodar nada à
mão (item 1.4 do plano). Enquanto a publicação automática não existe, o `iniciar` mostra a data
da cotação local e o comando para atualizar (`python -m scripts.baixar_dados_ativos` e
`python -m scripts.atualizar_ativos`). Os metadados dos dados entram em cada checkpoint.

## O que o GitHub faz por este protocolo

- **CI (`quality`)**: roda a suíte e os testes do protocolo (formato das reservas, sem reserva
  duplicada, nomes do diário, `QUADRO.md` válido, varredura de segredos). Não bloqueia a `main`.
- **Robôs** (`atualizar-curva`, `atualizar-focus`): tentam de novo com `git pull --rebase`.
- **Tags `ckpt-*`**: marcos de ciclo. Sem Issues, Project ou PR obrigatório por ora.

## Revisão do próprio protocolo

No checkpoint do Ciclo 1, o integrador revisa o que ninguém usou e **corta**. Protocolo que
vira cerimônia sem benefício deve encolher.
